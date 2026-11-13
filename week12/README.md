# Week 12 — Bacterial Variant Calling and Functional Annotation

## 1. Overview

### Objective

The objective of Week 12 was to develop a practical understanding of bacterial whole-genome sequencing (WGS) analysis, starting with raw sequencing reads and ending with functional annotation of detected variants.

The workflow covered:

1. Preparing a bacterial reference genome.
2. Aligning paired-end sequencing reads to the reference.
3. Inspecting alignment quality.
4. Calling SNPs and small insertions/deletions (indels).
5. Filtering candidate variants.
6. Investigating read-level evidence for selected variants.
7. Understanding bacterial genome annotation and GFF3 structure.
8. Annotating variants using SnpEff.
9. Interpreting predicted effects on genes and proteins.

The emphasis was not simply on obtaining a VCF file. It was on understanding what each tool does, why it was selected, how to recognize problems, and how to interpret the output without overstating the evidence.

### Dataset

We used sequencing sample **SRR2589044**, from the *Escherichia coli* B REL606 lineage associated with the Long-Term Evolution Experiment (LTEE).

This is an experimental evolution dataset, not an antimicrobial resistance study. It was selected as a practical bacterial variant-analysis dataset.

| Item | Details |
|---|---|
| Organism | *Escherichia coli* B |
| Reference strain | REL606 |
| Sample | SRR2589044 |
| Reference accession | NC_012967.1 |
| Assembly accession | GCF_000017985.1 |
| Assembly name | ASM1798v1 |
| Reference length | 4,629,812 bp |
| Annotation source | NCBI RefSeq |
| Annotation date | 13 June 2025 |

### Main tools

| Tool | Version | Purpose |
|---|---|---|
| BWA | 0.7.19-r1273 | Read alignment |
| SAMtools | Version used in the environment | BAM processing and inspection |
| BCFtools | 1.22 | Variant calling and filtering |
| HTSlib | 1.22.1 | Supporting sequence-file operations |
| SnpEff | 5.4c | Functional consequence annotation |

All tools were run in the Conda environment named `bioml`.

---

## 2. Reference genome preparation

### Why a reference genome?

Variant calling requires a reference against which sequencing reads can be compared. The reference provides the coordinate system for identifying substitutions, insertions, and deletions.

We used the complete REL606 reference genome:

`week12/reference/ecoli_B_REL606.fasta`

The corresponding accession was NC_012967.1.

### Indexing with BWA

BWA requires an indexed reference genome before it can efficiently align sequencing reads.

We used:

```bash
bwa index week12/reference/ecoli_B_REL606.fasta
```

This generated the index files required by BWA.

We also generated a FASTA index using SAMtools:

```bash
samtools faidx week12/reference/ecoli_B_REL606.fasta
```

The `.fai` file provides sequence names, lengths, and offsets that allow efficient access to reference sequences.

### Important distinction

BWA indexing and FASTA indexing are not the same operation:

- `bwa index` prepares the reference for read alignment.
- `samtools faidx` prepares the reference for rapid sequence retrieval.

Both were required by different parts of the workflow.

---

## 3. Read alignment

### Why BWA-MEM?

Before identifying variants, sequencing reads must be mapped to the reference genome.

We used BWA-MEM because it is a widely used short-read aligner and is suitable for paired-end bacterial WGS data.

The trimmed paired-end reads were:

- `data/raw_fastq/SRR2589044_1.trim.fastq`
- `data/raw_fastq/SRR2589044_2.trim.fastq`

BWA-MEM was used to align these reads against the REL606 reference.

The general alignment command structure was:

```bash
bwa mem -t 4 \
  -R '@RG\tID:SRR2589044\tSM:SRR2589044\tPL:ILLUMINA' \
  week12/reference/ecoli_B_REL606.fasta \
  data/raw_fastq/SRR2589044_1.trim.fastq \
  data/raw_fastq/SRR2589044_2.trim.fastq \
  > week12/alignment/SRR2589044.sam
```

