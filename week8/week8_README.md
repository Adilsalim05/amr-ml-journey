# Week 8 --- SAMtools Fluency

## Overview

Week 8 focused on becoming comfortable with SAMtools and understanding
what an aligned sequencing dataset actually contains.

The week used the RNA-seq dataset from Week 6:

-   SRA accession: `SRR975567`
-   Paired-end RNA-seq
-   Only the first 100,000 paired fragments were used for the teaching
    workflow.
-   Reference: human hg19 chromosome 21 (`chr21.fa`)
-   HISAT2: 2.2.3
-   SAMtools: 1.24

This was a **learning workflow**, not a production RNA-seq analysis.

------------------------------------------------------------------------

## The Week 6--8 alignment workflow

The conceptual pipeline was:

``` text
FASTQ reads
    ↓
Quality control and trimming
    ↓
Reference FASTA: chr21.fa
    ↓
HISAT2 reference index
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
SAMtools inspection and analysis
```

### Two different indexes

An important distinction learned during Week 8:

**HISAT2 reference index**

-   Built from the reference FASTA.
-   Used by HISAT2 to efficiently align sequencing reads to the
    reference.

**BAM index (`.bai`)**

-   Built from a coordinate-sorted BAM.
-   Used by SAMtools and downstream tools to quickly access genomic
    regions.

These indexes serve completely different purposes.

------------------------------------------------------------------------

# Day 50 --- Sorting and indexing

## Why sort?

An ordinary BAM does not necessarily have alignments arranged by genomic
coordinate.

A coordinate-sorted BAM organizes records approximately as:

``` text
chromosome → genomic position
```

This is important for downstream analysis and is required for normal BAM
indexing.

Command:

``` bash
samtools sort alignment/SRR975567_chr21.bam \
    -o alignment/SRR975567_chr21.sorted.bam
```

## Why index?

The BAM index allows programs to jump directly to a genomic region
without scanning the entire BAM.

Example:

``` text
chr21:9461381-9461400
```

Command:

``` bash
samtools index alignment/SRR975567_chr21.sorted.bam
```

This produces:

``` text
SRR975567_chr21.sorted.bam.bai
```

We also deliberately tried to index the unsorted BAM and saw that
indexing failed because the alignments were not coordinate sorted.

------------------------------------------------------------------------

# Day 51 --- SAM flags

Every SAM/BAM alignment record contains a numeric **FLAG**.

The FLAG is a bitwise combination of properties describing the
alignment.

Important flags learned:

``` text
2      properly paired
4      read is unmapped
256    secondary alignment
```

For example:

``` text
329 = PAIRED + MUNMAP + READ1 + SECONDARY
```

## `-f` versus `-F`

This distinction is important:

``` text
-f FLAG     require the FLAG to be present
-F FLAG     exclude records having the FLAG
```

Examples:

``` bash
samtools view -f 2 alignment/SRR975567_chr21.sorted.bam
```

Keeps properly paired records.

``` bash
samtools view -F 4 alignment/SRR975567_chr21.sorted.bam
```

Excludes unmapped records, effectively retaining mapped records.

``` bash
samtools view -F 256 alignment/SRR975567_chr21.sorted.bam
```

Excludes secondary alignments.

To count the resulting alignment records:

``` bash
samtools view -F 4 alignment/SRR975567_chr21.sorted.bam | wc -l
```

`wc -l` counts output lines. Since SAMtools view outputs one alignment
record per line when headers are omitted, this effectively counts
alignment records.

Important distinction:

**Alignment-record count is not necessarily the same as biological
read-pair count.**

------------------------------------------------------------------------

# Day 52 --- Region queries and MAPQ

Because the BAM was indexed, we could directly query a genomic region:

``` bash
samtools view alignment/SRR975567_chr21.sorted.bam \
    chr21:20000000-21000000 | wc -l
```

This returned:

``` text
157
```

Important:

**157 was NOT the total number of mapped reads.**

It was the number of alignment records overlapping that particular 10-Mb
region.

## Mapping quality

`-q` specifies a minimum mapping quality (MAPQ):

``` bash
samtools view -q 30 alignment/SRR975567_chr21.sorted.bam \
    chr21:20000000-21000000 | wc -l
```

This returned:

``` text
142
```

The unrestricted query returned 157, so 15 alignment records in that
region had MAPQ below 30.

With:

``` bash
-q 0
```

all records with nonnegative MAPQ are retained, so the count remained
157.

MAPQ should not be interpreted simply as "percentage confidence"; its
exact meaning depends on the aligner and scoring model.

------------------------------------------------------------------------

# Day 53 --- `idxstats` and `stats`

## `samtools idxstats`

Command:

``` bash
samtools idxstats alignment/SRR975567_chr21.sorted.bam
```

Output:

``` text
chr21    48129895    2922       643
*        0           0          160686
```

Interpretation:

-   `chr21` is 48,129,895 bp long.
-   2,922 alignment records were mapped to chr21.
-   643 unmapped records were associated with that reference.
-   `*` represents unmapped records not associated with a reference.
-   160,686 records were unmapped and had no reference assignment.

The very large unmapped fraction was expected because the reference
contained **only chromosome 21**.

## `samtools stats`

Command:

``` bash
samtools stats alignment/SRR975567_chr21.sorted.bam \
    > results/week8_samtools_stats.txt
```

To inspect the high-level summary:

``` bash
grep ^SN results/week8_samtools_stats.txt | head -n 20
```

Important values observed included:

``` text
raw total sequences:       163950
is sorted:                      1
1st fragments:              81975
last fragments:             81975
reads mapped:                 2621
reads mapped and paired:      1978
reads unmapped:             161329
reads properly paired:        1926
reads duplicated:                0
reads MQ0:                      61
non-primary alignments:        301
supplementary alignments:       0
```

