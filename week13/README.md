# Week 13 — Protein Mutation Analysis and Exploratory Machine Learning

## 1. Overview

Week 13 focused on the computational characterization of four protein-level mutations identified in the experimental-evolution project.

The workflow involved retrieving reference gene sequences from *Escherichia coli* K-12 MG1655, constructing wild-type (WT) and mutant protein sequences, comparing their theoretical physicochemical properties, and applying the previously developed Week 5 Random Forest classifier to these sequences.

The purpose was to explore whether the mutations alter sequence-derived protein properties or the predictions of a general AMR-associated protein classifier.

**Important:** The Week 5 classifier distinguishes AMR-associated proteins from non-AMR proteins. It was not trained to predict whether individual mutations increase or decrease antibiotic resistance.

## 2. Objectives

1. Retrieve reference gene and protein sequences for four genes.
2. Prepare structured metadata for the identified mutations.
3. Generate computationally constructed WT and mutant protein sequences.
4. Compare theoretical physicochemical properties between WT and mutant proteins.
5. Reconstruct and save the Week 5 Random Forest classifier.
6. Generate predictions for all eight protein sequences.
7. Export the results into CSV and Excel formats.
8. Document the computational limitations and biological interpretation of the results.

## 3. Mutations investigated

Four mutations were selected for analysis:

| Gene | Protein-level mutation | Mutation type |
|---|---|---|
| ompR | K6T | Amino acid substitution |
| parE | A504V | Amino acid substitution |
| yjgA | Q91L | Amino acid substitution |
| acrR | p.I16_L17insLD | Two-amino-acid insertion |

The nucleotide changes and genomic coordinates were not available from the protein-level annotations. They were therefore recorded as unknown rather than inferred.

## 4. Reference genome and sequence retrieval

**Day 85 — Reference sequence retrieval**

Reference gene sequences were retrieved from the *E. coli* K-12 MG1655 reference genome.

- Organism: *Escherichia coli* K-12 MG1655
- Reference accession: `NC_000913.3`
- Source: NCBI GenBank

The annotated coding sequences were extracted from the original GenBank record and translated to obtain the corresponding reference proteins.

The extraction procedure accounted for coding-strand orientation, including genes encoded on the reverse strand.

### Reference sequence lengths

| Gene | CDS length (bp) | Protein length (aa) |
|---|---:|---:|
| acrR | 648 | 215 |
| ompR | 720 | 239 |
| parE | 1893 | 630 |
| yjgA | 552 | 183 |

### Files generated

```text
week13/reference_genes/
├── acrR.gb
├── ompR.gb
├── parE.gb
└── yjgA.gb
```

The extracted CDS-only GenBank records use coordinates relative to the extracted sequences. These coordinates should not be interpreted as original chromosomal coordinates.

## 5. Mutation metadata

**Day 86 — Mutation annotation**

A structured CSV file was created to maintain consistent mutation information throughout the analysis.

File:

```text
week13/manuscript_mutations.csv
```

The file contains:

- Gene name
- Protein-level mutation
- Mutation type
- Nucleotide change
- Genomic coordinate

Nucleotide changes and genomic coordinates remain unknown because they were not established from the available protein-level annotations.

## 6. Construction of mutant protein sequences

**Day 87 — WT and mutant protein construction**

WT protein sequences were obtained from the reference gene annotations. Mutant sequences were computationally constructed according to the available protein-level mutation descriptions.

For amino acid substitutions, the specified reference residue was replaced with the mutant residue.

For AcrR, the amino acids `LD` were inserted between positions 16 and 17.

### Script

```text
week13/construct_mutant_proteins.py
```

### Output

```text
week13/mutant_proteins.faa
```

### Sequence validation

| Protein | WT length (aa) | Mutant length (aa) |
|---|---:|---:|
| OmpR | 239 | 239 |
| ParE | 630 | 630 |
| YjgA | 183 | 183 |
| AcrR | 215 | 217 |

The FASTA file contains eight sequences:

```text
ompR_WT
ompR_mutant
parE_WT
parE_mutant
yjgA_WT
yjgA_mutant
acrR_WT
acrR_mutant
```

**Limitation:** These mutant protein sequences were computationally constructed from protein-level annotations. They have not been independently validated by translating the nucleotide sequences of the evolved isolates.

## 7. Comparison of protein properties

**Day 88 — Physicochemical property analysis**

The theoretical properties of WT and mutant proteins were calculated and compared.

### Script

```text
week13/compare_protein_properties.py
```

### Outputs

```text
week13/protein_properties.csv
week13/mutation_analysis.xlsx
```

### Properties calculated

- Protein length
- Molecular weight
- Theoretical isoelectric point (pI)
- Grand average of hydropathicity (GRAVY)
- Instability index
- Aromaticity

### Results

| Protein | Length (aa) | Molecular weight (Da) | Theoretical pI | GRAVY | Instability index | Aromaticity |
|---|---:|---:|---:|---:|---:|---:|
| ompR_WT | 239 | 27353.32 | 6.038 | -0.346 | 41.316 | 0.0628 |
| ompR_mutant | 239 | 27326.25 | 5.786 | -0.332 | 41.316 | 0.0628 |
| parE_WT | 630 | 70243.10 | 5.436 | -0.345 | 40.538 | 0.0651 |
| parE_mutant | 630 | 70271.15 | 5.436 | -0.341 | 40.418 | 0.0651 |
| yjgA_WT | 183 | 21359.01 | 5.300 | -0.905 | 53.814 | 0.0328 |
| yjgA_mutant | 183 | 21344.04 | 5.300 | -0.866 | 53.814 | 0.0328 |
| acrR_WT | 215 | 24766.38 | 5.656 | -0.186 | 60.176 | 0.0791 |
| acrR_mutant | 217 | 24994.62 | 5.509 | -0.182 | 59.713 | 0.0783 |

### Main observations

- **OmpR K6T:** Theoretical pI decreased from approximately 6.04 to 5.79.
- **ParE A504V:** GRAVY increased slightly from -0.345 to -0.341.
- **YjgA Q91L:** GRAVY increased from -0.905 to -0.866.
- **AcrR insertion:** Protein length increased from 215 to 217 amino acids.

These are sequence-derived theoretical properties. They do not establish changes in protein structure, folding, stability, abundance, or biological function.

The instability index is a sequence-based heuristic and is not direct evidence of in-vivo protein instability.

## 8. Reconstruction of the Week 5 Random Forest classifier

**Day 89 — AMR classifier reconstruction**

The Week 5 binary AMR classifier was reconstructed and saved for application to the WT and mutant protein sequences.

### Classification objective

The original classifier distinguishes:

- Label 1: AMR-associated proteins
- Label 0: Non-AMR proteins

This is distinct from the separate mechanism-classification analysis.

### Training dataset

Input:

```text
data/kmer_features.csv
```

Dataset characteristics:

| Feature | Value |
|---|---:|
| Total proteins | 2158 |
| AMR-associated proteins | 1079 |
| Non-AMR proteins | 1079 |
| 3-mer features | 8452 |
| Total columns | 8454 |

The dataset contains 8,452 normalized overlapping amino acid 3-mer frequency features, together with protein accession and class label columns.

The feature matrix was checked for missing values, duplicate feature names, and normalized feature sums. No missing values or duplicate feature names were detected. Feature sums were approximately 1 for all training proteins.

### Model configuration

The Random Forest classifier used:

```python
RandomForestClassifier(
    n_estimators=200,
    random_state=42,
    n_jobs=-1
)
```

The dataset was divided into training and test subsets using an 80:20 split, with stratification and `random_state=42`.

### Model performance

| Metric | Result |
|---|---:|
| Accuracy | 0.933 |
| Precision | 0.990 |
| Recall | 0.875 |
| F1-score | 0.929 |

Confusion matrix:

```text
                 Predicted
                 Non-AMR  AMR
Actual Non-AMR      214     2
Actual AMR           27   189
```

