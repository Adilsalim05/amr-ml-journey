# Week 6 — RNA-seq Quality Control, Trimming, and HISAT2 Alignment

## 1. Week 6 objective

The goal of Week 6 was to learn a complete RNA-seq preprocessing and alignment workflow, from raw paired-end FASTQ reads through quality control, adapter/quality trimming, reference indexing, HISAT2 alignment, BAM processing, and alignment QC.

This week was deliberately treated as a **learning workflow**, not as a publication-ready analysis of the complete GSE50760 dataset.

The major workflow was:

```text
Raw paired-end FASTQ
        ↓
FastQC
        ↓
Trimmomatic
        ↓
Post-trimming FastQC
        ↓
Reference genome
        ↓
HISAT2 index
        ↓
HISAT2 alignment
        ↓
SAM
        ↓
BAM
        ↓
Coordinate-sorted BAM
        ↓
BAM index (.bai)
        ↓
samtools flagstat
```

---

## 2. Dataset used

### GEO dataset

- GEO accession: **GSE50760**
- Organism: **Homo sapiens**
- Biological context: normal colon, primary colorectal cancer, and liver metastasis samples
- Sequencing platform: Illumina HiSeq 2000
- Read type: paired-end
- Read length: approximately 2 × 100 bp
- Library preparation: TruSeq RNA Sample Prep v2
- Genome build reported in the study metadata: **hg19**

### Teaching subset

Because the complete sequencing data were too large for the available disk space, one SRA run was used as a small teaching subset:

- SRA run: **SRR975567**
- Original subset: **100,000 paired fragments**
- Reads are the **first 100,000 paired records**, not a random sample.
- Therefore the subset may not represent the complete sequencing run.

The raw files were:

```text
week6/raw_rnaseq/SRR975567_1.fastq
week6/raw_rnaseq/SRR975567_2.fastq
```

Each contains 100,000 reads.

---

# 3. FASTQ concepts

FASTQ stores sequencing reads and their base-quality information.

Each read normally occupies four lines:

```text
@read_identifier
SEQUENCE
+
QUALITY_STRING
```

The sequence contains the observed nucleotide bases.

The quality string contains one quality character for each base. These characters encode **Phred quality scores**.

Higher Phred score = greater confidence in the base call.

For paired-end sequencing:

- R1 = first mate
- R2 = second mate

The two reads originate from opposite ends of the same original DNA/cDNA fragment.

Paired-end information is useful because knowing both ends of a fragment provides additional information about where the fragment belongs in the reference.

---

# 4. Raw-read quality control with FastQC

FastQC was run before trimming.

The purpose of FastQC is **diagnostic**:

> It tells us what properties of the sequencing data may require attention.

FastQC does not automatically tell us that every FAIL means the data are unusable, and the goal should not be to make every FastQC box green.

## Raw FastQC summary

Both R1 and R2 initially showed:

- Basic Statistics: PASS
- Per-base sequence quality: **FAIL**
- Per-tile sequence quality: PASS
- Per-sequence quality scores: PASS
- Per-base sequence content: **FAIL**
- Per-sequence GC content: PASS
- Per-base N content: PASS
- Sequence length distribution: PASS
- Sequence duplication: PASS
- Adapter content: PASS
- R2 had an additional overrepresented-sequence warning

The most important initial problem was the declining **per-base quality toward the end of reads**.

## Important lesson

A sample can pass the **per-sequence quality** module while failing **per-base quality**.

These tests ask different questions:

- Per-sequence quality: Are complete reads generally of reasonable quality?
- Per-base quality: Does quality decline at particular positions within reads?

Thus, a poor-quality tail can produce a per-base failure without necessarily causing the entire read-level quality distribution to fail.

---

# 5. Why trimming was performed

The raw data showed poor-quality tails, so quality trimming was justified.

Trimming can:

- remove sequencing-adapter sequence,
- remove low-quality terminal regions,
- discard reads that become too short to be useful.

However:

> Trimming should be driven by evidence and downstream requirements, not by a desire to eliminate every FastQC warning.

---

# 6. Adapter selection

The study used:

**TruSeq RNA Sample Prep v2**

The Trimmomatic installation contained several adapter files.

The selected adapter file was:

```text
$CONDA_PREFIX/share/trimmomatic-0.41-0/adapters/TruSeq2-PE.fa
```

This was selected because the library preparation information was consistent with the TruSeq v2 paired-end adapter set.

---

# 7. Trimmomatic parameters

The corrected trimming order was:

```bash
ILLUMINACLIP:"$ADAPTERS":2:40:15 \
SLIDINGWINDOW:4:20 \
MINLEN:25
```

The order is important.

## ILLUMINACLIP

Removes sequencing adapter sequence.

The parameters used were:

```text
2:40:15
```

These control adapter matching/stringency behavior in Trimmomatic.

## SLIDINGWINDOW:4:20

Trimmomatic examines the read using a sliding window of 4 bases.

When the average quality within the window falls below Q20, the read is cut at that point.

This is intended to remove poor-quality tails.

## MINLEN:25

After the preceding operations, reads shorter than 25 bases are discarded.

---

# 8. Important debugging lesson: Trimmomatic operation order

The first version of the pipeline used:

```bash
SLIDINGWINDOW:4:20 \
MINLEN:25 \
ILLUMINACLIP:"$ADAPTERS":2:40:15
```

This produced an apparently impossible result:

**193 R2 reads shorter than 25 bp remained in the paired output.**

Investigation of one read showed:

```text
Raw R2:
~100 bp

After adapter removal:
CTG

Final paired read:
CTG
```

The explanation was the order of operations.

Trimmomatic applies processing steps **in the order specified**.

In the buggy version:

```text
raw read
   ↓
SLIDINGWINDOW
   ↓
MINLEN:25
   ↓
ILLUMINACLIP
   ↓
3 bp read remains
```

The read was longer than 25 bp when MINLEN was evaluated, so it survived. Adapter removal subsequently reduced it to 3 bp.

The corrected order is:

```text
raw read
   ↓
ILLUMINACLIP
   ↓
SLIDINGWINDOW
   ↓
MINLEN:25
   ↓
final read
```

Thus:

```text
~100 bp
   ↓
adapter removed
   ↓
3 bp
   ↓
MINLEN removes it
```

This was a genuine pipeline-order bug and an important lesson in reproducible bioinformatics:

> **Pipeline operations are not interchangeable. Their order can change the biological dataset that reaches downstream analysis.**

---

# 9. Corrected trimming results

The corrected pipeline was run into:

```text
week6/qc_trimmed_v2/
```

Paired output:

```text
R1 paired reads: 81,975
R2 paired reads: 81,975
```

Therefore:

```text
81,975 paired fragments retained
```

from the original:

```text
100,000 paired fragments
```

Retention:

```text
81,975 / 100,000 = 81.975%
```

Approximately **82% of the original paired fragments remained fully paired**.

Unpaired outputs contained:

```text
R1 unpaired: 8,793
R2 unpaired: 2,860
```

The remaining reads/fragments were removed during processing.

Exact reasons for every discarded read should not be inferred without the Trimmomatic log, but the substantial reduction demonstrates that trimming materially changed the dataset.

---

# 10. Post-trimming FastQC

After corrected trimming, both R1 and R2 showed:

- Basic Statistics: PASS
- Per-base sequence quality: **PASS**
- Per-tile sequence quality: PASS
- Per-sequence quality scores: PASS
- Per-base sequence content: **FAIL**
- Per-sequence GC content: PASS
- Per-base N content: PASS
- Sequence duplication: PASS
- Overrepresented sequences: PASS
- Adapter content: PASS
- Sequence length distribution: WARN

## Interpretation

The most important improvement was:

```text
Per-base sequence quality:
FAIL → PASS
```

This supports the conclusion that quality trimming successfully removed the problematic low-quality tails.

### Remaining per-base sequence-content FAIL

This was not automatically treated as a reason for further trimming.

Sequence-content bias can arise from:

- transcript composition,
- RNA-seq library preparation,
- random priming,
- biological sequence composition,
- technical effects.

A FastQC FAIL is a **signal to investigate**, not an automatic instruction to modify the data.

### Sequence-length WARN

This was expected because trimming produces variable-length reads.

The workflow explicitly allowed reads to be shortened while requiring a minimum final length of 25 bp.

