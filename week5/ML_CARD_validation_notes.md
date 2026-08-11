ML Fundamentals & CARD Concepts — Revision Notes

1. The core ML question

For our CARD-based AMR project, the basic prediction problem is:

Input (X): bacterial protein sequenceOutput (y): antibiotic/drug class

The important distinction is that the model should learn a relationship between the sequence and the target, rather than being handed annotations that already reveal the answer.

A useful mental model is:

Protein sequence
      ↓
sequence representation/features
      ↓
Machine-learning model
      ↓
Predicted antibiotic class

2. What is X and what is y?

X (features/input): information available to the model when making a prediction.

y (target/label): what we want the model to predict.

For the eventual sequence-classification task:

X = protein sequence (or a representation derived from it)
y = antibiotic/drug class

Examples of sequence-derived features could include:

k-mer frequencies

amino-acid composition

sequence embeddings

other representations of the protein sequence

These are different from simply feeding the model CARD annotations that already describe resistance.

3. Understanding a CARD record

A CARD record can contain several biologically different concepts.

For the CblA-1 example:

AMR Gene Family:
    CblA beta-lactamase

Antibiotic:
    cephaloridine

Drug Class:
    cephalosporin

Resistance Mechanism:
    antibiotic inactivation

Protein sequence:
    CblA-1 protein sequence

These concepts should not be treated as interchangeable.

AMR Gene Family ≠ Drug Class

An AMR gene family groups related resistance genes/proteins.

A drug class describes the class of antibiotic against which resistance occurs.

A gene family can be associated with one or multiple antibiotic classes, and an antibiotic class can be associated with many different gene families.

Therefore:

Gene family is not the same thing as the prediction target.

4. Feature leakage

Data leakage occurs when information unavailable in a realistic prediction setting, or information that directly/indirectly reveals the target, enters the model during training.

For example, suppose:

X = protein sequence
y = drug class

and we also give the model:

Resistance mechanism

If the resistance mechanism contains information strongly associated with the drug class, the model may obtain an artificially easy route to the answer.

The model may achieve high accuracy without learning the intended biological relationship.

Key question

Before using a variable as X, ask:

Would I genuinely have this information when I receive an unknown protein sequence and need to make a prediction?

If not, it is a poor candidate for the final input.

5. Why 98% accuracy may not mean much

Suppose a model obtains:

Accuracy = 98%

We should immediately ask:

What exactly did the model learn to achieve 98%?

It might have learned meaningful sequence patterns.

But it might instead be exploiting:

highly similar sequences appearing in both train and test sets

gene-family information

leaked annotations

class imbalance

dataset-specific artifacts

another hidden confounder

Therefore, validation is an experimental-design problem, not merely a metric calculation.

MODEL VALIDATION FRAMEWORK

6. Train/test splitting

The simplest approach is to divide the data:

Dataset
   ↓
Training set + Test set

The model learns from the training set and is evaluated on the test set.

But random splitting can be dangerous for biological sequences.

Example:

Training:
CblA-1
CblA-3

Test:
CblA-2

If these proteins are highly similar, the test is not truly independent.

The model may effectively be recognizing a family it has already seen.

7. Sequence/homology-aware splitting

For biological sequence ML, we should consider sequence similarity when designing train/test splits.

A stronger test can deliberately separate related sequences or gene families.

Conceptually:

Training families:
Family A
Family B
Family C

Test families:
Family D
Family E

Now we ask a harder question:

Can the model generalize to genuinely different sequences rather than simply recognize homologs?

This can provide a much more realistic estimate of biological generalization.

8. Cross-validation

Cross-validation repeatedly divides the data into training and validation portions.

For example, 5-fold cross-validation:

Fold 1 → validation
Fold 2 → validation
Fold 3 → validation
Fold 4 → validation
Fold 5 → validation

This tells us whether performance is reasonably stable across different subsets.

Important limitation

Cross-validation does not automatically solve leakage.

If highly similar sequences occur across the folds, every fold can still produce an overly optimistic result.

The splitting strategy must match the biological question.

9. Baseline models

Before celebrating a sophisticated ML model, compare it with a simple baseline.

Example:

If 70% of observations belong to one class, a model that always predicts that majority class gets:

70% accuracy

Therefore:

Fancy ML model = 72%
Baseline       = 70%

is not impressive.

A useful model should demonstrate meaningful improvement over an appropriate baseline.

