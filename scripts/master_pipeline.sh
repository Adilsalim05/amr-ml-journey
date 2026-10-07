#!/bin/bash

# scripts/master_pipeline.sh
#
# Usage:
# bash scripts/master_pipeline.sh <raw_fastq_dir> <reference_index_base> <adapter_file> <output_dir>

set -e

log_step () {
    echo
    echo "========================================"
    echo "[$(date '+%H:%M:%S')] $1"
    echo "========================================"
}

# Check arguments
if [ "$#" -ne 4 ]; then
    echo "Usage: bash scripts/master_pipeline.sh <raw_fastq_dir> <reference_index_base> <adapter_file> <output_dir>"
    exit 1
fi

RAW_DIR="$1"
REFERENCE_INDEX="$2"
ADAPTERS="$3"
OUT_DIR="$4"

# Convert paths to absolute paths
RAW_DIR=$(cd "$RAW_DIR" && pwd)
ADAPTERS=$(cd "$(dirname "$ADAPTERS")" && pwd)/$(basename "$ADAPTERS")
OUT_DIR=$(mkdir -p "$OUT_DIR" && cd "$OUT_DIR" && pwd)

# ----------------------------------------
# Step 1: QC + trimming
# ----------------------------------------

log_step "Running QC and trimming"

bash scripts/qc_trim_pipeline.sh \
    "$RAW_DIR" \
    "$OUT_DIR/qc_trim" \
    "$ADAPTERS"

# ----------------------------------------
# Step 2: HISAT2 alignment
# ----------------------------------------

log_step "Running HISAT2 alignment"

mkdir -p "$OUT_DIR/alignment"

for infile in "$OUT_DIR/qc_trim/trimmed/"*_1.trim.fastq; do

    base=$(basename "$infile" _1.trim.fastq)

    echo "Aligning sample: $base"

    hisat2 \
        -x "$REFERENCE_INDEX" \
        -1 "$OUT_DIR/qc_trim/trimmed/${base}_1.trim.fastq" \
        -2 "$OUT_DIR/qc_trim/trimmed/${base}_2.trim.fastq" \
        -S "$OUT_DIR/alignment/${base}.sam"

done

# ----------------------------------------
# Step 3: SAM → BAM
# ----------------------------------------

log_step "Converting SAM to BAM"

for samfile in "$OUT_DIR/alignment/"*.sam; do

    base=$(basename "$samfile" .sam)

    samtools view -b \
        "$samfile" \
        -o "$OUT_DIR/alignment/${base}.bam"

done

# ----------------------------------------
# Step 4: Sort BAM
# ----------------------------------------

log_step "Sorting BAM files"

for bamfile in "$OUT_DIR/alignment/"*.bam; do

    base=$(basename "$bamfile" .bam)

    samtools sort \
        "$bamfile" \
        -o "$OUT_DIR/alignment/${base}.sorted.bam"

done

# ----------------------------------------
# Step 5: Index sorted BAM
# ----------------------------------------

log_step "Indexing sorted BAM files"

for sorted_bam in "$OUT_DIR/alignment/"*.sorted.bam; do

    samtools index "$sorted_bam"

done

# ----------------------------------------
# Step 6: Alignment statistics
# ----------------------------------------

log_step "Generating samtools statistics"

mkdir -p "$OUT_DIR/stats"

for sorted_bam in "$OUT_DIR/alignment/"*.sorted.bam; do

    base=$(basename "$sorted_bam" .sorted.bam)

    samtools stats \
        "$sorted_bam" \
        > "$OUT_DIR/stats/${base}_samtools_stats.txt"

done

# ----------------------------------------
# Step 7: MultiQC
# ----------------------------------------

log_step "Running MultiQC"

mkdir -p "$OUT_DIR/multiqc"

multiqc \
    "$OUT_DIR/qc_trim" \
    "$OUT_DIR/stats" \
    --dirs \
    -o "$OUT_DIR/multiqc"

log_step "MASTER PIPELINE COMPLETE"

echo "Final MultiQC report:"
echo "$OUT_DIR/multiqc/multiqc_report.html"