---

# 11. Reference genome decision

The study metadata indicated:

```text
Genome build: hg19
```

Therefore the reference should be consistent with hg19 rather than silently mixing hg19 reads with an hg38 reference.

Because the computer had only approximately:

```text
7.5 GiB free disk space
```

a complete human reference/index was avoided.

Instead, chromosome 21 from hg19 was used as a **small teaching reference**.

Reference:

```text
week6/reference/hg19/chr21.fa
```

Reference properties measured:

```text
File size: ~47 MB
Total sequence: 48,129,895 bp
Non-N sequence: 36,069,240 bp
```

The remaining positions were represented by N.

`N` means that the reference nucleotide is unknown/unresolved at that position. It is a legitimate reference character, not an error in the FASTA file.

---

# 12. Why chromosome 21 was used

The purpose was to learn the alignment workflow without requiring many gigabytes of storage.

This creates a **major analytical limitation**:

The RNA-seq sample contains transcripts from across the human genome, but our reference contains only chromosome 21.

Therefore:

```text
Reads from chr1 → cannot align
Reads from chr2 → cannot align
...
Reads from chr21 → may align
...
Reads from chr22 → cannot align
```

Consequently, the resulting mapping percentage **cannot be interpreted as a whole-sample RNA-seq quality metric**.

The chr21 alignment is a workflow demonstration.

It is not a valid replacement for whole-genome alignment.

---

# 13. HISAT2 indexing

HISAT2 requires an index of the reference for efficient alignment.

The reference:

```text
chr21.fa
```

was converted into an HISAT2 index using:

```bash
hisat2-build \
  week6/reference/hg19/chr21.fa \
  week6/reference/hg19/hisat2_index/hg19_chr21
```

The resulting index consisted of:

```text
hg19_chr21.1.ht2
hg19_chr21.2.ht2
hg19_chr21.3.ht2
hg19_chr21.4.ht2
hg19_chr21.5.ht2
hg19_chr21.6.ht2
hg19_chr21.7.ht2
hg19_chr21.8.ht2
```

## Concept

The FASTA is the actual reference sequence.

The HISAT2 index is a specialized searchable representation of that reference.

Conceptually:

```text
Reference genome
      ↓
hisat2-build
      ↓
searchable index
      ↓
HISAT2 can efficiently find read/reference matches
```

`hisat2-build` does not itself perform read alignment.

---

# 14. HISAT2 alignment

Corrected paired reads were aligned using:

```bash
hisat2 \
  -x week6/reference/hg19/hisat2_index/hg19_chr21 \
  -1 week6/qc_trimmed_v2/trimmed/SRR975567_1.trim.fastq \
  -2 week6/qc_trimmed_v2/trimmed/SRR975567_2.trim.fastq \
  -S week6/alignment/SRR975567_chr21.sam
```

HISAT2 processed:

```text
81,975 paired fragments
```

Alignment summary:

```text
98.83% of pairs aligned concordantly 0 times
1.16% aligned concordantly exactly once
0.01% aligned concordantly >1 times
```

Additional results:

```text
7 pairs aligned discordantly
1.60% overall alignment rate
```

## Interpretation

The 1.60% alignment rate is **not evidence of poor RNA-seq quality**.

It is largely a consequence of using a chromosome-21-only reference.

The correct interpretation is:

> Only a small fraction of the transcriptome reads can find appropriate matches in the chromosome-21 reference.

A whole-human-genome reference would be required to evaluate the true global mapping rate.

---

# 15. SAM format

HISAT2 produced:

```text
week6/alignment/SRR975567_chr21.sam
```

SAM means:

**Sequence Alignment/Map**

SAM is:

- plain text,
- human-readable,
- relatively large,
- convenient for inspection.

The SAM file was approximately:

```text
35 MB
```

A SAM alignment record contains information such as:

- read identifier,
- SAM flags,
- reference chromosome,
- alignment position,
- mapping quality,
- CIGAR string,
- mate information,
- template length,
- read sequence,
- base qualities.

---

# 16. BAM format

SAM was converted to BAM:

```bash
samtools view -b \
  week6/alignment/SRR975567_chr21.sam \
  -o week6/alignment/SRR975567_chr21.bam
```