The read-group information identifies the sequencing sample in the alignment file. This becomes useful when handling multiple samples or downstream analyses that use sample metadata.

### SAM to BAM conversion and sorting

The SAM file is a text-based alignment format. BAM is its compressed binary equivalent and is more efficient for storage and downstream processing.

The alignment was converted to BAM, sorted, and indexed using SAMtools.

Typical commands:

```bash
samtools view -bS week12/alignment/SRR2589044.sam \
  -o week12/alignment/SRR2589044.bam
```

```bash
samtools sort week12/alignment/SRR2589044.bam \
  -o week12/alignment/SRR2589044.sorted.bam
```

```bash
samtools index week12/alignment/SRR2589044.sorted.bam
```

The sorted BAM and its index were used for subsequent variant calling and read-level inspection.

### Alignment quality assessment

We used:

```bash
samtools flagstat week12/alignment/SRR2589044.sorted.bam
```

Key results:

| Metric | Result |
|---|---:|
| Total reads | 1,789,959 |
| Mapped reads | 99.94% |
| Properly paired reads | 95.83% |

### Interpretation

The high mapping percentage indicates that nearly all reads could be aligned to the REL606 reference.

The high proportion of properly paired reads also suggests that most read pairs mapped in an expected orientation and distance.

However, these metrics do not prove that every alignment is correct. They do not establish uniform coverage, unique mapping, or the authenticity of individual variants.

**Important limitation:** We did not perform duplicate marking. Therefore, a zero-duplicate count in `flagstat` must not be interpreted as evidence that the dataset contains no PCR duplicates. Duplicate reads that have not been marked cannot be counted as marked duplicates.

---

## 4. Variant calling with BCFtools

### Why BCFtools?

After alignment, the next task was to identify differences between the sequencing reads and the reference genome.

We used BCFtools for variant calling.

BCFtools is suitable for bacterial variant analysis. Bacterial genomes are generally haploid, so we explicitly specified haploid ploidy during variant calling.

### Step 1: Generate pileup information

We used `bcftools mpileup` to summarize read evidence at genomic positions.

The analysis included:

- Minimum mapping quality: 20
- Minimum base quality: 20
- Read depth (DP)
- Allelic depth (AD)

The command structure was:

```bash
bcftools mpileup \
  -q 20 \
  -Q 20 \
  -a FORMAT/DP,FORMAT/AD \
  -f week12/reference/ecoli_B_REL606.fasta \
  week12/alignment/SRR2589044.sorted.bam \
  -Ou
```

Here:

- `-q 20` sets the minimum mapping quality.
- `-Q 20` sets the minimum base quality.
- `FORMAT/DP` records read depth.
- `FORMAT/AD` records the number of reads supporting reference and alternate alleles.
- `-Ou` outputs uncompressed BCF for efficient piping into another BCFtools command.

### Step 2: Call variants

We used the multiallelic caller with haploid ploidy:

```bash
bcftools call \
  --ploidy 1 \
  -m \
  -v \
  -Oz \
  -o week12/variants/SRR2589044.raw.vcf.gz
```

The complete workflow pipes the output of `mpileup` directly into `call`.

The important options were:

- `--ploidy 1`: treats the organism as haploid.
- `-m`: uses the multiallelic calling model.
- `-v`: outputs variant sites rather than all sites.
- `-Oz`: produces compressed VCF output.

### Initial result

The raw VCF contained:

- 15 total variant records
- 11 SNPs
- 4 indels

At this stage, the variants were candidates, not validated mutations.

### Understanding the VCF FILTER field

One important observation was that the raw VCF contained a FILTER value of `.`.

This does **not** mean that the variants passed filtering.

It means that no filter status had been assigned.

This distinction matters because a variant with FILTER `.` should not automatically be treated as a high-confidence PASS variant.

---

## 5. Variant filtering

We applied a provisional filter:

```text
QUAL >= 30 && FORMAT/DP >= 10
```

This retained nine variants:

- 6 SNPs
- 3 indels

The purpose was to remove candidates with weak quality scores or insufficient read depth.