The distinction between 2,922 mapped alignment records and 2,621 primary
mapped reads reflects the presence of secondary alignments.

------------------------------------------------------------------------

# Day 54 --- `mpileup` and `depth`

## What is a pileup?

A pileup is a representation of reads **stacked against a reference
position by position**.

Conceptually:

``` text
Reference:   A C T G C A
Read 1:        C T G C A
Read 2:        C T G C A
Read 3:        C T A C A
                    ↑
                possible variant
```

At each genomic position we can ask:

-   How many reads cover this position?
-   Which bases do they contain?
-   What are their base qualities?
-   How confidently were the reads mapped?

These are the types of evidence used by variant callers.

## `samtools mpileup`

Command:

``` bash
samtools mpileup \
    -f reference/hg19/chr21.fa \
    alignment/SRR975567_chr21.sorted.bam | head -n 20
```

Example output:

``` text
chr21  9461381  c  1  ^].  C
chr21  9461382  t  1  .    C
chr21  9461383  c  1  .    C
...
```

The important columns are:

1.  chromosome
2.  position
3.  reference base
4.  depth
5.  base/alignment information
6.  base quality information

Symbols such as `.` and `,` indicate bases matching the reference on
forward/reverse strands; other symbols encode mismatches, indels, and
read boundaries.

## `samtools depth`

Command:

``` bash
samtools depth \
    -r chr21:9461381-9461400 \
    alignment/SRR975567_chr21.sorted.bam
```

Output:

``` text
chr21    9461384    1
chr21    9461385    1
...
chr21    9461400    1
```

`depth` is a simpler view than `mpileup`:

``` text
mpileup → bases + alignment information + depth
depth   → position + depth
```

In our example, depth was only 1× across the observed positions.

------------------------------------------------------------------------

# Why was the mapping rate only \~1.6%?

This is one of the most important Week 6/8 interpretations.

The low mapping rate should **not** be interpreted as poor quality of
the original RNA-seq experiment.

We deliberately used:

1.  only the first 100,000 paired fragments, and
2.  a reference containing only chromosome 21.

Human RNA-seq reads originating from chromosomes other than chr21 had no
corresponding reference sequence available.

Therefore, a large fraction of reads could not map.

This was a deliberate teaching simplification caused by
computational/disk constraints.

------------------------------------------------------------------------

# Important terminology corrections

### Mapped vs paired

These are different concepts.

A read can belong to a paired-end experiment but still be unmapped.

Likewise, a read can be mapped but not properly paired.

### We did not permanently remove unmapped reads

Commands such as:

``` bash
samtools view -F 4 ...
```

filter unmapped records from that particular command's output.

They do not modify or delete the original BAM.

### 157 was not the total number of mapped reads

157 was the number of alignment records overlapping:

``` text
chr21:20000000-21000000
```

The whole BAM contained thousands of mapped alignment records.

------------------------------------------------------------------------

# SAMtools command memory

  Question                    Command
  --------------------------- -----------------------------------
  Sort BAM                    `samtools sort`
  Create BAM index            `samtools index`
  Inspect/filter alignments   `samtools view`
  Require a FLAG              `samtools view -f`
  Exclude a FLAG              `samtools view -F`
  Filter by MAPQ              `samtools view -q`
  Query a region              `samtools view ... chr:start-end`
  Count records               `wc -l`
  Summary by reference        `samtools idxstats`
  Detailed statistics         `samtools stats`
  Per-position bases/depth    `samtools mpileup`
  Per-position depth          `samtools depth`

------------------------------------------------------------------------

# Main Week 8 learning outcomes

By the end of Week 8, the goal was to understand rather than memorize
the SAMtools commands.

The major accomplishments were:

-   Understand why BAM files are coordinate sorted.
-   Understand why a sorted BAM can be indexed.
-   Distinguish the HISAT2 reference index from the BAM index.
-   Understand SAM FLAGs and bitwise filtering.
-   Distinguish `-f` from `-F`.
-   Use MAPQ filtering with `-q`.
-   Query specific genomic regions.
-   Summarize mapped/unmapped records with `idxstats`.
-   Inspect detailed alignment statistics with `stats`.
-   Understand pileup and per-base coverage.
-   Distinguish coverage/depth from pileup.
-   Understand why our 1.6% mapping rate was expected from the
    chr21-only reference.
-   Recognize that this dataset is a teaching workflow rather than a
    complete RNA-seq analysis.

------------------------------------------------------------------------

# Week 8 limitation statement

This workflow should **not** be presented as a complete RNA-seq
analysis.

We did not perform:

-   whole-genome alignment
-   complete transcriptome alignment
-   gene-level quantification
-   normalization
-   differential expression analysis
-   biological interpretation of gene expression
-   production-grade variant calling

The purpose was to develop **alignment-file literacy and SAMtools
fluency**.

------------------------------------------------------------------------

# Week 8 completion checkpoint

At the end of Week 8, the project had two major learning achievements:

### Week 7

A multi-class AMR resistance-mechanism classifier was evaluated at both
protein-level random splits and family-aware splits. Family-aware
validation showed substantially weaker generalization, highlighting the
importance of biological grouping during evaluation.

### Week 8

The RNA-seq alignment workflow was revisited at the alignment-file
level, developing practical fluency with SAM/BAM structure, sorting,
indexing, SAM flags, MAPQ, regional queries, alignment statistics,
pileup, and coverage.

Together, Weeks 7--8 marked the halfway point of the planned 16-week
AMR-ML journey.
