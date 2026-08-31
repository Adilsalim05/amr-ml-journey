# Week 5 — Protein Sequence Features and First AMR Classifiers

## Project

**AMR Protein Classification Using Protein Sequence k-mers**

The goal of this week was to move from raw protein sequences to machine-learning-ready numerical features and train our first AMR-vs-non-AMR classifiers.

The two models used were:

1. Logistic Regression
2. Random Forest

The purpose of this stage is primarily **learning the machine-learning workflow**, not producing a publication-ready AMR prediction tool.

---

# 1. What are we trying to predict?

Each protein is assigned one of two labels:

```text
1 = AMR-associated protein
0 = non-AMR protein
```

This is a **binary classification problem**.

The model receives a protein sequence and attempts to predict whether it belongs to class 1 or class 0.

Conceptually:

```text
Protein sequence
       ↓
Convert sequence into numerical features
       ↓
Train machine-learning model
       ↓
Model learns patterns associated with the two classes
       ↓
Predict AMR probability/class for unseen proteins
```

---

# 2. Positive Dataset

The positive dataset was constructed from CARD protein sequences and annotations.

Source:

**Comprehensive Antibiotic Resistance Database (CARD)**

The dataset contains:

```text
Rows: 6052
Label: 1
```

The main columns are:

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

The operational definition used in this project was:

> A protein represented in the selected CARD protein sequence dataset is treated as AMR-associated and assigned label 1.

### Important data-processing detail

The CARD sequence FASTA contained:

```text
6052 sequences
```

The CARD annotation index contained:

```text
6445 rows
```

After joining sequence and annotation information:

```text
Merged rows: 6053
```

One duplicated observation resulted from multiple CARD annotations associated with the same protein sequence.

Rather than treating multiple annotations as multiple independent training observations, we aggregated annotations belonging to the same:

```text
Protein Accession + sequence
```

This produced:

```text
Final positive proteins: 6052
```

This is important because **one protein should represent one training observation**, even if CARD contains multiple annotations for that protein.

---

# 3. Positive-class organism distribution

The positive dataset contains:

```text
676 unique CARD organism labels
```

The largest groups included:

```text
Pseudomonas aeruginosa       1079
Acinetobacter baumannii       731
Klebsiella pneumoniae         700
Escherichia coli              558
Enterobacter cloacae          170
Citrobacter freundii          123
...
```

We also examined organism labels and normalized related labels.

For example:

```text
Pseudomonas aeruginosa PAO1
        ↓
Pseudomonas aeruginosa

Escherichia coli str. K-12 substr. MG1655
        ↓
Escherichia coli
```

Potential parent/child relationships were also identified, including:

```text
Enterobacter cloacae
Enterobacter cloacae complex

Pseudomonas
Pseudomonas aeruginosa
```

This analysis showed that organism composition is an important consideration when constructing the negative dataset and evaluating the classifier.

---

# 4. Negative Dataset

The negative dataset was constructed from RefSeq protein sequences associated with:

```text
Pseudomonas aeruginosa
```

AMR-related annotation keywords were excluded where possible.

The resulting dataset contained:

```text
Rows: 1079
Label: 0
```

Columns:

```text
Protein Accession
sequence
description
organism
label
length
length_bin
```

The negative dataset was deliberately kept at:

```text
1079 proteins
```

because this matched the number of proteins from the dominant positive organism group used for the simplified learning dataset.

---

# 5. Important limitation of the negative dataset

The negative class is **not equivalent to a rigorously validated biological non-AMR class**.

A protein was considered negative largely because it came from a RefSeq dataset and did not have an explicitly AMR-associated annotation under our filtering procedure.

This does NOT prove that every negative protein is biologically unrelated to antimicrobial resistance.

Therefore:

```text
label 0
```

should be interpreted as:

> operationally non-AMR-associated under the dataset construction procedure

rather than:

> experimentally proven non-AMR protein.

This distinction is important.

The negative dataset was intentionally simplified because the primary purpose of this project is to learn the machine-learning workflow.

---

# 6. Why did we try to match protein-length distributions?

Protein length can influence k-mer composition.

For example, a short protein has fewer possible 3-mers than a long protein.

If AMR proteins were mostly short and negative proteins were mostly long, a classifier could potentially exploit length-related sequence characteristics rather than meaningful AMR-associated patterns.

Therefore, we attempted to make the negative dataset resemble the positive dataset in its protein-length distribution.

The important principle is:

> **We don't want every negative protein to have the same length as a positive protein; we want the distribution of lengths in the negative class to resemble the distribution of lengths in the positive class.**

This is **distribution matching**, not one-to-one length matching.

---

# 7. Final ML Dataset

Because the negative dataset contained 1079 proteins, we sampled:

```text
1079 positive proteins
1079 negative proteins
```

giving:

```text
Total proteins: 2158
```

Class distribution:

```text
AMR (1):      1079
Non-AMR (0):  1079
```

The resulting dataset is therefore balanced:

```text
50% positive
50% negative
```

This makes accuracy easier to interpret because the two classes have equal representation.

---

# 8. What is a k-mer?

A **k-mer** is a sequence of `k` consecutive characters.

For proteins, the characters are amino acids.

For example:

```text
Sequence:

MKTAL
```

If:

```text
K = 3
```

we take every consecutive group of three amino acids:

```text
MKT
KTA
TAL
```

Therefore:

```text
MKTAL
 ↓
MKT
KTA
TAL
```

The number of 3-mers in a sequence of length `L` is:

```text
L - k + 1
```

For this example:

```text
5 - 3 + 1 = 3
```

---

# 9. Why use k-mers?

A machine-learning algorithm cannot directly work with a protein sequence such as:

```text
MKTAL...
```

We need to convert the sequence into numerical information.

k-mers provide a simple way of representing sequence composition.

For example:

```text
Protein A

MKTAL
```

produces:

```text
MKT = 1
KTA = 1
TAL = 1
```

The counts can then be converted into frequencies.

In our example:

```text
MKT frequency = 1/3
KTA frequency = 1/3
TAL frequency = 1/3
```

For a real protein containing hundreds of amino acids, the same process generates many 3-mer frequencies.

---

# 10. Why use k-mer frequencies rather than raw counts?

Longer proteins naturally contain more k-mers.

For example:

```text
Protein A = 100 amino acids
Protein B = 500 amino acids
```

Protein B will naturally have many more 3-mers.

Using frequencies partially removes this dependence on protein length.

The feature represents:

> How common is this k-mer within this protein?

rather than simply:

> How many times did this k-mer occur?

---

# 11. Our k-mer representation

We used:

```text
K = 3
```

Therefore:

```text
K = 3 means 3 amino acids per k-mer.
```

It does NOT mean:

```text
number of train/test splits
```

and it does NOT mean:

```text
number of times the model is trained.
```

For example:

```text
MKTAL...
```

produces:

```text
MKT
KTA
TAL
...
```

---

# 12. k-mer feature matrix

The 2158 proteins were converted into a numerical feature matrix.

Result:

```text
Shape: (2158, 8454)
```

There were:

```text
8452 3-mer features
```

plus:

```text
Protein Accession
label
```

Thus:

```text
2158 proteins
×
8452 numerical sequence features
```

The machine-learning model therefore receives a numerical representation of each protein.

Conceptually:

```text
                 MKT     KTA     TAL     ...
Protein 1       0.0038  0.0038  0.0000   ...
Protein 2       0.0000  0.0000  0.0042   ...
Protein 3       0.0000  0.0017  0.0000   ...
```

---

# 13. Non-standard amino-acid symbols

The dataset contained four non-standard amino-acid symbols:

```text
B
J
X
Z
```

Counts:

```text
B = 2
J = 1
X = 278
Z = 2
```

The presence of these symbols is worth documenting because they can generate unusual k-mers.

We did not remove them at this stage because this is a learning dataset and their overall occurrence is relatively limited.

This should be reconsidered in a more rigorous future analysis.

---

# 14. Train/Test Split

We divided the 2158 proteins into:

```text
Training set: 1726 proteins
Test set:       432 proteins
```

using:

```text
TEST_SIZE = 0.20
RANDOM_STATE = 42
stratify = y
```

Therefore:

```text
80% training
20% testing
```

---

# 15. What is the training set?

The training set is the data the model is allowed to learn from.

Here:

```text
1726 proteins
```

were used to train the models.

The model sees:

```text
k-mer features + known label
```

and learns patterns that help distinguish:

```text
AMR vs non-AMR
```

---

# 16. What is the test set?

The test set contains:

```text
432 proteins
```

that were not used to fit the model.

After training, we give these proteins to the model and ask:

> "What do you predict?"

We then compare the predictions with the known labels.

This provides an estimate of how the model performs on unseen data.

---

# 17. What does random_state = 42 mean?

`random_state = 42` is simply a fixed random seed.

The train/test split involves randomization.

Without fixing the seed, running the code again could produce a different split.

For example:

```text
Run 1:
Protein A → training

Run 2:
Protein A → test
```

would make direct comparisons less convenient.

By using:

```text
random_state = 42
```

we tell Python:

> Use the same reproducible randomization every time.

The number `42` itself has no biological meaning.

It could have been:

```text
1
10
42
100
12345
```

The important property is that we keep it fixed when we want reproducible results.

---

# 18. What does stratify = y mean?

We have two classes:

```text
1079 AMR
1079 non-AMR
```

`stratify=y` tells the splitting procedure to preserve approximately the same class proportions in training and test sets.

Our result was:

### Training

```text
Non-AMR: 863
AMR:     863
```

### Test

```text
Non-AMR: 216
AMR:     216
```

This prevents the random split from accidentally producing an imbalanced test set.

---

# 19. Logistic Regression

Our first classifier was **Logistic Regression**.

Despite its name, logistic regression is commonly used for binary classification.

Conceptually, it asks:

> How strongly do the observed features support class 1 versus class 0?

Each k-mer receives a learned coefficient.

The model combines these feature contributions to estimate the probability that a protein belongs to the AMR class.

---

# 20. Logistic Regression results

### Training

```text
Accuracy:  0.899
Precision: 0.996
Recall:    0.802
F1:        0.888
```

### Test

```text
Accuracy:  0.882
Precision: 0.988
Recall:    0.773
F1:        0.868
```

Training-test gaps:

```text
Accuracy:  0.017
Precision: 0.008
Recall:    0.029
F1:        0.021
```

The relatively small train-test differences suggest that the model's performance is fairly consistent between the training and held-out test sets.

---

# 21. Random Forest

The second classifier was a **Random Forest**.

A Random Forest consists of many decision trees.

Instead of relying on one decision tree, the model combines predictions from many trees.

This allows the model to capture more complex and non-linear relationships between features.

Our model used:

```text
n_estimators = 200
```

meaning 200 decision trees.

---

# 22. Random Forest results

### Training

```text
Accuracy:  1.000
Precision: 1.000
Recall:    1.000
F1:        1.000
```

### Test

```text
Accuracy:  0.933
Precision: 0.990
Recall:    0.875
F1:        0.929
```

Train-test gaps:

```text
Accuracy:  0.067
Precision: 0.010
Recall:    0.125
F1:        0.071
```

---

# 23. What does a training score of 1.0 mean?

It means the Random Forest correctly classified essentially every training protein.

It does NOT mean:

> The model has learned AMR perfectly.

It means:

> The model can classify the data it was trained on perfectly.

A highly flexible model can fit the training data extremely well.

Therefore, training performance alone is not sufficient for judging a model.

The crucial question is:

> How does it perform on proteins it has never seen?

Our Random Forest achieved:

```text
Training F1 = 1.000
Test F1     = 0.929
```

Therefore, there is some evidence of overfitting, but the model still performs strongly on the held-out test set.

---

# 24. What is overfitting?

Overfitting occurs when a model learns the training data too specifically and consequently performs substantially worse on new data.

An extreme example would be:

```text
Training F1 = 1.00
Test F1     = 0.50
```

That would be strong evidence that the model has learned patterns specific to the training data.

Our situation is less extreme:

```text
Training F1 = 1.00
Test F1     = 0.929
```

Therefore, we retain the Random Forest but explicitly document the train-test gap.

---

# 25. Formal model comparison

| Metric             | Logistic Regression | Random Forest |
| ------------------ | ------------------: | ------------: |
| Training accuracy  |               0.899 |         1.000 |
| Test accuracy      |               0.882 |     **0.933** |
| Training precision |               0.996 |         1.000 |
| Test precision     |               0.988 |     **0.990** |
| Training recall    |               0.802 |     **1.000** |
| Test recall        |               0.773 |     **0.875** |
| Training F1        |               0.888 |         1.000 |
| **Test F1**        |               0.868 |     **0.929** |
| Train-test F1 gap  |           **0.021** |         0.071 |

Random Forest performed better on every test-set metric.

The most substantial improvement was recall:

```text
Logistic Regression = 0.773
Random Forest       = 0.875
```

---

# 26. Confusion Matrix

For Random Forest:

```text
                 Predicted
                 Non-AMR   AMR

Actual Non-AMR      214      2
Actual AMR           27    189
```

Therefore:

```text
True negatives  = 214
False positives = 2
False negatives = 27
True positives  = 189
```

The model correctly identified:

```text
189 / 216 AMR proteins
```

and correctly rejected:

```text
214 / 216 non-AMR proteins
```

---

# 27. Accuracy

Accuracy is:

```text
correct predictions
-------------------
total predictions
```

For Random Forest:

```text
(214 + 189) / 432
= 0.933
```

Therefore:

```text
Accuracy = 93.3%
```

Accuracy answers:

> Overall, how often was the classifier correct?

---

# 28. Precision

Precision asks:

> When the model predicts AMR, how often is it correct?

Formula:

```text
TP
----------------
TP + FP
```

For Random Forest:

```text
189
---------
189 + 2
```

≈

```text
0.990
```

Therefore, approximately 99% of proteins predicted to be AMR were actually AMR in this test set.

---

# 29. Recall

Recall asks:

> Of all the truly AMR proteins, how many did the model find?

Formula:

```text
TP
----------------
TP + FN
```

For Random Forest:

```text
189
---------
189 + 27
```