### Important limitation

These thresholds were used as practical teaching criteria. They are not universal thresholds for bacterial variant calling.

A more rigorous analysis would also consider:

- Mapping quality distribution
- Base quality distribution
- Strand bias
- Allele fraction
- Read position bias
- Local sequence complexity
- Repetitive regions
- Evidence from independent sequencing or validation

A high QUAL score or read depth alone does not prove that a variant is genuine.

---

## 6. Read-level inspection

Variant callers summarize evidence, but it is important to understand what the underlying reads actually show.

We therefore inspected selected candidate variants using SAMtools pileup and alignment information.

### Understanding pileup notation

In the pileup output:

| Symbol | Meaning |
|---|---|
| `.` | Reference base on a forward-strand read |
| `,` | Reference base on a reverse-strand read |
| `A`, `C`, `G`, `T` | Alternate base on a forward-strand read |
| `a`, `c`, `g`, `t` | Alternate base on a reverse-strand read |
| `-2GG` | A deletion of two reference bases, represented in the pileup notation |

This allowed us to distinguish reference-supporting reads from alternate-supporting reads and examine strand representation.

### Understanding CIGAR strings

We also examined read alignments and CIGAR strings.

For example:

```text
113M2D37M
```

means:

- 113 aligned bases
- 2 deleted reference bases
- 37 additional aligned bases

This indicates that the alignment contains matched sequence on both sides of a two-base deletion.

We also encountered an `NM:i:2` tag. This indicates two differences between the read and reference in the alignment, consistent with the two-base deletion in this example.

### Mapping quality

Some inspected reads had:

```text
MAPQ = 60
```

This represents high mapping confidence according to the aligner's scoring system.

However, MAPQ is not a direct measure of base-call quality, and it does not independently prove that the observed deletion is authentic.

### Candidate at position 4431393

One particularly useful example was the candidate deletion at position 4431393.

The evidence included:

- Read depth: 56
- Alternate-supporting reads: 55
- Allele fraction: approximately 98.2%
- Evidence from both read orientations
- MAPQ 60 in the inspected reads
- CIGAR evidence containing `2D`
- MD tag showing `^GG`

This provided strong read-level support for the deletion.

However, read-level support is not the same as independent experimental validation. A definitive confirmation would require an independent method, such as bidirectional Sanger sequencing, ideally using a single-colony isolate if the biological sample may contain a mixed population.

### A useful lesson

A variant caller gives us a candidate. Read-level inspection helps us evaluate its evidence. Experimental validation provides a separate level of confirmation.

These are three different stages and should not be conflated.

---

## 7. Investigating the bacterial annotation file

Before functional annotation, we needed a genome annotation file describing the locations and structures of genes and coding sequences.

We downloaded the NCBI RefSeq GFF3 annotation corresponding to the same REL606 reference assembly.

Files:

- `week12/annotation/REL606_genomic.gff.gz`
- `week12/annotation/REL606_genomic.gff`

The GFF3 header confirmed:

- Assembly: GCF_000017985.1
- Assembly name: ASM1798v1
- Sequence accession: NC_012967.1
- Genome coordinates: 1–4,629,812
- Annotation date: 13 June 2025

Using the exact reference and its corresponding annotation is important. A mismatch in genome version or coordinate system can result in incorrect functional annotations.

### GFF3 annotation audit

We examined the feature counts and relationships in the annotation file.

| Feature | Count |
|---|---:|
| Genes | 4,320 |
| CDS features | 4,431 |
| tRNA features | 85 |
| Protein-coding genes | 4,204 |
| Pseudogenes | 187 |
| rRNA genes | 22 |

The annotation also contained several other RNA biotypes.

All 4,431 CDS features had an associated gene or pseudogene parent.

However, the number of CDS records was greater than the number of unique CDS identifiers.

There were:

- 4,431 CDS records
- 4,391 unique CDS identifiers

This difference required investigation.

### Why were there more CDS records than unique CDS identifiers?

We discovered that 40 protein-coding genes had multiple CDS segments.

