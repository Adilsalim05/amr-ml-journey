# Week 9 --- Feature Engineering, Literature, and Model Interpretation

## Overview

Week 9 focused on moving beyond basic sequence-based machine learning by adding biologically meaningful protein physicochemical features, comparing different feature representations, reviewing relevant AMR machine-learning literature, and examining which features the model actually used.

The week continued the Week 7 resistance-mechanism classification task using AMR proteins from the Comprehensive Antibiotic Resistance Database (CARD).

The central question was:

> Do broad protein physicochemical properties provide information beyond amino-acid k-mer composition when predicting AMR resistance mechanism?

This was a learning and research-development workflow rather than a production AMR prediction system.

---

# Week 9 dataset

The Week 9 analysis used the mechanism dataset generated during Week 7:

```text
data/mechanism_dataset.csv
```

The dataset contains AMR proteins from CARD with fields including:

* Protein Accession
* sequence
* CARD Organism
* AMR Gene Family
* Drug Class
* Resistance Mechanism
* label

The five-class classification task retained the following resistance mechanisms:

```text
0  antibiotic inactivation
1  antibiotic target alteration
2  antibiotic efflux
3  antibiotic target protection
4  antibiotic target replacement
```

The original dataset contained:

```text
6033 proteins
```

Original class distribution:

```text
0    5239
1     285
2     269
3     170
4      70
```

---

# Day 57 --- Protein physicochemical features

## Objective

The first goal was to add protein-level physicochemical features that capture properties not directly represented by individual amino-acid 3-mers.

Biopython's `ProteinAnalysis` was used for feature calculation.

The implementation was added as:

```text
src/physicochemical.py
```

## Features calculated

Eight features were calculated for each valid protein:

| Feature             | Meaning                                                             |
| ------------------- | ------------------------------------------------------------------- |
| `molecular_weight`  | Approximate molecular mass of the protein                           |
| `isoelectric_point` | Estimated pH at which the protein has approximately zero net charge |
| `instability_index` | Sequence-derived estimate of protein stability                      |
| `aromaticity`       | Fraction of aromatic residues F, W, and Y                           |
| `gravy`             | Grand average of hydropathy; overall hydrophobicity                 |
| `helix_fraction`    | Sequence-based alpha-helical propensity estimate                    |
| `turn_fraction`     | Sequence-based beta-turn propensity estimate                        |
| `sheet_fraction`    | Sequence-based beta-sheet propensity estimate                       |

The secondary-structure fractions are sequence-derived estimates and should not be interpreted as experimentally measured protein structures.

## Sequence validation

The feature-extraction function first converted sequences to uppercase, removed terminal `*` characters, and checked that all remaining residues belonged to the standard 20 amino-acid set.

Of the 6033 proteins:

```text
6028 valid proteins
5 excluded proteins
```

The five excluded sequences contained non-standard amino-acid characters that were not accepted by the feature-extraction function.

The sequences were not silently converted to zeros or otherwise imputed because doing so could create biologically meaningless feature values.

The five exclusions represented approximately 0.08% of the dataset.

For the Day 58 comparison, the same 6028 valid proteins were used for all feature sets to ensure a fair comparison.

## Feature extraction test

A test protein was used to verify that the implementation returned the expected physicochemical feature dictionary before applying the function to the full dataset.

The resulting feature matrix had:

```text
6028 valid proteins
8 physicochemical features
```

---

# Day 58 --- Comparing feature representations

## Objective

Three feature representations were compared:

1. Amino-acid 3-mer frequencies
2. Physicochemical features
3. Combined 3-mer + physicochemical features

The existing k-mer representation was based on **amino-acid 3-mers**, not nucleotide k-mers.

The original k-mer matrix contained:

```text
6033 proteins
7954 3-mer features
```

After restricting the analysis to the 6028 valid proteins:

```text
k-mer features:             6028 × 7954
physicochemical features:   6028 × 8
combined features:          6028 × 7962
```

The five excluded proteins were removed from all three representations.

## Class distribution after validation

The resulting dataset contained:

```text
class 0    5236
class 1     285
class 2     267
class 3     170
class 4      70
```

---

## Model

A Random Forest classifier was used:

```python
RandomForestClassifier(
    n_estimators=300,
    class_weight="balanced",
    random_state=42
)
```

The model used class weighting because the mechanism classes were strongly imbalanced.

---

## Validation

Performance was evaluated using five-fold stratified cross-validation:

```python
StratifiedKFold(
    n_splits=5,
    shuffle=True,
    random_state=42
)
```

The evaluation metric was:

```text
F1_macro
```

Macro-F1 calculates the F1 score independently for each class and then takes the mean, giving every mechanism class equal weight regardless of its frequency.

This is more informative than accuracy for this strongly imbalanced classification problem.

---

# Day 58 results

| Feature representation | Mean Macro-F1 | Standard deviation |
| ---------------------- | ------------: | -----------------: |
| 3-mer k-mers only      |         0.879 |              0.021 |
| Physicochemical only   |         0.837 |              0.030 |
| Combined               |         0.894 |              0.022 |

