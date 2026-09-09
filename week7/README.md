# Week 7 — AMR Resistance Mechanism Prediction

## 1. Overview

Week 7 extends the AMR-ML project from binary classification of antimicrobial resistance (AMR) proteins to prediction of the **mechanism by which an AMR protein contributes to resistance**.

### Week 5

The original task was:

```text
CARD AMR proteins + non-AMR proteins
              ↓
          3-mer features
              ↓
   Logistic Regression / Random Forest
              ↓
       AMR vs non-AMR
```

### Week 7

The new task is:

```text
CARD AMR proteins
       ↓
Resistance mechanism labels
       ↓
     3-mer features
       ↓
  Logistic Regression
       ↓
Resistance mechanism
```

Unlike Week 5, a negative/non-AMR dataset is not required because the objective is to distinguish between **different resistance mechanisms among proteins already known to be associated with AMR**.

---

# 2. Biological Question

The biological question for Week 7 is:

> **Can protein sequence alone be used to predict the resistance mechanism associated with an AMR protein?**

The CARD database assigns AMR proteins to resistance mechanisms such as:

* antibiotic inactivation
* antibiotic target alteration
* antibiotic efflux
* antibiotic target protection
* antibiotic target replacement
* reduced permeability to antibiotic
* resistance by host-dependent nutrient acquisition

The machine-learning task is therefore a **multi-class classification problem**.

---

# 3. Dataset

The analysis used the CARD-derived dataset generated during the earlier AMR-ML workflow.

The existing file was:

```text
data/positive_class.csv
```

It contained 6,052 AMR protein sequences and the following columns:

```text
Protein Accession
sequence
CARD Organism
ARO Accession
Model Name
AMR Gene Family
Drug Class
Resistance Mechanism
label
```

Importantly, the resistance mechanism information was already present in this dataset. Therefore, no additional blind join between protein sequences and the CARD ARO index was necessary.

---

# 4. Initial Resistance Mechanism Distribution

The original CARD dataset contained 10 distinct mechanism labels.

| Resistance mechanism                                       | Proteins |
| ---------------------------------------------------------- | -------: |
| antibiotic inactivation                                    |    5,239 |
| antibiotic target alteration                               |      285 |
| antibiotic efflux                                          |      269 |
| antibiotic target protection                               |      170 |
| antibiotic target replacement                              |       70 |
| reduced permeability to antibiotic                         |        8 |
| antibiotic efflux;reduced permeability to antibiotic       |        4 |
| antibiotic efflux;antibiotic target alteration             |        4 |
| antibiotic target alteration;antibiotic target replacement |        2 |
| resistance by host-dependent nutrient acquisition          |        1 |

There were no missing resistance-mechanism labels.

The dataset was therefore **extremely imbalanced**, with antibiotic inactivation representing the overwhelming majority of proteins.

---

# 5. Handling Multi-Mechanism and Extremely Rare Classes

Two methodological decisions were made before training the first classifier.

## 5.1 Multi-mechanism records

Ten proteins had multiple mechanism annotations.

Rather than arbitrarily assigning each protein to one mechanism, these records were excluded from the first single-label classifier.

This produces a cleaner biological interpretation because the model is explicitly being asked to predict **one mechanism per protein**.

## 5.2 Extremely rare mechanisms

The following classes were excluded:

* reduced permeability to antibiotic — 8 proteins
* resistance by host-dependent nutrient acquisition — 1 protein

The remaining five mechanisms were:

```text
0 = antibiotic inactivation
1 = antibiotic target alteration
2 = antibiotic efflux
3 = antibiotic target protection
4 = antibiotic target replacement
```

The resulting dataset contained:

**6,033 proteins**

with the following distribution:

| Label | Mechanism                     | Proteins |
| ----: | ----------------------------- | -------: |
|     0 | antibiotic inactivation       |    5,239 |
|     1 | antibiotic target alteration  |      285 |
|     2 | antibiotic efflux             |      269 |
|     3 | antibiotic target protection  |      170 |
|     4 | antibiotic target replacement |       70 |

---

# 6. Sequence Duplication Check

Before machine learning, exact sequence duplication was checked.

Results:

```text
Total proteins:              6033
Unique sequences:            6033
Duplicate sequence records:     0
Sequences occurring >1 time:   0
```

Therefore, there were no exact duplicate protein sequences in the retained dataset.

However, absence of exact duplicates does **not** mean that all sequences are independent.

Proteins belonging to the same AMR gene family can still be highly similar. This became an important issue during validation.

---

# 7. Gene-Family Diversity

A critical part of understanding this dataset was examining the number of independent AMR gene families represented within each mechanism.

| Mechanism               | Proteins | Gene families |
| ----------------------- | -------: | ------------: |
| antibiotic inactivation |    5,239 |           333 |
| target alteration       |      285 |            32 |
| efflux                  |      269 |            10 |
| target protection       |      170 |            10 |
| target replacement      |       70 |             3 |

This revealed an important structural property of the dataset.

Some mechanisms contain many independent gene families, while others are represented by only a handful.

For example:

* antibiotic inactivation: 333 families
* antibiotic efflux: 10 families
* target protection: 10 families
* target replacement: only 3 families

Therefore, **protein count is not equivalent to biological diversity**.

A mechanism with 269 proteins may have considerably less independent sequence diversity than a mechanism with 285 proteins if those proteins come from fewer gene families.

---

# 8. Gene-Family Concentration

The distribution within several mechanisms was highly concentrated.

### Antibiotic inactivation

The largest families included:

* PDC beta-lactamase — 639
* OXA beta-lactamase;OXA-51-like beta-lactamase — 383
* ADC beta-lactamases pending classification for carbapenemase activity — 274
* CTX-M beta-lactamase — 267
* KPC beta-lactamase — 229

The top five families accounted for approximately **34%** of all antibiotic-inactivation proteins.

The top ten accounted for approximately **51%**.

### Target alteration

The top five families accounted for approximately **67%** of the class.

### Efflux

The top five families accounted for approximately **97%** of the class.

### Target protection

The top five families accounted for approximately **91%** of the class.

### Target replacement

All 70 proteins belonged to only three gene families:

* dfr — 59
* methicillin resistant PBP2 — 7
* sul — 4

This means that a random protein split can easily place highly related proteins from the same family in both training and testing sets.

---

# 9. Feature Engineering

Protein sequences were converted into **3-mer features**.

A 3-mer is a sequence of three consecutive amino acids.

For example:

```text
MKTAVLG
```

produces:

```text
MKT
KTA
TAV
AVL
VLG
```

The model therefore does not directly receive the complete protein sequence. Instead, it receives numerical features describing the occurrence of short amino-acid sequence patterns.

The resulting feature file was:

```text
data/mechanism_kmer_features.csv
```

It contained:

```text
6033 proteins
7954 distinct 3-mer features
```

The complete dataframe contained 7,958 columns because it also included metadata such as protein accession and label.

---

# 10. Protein-Level Train/Test Split

The initial experiment used a stratified protein-level 80/20 split.

Parameters:

```text
test_size = 0.20
random_state = 42
stratify = y
```

Result:

```text
Training proteins: 4,826
Test proteins:     1,207
```

Class distribution:

| Mechanism          | Training |  Test |
| ------------------ | -------: | ----: |
| inactivation       |    4,191 | 1,048 |
| target alteration  |      228 |    57 |
| efflux             |      215 |    54 |
| target protection  |      136 |    34 |
| target replacement |       56 |    14 |

This preserves approximately the same class proportions between training and testing.

---

# 11. Initial Logistic Regression

The first model was standard multinomial Logistic Regression.

The initial model did **not** use class weighting.

The model predicted essentially everything as the majority class:

```text
[[1048,    0,    0,    0,    0],
 [  57,    0,    0,    0,    0],
 [  54,    0,    0,    0,    0],
 [  34,    0,    0,    0,    0],
 [  14,    0,    0,    0,    0]]
```

The resulting accuracy was approximately:

```text
0.868
```

At first glance this appears reasonable.

It is not.

Because antibiotic inactivation represents 5,239 of 6,033 proteins, predicting the majority class can produce high overall accuracy without successfully identifying the minority mechanisms.