These were associated with programmed ribosomal frameshifting, also called ribosomal slippage.

In these cases, the annotated coding sequence is represented by multiple feature records rather than one uninterrupted CDS feature.

This is biologically meaningful and should not automatically be treated as an annotation error.

### Understanding CDS phase

The GFF3 CDS phase indicates how many bases at the beginning of a CDS feature must be skipped to reach the next complete codon, taking the strand and feature structure into account.

We observed:

| Phase | Number of CDS features |
|---|---:|
| 0 | 4,392 |
| 1 | 1 |
| 2 | 38 |

All CDS features had a defined phase.

This was useful when investigating the split CDS records and understanding why a bacterial annotation may contain multiple CDS features for a single protein.

### Example: conventional CDS — thrA

The `thrA` gene (`ECB_RS00010`) was located at:

- Coordinates: 336–2798
- Strand: positive
- One CDS feature
- Phase: 0

This was a conventional, uninterrupted coding sequence.

### Example: programmed frameshift

One example was `ECB_RS10260`.

It contained two CDS segments on the negative strand:

- 2034789–2035038, phase 0
- 2034341–2034789, phase 2

For a negative-strand gene, the translation order is from higher to lower genomic coordinates.

This matters when interpreting CDS order and phase. Simply reading the coordinates from low to high would give the wrong biological order for this gene.

---

## 8. Attempting consequence annotation with BCFtools csq

### Why did we investigate BCFtools csq?

BCFtools includes `csq`, a tool for predicting the consequences of variants using genome annotation.

Since we were already using BCFtools for variant calling, it was reasonable to investigate whether the same software could also perform consequence annotation.

### The problem

Our original NCBI GFF3 annotation used a direct gene-to-CDS relationship.

However, BCFtools `csq` expects a transcript hierarchy in its supported Ensembl-style GFF3 input structure.

When we supplied the original NCBI GFF3, the parser did not recognize the CDS features as expected and reported zero CDSs.

This was a compatibility issue involving the annotation hierarchy, not evidence that BCFtools cannot be used for bacterial variant calling.

### Testing a simplified annotation

To understand the problem, we created a minimal test annotation for `thrA` with an explicit hierarchy:

```text
gene
  └── mRNA
        └── CDS
```

The test annotation was successfully parsed and one CDS was recognized.

We then tested a gene containing multiple CDS segments.

Although the CDS segments were parsed, BCFtools produced an overlap warning.

This was another indication that adapting the annotation structure would require additional care, particularly for programmed frameshift genes.

### Decision

We did not continue converting the entire NCBI GFF3 file for `bcftools csq`.

This would have added unnecessary complexity to a teaching workflow when a dedicated consequence annotation tool was available.

The important lesson was:

**A tool can support bacterial variant analysis while still requiring a particular annotation-file structure for its consequence annotation module.**

We therefore retained BCFtools for variant calling and selected SnpEff for functional annotation.

---

## 9. Choosing SnpEff for functional annotation

### Why SnpEff?

SnpEff is designed to predict the functional effects of genetic variants.

It can classify variants according to their predicted consequences, including:

- Synonymous variants
- Missense variants
- Stop-gained variants
- Frameshift variants
- Upstream and downstream variants
- Intergenic variants

SnpEff is suitable for bacterial genomes, including custom reference databases.

### Installation problem

Initially, the Conda environment did not contain SnpEff.

We checked for the package and attempted to identify the correct installation route.

The first package lookup did not find an available package under the name we tried.

We resolved this by installing the versioned Bioconda package:

```bash
conda install -c bioconda snpeff=5.4.0c
```

SnpEff 5.4c was then available in the `bioml` environment.

### First attempt: using a prebuilt database

SnpEff already had a prebuilt database for:

`Escherichia_coli_b_str_rel606`

It was tempting to use this database directly.

However, closer inspection revealed important differences:

- It was based on Ensembl Genomes release 46.
- Its retrieval date was 26 January 2020.
- It contained 4,533 genes.
- It contained 4,380 protein-coding genes.
- It contained 4,210 CDS records.
- It produced numerous database integrity warnings.