## Interpretation

Under random protein-level five-fold cross-validation:

* 3-mer features were already highly informative.
* Physicochemical features alone performed somewhat less strongly than k-mers.
* Combining the two representations produced the highest mean Macro-F1.
* The combined representation improved over k-mers alone by approximately 0.015 absolute Macro-F1.

The combined model therefore showed an approximately 1.7% relative improvement over the k-mer-only mean Macro-F1:

```text
(0.894 - 0.879) / 0.879 ≈ 1.7%
```

This suggests that physicochemical properties contain information that is at least partly complementary to amino-acid 3-mer composition.

However, this result does **not** establish improved generalization to previously unseen AMR gene families.

That limitation is important because of the family-aware validation performed during Week 7.

---

# Relationship to Week 7 family-aware validation

Week 7 demonstrated that protein-level random splitting can produce substantially different results from family-aware evaluation.

The earlier random protein-level model achieved:

```text
Macro-F1 = 0.727
```

whereas family-aware validation produced:

```text
Macro-F1 = 0.391 ± 0.063
```

The family-aware result was substantially weaker because related proteins were prevented from appearing across both training and validation folds.

Therefore, the Week 9 result:

```text
Combined features: 0.894 ± 0.022 Macro-F1
```

should be interpreted specifically as a result from **random protein-level cross-validation**.

It should not be presented as evidence that the model will achieve 0.894 Macro-F1 on completely unseen AMR gene families.

This distinction is one of the major methodological lessons of the project.

---

# Day 59 --- Literature review

## Objective

The literature review examined machine-learning approaches to AMR prediction, particularly the use of sequence-derived features and k-mer representations.

Three relevant resources were examined.

## Davis et al. — AMR prediction using PATRIC

Davis et al. investigated antimicrobial resistance prediction using machine learning within PATRIC.

Their work used nucleotide k-mer features from whole-genome sequence data and machine-learning classifiers to predict antimicrobial phenotypes.

This provides precedent for using short sequence-derived features for AMR prediction.

However, the task differs from the present project:

```text
Davis et al.
whole genome → antimicrobial phenotype

This project
AMR protein sequence → resistance mechanism
```

Therefore, their reported performance values should not be directly compared with the Macro-F1 values from this project because the datasets, prediction tasks, feature representations, and evaluation metrics differ.

---

## ValizadehAslani et al. — amino-acid k-mer features

ValizadehAslani et al. investigated amino-acid k-mer features for quantitative AMR prediction and compared them with other genomic representations.

This work is particularly relevant because the present project also uses amino-acid k-mers rather than nucleotide k-mers.

Their work demonstrates that protein-level sequence composition can capture useful information for AMR-related machine-learning tasks.

The present project differs by focusing specifically on prediction of the **resistance mechanism** associated with an AMR protein.

---

## BV-BRC

The Bacterial and Viral Bioinformatics Resource Center (BV-BRC) provides AMR phenotype data and machine-learning-based AMR prediction resources.

This demonstrates the broader use of machine learning for AMR phenotype prediction and provides an example of how computational models can be integrated with large biological databases.

---

## Literature takeaway

The literature supports the use of sequence-derived features for AMR prediction, including both nucleotide and amino-acid k-mers.

The Week 9 analysis extends this idea by asking whether combining amino-acid k-mer composition with broad protein physicochemical properties can improve prediction of resistance mechanism.

A major open issue remains **generalization across biological families**. High performance under random sequence-level splits may not translate to performance on genuinely novel AMR gene families.

---

# Day 60 --- What is the model actually learning?

## Objective

After comparing the feature representations, the combined Random Forest was fitted to the valid dataset and feature importances were examined.

The purpose was not to claim biological causation, but to determine whether physicochemical features were actually being used by the model.

## Top 20 features

The top 20 features were:

```text
gravy               0.014122
molecular_weight    0.013909
GRK                 0.007309
VIG                 0.006578
KTG                 0.006293
sheet_fraction      0.006125
TFK                 0.005804
DEP                 0.005030
STF                 0.004866
EKC                 0.004325
IPW                 0.004253
TFE                 0.004190
PNR                 0.004125
SYA                 0.003976
PTN                 0.003942
MGR                 0.003756
DHG                 0.003721
DLT                 0.003620
FFP                 0.003616
EPT                 0.003508
```

## Physicochemical feature importances

All eight physicochemical features received non-zero importance:

```text
gravy                0.014122
molecular_weight     0.013909
sheet_fraction       0.006125
isoelectric_point    0.003372
turn_fraction        0.002909
aromaticity          0.002482
helix_fraction       0.002477
instability_index    0.001446
```

Three physicochemical features appeared among the overall top 20:

```text
1.  gravy
2.  molecular_weight
6.  sheet_fraction
```

GRAVY and molecular weight were the two highest-ranked features in the combined model.

---

# Interpretation of feature importance

