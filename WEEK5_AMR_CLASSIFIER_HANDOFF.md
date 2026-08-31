Absolutely. Here is a **self-contained handoff summary** you can paste into a new chat. It includes the methodological decisions, current files, commands, and exact stopping point.

# AMR Classifier — Week 5 Handoff Summary

I am building an **AMR-vs-non-AMR protein classifier** as part of my AMR bioinformatics/ML project. Act as my research mentor/PI and ML tutor. Teach progressively: explain what commands/code do and why before I run them; don't jump ahead or rewrite working code unnecessarily. Challenge methodological weaknesses like a reviewer.

## Project/repository

Repository:

```bash
~/Projects/amr-ml-journey
```

Conda environment:

```bash
bioml
```

Python 3.11.

---

# 1. CARD positive dataset

We constructed the CARD positive class from:

```text
data/card/...
```

The finalized positive dataset is:

```text
data/positive_class.csv
```

It contains:

**6,052 AMR protein sequences**

Current columns:

```text
sequence
ARO Accession
Model Name
AMR Gene Family
Drug Class
Resistance Mechanism
label
```

`label = 1`.

Important: **positive_class.csv currently does NOT contain the organism annotation.**

This is the issue we discovered at the end of this chat.

The script used to construct it is:

```text
src/build_positive_class.py
```

We need to inspect this script next to determine where CARD organism information was available during construction and how to carry it into the positive dataset.

---

# 2. CARD organism distribution

We generated:

```text
data/card_organism_counts.csv
```

This contains **676 CARD organism labels** and their positive counts.

The top portion included:

```text
Pseudomonas aeruginosa             1079
Acinetobacter baumannii             731
Klebsiella pneumoniae               700
Escherichia coli                    558
Enterobacter cloacae               170
Bacteria, Viruses, Fungi...        132
Citrobacter freundii               123
...
```

The complete ≥20 subset contains **33 organism labels**, representing:

**4,530 / 6,052 = 74.85%**

We evaluated:

* ≥20 → 4,530 / 6,052 = **74.85%**
* ≥10 → 4,888 / 6,052 = **80.77%**
* ≥5 → 5,259 / 6,052 = **86.90%**

We chose:

> **≥20 as the operational cutoff.**

Reason: it gives a manageable organism set while covering ~75% of CARD. This is a **pragmatic sampling-design cutoff**, not a biological claim that rare organisms are unimportant.

---

# 3. Negative-class design agreed upon

The negative class will come from **NCBI RefSeq proteins**, not arbitrary proteins.

Our design principles are:

1. **Species-aware sampling**, rather than E. coli-only.
2. **Strain labels merged into parent species.**
3. Species remain species.
4. Genus-level labels remain genus-level unless there is a defensible reason to merge.
5. Complex-level labels remain separate.
6. Ambiguous/non-organism categories are not used as NCBI organism targets.
7. NCBI proteins are filtered for:

   * partial sequences
   * obvious AMR-associated annotations/keywords
8. Exact duplicate protein sequences are removed.
9. Negative protein **length distributions** should resemble the corresponding positive distributions.
10. Negative counts should match the corresponding CARD-positive representation.
11. Sampling uses:

```python
random_state = 42
```

Important methodological principle:

> **We don't want every negative protein to have the same length as a positive protein; we want the distribution of lengths in the negative class to resemble the distribution in the positive class.**

For the final dataset, we want to make the negative class comparable to the positive class in **organism/taxonomic representation and protein-length distribution**.

---

# 4. Successful Pseudomonas pilot

We already successfully tested the negative-sampling approach for:

```text
Pseudomonas aeruginosa
```

CARD positives:

**1,079**

NCBI negatives:

**1,079**

The negative dataset had:

* RefSeq proteins
* partial proteins removed
* obvious AMR-associated annotations removed
* exact duplicate sequences removed
* length distribution matched to CARD
* 1,079 unique negative sequences
* reproducible sampling

File:

```text
data/negative_class_Pseudomonas_aeruginosa.csv
```

Current negative script:

```text
src/build_negative_class.py
```

This is a **working single-organism prototype** that we want to generalize rather than rewrite blindly.

---

# 5. The 33 organism labels ≥20

The exact 33 labels were:

```text
Pseudomonas aeruginosa                         1079
Acinetobacter baumannii                        731
Klebsiella pneumoniae                          700
Escherichia coli                               558
Enterobacter cloacae                           170
Bacteria, Viruses, Fungi, and other genome
sequence associated with antimicrobial
resistance                                     132
Citrobacter freundii                           123
Acinetobacter pittii                             93
Campylobacter jejuni                             76
Klebsiella oxytoca                               72
Proteus mirabilis                                67
uncultured bacterium                             63
Enterococcus faecium                             45
Enterobacter hormaechei                          45
Acinetobacter calcoaceticus                      41
Aeromonas caviae                                 40
Staphylococcus aureus                            39
Elizabethkingia meningoseptica                   37
Pseudomonas aeruginosa PAO1                      35
Burkholderia multivorans                         35
Enterococcus faecalis                            34
Serratia marcescens                              33
Bacteroides fragilis                             33
Achromobacter xylosoxidans                       31
Vibrio parahaemolyticus                          30
Enterobacter cloacae complex                     27
Enterobacter asburiae                            26
Acinetobacter bereziniae                         25
Elizabethkingia anophelis                        24
Pseudomonas                                       24
Chryseobacterium indologenes                     21
Escherichia coli str. K-12 substr. MG1655        21
Morganella morganii                              20
```

Total:

**33 labels / 4,530 sequences**

---

# 6. Explicit organism normalization decisions

We deliberately decided **not to write automatic taxonomy rules**.

We created an auditable mapping:

```text
data/card_organism_mapping.csv
```

Columns:

```text
card_organism
positive_count
decision
normalized_target
```

Final decision categories:

```text
species
merge
genus
complex
keep_unmatched
exclude
```

Counts:

```text
species          27 labels / 4,228 sequences
merge             2 labels /    56 sequences
genus             1 label  /    24 sequences
complex           1 label  /    27 sequences
keep_unmatched    1 label  /    63 sequences
exclude           1 label  /   132 sequences
```

Total:

**33 labels / 4,530 sequences**

---

# 7. Exact taxonomy decisions

### Species

Use directly as species-level NCBI targets.

Examples:

```text
Pseudomonas aeruginosa
Acinetobacter baumannii
Klebsiella pneumoniae
Escherichia coli
Enterobacter cloacae
Citrobacter freundii
...
```

### Strains → parent species

Two explicit merges:

```text
Pseudomonas aeruginosa PAO1
    →
Pseudomonas aeruginosa
```

and:

```text
Escherichia coli str. K-12 substr. MG1655
    →
Escherichia coli
```

Therefore normalized counts become:

```text
Pseudomonas aeruginosa = 1,079 + 35 = 1,114
Escherichia coli        =   558 + 21 =   579
```

### Genus

Keep:

```text
Pseudomonas → Pseudomonas
```

**Do NOT merge it into Pseudomonas aeruginosa.**

This was explicitly discussed and decided because the CARD annotation is genus-level and we should not invent species-level information.

### Complex

Keep:

```text
Enterobacter cloacae complex
```

Do NOT force it into *Enterobacter cloacae*.

### `uncultured bacterium`

Decision:

**Keep the 63 positives in the positive dataset.**

However, it has no defensible organism-specific NCBI target, so it currently receives:

```text
keep_unmatched
normalized_target = NaN
```

### Broad category

This label:

```text
Bacteria, Viruses, Fungi, and other genome sequence associated with antimicrobial resistance
```

contains 132 positives.

Decision:

**Do NOT delete these 132 proteins from `positive_class.csv`.**

However, they are **not used to create an organism-matched negative stratum**, because this is not a usable organism/taxonomic target.

So:

> Positive-dataset membership and eligibility for organism-matched negative sampling are separate concepts.

---

# 8. Final normalized target table

After excluding the two labels without a normalized target:

* 63 `uncultured bacterium`
* 132 broad Bacteria/Viruses/Fungi category

we have:

**4,335 positive sequences**

represented by:

**29 normalized organism targets**

Final normalized counts:

```text
Pseudomonas aeruginosa          1114
Acinetobacter baumannii          731
Klebsiella pneumoniae            700
Escherichia coli                 579
Enterobacter cloacae             170
Citrobacter freundii             123
Acinetobacter pittii              93
Campylobacter jejuni              76
Klebsiella oxytoca                72
Proteus mirabilis                 67
Enterobacter hormaechei           45
Enterococcus faecium              45
Acinetobacter calcoaceticus       41
Aeromonas caviae                  40
Staphylococcus aureus             39
Elizabethkingia meningoseptica    37
Burkholderia multivorans          35
Enterococcus faecalis             34
Bacteroides fragilis              33
Serratia marcescens               33
Achromobacter xylosoxidans        31
Vibrio parahaemolyticus           30
Enterobacter cloacae complex      27
Enterobacter asburiae             26
Acinetobacter bereziniae          25
Pseudomonas                       24
Elizabethkingia anophelis        24
Chryseobacterium indologenes      21
Morganella morganii               20
```