These metrics reproduce the model's performance on the original random test split. They do not represent independent external validation.

### Top 20 features

| Rank | 3-mer | Importance |
|---:|---|---:|
| 1 | KTG | 0.015285 |
| 2 | ALR | 0.007810 |
| 3 | YGN | 0.007339 |
| 4 | TFK | 0.006794 |
| 5 | RDT | 0.006739 |
| 6 | STF | 0.006343 |
| 7 | IPG | 0.005939 |
| 8 | VGW | 0.005810 |
| 9 | SDN | 0.005104 |
| 10 | GPL | 0.004987 |
| 11 | DTT | 0.004726 |
| 12 | TGS | 0.004373 |
| 13 | GYG | 0.004233 |
| 14 | SIG | 0.003908 |
| 15 | FWL | 0.003908 |
| 16 | TTG | 0.003815 |
| 17 | DER | 0.003778 |
| 18 | FGY | 0.003651 |
| 19 | AAN | 0.003651 |
| 20 | GWE | 0.003645 |

Feature importance describes the contribution of features to this fitted classifier. It does not establish that these 3-mers are causal determinants of AMR.

### Saved model

```text
week13/week5_random_forest.joblib
```

The saved object contains the fitted model and the original feature-column order, allowing the prediction script to reproduce the training representation.

## 9. Prediction of WT and mutant proteins

**Day 89 — Exploratory ML predictions**

The reconstructed Week 5 classifier was applied to the eight protein sequences.

### Script

```text
week13/predict_mutant_proteins.py
```

### Inputs

```text
week13/mutant_proteins.faa
week13/week5_random_forest.joblib
```

The script generates normalized overlapping 3-mer frequencies, aligns them to the original 8,452-feature vocabulary, and predicts the class and class probabilities.

### Results

| Protein | Length (aa) | Predicted label | Probability non-AMR | Probability AMR |
|---|---:|---:|---:|---:|
| ompR_WT | 239 | 0 | 0.720 | 0.280 |
| ompR_mutant | 239 | 0 | 0.780 | 0.220 |
| parE_WT | 630 | 0 | 0.750 | 0.250 |
| parE_mutant | 630 | 0 | 0.745 | 0.255 |
| yjgA_WT | 183 | 0 | 0.565 | 0.435 |
| yjgA_mutant | 183 | 0 | 0.585 | 0.415 |
| acrR_WT | 215 | 0 | 0.670 | 0.330 |
| acrR_mutant | 217 | 0 | 0.675 | 0.325 |

### WT versus mutant comparison

| Gene | Mutation | WT AMR probability | Mutant AMR probability | Change |
|---|---|---:|---:|---:|
| ompR | K6T | 0.280 | 0.220 | -0.060 |
| parE | A504V | 0.250 | 0.255 | +0.005 |
| yjgA | Q91L | 0.435 | 0.415 | -0.020 |
| acrR | I16_L17insLD | 0.330 | 0.325 | -0.005 |

### Main result

All eight sequences were classified as non-AMR (label 0). None of the four mutations changed the predicted classification.

OmpR K6T showed the largest change in AMR-associated probability (-0.060), while ParE A504V showed a very small increase (+0.005). YjgA Q91L and the AcrR insertion showed small decreases.

These values represent changes in classifier output only. They are not probabilities of antibiotic resistance and cannot be interpreted as evidence that a mutation increases or decreases norfloxacin resistance.

### Prediction output

```text
week13/wt_mutant_predictions.csv
```

## 10. Unseen 3-mer in ParE sequences

One 3-mer, `WCY`, was present in both ParE sequences but absent from the Week 5 training vocabulary.

```text
parE_WT unseen 3-mers: {'WCY': 1}
parE_mutant unseen 3-mers: {'WCY': 1}
```

Because the model uses a fixed training vocabulary, this feature was omitted from both ParE input vectors.

Consequently, the ParE feature sums were approximately 0.9984 rather than 1.0. The original feature representation was retained without renormalizing the remaining features.

