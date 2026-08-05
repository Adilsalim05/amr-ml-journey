#!/bin/bash
# scripts/qc_summary.sh
set -e
INPUT_DIR=$1
OUTPUT_DIR=$2

mkdir -p "$OUTPUT_DIR"
fastqc "$INPUT_DIR"/*.fastq* -o "$OUTPUT_DIR"

cd "$OUTPUT_DIR"
for zipfile in *.zip; do
    unzip -o "$zipfile" > /dev/null
done
echo "Unzipped all FastQC reports in $OUTPUT_DIR"