This was an important demonstration of why **accuracy alone is inappropriate for this problem**.

---

# 12. Class-Weighted Logistic Regression

To account for the severe class imbalance, the model was changed to:

```python
LogisticRegression(
    max_iter=1000,
    random_state=42,
    class_weight="balanced"
)
```

`class_weight="balanced"` gives greater importance to observations belonging to smaller classes during model training.

It does not make the biological dataset balanced, nor does it eliminate the underlying limitation of having few independent families.

It simply prevents the optimization process from treating the majority class as overwhelmingly important.

---

# 13. Protein-Level Results

The class-weighted model produced:

| Metric            |    Result |
| ----------------- | --------: |
| Accuracy          |     0.863 |
| Balanced accuracy | **0.803** |
| Macro precision   | **0.746** |
| Macro recall      | **0.803** |
| Macro F1          | **0.727** |

The confusion matrix was:

```text
                         Predicted
                 0     1     2     3     4

Actual 0       915    80    53     0     0
       1         0    45    12     0     0
       2         0     6    48     0     0
       3         0     9     2    23     0
       4         0     2     1     0    11
```

The results were substantially better than the unweighted model.

The most important metrics here are balanced accuracy and macro-F1 because they prevent the large inactivation class from dominating the evaluation.

---

# 14. Interpretation of Protein-Level Results

The model appears capable of distinguishing several mechanisms from protein sequence.

For example, target protection had:

```text
Precision: 1.00
Recall:    0.68
F1:        0.81
```

Target replacement had:

```text
Precision: 1.00
Recall:    0.79
F1:        0.88
```

However, these values must be interpreted cautiously.

Target replacement had only 14 proteins in the test set and only three gene families in the entire dataset.

Therefore, strong performance on this class does not demonstrate that the model can generalize to previously unseen target-replacement mechanisms.

---

# 15. The Major Validation Problem

The protein-level split assumes that individual proteins are sufficiently independent.

For AMR proteins, this assumption is questionable.

Suppose the dataset contains:

```text
Family A
 ├── Protein 1
 ├── Protein 2
 ├── Protein 3
 └── Protein 4
```

A random protein split could produce:

```text
Training:
Protein 1
Protein 2
Protein 3

Testing:
Protein 4
```

The model has therefore already seen highly related sequences from Family A during training.

This can make the test set easier than the real-world problem of encountering a **new AMR gene family**.

The correct scientific question is therefore more demanding:

> Can the model predict the resistance mechanism of a protein belonging to an AMR gene family that was completely absent from training?

---

# 16. Family-Aware Validation

To address this problem, family-aware cross-validation was performed.

The grouping variable was:

```text
AMR Gene Family
```

The validation method was:

```python
StratifiedGroupKFold(
    n_splits=5,
    shuffle=True,
    random_state=42
)
```

This simultaneously attempts to:

1. keep related proteins from the same gene family together;
2. maintain reasonable mechanism-class distributions across folds.

For every fold, the number of AMR gene families shared between training and validation was:

```text
0
```

Therefore, validation proteins came from gene families that were not present in the corresponding training set.

This is a much more stringent test of generalization.

---

# 17. Family-Aware Cross-Validation Results

The five-fold results were:

| Fold | Accuracy | Balanced Accuracy | Macro F1 |
| ---- | -------: | ----------------: | -------: |
| 1    |    0.832 |             0.516 |    0.364 |
| 2    |    0.760 |             0.508 |    0.410 |
| 3    |    0.823 |             0.626 |    0.475 |
| 4    |    0.672 |             0.498 |    0.305 |
| 5    |    0.772 |             0.509 |    0.402 |

Mean ± SD:

```text
Accuracy:            0.772 ± 0.064
Balanced accuracy:   0.531 ± 0.053
Macro precision:     0.383 ± 0.059
Macro recall:        0.531 ± 0.053
Macro F1:            0.391 ± 0.063
```

---

# 18. Protein-Level vs Family-Aware Performance

The difference is substantial.

| Validation strategy | Balanced accuracy |          Macro F1 |
| ------------------- | ----------------: | ----------------: |
| Protein-level split |         **0.803** |         **0.727** |
| Family-aware CV     | **0.531 ± 0.053** | **0.391 ± 0.063** |