The feature-importance analysis suggests that broad protein properties contribute information beyond the 3-mer representation under the random protein-level evaluation.

However, Random Forest impurity-based feature importance has important limitations.

Feature importance:

* does not establish causation
* does not mean that a feature explains that percentage of biological mechanism
* can distribute importance unevenly among correlated features
* depends on the trained model and dataset

Therefore, the appropriate interpretation is:

> Physicochemical properties, particularly GRAVY and molecular weight, were among the most important features in the combined Random Forest under the random protein-level evaluation.

This is an observation about the model, not a biological causal claim.

---

# Week 9 scientific lessons

## 1. Feature engineering matters

Different representations capture different aspects of biological sequences.

```text
3-mer composition
        +
physicochemical properties
        ↓
combined representation
```

The combined representation performed better than either feature set alone under the chosen random protein-level validation.

## 2. Protein properties can carry predictive information

Features such as hydrophobicity, molecular weight, and predicted secondary-structure propensity contributed measurable information to the model.

## 3. Performance depends strongly on the validation strategy

The Week 7 family-aware analysis demonstrated that random protein-level validation can give substantially more optimistic results when related protein families occur across training and validation data.

This remains a central methodological consideration for future AMR models.

## 4. Biological interpretation requires caution

Machine-learning feature importance identifies patterns used by the model. It does not automatically identify biological mechanisms.

Further biological interpretation would require additional analyses and independent validation.

---

# Week 9 limitations

The Week 9 results have several important limitations:

* The dataset is derived from CARD and therefore does not represent all bacterial proteins or all AMR mechanisms.
* The mechanism classes are highly imbalanced.
* Five sequences were excluded because they contained non-standard amino acids.
* The main Week 9 evaluation used random protein-level cross-validation.
* Random protein-level splitting can allow related AMR families to occur across training and validation sets.
* The 0.894 combined Macro-F1 should therefore not be interpreted as a cross-family generalization estimate.
* The physicochemical features are sequence-derived estimates rather than experimentally measured protein properties.
* Random Forest impurity-based feature importance is not causal evidence.
* No statistical test was performed to establish that the difference between the three feature representations is statistically significant.
* The literature comparison involved different datasets, tasks, models, and evaluation metrics; reported performance values should therefore not be treated as directly comparable.

---

# Week 9 learning outcomes

By the end of the completed technical work for Week 9, the following skills had been developed:

* Protein physicochemical feature extraction with Biopython.
* Sequence validation before feature calculation.
* Feature matrix construction with pandas.
* Combining heterogeneous feature representations.
* Random Forest classification with class weighting.
* Stratified five-fold cross-validation.
* Macro-F1 interpretation for imbalanced multi-class problems.
* Literature-based evaluation of feature choices.
* Random Forest feature-importance analysis.
* Critical interpretation of model performance.
* Recognition of family-level information leakage as a biological validation concern.
* Distinguishing predictive association from biological causation.

---

# Week 9 completion checkpoint

The main technical and scientific work for Week 9 was completed:

* [x] Physicochemical feature extraction implemented.
* [x] Protein sequence validation performed.
* [x] Five invalid/non-standard sequences documented and excluded.
* [x] 3-mer-only model evaluated.
* [x] Physicochemical-only model evaluated.
* [x] Combined model evaluated.
* [x] Five-fold stratified cross-validation completed.
* [x] Literature review completed.
* [x] Feature importance analyzed.
* [x] Week 7 family-aware validation results incorporated into interpretation.
* [x] Scientific limitations documented.

Remaining administrative/project closure steps:

* [ ] Send the planned advisor update email.
* [ ] Perform final Week 9 repository consolidation.
* [ ] Commit and push the completed Week 9 work.

---

# Week 9 key result

The central quantitative result of Week 9 was:

```text
3-mer k-mers only:        0.879 ± 0.021 Macro-F1
Physicochemical only:     0.837 ± 0.030 Macro-F1
Combined features:        0.894 ± 0.022 Macro-F1
```

These values were obtained using random protein-level five-fold stratified cross-validation.

The combined representation produced the highest mean Macro-F1, suggesting that physicochemical features provide complementary information beyond amino-acid 3-mer composition.

However, the most important methodological conclusion is:

> A high score under a random protein-level split does not necessarily indicate generalization to unseen AMR gene families.

This builds directly on the family-aware validation lesson from Week 7 and will inform the design of future AMR machine-learning workflows.

---

# Important Week 9 files

```text
src/physicochemical.py
data/mechanism_dataset.csv
data/mechanism_kmer_features.csv
week9/week9_README.md
```

The literature notes will be stored separately in:

```text
notes/literature_review.md
```

once the literature documentation step is committed.

---

# Week 9 status

**Technical analysis: Complete**

**Documentation: In progress**

**Final repository consolidation: Pending**

EOF

After pasting, save it with:

```text
Ctrl + O
```

Then press **Enter** to confirm the filename.

Finally exit nano with:

```text
Ctrl + X
```

Then **do not commit yet**. We will verify the file first.