The reported database checks included length, start-codon, and stop-codon errors.

The chromosome name was also `Chromosome`, whereas our VCF used `NC_012967.1`.

Although the `thrA` coordinates matched after accounting for coordinate conventions, the database was not the exact annotation source used for our reference.

### Why we did not use the prebuilt database

A prebuilt database is not automatically the best database for every analysis.

For reliable annotation, the reference sequence and its annotation should match the genome used during alignment and variant calling.

We therefore decided to build a custom SnpEff database using the exact GenBank record corresponding to NC_012967.1.

This avoided relying on an older, independently maintained annotation.

---

## 10. Building a custom SnpEff database

### Step 1: Download the exact GenBank record

We downloaded the GenBank record from NCBI using the accession NC_012967.1.

```bash
curl -L "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=nuccore&id=NC_012967.1&rettype=gbwithparts&retmode=text" \
  -o week12/annotation/REL606_NC_012967.1.gb
```

The download completed successfully.

The file contained the reference sequence and its annotated genomic features.

### Step 2: Configure SnpEff

SnpEff requires a genome entry in its configuration file.

We added:

```text
NC_012967.1.genome : E_coli_REL606
```

to:

```text
~/miniforge3/envs/bioml/share/snpeff-5.4.0c-0/snpEff.config
```

The left-hand identifier is the genome database name used in the SnpEff configuration. The right-hand side is the genome description.

### Step 3: Place the GenBank file in the expected directory

SnpEff expects the GenBank file to be located in its data directory under the configured genome identifier.

We placed it at:

```text
~/miniforge3/envs/bioml/share/snpeff-5.4.0c-0/data/NC_012967.1/genes.gbk
```

### Step 4: Build the database

We ran:

```bash
snpEff build -genbank -v NC_012967.1
```

The build completed successfully.

### Build results

The output included:

- Reference chromosome: NC_012967.1
- Genome length: 4,629,812 bp
- Exons created for 4,391 transcripts
- 4,431 exon sequences added
- 187 transcripts marked as noncoding
- Protein check: 4,204 OK
- 187 not found
- 0 errors

The 187 missing proteins corresponded to the noncoding/pseudogene component of the annotation and were not reported as protein-sequence errors.

SnpEff also reported that optional files such as `protein.fa`, regulation files, or motif files were absent.

These warnings did not prevent database construction. The build had successfully used the GenBank record and completed its protein check.

### Important lesson

The database build was not just a technical installation step. It was an opportunity to verify that the annotation was being built from the intended reference and that the coding sequences were being interpreted consistently.

---

## 11. Functional annotation of the variants

Once the custom database was ready, we annotated the filtered VCF:

```bash
snpEff NC_012967.1 \
  week12/variants/SRR2589044.filtered.vcf.gz \
  > week12/variants/SRR2589044.snpeff.vcf
```

The command did not necessarily print a detailed result to the terminal. This was expected because the annotated VCF was redirected to an output file.

We checked the number of variant records:

```bash
grep -v '^#' week12/variants/SRR2589044.snpeff.vcf | wc -l
```

The output was:

```text
9
```

All nine filtered variants were retained in the annotated VCF.

### Predicted consequences

| Position | Gene | Predicted effect | Impact | Protein consequence |
|---:|---|---|---|---|
| 648692 | `mrdB` | Missense | MODERATE | p.Arg69His |
| 1331794 | `topA` | Missense | MODERATE | p.Thr792Lys |
| 1733343 | `pykF` | Missense | MODERATE | p.Asp127Asn |
| 2103887 | `ECB_RS23820` | Frameshift | HIGH | p.Arg62fs |
| 3444175 | `dam` | Missense | MODERATE | p.Pro141Thr |
| 3481820 | `malT` | Missense | MODERATE | p.Thr46Ala |
| 3893550 | Between `kup` and `ECB_RS25215` | Intergenic insertion | MODIFIER | No protein consequence |
| 4100183 | `hslU` | Missense | MODERATE | p.Ser350Pro |
| 4431393 | `tamB` | Frameshift | HIGH | p.Gly1176fs |