BAM means:

**Binary Alignment/Map**

BAM contains essentially the same alignment information as SAM but in a compressed binary representation.

In this run:

```text
SAM: ~35 MB
BAM: ~12 MB
```

Conceptually:

```text
SAM = readable text representation
BAM = compressed computer-oriented representation
```

---

# 17. Sorting BAM

The BAM was coordinate sorted:

```bash
samtools sort \
  week6/alignment/SRR975567_chr21.bam \
  -o week6/alignment/SRR975567_chr21.sorted.bam
```

Sorting organizes alignments according to genomic coordinates.

This is important for downstream genomic operations.

Conceptually:

```text
Unsorted alignments
       ↓
samtools sort
       ↓
chr21 position 1
chr21 position 2
chr21 position 3
...
```

Important distinction:

> SAM/BAM describes the file format; **sorted** describes how alignments are ordered within the BAM.

---

# 18. BAM indexing

The coordinate-sorted BAM was indexed:

```bash
samtools index \
  week6/alignment/SRR975567_chr21.sorted.bam
```

This produced:

```text
SRR975567_chr21.sorted.bam.bai
```

The BAI index allows software to rapidly retrieve alignments from particular genomic regions without scanning the entire BAM.

Conceptually:

```text
sorted BAM = indexed genomic alignment data
       +
      BAI
       ↓
fast regional access
```

---

# 19. Alignment QC with samtools flagstat

The final `samtools flagstat` result was:

```text
164251 + 0 in total
163950 + 0 primary
301 + 0 secondary
0 + 0 supplementary
0 + 0 duplicates
0 + 0 primary duplicates
2922 + 0 mapped (1.78% : N/A)
2621 + 0 primary mapped (1.60% : N/A)
163950 + 0 paired in sequencing
81975 + 0 read1
81975 + 0 read2
1926 + 0 properly paired (1.17% : N/A)
1978 + 0 with itself and mate mapped
643 + 0 singletons (0.39% : N/A)
0 + 0 with mate mapped to a different chr
0 + 0 with mate mapped to a different chr (mapQ>=5)
```

## Why are there 164,251 records if we started with 163,950 reads?

Original primary reads:

```text
81,975 pairs × 2 mates = 163,950
```

The BAM has:

```text
163,950 primary records
301 secondary records
```

Secondary records represent additional alignments associated with reads that have multiple possible mapping locations.

Therefore the total alignment-record count can be greater than the number of original reads.

---

# 20. HISAT2 vs samtools alignment rate

HISAT2 reported:

```text
1.60% overall alignment rate
```

`samtools flagstat` reported:

```text
2621 primary mapped
1.60%
```

The agreement between the primary mapped fraction and the HISAT2 alignment statistic provides a useful internal consistency check.

However, different tools count alignment records differently, especially when secondary/multiple alignments exist. Therefore, numbers from different programs should not be expected to match perfectly in every category.

---

# 21. Major conceptual lessons from Week 6

## Lesson 1 — QC is interpretation, not checkbox hunting

A FastQC FAIL is a diagnostic signal.

Do not automatically trim or discard data simply to make FastQC green.

---

## Lesson 2 — Pipeline order matters

The Trimmomatic bug was an important practical example.

These two pipelines are not equivalent:

```text
MINLEN → adapter removal
```

and:

```text
adapter removal → MINLEN
```

The first can allow extremely short reads to survive if adapter removal happens afterward.

---

## Lesson 3 — A biological dataset can contain technical sequence artifacts

Individual reads can contain adapter sequence even when the overall FastQC adapter-content module passes.

A PASS means the module did not detect enough evidence to trigger its threshold; it does not mean every read contains zero adapter sequence.

---

## Lesson 4 — Reference choice controls interpretation

An alignment percentage has meaning only relative to the reference.

A 1.6% mapping rate to chr21 is not comparable to a 95% mapping rate to the whole human genome.

---

## Lesson 5 — Genome builds must be consistent

If the experiment uses hg19, the reference and annotation should normally also be hg19 unless a deliberate, documented conversion strategy is used.

Do not silently mix hg19 and hg38.

---

## Lesson 6 — Paired-end reads are fragments, not simply independent observations

81,975 paired fragments correspond to:

```text
81,975 R1 reads
+
81,975 R2 reads
=
163,950 primary read records
```

The mates originate from the same sequencing fragment and provide complementary mapping information.

---

## Lesson 7 — SAM, BAM, sorted BAM, and BAI have different roles

```text
SAM
= text alignment format

BAM
= binary/compressed alignment format

sorted BAM
= BAM organized by genomic coordinate

BAI
= index for rapid access to genomic regions
```

---

# 22. Final Week 6 directory structure

The important outputs are:

```text
week6/
├── raw_rnaseq/
│   ├── SRR975567_1.fastq
│   └── SRR975567_2.fastq
│
├── qc_raw/
│   ├── SRR975567_1.subset_fastqc.html
│   ├── SRR975567_1.subset_fastqc.zip
│   ├── SRR975567_2.subset_fastqc.html
│   └── SRR975567_2.subset_fastqc.zip
│
├── qc_trimmed_v2/
│   ├── fastqc_raw/
│   ├── trimmed/
│   │   ├── SRR975567_1.trim.fastq
│   │   ├── SRR975567_2.trim.fastq
│   │   ├── SRR975567_1un.trim.fastq
│   │   └── SRR975567_2un.trim.fastq
│   └── fastqc_trimmed/
│
├── reference/
│   └── hg19/
│       ├── chr21.fa
│       └── hisat2_index/
│           ├── hg19_chr21.1.ht2
│           ├── hg19_chr21.2.ht2
│           ├── hg19_chr21.3.ht2
│           ├── hg19_chr21.4.ht2
│           ├── hg19_chr21.5.ht2
│           ├── hg19_chr21.6.ht2
│           ├── hg19_chr21.7.ht2
│           └── hg19_chr21.8.ht2
│
├── alignment/
│   ├── SRR975567_chr21.sam
│   ├── SRR975567_chr21.bam
│   ├── SRR975567_chr21.sorted.bam
│   └── SRR975567_chr21.sorted.bam.bai
│
└── test/
    ├── reference.fa
    ├── reads_1.fastq
    ├── reads_2.fastq
    ├── test_index.*.ht2
    └── test.sam
```

---

# 23. Limitations

This Week 6 workflow should not be presented as a complete biological analysis.

Important limitations:

1. Only **100,000 paired fragments** were used.
2. The subset represents the **first records**, not a random sample.
3. Only **chromosome 21** was used as the reference.
4. Therefore the 1.60% mapping rate is not a whole-genome RNA-seq mapping metric.
5. The alignment was performed without a full gene annotation/GTF.
6. A complete differential-expression workflow would require the full dataset, a complete matching genome reference, appropriate annotation, gene-level quantification, and appropriate statistical analysis.
7. The trimming parameters were selected for this educational workflow and should not automatically be treated as optimal parameters for a publication dataset.

---

# 24. Week 6 completion status

### QC

- [x] Raw FASTQ inspection
- [x] FastQC
- [x] Interpret per-base quality failure
- [x] Identify adapter strategy
- [x] Trimmomatic
- [x] Discover and fix operation-order bug
- [x] Post-trimming FastQC
- [x] Confirm paired reads contain no sequences <25 bp

### Reference

- [x] Identify hg19 genome build
- [x] Obtain hg19 chr21 reference
- [x] Inspect reference
- [x] Build HISAT2 index
- [x] Verify all eight index files

### Alignment

- [x] Paired-end HISAT2 alignment
- [x] Generate SAM
- [x] Convert SAM → BAM
- [x] Coordinate-sort BAM
- [x] Create BAM index
- [x] Run samtools flagstat
- [x] Interpret alignment statistics

**Week 6: COMPLETE**

---

# 25. Transition to Week 7

The next stage should build on the alignment concepts rather than simply repeat commands.

A publication-style RNA-seq workflow would next require moving from **read alignments to gene-level information**, followed by appropriate normalization and statistical analysis.

Before doing that, the Week 7 plan should explicitly distinguish between:

```text
teaching workflow
```

and

```text
biologically valid full-dataset analysis
```

The chr21 alignment from Week 6 is primarily a foundation for understanding how RNA-seq reads become genomic alignments and how alignment files are represented and QC'd.
