Yes. I think the best way to preserve this work is to create **two artifacts**:

1. A detailed `README` for Week 5 that documents the scientific rationale, decisions, improvements, learning points, and current state.
2. A **new-chat handoff summary** that you can paste into the next chat so it starts at exactly the same point and maintains the mentoring style.

I have also checked the primary/official resources for CARD, NCBI Entrez, scikit-learn, and peer-reviewed literature on protein k-mers. CARD's current documentation emphasizes curated AMR reference sequences and detection models, while its original database paper describes the Antibiotic Resistance Ontology and curated resistance data. ([GitHub][1])

# Week 5 — AMR-vs-Non-AMR Protein Classifier

## Project

**Machine Learning for AMR Biology — CARD → AMR-vs-Non-AMR Protein Classifier**

The goal of Week 5 is to build the first real machine-learning classifier in the project:

> Given a protein sequence, can we distinguish CARD-associated AMR proteins from proteins that are not represented as AMR proteins in CARD?

This is deliberately a **baseline classifier**, not a production AMR prediction system.

The purpose of this week is to learn the complete workflow:

```text
Biological question
        ↓
Dataset definition
        ↓
Positive-class construction
        ↓
Negative-class construction
        ↓
Quality control
        ↓
Feature extraction
        ↓
Machine learning
        ↓
Evaluation
        ↓
Biological interpretation
```

CARD is an appropriate positive reference because it is a curated resource for antimicrobial-resistance genes and associated detection models, organized through the Antibiotic Resistance Ontology (ARO). ([PubMed][2])

---

# 1. Original Week 5 Plan

The original plan was:

### Day 29

Build the positive class from the CARD protein homolog FASTA.

### Day 30

Build a negative class from NCBI RefSeq proteins, initially using *E. coli* and excluding obvious resistance-related keywords.

### Day 31

Extract amino-acid k-mer frequencies.

### Day 32

Train logistic regression.

### Day 33

Train random forest and inspect feature importance.

### Day 34

Write the classifier README.

### Day 35

Polish the repository and push Week 5.

The original plan was intentionally simple so that the first classifier could be completed without excessive complexity.

---

# 2. What We Improved

The original plan was useful as a learning scaffold, but we identified several weaknesses before accepting it as a scientifically defensible dataset.

## Improvement 1 — Negative class is no longer E. coli-only

### Original

The original plan proposed:

```text
E. coli RefSeq proteins
        ↓
exclude resistance/efflux/antibiotic
        ↓
negative class
```

### Improved

We decided that an E. coli-only negative class could allow the model to learn **species differences rather than AMR biology**.

The improved design is:

```text
CARD organism distribution
        ↓
organism-aware NCBI sampling
        ↓
negative proteins matched to CARD organism representation
```

This is a major improvement because the classifier should not be able to distinguish AMR from non-AMR simply because the two classes have different taxonomic compositions.

---

# 3. Improvement 2 — Explicit CARD organism normalization

The CARD FASTA contains organism information in the FASTA description.

Examples include:

```text
[Klebsiella pneumoniae]
[Escherichia coli]
[Pseudomonas aeruginosa PAO1]
[uncultured bacterium BLR12]
[mixed culture bacterium AX_gF3SD01_15]
```

We therefore decided to preserve the original CARD organism annotation and create a separate explicit normalization table.

The principle is:

```text
strain → parent species
species → species
genus → retain as genus
complex → retain as complex
ambiguous category → handle explicitly
```

For example:

```text
Pseudomonas aeruginosa
+
Pseudomonas aeruginosa PAO1
        ↓
Pseudomonas aeruginosa
```

and:

```text
Escherichia coli
+
Escherichia coli str. K-12 substr. MG1655
        ↓
Escherichia coli
```

This produced:

```text
Pseudomonas aeruginosa = 1,114
Escherichia coli       =   579
```

We deliberately do **not** automatically convert genus or complex labels into species because that would introduce unsupported biological assumptions.

---

# 4. Organism Coverage Decision

CARD contains:

```text
Total organism labels: 676
Total protein sequences: 6052
```

We evaluated practical organism-frequency thresholds:

| Minimum CARD sequences | Positive sequences represented | Coverage |
| ---------------------: | -----------------------------: | -------: |
|                    ≥20 |                          4,530 |   74.85% |
|                    ≥10 |                          4,888 |   80.77% |
|                     ≥5 |                          5,259 |   86.90% |

We selected:

> **≥20 CARD sequences as the operational organism-sampling cutoff.**

This is a **practical dataset-construction cutoff**, not a biological statement that rare organisms are unimportant.

The objective is to obtain enough sequences per organism to construct meaningful NCBI negative samples without creating dozens or hundreds of tiny, poorly supported sampling strata.

---

# 5. Handling Ambiguous CARD Categories

One CARD label was:

```text
Bacteria, Viruses, Fungi, and other genome sequence associated with antimicrobial resistance
```

It contained:

```text
132 sequences
```

We decided:

> Do not use this category to construct organism-matched negative samples.

The rationale is that it is not a biologically coherent organism category.

Importantly:

**Excluding a category from negative sampling does NOT mean deleting those positive CARD proteins from the CARD dataset.**

This distinction must remain explicit in the README.

We also encountered:

```text
uncultured bacterium
```

with 63 sequences.

We decided not to force these proteins into an arbitrary species-level negative target. They remain part of the positive CARD resource but are not assigned a matched species-specific negative target.

---

# 6. Important Dataset Design Decision

After normalization:

```text
Normalized organism targets: 29
CARD positives represented: 4,335
```

This leaves a substantial number of CARD positives outside the organism-matched sampling framework.

We therefore need to distinguish:

### Matched-core classifier dataset

```text
4,335 CARD positives
+
4,335 organism-matched NCBI negatives
```

This is the preferred first classifier dataset because the two classes can be matched at the organism level.

The remaining CARD positives should not simply disappear. They should be retained separately for possible future positive-only evaluation or broader analyses.

This distinction is important because otherwise a reviewer could reasonably ask why the negative class was taxonomically matched to only part of the positive dataset.

---

# 7. Positive Class

The positive class originates from:

```text
data/card/protein_fasta_protein_homolog_model.fasta
```

The CARD protein FASTA contained:

```text
6052 sequences
```

The annotation index contained:

```text
6445 rows
```

The sequence accessions were joined to CARD annotations.

Because one protein accession can have multiple CARD annotations, we decided:

> One protein sequence = one ML observation.

Multiple annotations are aggregated rather than creating multiple observations of the same protein.

This prevents artificial duplication of the same sequence in the training dataset.

The resulting positive dataset contains the sequence plus CARD annotation information.

---

# 8. Critical Positive-Class Improvement

We discovered that the original `positive_class.csv` did not contain organism information.

It contained:

```text
Protein Accession
sequence
ARO Accession
Model Name
AMR Gene Family
Drug Class
Resistance Mechanism
label
```

The original pipeline had extracted the protein sequence but discarded the organism metadata present in the CARD FASTA description.

This was identified as a critical problem before constructing the multi-organism negative dataset.

The pipeline is therefore being modified so that every positive protein carries:

```text
Protein Accession
sequence
CARD Organism
CARD annotations
label
```

The intended integrity check is:

```text
FASTA sequences: 6052
Missing CARD organisms: 0
Unique protein accessions: 6052
```

The organism must remain attached to the individual protein rather than being reconstructed later from aggregate counts.

---

# 9. Negative-Class Philosophy

The original negative-class design was:

```text
NCBI RefSeq
+
exclude resistance
+
exclude efflux
+
exclude antibiotic
```

We retained this basic principle but substantially strengthened the sampling framework.

The negative class is intended to represent:

> proteins that are not identified as AMR proteins under our operational CARD-based definition.

This is **not equivalent to proving that a protein has no relationship whatsoever to antimicrobial resistance**.

That distinction must remain explicit.

A protein may be biologically involved in resistance without having an obvious AMR-related annotation.

Therefore, the negative class is an operational negative class, not an absolute biological truth.

---

# 10. AMR Keyword Filtering

Current exclusion keywords include:

```text
resistance
antibiotic
antimicrobial
efflux
beta-lactamase
carbapenemase
aminoglycoside
chloramphenicol acetyltransferase
```

The NCBI search itself currently excludes several major terms, followed by local annotation filtering.

The local filtering is important because search-level exclusions alone cannot guarantee a clean negative class.

We explicitly observed AMR-like proteins appearing among NCBI candidates, including examples such as:

```text
aminoglycoside 6'-N-acetyltransferase AAC(6')-29
OXA-2 family class D beta-lactamase
aminoglycoside O-phosphotransferase APH(3'')-Ib
DHA2 family efflux MFS transporter permease
```

This demonstrated why the filtering stage cannot be treated as cosmetic.

---

# 11. Partial Protein Filtering

Partial proteins are excluded.

In the *Pseudomonas aeruginosa* pilot:

```text
Retrieved: 1500
Partial: 298
Non-partial: 1202

Partial percentage: 19.87%
```

This was an important empirical finding.

Partial proteins can produce unusual sequence-length distributions and incomplete motifs and therefore are undesirable for the baseline negative dataset.

---

# 12. Exact Duplicate Removal

Exact sequence duplicates are removed before sampling.

In the *Pseudomonas aeruginosa* pilot:

```text
Candidate pool: 4011
Unique sequences: 4011
Exact duplicate sequences: 0
```

The pipeline nevertheless retains the duplicate-removal step because duplication can occur in other organisms or future downloads.

---

# 13. The Most Important Length-Matching Principle

This sentence should remain prominently documented:

> **We don't want every negative protein to have the same length as a positive protein; we want the distribution of lengths in the negative class to resemble the distribution in the positive class.**

This is an important conceptual distinction.

We are not doing:

```text
positive protein 1 = 273 aa
negative protein 1 = 273 aa

positive protein 2 = 289 aa
negative protein 2 = 289 aa
```

Instead, we are doing:

```text
CARD length distribution
        ↓
negative sampling probabilities
        ↓
NCBI negative length distribution
```

For the 6,052 CARD positives:

```text
<100        14       0.23%
100-199    231       3.82%
200-299   3530      58.33%
300-399   1893      31.28%
400-499    132       2.18%
500-699    200       3.30%
700-999     14       0.23%
>=1000      38       0.63%
```

The negative sampler reproduces these proportions within each organism target.

---

# 14. Why Length Matching Matters

Protein length is not the biological question.

If the positive class contained mostly 200–400 aa proteins while the negative class contained mostly 50–150 aa proteins, a classifier could potentially learn length-associated sequence statistics rather than AMR-associated biology.

Therefore:

```text
AMR status
```

should be the intended predictive signal, rather than:

```text
protein length
```

Length matching does not eliminate all confounding. It simply removes one obvious and measurable source of distributional difference.

---

# 15. Organism + Length Matching

The final intended design is stronger than length matching alone.

For each normalized organism:

```text
CARD positives for organism
        ↓
calculate organism-specific length distribution
        ↓
retrieve NCBI proteins from same organism
        ↓
filter partial/AMR-associated proteins
        ↓
remove exact duplicates
        ↓
sample negatives according to that length distribution
        ↓
number of negatives = number of positives
```

Conceptually:

```text
                 CARD
                  │
          ┌───────┴────────┐
          ↓                ↓
      organism          length
          │                │
          └───────┬────────┘
                  ↓
          negative sampling
                  ↓
               NCBI
```

This is much stronger than the original E. coli-only design.

---

# 16. Successful Pseudomonas Pilot

The pipeline has already been tested on:

```text
Pseudomonas aeruginosa
```

CARD positives:

```text
1079
```

NCBI candidates:

```text
6000
```

Usable candidates:

```text
4011
```

Exact unique sequences:

```text
4011
```

Target negatives:

```text
1079
```

Final negatives:

```text
1079
```

Final length distribution:

```text
<100         2
100-199     41
200-299    630
300-399    337
400-499     24
500-699     36
700-999      2
>=1000       7
```

The target distribution is derived directly from CARD rather than manually entered.

---

# 17. Reproducibility

Sampling uses:

```python
random_state = 42
```

Therefore, given the same candidate pool and code, the sampling procedure is reproducible.

However, reproducibility does not mean that NCBI itself is static.

Future NCBI database updates may change:

* candidate counts
* annotations
* available sequences
* search results

Therefore, the exact database retrieval context should eventually be recorded in the final project documentation.

---

# 18. NCBI Retrieval Concepts Learned

The pipeline uses Biopython's Entrez interface.

The conceptual workflow is:

```text
ESearch
   ↓
NCBI protein UIDs
   ↓
EFetch
   ↓
FASTA records
```

NCBI's E-utilities provide programmatic access to Entrez databases, including Protein, and ESearch/EFetch form a standard search-and-retrieval workflow. ([NCBI][3])

Important programming concepts learned:

* API/database querying
* search terms
* Boolean operators
* organism fields
* RefSeq filtering
* UIDs
* FASTA retrieval
* batching requests
* rate limiting
* parsing FASTA records

---

# 19. Python Concepts Learned

This week has also been a Python-learning exercise.

Important concepts include:

### DataFrames

Using pandas to represent biological observations.

### Lists

Collecting sequences and organism labels before creating a DataFrame.

### Dictionaries

Representing sampling targets by length bin.

### Loops

Iterating over FASTA records and organism-specific groups.

### List comprehensions

Compact sequence extraction.

### Functions

Separating reusable feature-extraction operations.

### `Counter`

Counting organism labels.

### `groupby`

Aggregating multiple CARD annotations belonging to the same protein.

### `drop_duplicates`

Removing exact duplicate sequences.

### `pd.cut`

Converting continuous protein lengths into predefined bins.

### `value_counts`

Calculating the distribution of organisms or length categories.

### `sample`

Performing reproducible random sampling.

---

# 20. Machine Learning Concepts to Learn

## Supervised learning

We have known labels:

```text
1 = CARD-associated AMR protein
0 = operational non-AMR protein
```

The model learns a mapping:

```text
protein sequence → feature vector → class
```

---

## Feature extraction

Machine-learning algorithms generally require numerical representations.

Our first representation is amino-acid k-mers.

For protein sequences, the alphabet contains 20 standard amino acids.

For k = 3:

```text
20^3 = 8000 possible tripeptides
```

Therefore each protein becomes an 8,000-dimensional feature vector.

k-mer representations are an established approach for biological sequence representation and have been used specifically for AMR prediction. ([Science Public Journal][4])

---

# 21. Why k-mer Frequencies Rather Than Raw Counts?

Suppose:

```text
Protein A = 100 aa
Protein B = 500 aa
```