Total:

**29 targets / 4,335 positives**

---

# 9. Important correction we caught

At one point we grouped by:

```python
groupby(["normalized_target", "decision"])
```

which incorrectly kept the strain merges separate.

We corrected this to:

```python
groupby("normalized_target")
```

so:

```text
P. aeruginosa + PAO1 → 1,114
E. coli + MG1655      →   579
```

Final result:

**29 targets / 4,335 sequences**

---

# 10. Existing `build_negative_class.py`

Current script is designed for one organism.

Hard-coded:

```python
ORGANISM = "Pseudomonas aeruginosa"
TARGET = 1079

SEARCH_SIZE = 6000
RANDOM_STATE = 42
```

AMR exclusion keywords include:

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

NCBI query currently uses:

```text
"{ORGANISM}"[Organism]
AND refseq[filter]
NOT resistance[All Fields]
NOT efflux[All Fields]
NOT antibiotic[All Fields]
```

Then it:

1. downloads FASTA records;
2. removes `"partial"` descriptions;
3. removes descriptions containing AMR keywords;
4. creates a DataFrame;
5. removes exact duplicate sequences;
6. calculates protein lengths;
7. bins lengths;
8. calculates CARD length distribution;
9. calculates negative sampling targets;
10. checks that enough candidates exist;
11. samples randomly;
12. combines bins;
13. verifies;
14. saves the negative CSV.

The current output is:

```text
data/negative_class_Pseudomonas_aeruginosa.csv
```

---

# 11. Current methodological question

We want the final negative class to be equivalent/comparable to the positive class in multiple dimensions.

Conceptually:

```text
CARD positives
      ↓
organism distribution
      +
protein-length distribution
      ↓
NCBI negative sampling
```

For the multi-organism version, the preferred design we were moving toward was:

```text
For each normalized organism target:

CARD positives
      ↓
determine organism-specific length distribution
      ↓
retrieve NCBI candidates from same taxonomic target
      ↓
filter AMR-associated/partial proteins
      ↓
remove exact duplicates
      ↓
sample same number as CARD positives
      ↓
match that organism's length distribution
```

This is stronger than matching only the **global** length distribution.

---

# 12. Critical issue where we stopped

We discovered that:

```text
data/positive_class.csv
```

does **not contain the CARD organism annotation**.

Current columns are only:

```text
sequence
ARO Accession
Model Name
AMR Gene Family
Drug Class
Resistance Mechanism
label
```

Therefore, although we know the aggregate organism counts, we currently cannot say:

```text
protein X → P. aeruginosa
protein Y → E. coli
protein Z → Acinetobacter baumannii
```

for all 6,052 positives.

We **must not guess this information** from protein accession or external databases if the original CARD metadata already contained the organism annotation.

### Immediate next step

Inspect:

```bash
sed -n '1,260p' src/build_positive_class.py
```

The purpose is to find where the organism information was available during construction of `positive_class.csv`.

We want to determine whether we can simply carry the CARD organism annotation into the positive dataset.

---

# 13. Files currently relevant

```text
data/positive_class.csv
data/negative_class_Pseudomonas_aeruginosa.csv
data/card_organism_counts.csv
data/card_organism_mapping.csv

src/build_positive_class.py
src/build_negative_class.py
```

Do **not** modify `build_negative_class.py` yet.

---

# 14. Git checkpoint

At the start of this work, `git status` showed:

```text
Changes to be committed:

modified:   data/negative_class_Pseudomonas_aeruginosa.csv
new file:   data/positive_class.csv
modified:   src/build_negative_class.py
new file:   src/build_positive_class.py

Untracked files:

data/card_organism_counts.csv
```

`data/card_organism_mapping.csv` was subsequently created.

We have **not committed the current work yet**.

---

# Exact stopping point

**Next action:**

```bash
sed -n '1,260p' src/build_positive_class.py
```

Then inspect how the original CARD data were merged and determine how to restore/carry the **per-protein organism annotation**.

After that:

```text
per-protein CARD organism
        ↓
explicit mapping
        ↓
29 normalized targets
        ↓
organism-specific positive length distributions
        ↓
NCBI candidate retrieval
        ↓
negative filtering
        ↓
organism + length matched negatives
```

**Do not skip the per-protein organism step, and do not modify the negative-class script until we resolve it.**

