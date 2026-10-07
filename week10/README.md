# Week 10 — RNA-seq Pipeline Automation and Validation

## Goal

Integrate the previously developed RNA-seq quality-control, trimming, alignment, BAM processing, and reporting steps into a reproducible end-to-end pipeline.

The main objectives were to:

1. Automate QC and adapter trimming.
2. Align paired-end reads to the Week 6 hg19 chromosome 21 reference using HISAT2.
3. Convert, sort, and index BAM files.
4. Generate alignment statistics with samtools.
5. Combine QC and alignment results into a MultiQC report.
6. Validate BAM integrity and pipeline reproducibility.
7. Interpret QC and alignment results without over-interpreting the deliberately limited reference.

---

## Dataset

* Sample: `SRR975567`
* Experiment: `GSE50760`
* Sequencing: paired-end RNA-seq
* Read length: approximately 2 × 101 bp
* Primary sequences: 163,380
* Reference: hg19 chromosome 21 only
* Reference length: 48,129,895 bp

### Important reference limitation

Only chromosome 21 from hg19 was used as the reference.

Therefore, the observed ~1.6% mapping rate must **not** be interpreted as the overall mapping efficiency of the RNA-seq experiment. Reads originating from other chromosomes cannot map to this reference.

This chromosome-21-only reference was intentionally used as part of the earlier learning workflow.

---

## Pipeline

The master pipeline was implemented in:

`scripts/master_pipeline.sh`

The QC and trimming component was implemented in:

`scripts/qc_trim_pipeline.sh`

### 1. Raw-read quality control

FastQC was run on both raw paired-end FASTQ files.

### 2. Adapter trimming and quality filtering

Trimmomatic PE was used with:

* Adapter file: `TruSeq3-PE.fa`
* `ILLUMINACLIP:2:40:15`
* `SLIDINGWINDOW:4:20`
* `MINLEN:25`

Both paired and unpaired output reads were generated.

Only the surviving paired reads were subsequently used for HISAT2 alignment.

### 3. Post-trimming quality control

FastQC was run on the trimmed paired reads.

### 4. HISAT2 alignment

The paired trimmed reads were aligned against the hg19 chromosome 21 HISAT2 index.

### 5. SAM → BAM conversion

SAM output from HISAT2 was converted to BAM using samtools.

### 6. BAM sorting and indexing

The BAM file was sorted and indexed for downstream analysis.

### 7. Alignment statistics

`samtools stats` was used to generate alignment statistics.

Additional validation was performed with:

* `samtools quickcheck`
* `samtools idxstats`
* `samtools flagstat`

### 8. MultiQC reporting

FastQC and samtools results were aggregated using MultiQC.

Final report:

`week10/pipeline_output/multiqc/multiqc_report.html`

---

## Output Structure

```text
week10/
├── README.md
└── pipeline_output/
    ├── alignment/
    │   ├── SRR975567.sam
    │   ├── SRR975567.bam
    │   ├── SRR975567.sorted.bam
    │   └── SRR975567.sorted.bam.bai
    ├── qc_trim/
    │   ├── fastqc_raw/
    │   ├── fastqc_trimmed/
    │   └── trimmed/
    ├── stats/
    │   └── SRR975567_samtools_stats.txt
    └── multiqc/
        ├── multiqc_report.html
        └── multiqc_data/
```

---

## Key Results

### Alignment

| Metric                                           |  Result |
| ------------------------------------------------ | ------: |
| Primary sequences                                | 163,380 |
| Primary mapped reads                             |   2,619 |
| Primary mapping rate                             |   1.60% |
| Mapped alignments including secondary alignments |   2,918 |
| Properly paired reads                            |   1,926 |
| Both mates mapped                                |   1,978 |
| Singletons                                       |     641 |
| Secondary alignments                             |     299 |
| Supplementary alignments                         |       0 |

The primary mapping rate of approximately 1.60% is consistent with the Week 6 result using the same chromosome-21-only reference.

### BAM validation

`samtools quickcheck` completed without reporting an error, providing a basic integrity check of the sorted BAM file.

`samtools idxstats` reported:

```text
chr21  48129895  2918  641
*      0         0     160120
```

The 2,918 chromosome-21 alignments agree with the corresponding `samtools flagstat` count.

---

## Quality-Control Findings

### Per-base sequence quality

