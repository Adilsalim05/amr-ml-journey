#!/bin/bash
set -e  # exit immediately if any command fails

log_step () {
    echo "[$(date '+%H:%M:%S')] $1"
}

if [ -z "$1" ] || [ -z "$2" ]; then
    echo "Usage: bash run_fastqc.sh <input_dir> <output_dir>"
    exit 1
fi

INPUT_DIR=$1
OUTPUT_DIR=$2

log_step "Checking input directory: $INPUT_DIR"
mkdir -p "$OUTPUT_DIR"
log_step "Running FastQC..."
fastqc "$INPUT_DIR"/*.fastq* -o "$OUTPUT_DIR"
log_step "Done. Reports in $OUTPUT_DIR"