This is the most important result of Week 7.

The model performs considerably better when related proteins from the same AMR gene families can appear in both training and testing.

When entire gene families are held out, performance decreases substantially.

---

# 19. Scientific Interpretation

The results suggest that the 3-mer Logistic Regression model is learning useful sequence patterns associated with resistance mechanisms.

However, a significant portion of the apparent performance under a random protein split is likely associated with **family-specific sequence signatures**.

In other words:

```text
Protein-level split
       ↓
Related families appear in both sets
       ↓
High performance
```

whereas:

```text
Family-aware split
       ↓
Entire families are unseen during training
       ↓
Much harder prediction problem
       ↓
Substantially lower performance
```

This does not mean that the model is useless.

Instead, it tells us what the model has actually learned and where its limitations are.

---

# 20. Structured Errors

The family-aware confusion matrices showed that the errors were not completely random.

In particular, there was substantial confusion between:

* target alteration and efflux
* target alteration and target protection
* inactivation and efflux
* inactivation and target alteration

The amount of confusion varied substantially between folds.

This indicates that performance depends strongly on which gene families happen to be held out.

---

# 21. Target Protection as an Example

Target protection illustrates the problem particularly well.

In one fold, 108 target-protection proteins were present in validation and 92 were correctly classified.

In other folds, the classifier correctly identified very few or none.

This variability occurs because the target-protection class contains only about 10 gene families.

When a particular family is held out, the model may have very little sequence information from related families available during training.

Therefore, the problem is not simply:

> "How many proteins do we have?"

It is also:

> "How many biologically independent families do we have?"

---

# 22. Target Replacement

Target replacement is even more limited.

The entire class contains only three gene families:

```text
dfr
methicillin resistant PBP2
sul
```

Although the protein-level test-set performance was apparently strong, there are insufficient independent families to make a strong claim about generalization to unseen target-replacement families.

For this reason, target replacement was excluded from the family-aware cross-validation analysis.

This is a limitation of the dataset rather than a failure of the machine-learning implementation.

---

# 23. Drug-Class Analysis

The relationship between resistance mechanism and CARD Drug Class was also examined.

After excluding target replacement, the dataset contained 115 exact Drug Class strings.

The mechanisms showed substantial differences in drug-class structure.

### Antibiotic inactivation

There were 31 exact Drug Class strings.

The five most common categories represented approximately:

```text
67.9% of the class
```

### Target alteration

There were 16 exact Drug Class strings.

The five most common categories represented approximately:

```text
90.2% of the class
```

### Target protection

There were 20 exact Drug Class strings.

The five most common categories represented approximately:

```text
87.1% of the class
```

### Efflux

There were 72 exact Drug Class strings.

The five most common categories represented approximately:

```text
41.3% of the class
```

These results show that resistance mechanisms and drug classes are strongly structured.

For example, target protection is heavily associated with particular antibiotic categories, while efflux is distributed across a broader range.

---

# 24. Potential Drug-Class Confounding

This creates a potential confounding issue.

If certain mechanisms are strongly associated with particular drug classes, a sequence classifier may indirectly exploit sequence patterns associated with those biological categories.

However, the current analysis does **not** establish that Drug Class is a causal confounder of the model.

It is therefore more appropriate to state:

> Drug Class is strongly structured with respect to resistance mechanism and may contribute to the observed classification patterns.

This should be treated as a limitation and possible future analysis rather than as a proven explanation for the model's performance.

---

# 25. Important Methodological Lessons

Week 7 demonstrated several important machine-learning principles.

### 1. Accuracy can be misleading

With severe class imbalance, a model can achieve high accuracy by favoring the majority class.

Therefore:

```text
Accuracy alone ≠ good classifier
```

Balanced accuracy and macro-F1 are more informative here.

### 2. Class weighting helps but does not solve the biological problem

`class_weight="balanced"` substantially improved minority-class recognition.

However, it cannot create new biological diversity.

### 3. Exact duplicate removal is not enough

There were no exact duplicate sequences, but related proteins within the same AMR gene family can still create information leakage.

