
# scripts/qc_trim_pipeline.sh
#
# Usage:
# bash scripts/qc_trim_pipeline.sh <raw_fastq_dir> <output_dir> <adapter_file>

set -e

log_step () {
    echo "[$(date '+%H:%M:%S')] $1"
}

# Check arguments
if [ -z "$1" ] || [ -z "$2" ] || [ -z "$3" ]; then
    echo "Usage: bash scripts/qc_trim_pipeline.sh <raw_fastq_dir> <output_dir> <adapter_file>"
    exit 1
fi

RAW_DIR=$(cd "$1" && pwd)
OUT_DIR=$(mkdir -p "$2" && cd "$2" && pwd)
ADAPTERS=$(cd "$(dirname "$3")" && pwd)/$(basename "$3")

# Check required files
if [ ! -f "$ADAPTERS" ]; then
    echo "ERROR: Adapter file not found: $ADAPTERS"
    exit 1
fi

if ! compgen -G "$RAW_DIR/*_1.fastq" > /dev/null; then
    echo "ERROR: No *_1.fastq files found in $RAW_DIR"
    exit 1
fi

mkdir -p "$OUT_DIR/fastqc_raw"
mkdir -p "$OUT_DIR/trimmed"
mkdir -p "$OUT_DIR/fastqc_trimmed"

log_step "Running FastQC on raw reads"
fastqc "$RAW_DIR"/*_1.fastq "$RAW_DIR"/*_2.fastq -o "$OUT_DIR/fastqc_raw"

log_step "Running Trimmomatic"

for infile in "$RAW_DIR"/*_1.fastq; do

    base=$(basename "$infile" _1.fastq)

    echo "Processing sample: $base"

    trimmomatic PE \
        "$RAW_DIR/${base}_1.fastq" \
        "$RAW_DIR/${base}_2.fastq" \
        "$OUT_DIR/trimmed/${base}_1.trim.fastq" \
        "$OUT_DIR/trimmed/${base}_1un.trim.fastq" \
        "$OUT_DIR/trimmed/${base}_2.trim.fastq" \
        "$OUT_DIR/trimmed/${base}_2un.trim.fastq" \
        SLIDINGWINDOW:4:20 \
        MINLEN:25 \
        ILLUMINACLIP:"$ADAPTERS":2:40:15

done

log_step "Running FastQC on trimmed paired reads"

fastqc \
    "$OUT_DIR"/trimmed/*_1.trim.fastq \
    "$OUT_DIR"/trimmed/*_2.trim.fastq \
    -o "$OUT_DIR/fastqc_trimmed"

log_step "Pipeline complete"
echo "Results: $OUT_DIR"