=

```text
0.875
```

Therefore, the model detected 87.5% of the AMR proteins in the test set.

---

# 30. F1 score

F1 combines precision and recall into one metric.

Formula:

```text
F1 = 2 × (Precision × Recall)
          --------------------
          Precision + Recall
```

It is useful when we want a balance between:

```text
not generating false AMR predictions
```

and:

```text
not missing genuine AMR proteins
```

Random Forest:

```text
F1 = 0.929
```

Logistic Regression:

```text
F1 = 0.868
```

Therefore, Random Forest performed better under this metric.

---

# 31. Feature Importance

Random Forest identified several 3-mers as important features.

Top features included:

```text
KTG    0.015285
ALR    0.007810
YGN    0.007339
TFK    0.006794
RDT    0.006739
STF    0.006343
IPG    0.005939
VGW    0.005810
SDN    0.005104
GPL    0.004987
```

Feature importance means:

> How useful was a feature for the Random Forest's decision-making across its trees?

It does NOT mean:

> This k-mer causes antimicrobial resistance.

The important k-mers could reflect protein families, taxonomy, conserved domains, sequence composition, dataset construction, or genuine AMR-associated patterns.

Biological interpretation therefore requires additional analysis.

---

# 32. Important methodological limitation: random splitting

Our train/test split was performed at the protein level.

This means related proteins may potentially occur in both training and test sets.

For example:

```text
Protein A
Protein A'
Protein A''
```

could be highly similar but randomly divided between training and testing.

If this occurs, the model may perform well partly because the test protein resembles something it already encountered.

Therefore:

> A strong result under a random protein-level split does not necessarily demonstrate generalization to evolutionarily distant or genuinely novel proteins.

This is one of the most important limitations of the current experiment.

---

# 33. Important limitation: negative-class construction

The negative class was created using a simplified procedure based primarily on RefSeq proteins and annotation filtering.

Potential problems include:

* Some negative proteins may actually have AMR-related functions.
* Absence of an AMR keyword does not prove absence of AMR function.
* The negative class comes disproportionately from Pseudomonas aeruginosa.
* Taxonomic differences between positive and negative classes may provide shortcuts for the classifier.
* Sequence similarity between training and test proteins may inflate performance.

Therefore, the current classifier should be considered a **learning demonstration**, not a validated AMR prediction system.

---

# 34. Current scientific interpretation

The main result from Week 5 is:

> Random Forest outperformed Logistic Regression on the held-out test set, achieving a test F1 score of 0.929 compared with 0.868 for Logistic Regression.

However:

> Random Forest showed a larger training-test performance gap, indicating greater overfitting.

And:

> The random protein-level split and simplified negative-class construction prevent us from concluding that the model will generalize reliably to novel biological sequences.

These limitations should remain attached to the result.

---

# 35. What we have learned

By the end of Week 5, the complete workflow is:

```text
CARD sequences
      ↓
Positive class
      ↓
RefSeq proteins
      ↓
Negative class
      ↓
Balanced ML dataset
      ↓
k-mer feature extraction
      ↓
Train/test split
      ↓
Logistic Regression
      ↓
Random Forest
      ↓
Performance evaluation
      ↓
Model comparison
```

The conceptual progression is:

```text
Biological sequence
       ↓
Feature representation
       ↓
Numerical matrix
       ↓
Machine learning
       ↓
Prediction
       ↓
Evaluation
       ↓
Critical interpretation
```

---

# 36. Current status

## Completed

* [x] CARD positive dataset
* [x] Negative dataset
* [x] Balanced ML dataset
* [x] Protein length analysis
* [x] 3-mer feature extraction
* [x] Non-standard amino-acid check
* [x] 80/20 stratified train/test split
* [x] Logistic Regression
* [x] Random Forest
* [x] Training performance
* [x] Test performance
* [x] Confusion matrices
* [x] Train-test comparison
* [x] Model comparison
* [x] Initial feature-importance analysis

## Current best model

```text
Random Forest
```

Test performance:

```text
Accuracy:  0.933
Precision: 0.990
Recall:    0.875
F1:        0.929
```

## Important caveat

These results are valid for the current dataset and random split.

They should **not** yet be interpreted as evidence that the classifier generalizes to novel AMR proteins.

---

# 37. Next stage

Before claiming biological significance, the next stage should investigate whether the apparent predictive performance is influenced by sequence similarity, taxonomy, or dataset construction.

Possible future evaluations include:

```text
Sequence-similarity-aware splitting
        ↓
Family/group-aware splitting
        ↓
More rigorous negative dataset
        ↓
Cross-validation
        ↓
Hyperparameter evaluation
        ↓
External validation
```

The goal is to move from:

> "Can the model classify this dataset?"

toward:

> "Can the model generalize to proteins that are genuinely new to the model?"

