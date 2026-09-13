# Week 9 Literature Review — Machine Learning-Based AMR Prediction

## Purpose

The purpose of this literature review was to place the Week 9 AMR mechanism-prediction work in the context of existing machine-learning approaches to antimicrobial resistance (AMR) prediction.

The main questions were:

1. How are sequence-derived features such as k-mers used for AMR prediction?
2. How does machine learning relate to established AMR resources such as CARD/RGI and PATRIC/BV-BRC?
3. How does the current project differ from published AMR prediction tasks?

---

## 1. Davis et al. (2016) — AMR Prediction in PATRIC and RAST

**Reference:** Davis et al. (2016), *Antimicrobial Resistance Prediction in PATRIC and RAST*, Scientific Reports.

### Main approach

The study used machine-learning approaches to predict antimicrobial resistance phenotypes from bacterial genome sequences.

The authors used nucleotide sequence features, including short sequence fragments (31-bp k-mers), and applied machine-learning models such as AdaBoost.

### Relevance to this project

This study provides an important precedent for using sequence-derived features for AMR prediction.

The major difference is the prediction target:

* Davis et al.: genome sequence → antimicrobial resistance phenotype
* This project: AMR protein sequence → resistance mechanism

Therefore, the reported performance values should not be directly compared with the Week 9 results.

### Key lesson

Sequence composition can contain predictive information about AMR, but performance depends strongly on the biological prediction task, dataset structure, feature representation, and validation strategy.

---

## 2. ValizadehAslani et al. (2020) — Amino-Acid k-mer Features

**Reference:** ValizadehAslani et al. (2020), *Amino Acid k-mer Feature Extraction for Quantitative Antimicrobial Resistance (AMR) Prediction by Machine Learning and Model Interpretation for Biological Insights*, Biology.

### Main approach

This study investigated amino-acid k-mer/oligopeptide features for quantitative AMR prediction.

The use of amino-acid sequence features is particularly relevant to the current project because the Week 7–9 mechanism classifier also represents proteins using amino-acid 3-mer frequencies.

### Relevance to this project

The study supports the idea that local amino-acid sequence composition can provide useful information for machine-learning models.

The current project differs because it predicts resistance mechanism classes rather than quantitative susceptibility or MIC.

### Key lesson

Protein sequence features can be useful for AMR-related prediction, but model interpretation requires caution because predictive sequence patterns do not automatically correspond to causal biological determinants.

---

## 3. CARD and RGI

### CARD

The Comprehensive Antibiotic Resistance Database (CARD) provides curated information about antimicrobial resistance genes, their associated resistance mechanisms, and related antibiotic information.

The current project uses CARD-derived protein sequences and mechanism annotations as its primary dataset.

### RGI

The Resistance Gene Identifier (RGI) is a CARD-associated computational tool for identifying AMR determinants using CARD models.

RGI is fundamentally different from the machine-learning classifier developed in this project.

RGI relies heavily on curated reference models and sequence/homology-based identification, whereas this project asks whether machine-learning models can learn relationships between protein sequence features and broad resistance-mechanism categories.

### Key lesson

Machine learning should not be presented as a replacement for established AMR identification systems such as CARD/RGI. Instead, it can be investigated as a complementary approach for prediction, classification, prioritization, or discovery.

---

## 4. PATRIC / BV-BRC

PATRIC and its successor, the Bacterial and Viral Bioinformatics Resource Center (BV-BRC), provide bacterial genomic and antimicrobial-resistance phenotype resources.

Machine-learning approaches using these resources have investigated prediction of antimicrobial resistance phenotypes from genomic information.

### Relevance to this project

These resources demonstrate the broader application of machine learning to AMR phenotype prediction.

However, phenotype prediction and resistance-mechanism classification are biologically different tasks.

The current project is therefore better viewed as a protein-level mechanism-classification exercise rather than a direct reproduction of genome-to-phenotype AMR prediction.

---

# Comparison with the Current Project