### Summary

The nine filtered variants were classified as:

| Consequence | Number |
|---|---:|
| Missense variants | 6 |
| Frameshift variants | 2 |
| Intergenic insertion | 1 |
| **Total** | **9** |

### Understanding the predicted effects

A missense variant changes an amino acid in the predicted protein sequence.

For example:

```text
p.Arg69His
```

means that the reference amino acid arginine at protein position 69 is predicted to be replaced by histidine.

A frameshift variant changes the reading frame of the coding sequence.

For example:

```text
p.Gly1176fs
```

indicates a predicted frameshift beginning at the glycine at position 1176.

A frameshift can have a substantial effect on protein sequence and function, but its actual biological effect still requires investigation.

An intergenic variant is located between annotated genes and does not directly alter a protein-coding sequence. It may still affect regulatory elements or gene expression, depending on its location and surrounding biology.

### Important distinction: predicted impact is not measured function

SnpEff assigns impact categories such as:

- HIGH
- MODERATE
- LOW
- MODIFIER

These categories describe predicted consequences based on annotation rules.

They do not directly measure protein activity, gene expression, bacterial fitness, or phenotype.

For example, a frameshift predicted as HIGH impact is not automatically proof that the gene is nonfunctional in the experimental organism.

Likewise, a missense mutation classified as MODERATE may have little, substantial, or no measurable effect on protein function.

---

## 12. Allele fractions and interpretation of indels

The three retained indels had different allele fractions.

| Position | Reference-supporting reads | Alternate-supporting reads | Total depth | Alternate allele fraction |
|---:|---:|---:|---:|---:|
| 2103887 | 8 | 27 | 35 | 77.1% |
| 3893550 | 3 | 40 | 43 | 93.0% |
| 4431393 | 1 | 55 | 56 | 98.2% |

The allele fraction was calculated as:

```text
Alternate allele fraction = Alternate-supporting reads / Total read depth
```

For example:

```text
27 / 35 = 0.771 = 77.1%
```

### What does an allele fraction below 100% mean?

It does not automatically mean that the variant is false.

Possible explanations include:

- A mixed population containing more than one genotype.
- Sequencing errors.
- Local mapping ambiguity.
- Repeat-associated alignment problems.
- Differences in read quality or coverage.

The allele fraction must be interpreted alongside the local read evidence and biological context.

The deletion at position 4431393 had the highest alternate allele fraction and strong read-level support in the reads we inspected. It is therefore a particularly strong candidate, although independent validation is still needed.

---

## 13. Problems encountered and how we resolved them

This section records the important troubleshooting lessons from Week 12.

### Problem 1: SnpEff was not installed

**What happened:** The initial package lookup did not find SnpEff.

**Why it happened:** The package was not installed in the active Conda environment, and the initial package name/lookup did not identify the versioned package.

**How we resolved it:** We installed SnpEff 5.4c from Bioconda:

```bash
conda install -c bioconda snpeff=5.4.0c
```

**Lesson:** Before running a bioinformatics tool, verify that it is installed in the active environment. Also verify that the environment is the one intended for the project.

### Problem 2: The prebuilt REL606 SnpEff database was not an exact match

**What happened:** A prebuilt database was available, but it contained different annotation counts and integrity warnings.

**Why it mattered:** A database based on a different annotation release may not represent the exact genome annotation used for the analysis.

**How we resolved it:** We abandoned the prebuilt database and downloaded the exact GenBank record for NC_012967.1 from NCBI.

**Lesson:** Matching the reference genome and annotation provenance is more important than convenience.

### Problem 3: SnpEff configuration did not initially contain the custom genome

**What happened:** SnpEff needed a genome identifier in its configuration file before it could build the custom database.

**How we resolved it:** We added:

```text
NC_012967.1.genome : E_coli_REL606
```

to the active SnpEff configuration file.

**Lesson:** A custom database requires both the sequence annotation file and a correctly configured genome identifier.