If both have similar amino-acid composition, Protein B will naturally contain many more k-mers simply because it is longer.

Raw counts therefore contain a strong length signal.

We use normalized frequencies:

```text
k-mer frequency =
k-mer count / total observed k-mers
```

This makes the representation more comparable across protein lengths.

This does not remove all length-associated effects, but it substantially reduces the direct dependence on sequence length.

---

# 22. k-mer Biological Interpretation

A k-mer is a contiguous sequence of amino acids.

For example:

```text
MKTAYIAK
```

contains 3-mers:

```text
MKT
KTA
TAY
AYI
YIA
IAK
```

The model therefore sees the protein as a collection of local sequence patterns.

This is conceptually similar to representing a protein as a "bag of words."

Protein-sequence machine learning literature explicitly discusses k-mers/n-grams as classical sequence representations. ([Science Public Journal][5])

---

# 23. Why k = 3?

We selected:

```text
k = 3
```

as the first baseline.

This gives:

```text
20^3 = 8000
```

features.

It is large enough to capture local amino-acid patterns while remaining manageable on our current dataset.

We should not assume that k=3 is optimal.

Later experiments could compare:

```text
k = 2
k = 3
k = 4
```

but that is beyond the first baseline.

Increasing k exponentially increases the theoretical feature space, which creates computational and statistical considerations. ([PubMed Central (PMC)][6])

---

# 24. Train/Test Separation

The original plan uses:

```python
train_test_split(
    test_size=0.2,
    stratify=y,
    random_state=42
)
```

The conceptual principle is:

> Never evaluate a model on the same observations used to train it.

Otherwise the model can memorize training examples and produce misleadingly high performance.

scikit-learn explicitly describes evaluating on held-out data as necessary to avoid this form of overfitting. ([Scikit-learn][7])

---

# 25. Stratification

Because we have two classes:

```text
AMR
non-AMR
```

we use:

```python
stratify=y
```

This preserves approximately the same class proportions in training and test sets.

---

# 26. Evaluation Metrics

The original plan deliberately emphasizes:

### Accuracy

```text
correct predictions / total predictions
```

Useful, but potentially misleading.

### Precision

Of the proteins predicted as AMR:

> How many were actually AMR?

### Recall

Of the actual AMR proteins:

> How many did the model identify?

These answer different biological questions.

We should report at least:

```text
accuracy
precision
recall
confusion matrix
```

and later consider:

```text
F1
specificity
balanced accuracy
ROC-AUC
PR-AUC
```

depending on the final dataset design.

---

# 27. Why Accuracy Alone Is Dangerous

If the classes are imbalanced, a classifier can obtain high accuracy by favoring the majority class.

Therefore:

> A high accuracy does not automatically mean a useful AMR classifier.

The model must be evaluated in the context of class balance and the biological cost of false positives versus false negatives.

---

# 28. Logistic Regression

The first model is:

```text
Logistic Regression
```

This provides a simple baseline.

Conceptually:

```text
8,000 k-mer features
        ↓
weighted combination
        ↓
probability of AMR
```

The coefficients can potentially provide information about which k-mers are associated with the prediction.

It is therefore useful as both:

* a baseline classifier
* an interpretable reference model

---

# 29. Random Forest

The second model is:

```text
Random Forest
```

The purpose is not simply to obtain a better number.

We want to ask:

> Does a nonlinear tree-based model capture sequence patterns that logistic regression does not?

The comparison therefore becomes scientifically useful.

---

# 30. Feature Importance

For the random forest we examine:

```python
rf_model.feature_importances_
```

This gives a first approximation of which k-mer features contributed most strongly to the forest's predictions.

However:

> Feature importance is not automatically biological mechanism.

A top-ranked k-mer might reflect:

* a real functional motif
* protein-family composition
* taxonomic composition
* sequence length
* dataset construction
* redundancy
* another confounder

Therefore the top k-mers must be interpreted cautiously.

---

# 31. The Core Scientific Question

The ultimate question is not:

> "Can machine learning classify these two datasets?"

It is:

> **"Does the model learn sequence characteristics associated with CARD-defined AMR proteins rather than simply learning artifacts of how we constructed the dataset?"**

This is why our dataset construction has received so much scrutiny.

---

# 32. Major Potential Confounders

Even after organism and length matching, important confounders remain.

### Homology / redundancy

Highly similar CARD proteins can appear in both training and testing sets.

This could make performance look much better than genuine generalization.

### Protein-family imbalance

Some AMR families are massively overrepresented in CARD.

For example, beta-lactamase families contribute many sequences.

### Taxonomic structure

Even within an organism, sequence composition can reflect phylogenetic structure.

### Annotation bias

CARD is not a random sample of all proteins.

It is intentionally enriched for AMR-associated sequences.

### Negative-class contamination

Some NCBI proteins may actually contribute to AMR biology despite lacking obvious AMR keywords.

### Closed-world assumption

Not being in CARD does not mean a protein is biologically unrelated to AMR.

Our label is therefore:

```text
CARD-associated AMR
vs.
not identified as CARD-associated AMR under our sampling criteria
```

not:

```text
AMR
vs.
biologically incapable of AMR
```

---

# 33. CARD Sampling Bias

We discussed whether matching the negative dataset to CARD's organism distribution constitutes "CARD sampling bias."

Our conclusion:

> CARD is deliberately our positive reference population because the question is specifically about distinguishing CARD-associated AMR proteins from non-CARD proteins.

Therefore we should not artificially make the positive dataset representative of all bacterial proteins.

However, we must clearly state that our classifier's learned concept is constrained by the CARD positive dataset.

This is a **dataset scope limitation**, not something we should hide.

---

# 34. Current Repository Structure

Current important files include:

```text
data/
    card/
        card.json
        aro_index.tsv
        protein_fasta_protein_homolog_model.fasta

    positive_class.csv
    negative_class_Pseudomonas_aeruginosa.csv
    card_organism_counts.csv
    card_organism_mapping.csv

src/
    build_positive_class.py
    build_negative_class.py
    features.py
```

The multi-organism negative pipeline has **not yet been completed**.

---

# 35. Current State

### Completed

* CARD protein FASTA inspection
* CARD positive dataset construction
* CARD annotation aggregation
* organism metadata discovery
* organism-frequency analysis
* ≥20 organism cutoff
* explicit organism normalization
* negative-class design
* NCBI retrieval
* partial-protein filtering
* AMR keyword filtering
* exact duplicate removal
* length-distribution matching
* successful *P. aeruginosa* pilot
* reproducible sampling
* Git tracking

### Currently being implemented

The positive dataset is being modified to preserve:

```text
CARD Organism
```

for every individual protein.

### Not yet completed

* final multi-organism NCBI negative sampler
* final matched-core negative dataset
* k-mer feature matrix
* logistic regression
* random forest
* evaluation
* biological interpretation
* final Week 5 README/results
* Week 5 final Git commit

---

# 36. Immediate Next Step

The next task is **not** to write the multi-organism sampler yet.

First modify `src/build_positive_class.py` so that organism information is retained.

Then verify:

```text
FASTA sequences: 6052
Missing CARD organisms: 0
Unique protein accessions: 6052
```

Only after this integrity check passes should we connect the protein-level organism annotations to:

```text
data/card_organism_mapping.csv
```

Then construct the normalized organism-specific positive subsets.

Then construct the NCBI negatives.

---

# 37. Final Planned Architecture

```text
CARD FASTA
    │
    ├── Protein accession
    ├── Sequence
    └── Original CARD organism
            │
            ↓
CARD annotation index
            │
            ↓
Protein-level positive dataset
            │
            ↓
Explicit organism normalization
            │
            ↓
29 organism targets
            │
            ↓
For each organism:
            │
            ├── CARD positive count
            ├── CARD length distribution
            │
            └── NCBI RefSeq search
                    │
                    ├── remove partials
                    ├── remove AMR-associated annotations
                    ├── remove exact duplicates
                    └── sample by CARD length distribution
                            │
                            ↓
                 organism-matched negatives
                            │
                            ↓
                 matched-core dataset
                            │
                            ↓
                     k-mer features
                            │
                  ┌─────────┴─────────┐
                  ↓                   ↓
           Logistic Regression   Random Forest
                  │                   │
                  └─────────┬─────────┘
                            ↓
                 held-out evaluation
                            ↓
              biological interpretation
```

---

# 38. Learning Resources

### CARD

The original CARD publication is:

McArthur AG et al. **The Comprehensive Antibiotic Resistance Database.** *Antimicrobial Agents and Chemotherapy.* 2013;57:3348–3357. DOI: **10.1128/AAC.00419-13**. ([PubMed][2])