The raw reads failed the FastQC per-base sequence-quality module.

After Trimmomatic processing, the per-base sequence-quality module passed for both R1 and R2.

This indicates that trimming improved the observed base-quality profile.

### Per-base sequence content

The per-base sequence-content module remained flagged after trimming.

The nucleotide composition was strongly biased during approximately the first 9 bases of the reads and then approached a more balanced composition.

Importantly, the same pattern was already present in the raw reads and remained after trimming.

Therefore, the bias was **not introduced by the trimming procedure**.

The FastQC result alone does not establish the biological or technical cause of this bias. It is treated here as a library/sequencing characteristic requiring context rather than as evidence of a failed pipeline.

### Overrepresented sequences

An overrepresented-sequence warning observed for R2 in the raw data was resolved after trimming.

### Read length

Trimming reduced the average read length:

* R1: approximately 88.98 bp
* R2: approximately 90.99 bp

The median remained approximately 100 bp.

This is expected because trimming removes low-quality or adapter-associated sequence from individual reads.

---

## Important Interpretation Notes

### 1. The 1.60% mapping rate is not a global RNA-seq mapping rate

Only chromosome 21 was available to HISAT2.

Therefore, low mapping to the chromosome-21-only reference does not mean that 98% of the RNA-seq reads failed to align to the human genome.

A whole-genome or appropriate transcriptome reference would be required to estimate genome-wide RNA-seq mapping efficiency.

### 2. Secondary alignments

`samtools flagstat` reports:

* 2,918 mapped alignments
* 2,619 primary mapped reads
* 299 secondary alignments

For comparison with the Week 6 workflow, the primary mapping rate of 1.60% is the appropriate value.

### 3. Proper pairing

There were 1,978 reads with both mates mapped and 1,926 reads marked as properly paired.

These metrics should not be interpreted as whole-genome paired-end performance because the reference contains only chromosome 21.

### 4. Unpaired trimmed reads

Trimmomatic generated unpaired reads when only one mate survived filtering.

These unpaired reads were **not used for HISAT2 alignment** in this workflow.

The master pipeline intentionally aligns only the surviving paired reads.

### 5. Duplicate interpretation

Duplicate marking was not performed in this workflow.

Therefore, the absence of marked duplicates in the alignment statistics should **not** be interpreted as proof that the sequencing library contains no PCR duplicates.

FastQC's sequence-duplication assessment is a separate metric and should not be conflated with BAM duplicate marking.

### 6. No transcript quantification

No GTF annotation was used in this workflow.

Therefore, Week 10 represents:

**QC → trimming → alignment → BAM processing → alignment statistics → reporting**

It does not yet represent transcript quantification or differential gene-expression analysis.

### 7. Single sample

Only one sample was processed.

Therefore, no biological comparison, differential expression analysis, or statistical inference is possible from this dataset alone.

---

## Reproducibility

The automated Week 10 pipeline reproduced the approximately 1.6% primary mapping rate obtained during the earlier Week 6 alignment workflow using the same sample and chromosome-21-only reference.

This demonstrates that the previously manual workflow has been successfully converted into a reproducible end-to-end pipeline.

---

## Final Week 10 Status

### Completed

* [x] Raw-read FastQC
* [x] Trimmomatic paired-end trimming
* [x] Trimmed-read FastQC
* [x] HISAT2 alignment
* [x] SAM → BAM conversion
* [x] BAM sorting
* [x] BAM indexing
* [x] samtools statistics
* [x] BAM integrity validation
* [x] MultiQC report
* [x] End-to-end master pipeline
* [x] Interpretation of QC and alignment results
* [x] Documentation

### Not performed

* [ ] Whole-genome alignment
* [ ] GTF-based transcript quantification
* [ ] Gene-level count generation
* [ ] Differential expression analysis
* [ ] Biological interpretation across multiple samples

These are outside the scope of the Week 10 validation exercise.

---

## Key Lesson

A pipeline should not be judged solely by whether every FastQC module turns green or whether a mapping percentage looks high.

The correct interpretation depends on:

**reference → preprocessing → alignment strategy → QC metrics → validation → biological context**

In this exercise, the low mapping percentage is expected from the chromosome-21-only reference, while the persistent 5′ nucleotide-composition bias requires cautious interpretation rather than aggressive trimming.