### Problem 4: SnpEff could not use the GenBank file until it was in the expected location

**What happened:** The GenBank file had been downloaded into the project directory, but SnpEff expects custom database files in its own data directory.

**How we resolved it:** We placed the file at:

```text
data/NC_012967.1/genes.gbk
```

within the active SnpEff installation directory.

**Lesson:** Bioinformatics tools often follow specific directory and naming conventions. A correct input file in the wrong location may not be recognized.

### Problem 5: BCFtools csq reported zero CDS features

**What happened:** The original NCBI GFF3 annotation was supplied to `bcftools csq`, but the parser did not recognize the CDS features.

**Why it happened:** The original NCBI GFF3 used a direct gene-to-CDS hierarchy, while the `csq` parser expected a transcript hierarchy in its supported GFF3 structure.

**How we investigated it:** We created a simplified `thrA` test annotation with an explicit gene → mRNA → CDS relationship. The CDS was then recognized.

**How we resolved it:** We did not convert the entire annotation for `csq`. We selected SnpEff for consequence annotation instead.

**Lesson:** Do not assume that every tool accepts every valid version of a file format. File structure and parser expectations matter.

### Problem 6: Multiple CDS records were initially confusing

**What happened:** There were 4,431 CDS features but only 4,391 unique CDS identifiers.

**Why it mattered:** It was not immediately clear whether the extra records represented duplicated or malformed annotations.

**How we investigated it:** We examined the genes with multiple CDS features and their annotation notes.

**What we found:** All 40 multiple-CDS protein-coding genes were annotated with programmed frameshift/ribosomal slippage information.

**How we resolved it:** We interpreted these as biologically meaningful split CDS annotations rather than automatically treating them as errors.

**Lesson:** Annotation files describe biological complexity. Unexpected feature counts should be investigated before being labelled as errors.

### Problem 7: BCFtools csq produced an overlap warning for a split CDS

**What happened:** A test annotation containing multiple CDS segments was parsed but generated an overlap warning.

**How we handled it:** We documented the behaviour and stopped expanding the test because SnpEff had already provided a suitable annotation route.

**Lesson:** A troubleshooting exercise should have a clear stopping point. Once the objective is achieved using an appropriate alternative, further tool adaptation may not add enough value to justify the time.

### Problem 8: SnpEff build produced warnings about optional files

**What happened:** The custom database build reported that some optional files, such as protein or regulatory files, were absent.

**How we evaluated it:** We examined the overall build output rather than assuming that every warning represented a failed build.

**What we found:** The reference sequence was loaded, the expected transcripts and exon sequences were created, and the protein check completed with zero errors.

**How we resolved it:** We proceeded because the database build itself had succeeded.

**Lesson:** Distinguish fatal errors from warnings about optional inputs. Evaluate whether the required output was successfully generated.

---

## 14. Final workflow and tool choices

The final workflow was:

```text
Trimmed paired-end FASTQ reads
             |
             v
       BWA-MEM alignment
             |
             v
          SAM file
             |
             v
     SAMtools conversion
             |
             v
       Sorted BAM + index
             |
             v
       BCFtools mpileup
             |
             v
       BCFtools call
             |
             v
          Raw VCF
             |
             v
     Variant quality filtering
             |
             v
        Filtered VCF
             |
             v
       SnpEff annotation
             |
             v
      Annotated VCF
             |
             v
     Predicted consequences
```

The annotation database was built separately from the exact NCBI GenBank record for the same reference genome.

### Why this combination?

| Tool | Why it was selected |
|---|---|
| BWA-MEM | To align short paired-end reads to the bacterial reference |
| SAMtools | To convert, sort, index, and inspect alignments |
| BCFtools | To generate pileup evidence and call haploid bacterial variants |
| SnpEff | To predict the functional consequences of variants |
| NCBI GenBank | To build a custom annotation database matching the exact reference accession |

BCFtools `csq` was investigated but not retained as the primary consequence annotation tool because of the GFF3 hierarchy issue encountered with the NCBI annotation.