[CARD database and downloads](https://card.mcmaster.ca/download/?utm_source=chatgpt.com)

The current CARD FAQ is particularly useful for understanding how CARD reference sequences and detection models are organized. ([GitHub][1])

### NCBI Entrez / E-utilities

For learning the exact API concepts used in this project:

[NCBI Entrez Programming Utilities documentation](https://www.ncbi.nlm.nih.gov/books/NBK25501/?utm_source=chatgpt.com)

[NCBI E-utilities Quick Start](https://www.ncbi.nlm.nih.gov/books/NBK25500/?report=reader&utm_source=chatgpt.com)

The documentation covers ESearch, EFetch, UIDs, query syntax, batching, and programmatic retrieval. ([NCBI][3])

### Protein k-mers

Moeckel C et al. **A survey of k-mer methods and applications in bioinformatics.** *Computational and Structural Biotechnology Journal.* 2024;23:2289–2303. DOI: **10.1016/j.csbj.2024.05.025**. ([Science Public Journal][4])

Ofer D, Brandes N, Linial M. **The language of proteins: NLP, machine learning & protein sequences.** *Computational and Structural Biotechnology Journal.* 2021;19:1750–1758. DOI: **10.1016/j.csbj.2021.03.022**. ([Science Public Journal][5])

For a directly AMR-related example of amino-acid k-mer machine learning:

**Amino Acid k-mer Feature Extraction for Quantitative Antimicrobial Resistance (AMR) Prediction by Machine Learning and Model Interpretation for Biological Insights.** ([PubMed Central (PMC)][6])

### scikit-learn

[scikit-learn train/test and cross-validation documentation](https://scikit-learn.org/stable/modules/cross_validation.html?utm_source=chatgpt.com)

[scikit-learn train_test_split documentation](https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.train_test_split.html?highlight=model_selection+train_test_split&utm_source=chatgpt.com)

These are useful for understanding why held-out testing is necessary and what `stratify` does. ([Scikit-learn][7])

---

# 39. Week 5 Scientific Take-Home Lessons

The most important lesson from this week is:

> **Machine learning starts with dataset design, not with choosing an algorithm.**

A sophisticated classifier trained on a poorly constructed dataset can produce impressive but meaningless results.

The hierarchy we are following is:

```text
Good biological question
        ↓
Defensible labels
        ↓
Controlled sampling
        ↓
Appropriate representation
        ↓
Model
        ↓
Evaluation
```

The model is therefore only one component of the scientific experiment.

The second major lesson is:

> **A negative class is not defined simply by "whatever is left over."**

We have to make an explicit operational definition of what constitutes a negative observation and then quantify the limitations of that definition.

The third is:

> **Matching distributions is different from matching individual observations.**

Our length-matching strategy is deliberately distributional rather than one-to-one.

Finally:

> **Every dataset-construction decision creates assumptions that the model can exploit.**

Our job is to identify those assumptions before the model does.

---

# 40. Current Stop Point

**STOP HERE.**

Do not begin k-mer extraction or model training yet.

The next session should begin with:

```text
Fix positive_class.py
        ↓
verify organism assignment for all 6052 proteins
        ↓
inspect normalized organism mapping
        ↓
build organism-specific positive subsets
        ↓
generalize negative sampler
```

Only then proceed to machine learning.

And here is the handoff I recommend pasting at the beginning of the new chat.

# Week 5 New-Chat Handoff

I am continuing my **Machine Learning for Biologists / AMR classifier project** from a previous chat. Treat this as the authoritative checkpoint and do not restart the project or repeat decisions already made.

## My learning preference

Act as my **research mentor / PI and Python/ML tutor**, not merely a code generator.

When giving me Python code:

1. Give me the code.
2. Briefly explain what it does and the Python concept I am learning.
3. Give me **one step at a time** rather than a large block of untested code.
4. Wait for my terminal output before moving to the next step.
5. Challenge my assumptions when appropriate.
6. Explain the biological/statistical reason for a computational decision.
7. Do not silently change the methodology.
8. If something is scientifically questionable, tell me explicitly.
9. Treat dataset construction as seriously as model selection.
10. Do not overwhelm me with future steps before the current checkpoint is verified.

I want to understand the Python and ML concepts while building the actual project.

---

# Project

Repository:

```text
~/Projects/amr-ml-journey
```

Environment:

```bash
conda activate bioml
```

Current goal:

> Build the first CARD-based AMR-vs-non-AMR protein classifier using amino-acid k-mer features, logistic regression, and random forest.

---

# CARD Positive Dataset

Original CARD protein FASTA:

```text
data/card/protein_fasta_protein_homolog_model.fasta
```

CARD annotation index:

```text
data/card/aro_index.tsv
```

CARD FASTA sequences:

```text
6052
```

CARD index rows:

```text
6445
```

Unique protein accessions after aggregation:

```text
6052
```

The positive class is operationally defined as:

> Protein sequences represented in the CARD protein homolog reference dataset being used for this project.

This does NOT mean that absence from CARD proves biological absence of AMR.

---

# Important Positive-Class Design

The original `positive_class.csv` accidentally discarded organism information.

It currently contains:

```text
Protein Accession
sequence
ARO Accession
Model Name
AMR Gene Family
Drug Class
Resistance Mechanism
label
```

We discovered that the original CARD FASTA description contains organism information, for example:

```text
gb|AEJ08681.1|ARO:3001109|SHV-52 [Klebsiella pneumoniae]
gb|AAD01868.1|ARO:3002867|dfrF [Enterococcus faecalis]
gb|AAT45742.1|ARO:3000988|TEM-126 [Escherichia coli]
```

Therefore, we are now modifying:

```text
src/build_positive_class.py
```

to preserve:

```text
CARD Organism
```

for every protein.

The next checkpoint is:

```text
FASTA sequences: 6052
Missing CARD organisms: 0
Unique protein accessions: 6052
```

Do NOT move to multi-organism negative sampling until this is verified.

---

# CARD Organism Distribution

CARD has:

```text
676 organism labels
```

Frequency thresholds:

```text
>=20: 4530 sequences = 74.85%
>=10: 4888 sequences = 80.77%
>=5: 5259 sequences = 86.90%
```

Final operational cutoff:

```text
>=20 CARD sequences
```

Reason:

* ~75% coverage
* manageable number of organism targets
* enough observations per target to construct NCBI negatives
* practical sampling cutoff, NOT a biological importance cutoff

There are:

```text
33 original organism labels >=20
```

After explicit normalization:

```text
29 normalized organism targets
4335 represented CARD positives
```

---

# Organism Normalization Decisions

We created:

```text
data/card_organism_mapping.csv
```

The rules are:

```text
strain → parent species
species → species
genus → retain as genus
complex → retain as complex
ambiguous categories → handle explicitly
```

Examples:

```text
Pseudomonas aeruginosa
+
Pseudomonas aeruginosa PAO1
→ Pseudomonas aeruginosa
= 1114 positives
```

```text
Escherichia coli
+
Escherichia coli str. K-12 substr. MG1655
→ Escherichia coli
= 579 positives
```

Do NOT automatically merge:

```text
Pseudomonas
```

into:

```text
Pseudomonas aeruginosa
```

Do NOT automatically merge:

```text
Enterobacter cloacae complex
```

into:

```text
Enterobacter cloacae
```

unless we have an explicit biological justification.

---

# Ambiguous Categories

This CARD category:

```text
Bacteria, Viruses, Fungi, and other genome sequence associated with antimicrobial resistance
```

contains:

```text
132 sequences
```

Decision:

* Do not construct organism-matched NCBI negatives for it.
* Do not delete its positive sequences from CARD.

Also:

```text
uncultured bacterium
```

has:

```text
63 sequences
```

Decision:

* retain in the positive CARD resource
* do not force it into a species-specific negative target

---

# Critical Dataset Decision

We identified that only:

```text
4335 / 6052
```

CARD positives are represented by the 29 normalized organism targets.

Therefore, for the first clean classifier, the preferred design is:

```text
4335 matched CARD positives
+
4335 organism-matched NCBI negatives
```

This is the **matched-core classifier dataset**.

The remaining CARD positives should not simply be deleted. They can be retained separately for future positive-only evaluation or broader analyses.

Do NOT silently create 6052 negatives with only 4335 organism-matched negatives.

---

# Negative-Class Design

The original Week 5 plan proposed E. coli-only NCBI negatives.

We improved this substantially.

Final design:

```text
CARD positive organism
        ↓
same organism NCBI RefSeq candidates
        ↓
remove partial proteins
        ↓
remove obvious AMR-associated annotations
        ↓
remove exact duplicate sequences
        ↓
match CARD protein-length distribution
        ↓
sample same number of negatives as positives
```

The negative class is an **operational negative class**:

> Protein not identified as CARD-associated AMR under our filtering/sampling criteria.

It is NOT proof that the protein is biologically unrelated to AMR.

---

# AMR Filtering

Current keywords:

```text
resistance
antibiotic
antimicrobial
efflux
beta-lactamase
carbapenemase
aminoglycoside
chloramphenicol acetyltransferase
```

We observed that NCBI candidates can contain obvious AMR proteins despite broad search exclusions, so local filtering is necessary.

---

# Partial Proteins

Partial proteins are excluded.

In the Pseudomonas pilot:

```text
Retrieved: 1500
Partial: 298
Non-partial: 1202
Partial percentage: 19.87%
```

---

# Duplicate Removal

Exact sequence duplicates are removed.

Pseudomonas pilot:

```text
Candidate pool: 4011
Unique sequences: 4011
Exact duplicate sequences: 0
```

Keep duplicate removal in the final pipeline even when zero duplicates occur.

---

# Most Important Length-Matching Principle

DO NOT forget this sentence:

> **We don't want every negative protein to have the same length as a positive protein; we want the distribution of lengths in the negative class to resemble the distribution in the positive class.**

We are doing distributional matching, not one-to-one matching.

CARD length distribution:

```text
<100        14       0.23%
100-199    231       3.82%
200-299   3530      58.33%
300-399   1893      31.28%
400-499    132       2.18%
500-699    200       3.30%
700-999     14       0.23%
>=1000      38       0.63%
```

For each organism target, the negative sampler should reproduce the corresponding positive length distribution.

---

# Successful Pseudomonas Pilot

```text
CARD positives: 1079
NCBI candidates: 6000
Usable candidates: 4011
Unique sequences: 4011
Final negatives: 1079
```

Final negative length distribution:

```text
<100         2
100-199     41
200-299    630
300-399    337
400-499     24
500-699     36
700-999      2
>=1000       7
```

Sampling uses:

```python
random_state = 42
```

The target counts are now calculated dynamically from the CARD length proportions rather than hard-coded.

---

# Current Scripts

Positive:

```text
src/build_positive_class.py
```

Negative:

```text
src/build_negative_class.py
```

The negative script is currently a **single-organism prototype**, not yet the final multi-organism pipeline.

It currently contains hard-coded values such as:

```python
ORGANISM = "Pseudomonas aeruginosa"
TARGET = 1079
```

These must eventually become dynamic.

Do not rewrite the negative script from scratch; generalize the working prototype.

---

# Current Immediate Task

We are currently modifying:

```text
src/build_positive_class.py
```

The first change is to extract organism information from the FASTA description.

The relevant logic is:

```python
organisms = []

for r in records:
    description = r.description

    if "[" in description and "]" in description:
        organism = description.split("[")[-1].split("]")[0]
    else:
        organism = None

    organisms.append(organism)
```

Then add:

```text
CARD Organism
```

to `sequence_df`.

The next step after that is to verify:

```text
Missing CARD organisms: 0
```

Do this one step at a time.

---

# Planned ML Workflow

After dataset construction is complete:

```text
organism-matched positive/negative dataset
        ↓
amino-acid k-mer features
        ↓
k=3
        ↓
8000 possible tripeptides
        ↓
normalized frequency vectors
        ↓
train/test split
        ↓
Logistic Regression
        ↓
Random Forest
        ↓
accuracy
precision
recall
confusion matrix
        ↓
feature importance
        ↓
biological interpretation
```

Why k=3?

```text
20^3 = 8000
```

This is deliberately a substantial but manageable baseline feature space.

k-mer methods are established representations for biological sequence machine learning, including AMR prediction.

---

# Important ML Caveats

Do NOT interpret high accuracy as automatically meaningful.

Potential confounders:

* sequence redundancy
* homologous proteins appearing in train/test
* CARD family imbalance
* taxonomic structure
* protein length
* NCBI negative-class contamination
* CARD annotation bias

A particularly important future issue is **homology-aware train/test splitting**.

Random splitting can place highly similar sequences in both training and testing sets and produce optimistic performance.

This should be discussed before treating the classifier as biologically generalizable.

---

# Original Plan vs Improved Plan

Original:

```text
CARD positives
+
E. coli negatives
+
k-mers
+
logistic regression
+
random forest
```

Improved:

```text
CARD positives
        ↓
preserve protein-level organism metadata
        ↓
explicit organism normalization
        ↓
species-aware NCBI negatives
        ↓
AMR annotation filtering
        ↓
partial-protein filtering
        ↓
exact duplicate removal
        ↓
organism-aware length-distribution matching
        ↓
matched-core dataset
        ↓
k-mer representation
        ↓
logistic regression + random forest
        ↓
careful evaluation
```

The major improvement is that we are trying to ensure that the classifier learns **AMR-associated sequence characteristics rather than obvious dataset artifacts**.

---

# Mentoring Rules for This Project

Please continue mentoring me in the same style:

* One step at a time.
* Explain Python briefly whenever code is given.
* Ask me to run the command and show the output.
* Do not jump ahead.
* Explain why a computational decision matters biologically.
* Challenge weak methodological assumptions.
* Think like a reviewer.
* Do not accept a high model accuracy without investigating possible leakage/confounding.
* Do not invent scientific references.
* Cite authentic published literature when making scientific claims.
* Preserve decisions already finalized above.
* If a previous decision appears scientifically problematic, explain why before changing it.
* Do not silently alter the methodology.

## Current stopping point

The next chat should start here:

```text
Modify src/build_positive_class.py
        ↓
preserve CARD Organism
        ↓
run script
        ↓
verify 6052 proteins have organism assignments
        ↓
then continue to organism normalization
```

Do NOT start k-mer extraction yet.
Do NOT start model training yet.
Do NOT rewrite the negative pipeline yet.

[1]: https://github.com/arpcard/FAQ?utm_source=chatgpt.com "GitHub - arpcard/FAQ: Frequently asked questions for CARD, RGI, and ARO. · GitHub"
[2]: https://pubmed.ncbi.nlm.nih.gov/23650175/?utm_source=chatgpt.com "The comprehensive antibiotic resistance database - PubMed"
[3]: https://www.ncbi.nlm.nih.gov/books/NBK25501/?utm_source=chatgpt.com "Entrez® Programming Utilities Help - NCBI Bookshelf"
[4]: https://spj.science.org/doi/10.1016/j.csbj.2024.05.025?utm_source=chatgpt.com "A survey of k-mer methods and applications in bioinformatics | Computational and Structural Biotechnology Journal"
[5]: https://spj.science.org/doi/abs/10.1016/j.csbj.2021.03.022?utm_source=chatgpt.com "The language of proteins: NLP, machine learning & protein sequences | Computational and Structural Biotechnology Journal"
[6]: https://pmc.ncbi.nlm.nih.gov/articles/PMC7694136/?utm_source=chatgpt.com "Amino Acid k-mer Feature Extraction for Quantitative Antimicrobial Resistance (AMR) Prediction by Machine Learning and Model Interpretation for Biological Insights - PMC"
[7]: https://scikit-learn.org/stable/modules/cross_validation.html?utm_source=chatgpt.com "3.1. Cross-validation: evaluating estimator performance — scikit-learn 1.9.0 documentation"