This limitation affects both ParE sequences equally and should be considered when interpreting their predictions.

The other six sequences had no unseen 3-mer types.

## 11. Consolidated results

The results were exported into a consolidated Excel workbook.

### Main workbook

```text
week13/week13_complete_analysis.xlsx
```

The workbook contains ten sheets:

| Sheet | Contents |
|---|---|
| Mutation_details | Mutation summary |
| Protein_properties | WT and mutant protein properties |
| WT_vs_mutant | Comparison of protein properties |
| Manuscript_mutations | Mutation metadata |
| ML_predictions | WT and mutant classifier predictions |
| Model_performance | Classifier performance metrics |
| Confusion_matrix | Test-set confusion matrix |
| Top_3mer_features | Top 20 model features |
| Unseen_3mers | Features absent from the training vocabulary |
| Interpretation_notes | Interpretation and limitations |

Additional outputs:

```text
week13/protein_properties.csv
week13/mutation_analysis.xlsx
week13/wt_mutant_predictions.csv
```

## 12. Scientific interpretation and limitations

Week 13 established a computational workflow for sequence-level characterization of four mutations.

The protein-property analysis identified modest differences between WT and mutant sequences. The reconstructed Week 5 classifier classified all eight proteins as non-AMR, with no change in predicted class following mutation.

However, several limitations must be considered:

1. **Mutation validation:** The mutant protein sequences were constructed from protein-level annotations and have not been independently validated against the original evolved-isolate nucleotide sequences.
2. **Classifier scope:** The model predicts AMR-associated versus non-AMR protein membership. It does not predict mutation-specific effects on antibiotic resistance.
3. **Training evaluation:** The reported metrics are from a random protein-level split, not an independent external test set.
4. **Potential homology leakage:** Homologous proteins may occur in both training and test subsets, potentially inflating performance.
5. **Feature vocabulary:** The `WCY` 3-mer was absent from the training vocabulary and omitted from both ParE feature vectors.
6. **Biological interpretation:** Sequence-derived property changes and classifier probability changes do not establish altered protein function or resistance phenotype.

The shared `parE A504V` mutation observed in norfloxacin-evolved populations remains an interesting candidate for further investigation because ParE is a subunit of DNA topoisomerase IV, a fluoroquinolone target. Its presence alone does not establish a causal role in resistance.

Future work should prioritize validation of the nucleotide variants, mutation-specific functional investigation, and comparison of mutation occurrence across independent evolution replicates and treatment groups.

## 13. Week 13 file structure

```text
week13/
├── reference_genes/
│   ├── acrR.gb
│   ├── ompR.gb
│   ├── parE.gb
│   └── yjgA.gb
├── fetch_reference_genes.py
├── manuscript_mutations.csv
├── construct_mutant_proteins.py
├── mutant_proteins.faa
├── compare_protein_properties.py
├── protein_properties.csv
├── mutation_analysis.xlsx
├── predict_mutant_proteins.py
├── week5_random_forest.joblib
├── wt_mutant_predictions.csv
├── export_week13_results.py
└── week13_complete_analysis.xlsx
```

## 14. Week 13 completion summary

| Day | Activity | Main output |
|---|---|---|
| Day 85 | Reference gene and protein retrieval | `reference_genes/` |
| Day 86 | Mutation metadata preparation | `manuscript_mutations.csv` |
| Day 87 | WT and mutant protein construction | `mutant_proteins.faa` |
| Day 88 | Protein-property comparison | `protein_properties.csv`, `mutation_analysis.xlsx` |
| Day 89 | Random Forest reconstruction and mutant predictions | `week5_random_forest.joblib`, `wt_mutant_predictions.csv`, `week13_complete_analysis.xlsx` |

**Status:** Week 13 computational analyses and result exports completed.

The next stage should focus on validating the original nucleotide variants and investigating the biological implications of the mutations, rather than interpreting the general AMR classifier as a mutation-effect predictor.