| Study/resource                | Input                          | Prediction/task                | Feature approach                             | Main relevance                                 |
| ----------------------------- | ------------------------------ | ------------------------------ | -------------------------------------------- | ---------------------------------------------- |
| Davis et al. (2016)           | Bacterial genomes              | AMR phenotype                  | Nucleotide k-mers                            | Demonstrates genomic k-mer ML for AMR          |
| ValizadehAslani et al. (2020) | Protein sequences              | Quantitative AMR prediction    | Amino-acid k-mers                            | Directly relevant to protein sequence features |
| CARD/RGI                      | AMR sequences/reference models | AMR determinant identification | Curated models/homology/SNP models           | Reference framework for AMR identification     |
| PATRIC/BV-BRC                 | Bacterial genomes + phenotypes | AMR phenotype prediction       | Multiple genomic features/ML approaches      | Broader AMR ML context                         |
| Current project               | AMR protein sequences          | Resistance mechanism           | Amino-acid 3-mers + physicochemical features | Tests protein-level mechanism classification   |

---

# Connection to Week 9 Results

The Week 9 comparison used five-fold stratified cross-validation with a balanced Random Forest:

* Amino-acid 3-mers only: **macro-F1 = 0.879 ± 0.021**
* Physicochemical features only: **macro-F1 = 0.837 ± 0.030**
* Combined features: **macro-F1 = 0.894 ± 0.022**

The combined representation therefore performed better than either feature set alone under the current random protein-level validation scheme.

Feature importance analysis also showed that physicochemical features were represented among the most important features. GRAVY and molecular weight ranked first and second overall, while sheet fraction ranked sixth.

These findings suggest that broad protein physicochemical properties may provide information complementary to local amino-acid sequence composition.

However, this should not be interpreted as evidence that physicochemical properties causally determine resistance mechanism.

---

# Important Limitation: Validation Structure

A major lesson from Week 7 is that random protein-level validation can produce substantially more optimistic results than family-aware validation.

The Week 7 family-aware analysis grouped proteins by AMR Gene Family and prevented members of the same family from appearing in both training and validation folds.

Results were substantially lower:

* Random protein-level validation: macro-F1 ≈ **0.727** for the earlier logistic-regression model
* Family-aware validation: macro-F1 ≈ **0.391**

This suggests that related protein families carry substantial predictive information.

Therefore, the Week 9 Random Forest results should be described as performance under **random protein-level cross-validation**, not as evidence of generalization to completely novel AMR families.

A stronger future evaluation would include family-held-out validation or another biologically independent test set.

---

# Main Literature Lessons

### 1. k-mers are an established representation

Both nucleotide and amino-acid k-mer representations have been used in AMR-related machine learning.

The current project therefore builds on an established feature-engineering concept rather than inventing a novel representation.

### 2. Prediction task matte
2. Prediction task matters

Genome → phenotype prediction, protein → mechanism prediction, and AMR-gene identification are different tasks.

Their performance values should not be compared directly.

3. Protein composition contains biological information

The Week 9 results support the broader literature suggesting that amino-acid sequence composition can contain predictive information relevant to AMR.

4. Feature importance is not causality

A feature being highly ranked by a Random Forest does not demonstrate that it mechanistically causes resistance or determines resistance mechanism.

5. Biological validation is critical

Random sequence-level splits can allow related protein families to appear in both training and validation data.

Family-aware validation is therefore important when the goal is to estimate performance on genuinely novel AMR proteins.

6. ML should complement, not replace, curated resources

CARD and RGI provide curated biological knowledge and established AMR identification models.

The machine-learning work here is best viewed as an educational and exploratory extension of that knowledge rather than a replacement for curated AMR detection.

References
Davis JJ, Boisvert S, Brettin T, et al. Antimicrobial Resistance Prediction in PATRIC and RAST. Scientific Reports. 2016.
ValizadehAslani T, et al. Amino Acid k-mer Feature Extraction for Quantitative Antimicrobial Resistance (AMR) Prediction by Machine Learning and Model Interpretation for Biological Insights. Biology. 2020.
McArthur AG, et al. The Comprehensive Antibiotic Resistance Database (CARD). Antimicrobial Agents and Chemotherapy. 2013.
Alcock BP, et al. CARD 2020: antibiotic resistome surveillance with the Comprehensive Antibiotic Resistance Database. Nucleic Acids Research. 2020.
Bacterial and Viral Bioinformatics Resource Center (BV-BRC), formerly PATRIC.
Week 9 Takeaway

The literature supports the use of sequence-derived features, including amino-acid k-mers, for AMR-related machine learning.

The Week 9 analysis extends this idea to a different problem: classification of broad resistance mechanisms from AMR protein sequences.

The most important methodological lesson is that apparent predictive performance must be interpreted together with the biological structure of the dataset. In particular, protein-family-aware validation is necessary before claiming strong generalization to previously unseen resistance families.