10. Ablation studies

An ablation study asks:

Which components or feature groups actually contribute to performance?

For example:

Full model:
sequence + metadata → 95%

Sequence only:
sequence → 84%

Metadata only:
metadata → 93%

This would tell us that much of the predictive power may be coming from metadata rather than sequence.

Ablation is particularly useful for distinguishing the contribution of different feature groups.

11. Permutation testing

Permutation testing deliberately destroys the relationship between X and y.

For example:

Real labels:
sequence → correct drug class

Shuffled labels:
sequence → randomly reassigned drug class

Then train the model again.

Example:

Real labels      → 88%
Shuffled labels  → 51%

This is reassuring because performance collapses when the biological relationship is destroyed.

But:

Real labels      → 88%
Shuffled labels  → 82%

would be a major warning sign.

Possible explanations could include leakage, confounding structure, or an evaluation problem.

12. Negative/control experiments

ML validation has an analogue of wet-lab controls.

We can construct inputs that should not contain meaningful information about the target.

If a model performs surprisingly well on such controls, something may be wrong with the experimental design or dataset.

The principle is:

A model should not be able to extract a strong biological signal from information that should not contain that signal.

13. Error analysis

Overall accuracy can hide important biological failures.

Suppose:

Overall accuracy = 91%

Break it down:

β-lactams       → 97%
aminoglycosides → 94%
tetracyclines   → 63%
macrolides      → 58%

The 91% headline hides poor performance for particular classes.

Therefore, inspect:

confusion matrix

per-class precision

per-class recall

F1 score

examples of incorrect predictions

Then ask:

What biological characteristics do the errors have in common?

14. Class imbalance

Accuracy can be misleading when classes are unevenly represented.

For example:

Class A = 900 sequences
Class B = 50 sequences
Class C = 50 sequences

A model can achieve high accuracy while performing poorly on B and C.

Therefore, for multiclass AMR classification, we should inspect class distributions and use appropriate metrics rather than relying only on accuracy.

15. External validation

One of the strongest tests is to train on one dataset and evaluate on genuinely independent data.

Conceptually:

Training:
CARD

        ↓

Model

        ↓

Independent dataset

If performance remains good, we have stronger evidence that the model generalizes beyond the dataset on which it was developed.

16. Calibration

A classifier may produce probabilities such as:

Cephalosporin = 0.95

Calibration asks whether predictions with approximately 95% confidence are actually correct about 95% of the time.

This matters when predictions will eventually be interpreted as confidence rather than simply as class labels.

17. Sensitivity analysis

A scientific conclusion should not completely depend on one arbitrary analytical choice.

We can ask:

Does performance change substantially with a different reasonable split?

Does it change with another sequence representation?

Does it change when certain feature groups are removed?

Does it change with reasonable model/hyperparameter choices?

If the biological conclusion remains similar, confidence increases.

THE BIG PRINCIPLE

Do not think:

"The model has 98% accuracy, therefore it works."

Think:

"What experiment would convince me that this 98% represents genuine biological generalization?"

That mindset is more important than knowing a particular ML algorithm.

A practical validation hierarchy for our CARD project

We do not need to perform every possible analysis immediately.

A sensible progression is:

1. Understand the dataset
          ↓
2. Define X and y
          ↓
3. Check for leakage
          ↓
4. Inspect class balance
          ↓
5. Establish a baseline
          ↓
6. Design an appropriate split
          ↓
7. Train a simple model
          ↓
8. Cross-validation
          ↓
9. Error analysis
          ↓
10. Ablation / permutation controls
          ↓
11. Similarity-aware validation
          ↓
12. External validation

The central question throughout is:

Is the model learning something biologically meaningful, or is our experimental design making the prediction artificially easy?

Connection to experimental biology

The concepts map closely onto how you already think as a microbiologist:

Wet-lab thinking

ML thinking

Experimental group

Training data

Independent experiment

Test/external dataset

Biological replicate

Independent observations

Negative control

Negative-control model/input

Positive control

Baseline/reference

Remove a component

Ablation

Randomization

Permutation/randomization

Confounder

Data leakage/bias

Reproducibility

Repeated validation

Mechanistic explanation

Error/feature analysis

The important lesson is:

Machine learning is still an experiment. The model is the experimental system, the dataset is the biological material, and the validation strategy determines whether the conclusion is trustworthy.