A microbial resequencing pipeline such as breseq could be considered for an independent comparison in a future exercise. It was not part of the completed Week 12 workflow.

---

## 15. Final results

The Week 12 analysis successfully progressed from paired-end reads to an annotated set of nine candidate variants.

### Key results

- 99.94% of reads mapped to the REL606 reference.
- 95.83% of reads were properly paired.
- 15 raw variant records were initially called.
- Nine variants were retained after provisional quality filtering.
- The retained variants included six SNPs and three indels.
- All nine variants were annotated using a custom SnpEff database built from the exact NCBI GenBank record.
- Six variants were predicted to cause missense changes.
- Two were predicted to cause frameshifts.
- One was an intergenic insertion.

### Final annotated variants

| Position | Gene/region | Consequence |
|---:|---|---|
| 648692 | mrdB | p.Arg69His |
| 1331794 | topA | p.Thr792Lys |
| 1733343 | pykF | p.Asp127Asn |
| 2103887 | ECB_RS23820 | p.Arg62fs |
| 3444175 | dam | p.Pro141Thr |
| 3481820 | malT | p.Thr46Ala |
| 3893550 | kup / ECB_RS25215 intergenic region | Intergenic insertion |
| 4100183 | hslU | p.Ser350Pro |
| 4431393 | tamB | p.Gly1176fs |

---

## 16. Limitations and responsible interpretation

The analysis achieved its technical learning objectives, but several limitations must be acknowledged.

1. **Variant filtering was provisional.** QUAL ≥ 30 and DP ≥ 10 were practical thresholds, not universally validated criteria.

2. **Duplicate marking was not performed.** The reported duplicate count cannot establish that PCR duplicates were absent.

3. **Mapping statistics are not sufficient to establish variant authenticity.** High overall mapping percentages do not guarantee that every read or variant is correctly aligned.

4. **Read-level inspection was limited to selected candidates.** The inspected deletion at position 4431393 had strong supporting evidence, but not every candidate received the same depth of investigation.

5. **Allele fractions below 100% require careful interpretation.** They may reflect biological heterogeneity or technical effects.

6. **SnpEff predicts consequences.** It does not experimentally establish gene disruption, altered protein activity, or a phenotype.

7. **No independent validation was performed.** Sanger sequencing or another orthogonal method would be needed to validate selected variants.

8. **This was a single-sample teaching analysis.** The results should not be used to make broad evolutionary or functional claims.

9. **The dataset is from an LTEE *E. coli* B context.** The analysis does not establish anything about antimicrobial resistance or the effects of polyphenols.

---

## 17. What I learned

The most important outcome of Week 12 was not simply learning to run BWA, SAMtools, BCFtools, or SnpEff. It was understanding the logic connecting the stages of bacterial genome analysis.

The main lessons were:

- Read alignment is the foundation of variant calling.
- Mapping statistics must be interpreted critically.
- Variant calls are candidates supported by read evidence, not automatically confirmed mutations.
- Allele depth and allele fraction provide important information beyond the variant quality score.
- Bacterial genomes are generally haploid, and this should be reflected in variant-calling parameters.
- Annotation files require careful inspection; their structure can affect downstream tools.
- Multiple CDS records may represent real biological features, such as programmed ribosomal frameshifting.
- A prebuilt annotation database should not be used blindly when an exact reference-matched database can be constructed.
- BCFtools can be used for bacterial variant calling even when its `csq` annotation parser requires a particular GFF3 hierarchy.
- SnpEff provides a practical route to bacterial consequence annotation using a custom GenBank database.
- Predicted consequences must not be confused with experimentally demonstrated functional effects.

### Final assessment

Week 12 is complete. We have established a working bacterial WGS variant-calling and annotation workflow, learned how to troubleshoot annotation compatibility problems, and produced a set of nine annotated candidate variants.

The next step in a more rigorous analysis would be to investigate selected variants in greater depth, assess their read-level evidence systematically, and validate important candidates independently. Those steps are beyond the main learning objective of this week.
