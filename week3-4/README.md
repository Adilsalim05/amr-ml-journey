# Weeks 3–4: Data Handling, CARD Exploration, and Sequencing QC

## Overview

Weeks 3–4 focused on moving from basic bioinformatics commands toward reusable data-analysis and sequencing-quality-control workflows. The main skills developed were working with biological data using pandas, exploring the CARD AMR database, performing quality control on paired-end FASTQ reads, trimming adapters and low-quality sequence, and automating the workflow with shell scripting.

---

## 1. Pandas and CARD Data Exploration

I used pandas to work with CARD data stored in tabular and JSON formats. The main operations practiced were:

* Loading tabular data with `pandas.read_csv()`
* Inspecting DataFrames using shape, columns, and summary operations
* Filtering and selecting data
* Grouping data with `groupby()`
* Counting observations within groups
* Combining datasets using `merge()`
* Identifying and investigating missing values
* Parsing structured CARD JSON data

A reusable CARD-loading function was developed in:

```text
src/load_card_data.py
```

This separates data-loading logic from individual analysis notebooks and provides a reusable starting point for future CARD-based analyses.

---

## 2. Raw Sequencing QC

FastQC was used to assess paired-end *E. coli* sequencing reads before preprocessing.

The dataset contained three samples:

```text
SRR2584863
SRR2584866
SRR2589044
```

Each sample contained two paired-end files:

```text
*_1.fastq
*_2.fastq
```

FastQC was used to identify sequencing-quality issues before trimming. For SRR2589044, adapter contamination was identified as an important issue requiring preprocessing.

The important methodological principle was to diagnose the reads first rather than applying trimming blindly.

---

## 3. Adapter and Quality Trimming

Trimmomatic was used to process the paired-end reads.

The adapter sequence file was:

```text
NexteraPE-PE.fa
```

The following parameters were used:

```text
ILLUMINACLIP:NexteraPE-PE.fa:2:40:15
SLIDINGWINDOW:4:20
MINLEN:25
```

### ILLUMINACLIP

`ILLUMINACLIP` was used to identify and remove Nextera adapter sequences. Adapter contamination can occur when sequencing extends beyond the biological DNA insert and enters adapter sequence.

### SLIDINGWINDOW:4:20

A four-base sliding window was used to monitor read quality. When the average Phred quality within the window fell below Q20, trimming was performed.

### MINLEN:25

Reads that were reduced to fewer than 25 bases after trimming were discarded.

The purpose of these parameters was to remove adapter contamination and low-quality sequence while retaining reads of sufficient length for downstream analysis.

---

## 4. Before/After QC Assessment

FastQC was performed both before and after trimming.

This comparison was used to determine whether the problems identified in the raw data were actually improved by preprocessing.

For SRR2589044, adapter contamination was substantially improved after Trimmomatic processing. Most relevant FastQC modules passed after trimming, while Sequence Length Distribution remained flagged.

The change in sequence-length distribution was expected because trimming removes variable amounts of sequence from individual reads. Therefore, a change in read-length distribution does not automatically indicate a failed trimming process.

Approximately 79% of the input data was retained following trimming. Read retention was considered together with the post-trimming FastQC results rather than against an arbitrary percentage threshold.

---

## 5. Scaling to Multiple Samples

Initially, Trimmomatic was run manually on SRR2589044. The workflow was subsequently generalized using a shell `for` loop so that the same procedure could be applied to all available paired-end samples.

The loop identifies files matching:

```text
*_1.fastq
```

and derives the sample identifier using `basename`. The corresponding `_2.fastq` file is then supplied as the paired read.

This allows the same Trimmomatic command to be applied consistently across multiple samples without manually rewriting the command for each sample.

---

## 6. Reusable QC and Trimming Pipeline

The complete workflow was combined into:

```text
scripts/qc_trim_pipeline.sh
```

The script accepts three arguments:

```text
<raw_fastq_dir>
<output_dir>
<adapter_file>
```

The pipeline performs:

```text
Raw FASTQ
    ↓
FastQC
    ↓
Trimmomatic
    ↓
Trimmed FASTQ
    ↓
FastQC
```

The pipeline was tested from a clean output directory using:

```bash
bash scripts/qc_trim_pipeline.sh \
    data/raw_fastq/ \
    results/week4_pipeline_final/ \
    data/raw_fastq/NexteraPE-PE.fa
```

The final run successfully processed all three samples and generated:

* Six raw-read FastQC reports
* Twelve Trimmomatic FASTQ outputs
* Six trimmed-read FastQC reports

The pipeline therefore provides a single-command workflow for the QC and trimming stage.

---

## 7. Reproducibility Lessons

An important lesson from developing the pipeline was that a script can execute successfully while still containing a logical problem.

The initial FastQC command used:

```bash
fastqc "$RAW_DIR"/*.fastq
```

Because previously trimmed FASTQ files were present in the same directory, this wildcard also selected processed files during the raw QC stage.

The command was therefore restricted to the paired raw reads:

```bash
fastqc "$RAW_DIR"/*_1.fastq "$RAW_DIR"/*_2.fastq
```

This ensured that the raw QC stage analyzed only the intended input reads.

The final pipeline was committed to Git and pushed to the repository. This provided version control for the workflow and documentation.

---

## 8. Skills Developed

By the end of Weeks 3–4, I can:

* Manipulate biological datasets using pandas
* Use filtering, `groupby()`, and `merge()` on real data
* Parse CARD data from tabular and JSON formats
* Use FastQC to diagnose sequencing-quality problems
* Apply Trimmomatic to paired-end reads
* Interpret adapter and quality-trimming parameters
* Compare sequencing QC before and after preprocessing
* Use shell variables and `basename`
* Use `for` loops to scale analyses across samples
* Build a parameterized shell pipeline
* Validate a pipeline by running it from a clean output directory
* Document computational methods and maintain them under Git version control

The major transition during these two weeks was from running individual bioinformatics commands to constructing a reusable and testable workflow.