### 4. Random protein splitting can overestimate generalization

A random protein-level test set may contain close relatives of proteins seen during training.

### 5. Family-aware validation provides a harder and more biologically meaningful test

Holding out entire gene families asks whether the model can generalize beyond the families it has already seen.

### 6. Protein count is not the same as biological diversity

A class with hundreds of proteins may still represent only a small number of independent gene families.

---

# 26. Limitations

The Week 7 model has several important limitations.

## Dataset limitations

* The classes are severely imbalanced.
* Several mechanisms contain very few proteins.
* Some mechanisms contain very few independent gene families.
* Ten multi-mechanism records were excluded.
* Extremely rare mechanisms were excluded from the initial model.
* CARD annotations represent database-defined biological categories and are not necessarily perfectly independent.

## Feature limitations

The model uses only 3-mer sequence features.

It does not explicitly model:

* protein domains
* protein structure
* evolutionary profiles
* genomic context
* gene neighborhood
* phylogenetic relationships
* functional annotations

## Validation limitations

The protein-level split is susceptible to family-related information leakage.

Family-aware validation addresses this problem but is itself difficult because some mechanisms contain very few independent families.

## Drug-class structure

Resistance mechanisms and drug classes are strongly associated in CARD.

This may contribute to sequence-level classification patterns and should be investigated further if mechanism prediction becomes a major research objective.

---

# 27. Final Scientific Conclusion

A 3-mer-based Logistic Regression classifier was able to predict antibiotic resistance mechanisms from CARD protein sequences with good performance under a stratified protein-level split, achieving a balanced accuracy of **0.803** and macro-F1 of **0.727**.

However, performance decreased substantially when validation was performed at the AMR gene-family level, with a balanced accuracy of **0.531 ± 0.053** and macro-F1 of **0.391 ± 0.063**.

This demonstrates that the apparent performance of the classifier depends strongly on whether related AMR gene families are shared between training and testing data.

The results therefore suggest that the model learns meaningful sequence patterns associated with resistance mechanisms, but has **limited generalization to previously unseen AMR gene families**.

Analysis of dataset composition revealed substantial concentration of several mechanisms within a small number of gene families, particularly antibiotic efflux and target protection. This limited family diversity likely contributes to the observed generalization gap.

Drug Class was also found to be strongly structured with respect to resistance mechanism, representing a potential source of biological confounding that should be considered in future analyses.

Overall, the main result of Week 7 is not simply that the classifier achieves high accuracy. Rather, the analysis demonstrates the importance of **family-aware validation when evaluating sequence-based AMR machine-learning models**.

---

# 28. Files Generated

### Dataset

```text
data/mechanism_dataset.csv
data/mechanism_kmer_features.csv
```

### Scripts

```text
src/train_mechanism_logistic_regression.py
src/evaluate_mechanism_logistic_regression.py
src/evaluate_mechanism_family_cv.py
src/analyze_mechanism_drugclass.py
```

### Input dataset

```text
data/positive_class.csv
```

---

# 29. Key Commands

Generate the mechanism dataset:

```bash
python src/<mechanism_dataset_script>.py
```

Generate 3-mer features:

```bash
python src/extract_kmers.py
```

Train the protein-level Logistic Regression model:

```bash
python src/train_mechanism_logistic_regression.py
```

Evaluate the protein-level model:

```bash
python src/evaluate_mechanism_logistic_regression.py
```

Run family-aware cross-validation:

```bash
python src/evaluate_mechanism_family_cv.py
```

Analyze mechanism/drug-class structure:

```bash
python src/analyze_mechanism_drugclass.py
```

---

# 30. Week 7 Take-Home Message

The central lesson from Week 7 is:

> **A sequence classifier can appear highly accurate when closely related proteins are distributed between training and testing sets. For biological sequence prediction, the real test is often whether the model generalizes to previously unseen gene families.**

For AMR prediction, therefore:

```text
Random protein split
        ↓
Useful for initial model development
        ↓
May overestimate performance

Family-aware validation
        ↓
More difficult
        ↓
Better test of biological generalization
```

Week 7 therefore establishes both a baseline mechanism classifier and a more realistic assessment of its limitations.

