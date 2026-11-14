Let's create `week11/README.md` in your repository. Run this single command from `amr-ml-journey`:

````
mkdir -p week11

cat > week11/README.md <<'EOF'
# Week 11 — AMR Gene Annotation Using RGI and CARD

## Objective

Use the Resistance Gene Identifier (RGI) and Comprehensive Antibiotic Resistance Database (CARD) to identify and annotate antimicrobial resistance-associated genes and mutations in the *Escherichia coli* K-12 MG1655 reference genome.

The goal was to understand reference-based AMR annotation, CARD detection models, and the distinction between genomic predictions and experimentally demonstrated resistance.

## Software and database

| Component | Version |
|---|---|
| RGI | 6.0.8 |
| CARD | 4.0.1 |
| CARD data release | May 30, 2025 |
| Alignment method | BLAST |
| Operating system | macOS (Apple Silicon) |

## Reference genome

- Organism: *Escherichia coli* K-12 substr. MG1655
- Accession: NC_000913.3
- Source: NCBI RefSeq
- File: `data/reference/ecoli_k12_mg1655/NC_000913.3.fasta`

## Workflow

### 1. Prepare the CARD database

CARD annotation FASTA files were generated from `card.json` and loaded into RGI.

```bash
rgi load \
  -i data/card/card.json \
  --card_annotation card_database_v4.0.1.fasta \
  --card_annotation_all_models card_database_v4.0.1_all.fasta \
  --local
````

### 2. Run RGI

The initial run encountered a contig-name parsing issue. RGI was subsequently reinstalled from the official source repository, incorporating the relevant upstream fix.

The patched analysis was performed using:

```
rgi main \
  -i data/reference/ecoli_k12_mg1655/NC_000913.3.fasta \
  -o results/week11_rgi/ecoli_mg1655_patched \
  -t contig \
  -a BLAST \
  -n 4 \
  --local \
  --clean
```

### 3. Output files

Results are stored in `results/week11_rgi/`.

| File                        | Description                 |
| --------------------------- | --------------------------- |
| `ecoli_mg1655.json`         | Original RGI JSON output    |
| `ecoli_mg1655.txt`          | Original RGI tabular output |
| `ecoli_mg1655_patched.json` | Patched RGI JSON output     |
| `ecoli_mg1655_patched.txt`  | Patched RGI tabular output  |

## Results

The patched analysis identified:

- 55 total hits
- 54 unique CARD ARO models
- 38 Perfect hits
- 17 Strict hits

Detection model distribution:

| Model type             | Hits |
| ---------------------- | ---- |
| Protein homolog        | 47   |
| Protein overexpression | 5    |
| Protein variant        | 3    |

The same CARD ARO model for EF-Tu-associated Pulvomycin resistance (ARO:3003369) matched two separate genomic ORFs. These represent two genomic matches to one CARD model, rather than duplicate records.

### Interpretation

RGI identifies genomic matches to CARD resistance models. Its results should not be interpreted as direct evidence of phenotypic antibiotic resistance.

Important distinctions:

- Perfect and Strict: CARD model detection categories, not clinical susceptibility classifications.
- Protein homolog models: identify sequence similarity to known resistance-associated proteins.
- Protein variant models: identify known resistance-associated sequence variants.
- Protein overexpression models: identify determinants associated with resistance when expression is increased; RGI does not measure expression.

Some matches may represent intrinsic housekeeping functions or weak sequence similarities. Individual hits require biological and experimental validation.

MG1655 is a laboratory reference strain, not a clinical isolate. Phenotypic susceptibility testing is required to establish actual resistance.

## Limitations

1. Genomic annotation does not establish gene expression.
2. Sequence similarity does not necessarily establish functional resistance.
3. CARD model detection does not replace antimicrobial susceptibility testing.
4. Organism specificity and the biological relevance of individual hits require careful evaluation.

## Key learning outcomes

By completing Week 11, I learned to:

- Install and configure RGI and CARD locally.
- Prepare a reference genome for AMR annotation.
- Run RGI using BLAST alignment.
- Interpret Perfect and Strict detection categories.
- Distinguish homolog, variant, and overexpression models.
- Evaluate annotation results critically rather than treating every hit as confirmed resistance.

## Reproducibility

The reference genome, FASTA index, and RGI output files are retained in the repository.

Generated CARD database FASTA files and the local RGI database (`localDB/`) are excluded through `.gitignore`. They must be generated or loaded locally before rerunning the analysis.

EOF

````

Then verify:

```bash
cat week11/README.md
````

Once verified, we will add, commit, and push this README to GitHub.
