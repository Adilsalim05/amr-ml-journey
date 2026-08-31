#python
from Bio import Entrez, SeqIO
import pandas as pd


# --------------------------------------------------
# 1. NCBI settings
# --------------------------------------------------

Entrez.email = "adilsaleem105@gmail.com"

ORGANISM = "Pseudomonas aeruginosa"
TARGET = 1079

SEARCH_SIZE = 6000
RANDOM_STATE = 42


# --------------------------------------------------
# 2. AMR annotation keywords to exclude
# --------------------------------------------------

AMR_KEYWORDS = [
    "resistance",
    "antibiotic",
    "antimicrobial",
    "efflux",
    "beta-lactamase",
    "carbapenemase",
    "aminoglycoside",
    "chloramphenicol acetyltransferase",
]


# --------------------------------------------------
# 3. Search NCBI
# --------------------------------------------------

term = (
    f'"{ORGANISM}"[Organism] '
    "AND refseq[filter] "
    "NOT resistance[All Fields] "
    "NOT efflux[All Fields] "
    "NOT antibiotic[All Fields]"
)

print(f"Searching NCBI for: {ORGANISM}")

handle = Entrez.esearch(
    db="protein",
    term=term,
    retmax=SEARCH_SIZE
)

search_record = Entrez.read(handle)
handle.close()

ids = search_record["IdList"]

print(f"NCBI candidates retrieved: {len(ids)}")


# --------------------------------------------------
# 4. Download protein sequences
# --------------------------------------------------

handle = Entrez.efetch(
    db="protein",
    id=ids,
    rettype="fasta",
    retmode="text"
)

records = list(SeqIO.parse(handle, "fasta"))
handle.close()

print(f"Protein records downloaded: {len(records)}")


# --------------------------------------------------
# 5. Remove partial proteins and AMR-associated
#    annotations
# --------------------------------------------------

usable = []

for record in records:

    description = record.description.lower()

    # Remove partial proteins
    if "partial" in description:
        continue

    # Remove explicitly AMR-associated annotations
    if any(keyword in description for keyword in AMR_KEYWORDS):
        continue

    usable.append(record)

print(f"Usable candidates after filtering: {len(usable)}")


# --------------------------------------------------
# 6. Convert to DataFrame
# --------------------------------------------------

negative_df = pd.DataFrame({
    "Protein Accession": [r.id for r in usable],
    "sequence": [str(r.seq) for r in usable],
    "description": [r.description for r in usable],
    "organism": ORGANISM,
    "label": 0
})

negative_df["length"] = negative_df["sequence"].str.len()


# --------------------------------------------------
# 7. Remove exact duplicate sequences
# --------------------------------------------------

before_duplicates = len(negative_df)

negative_df = negative_df.drop_duplicates(
    subset="sequence"
).reset_index(drop=True)

duplicates_removed = before_duplicates - len(negative_df)

print(f"Exact duplicate sequences removed: {duplicates_removed}")


# --------------------------------------------------
# 8. Define CARD length bins
# --------------------------------------------------

bins = [
    0, 100, 200, 300, 400,
    500, 700, 1000, float("inf")
]

labels = [
    "<100",
    "100-199",
    "200-299",
    "300-399",
    "400-499",
    "500-699",
    "700-999",
    ">=1000"
]

negative_df["length_bin"] = pd.cut(
    negative_df["length"],
    bins=bins,
    labels=labels,
    right=False
)

# --------------------------------------------------
# 9. Calculate CARD length distribution directly
# --------------------------------------------------

positive_df = pd.read_csv("data/positive_class.csv")

positive_df["length"] = positive_df["sequence"].str.len()

positive_df["length_bin"] = pd.cut(
    positive_df["length"],
    bins=bins,
    labels=labels,
    right=False
)

CARD_COUNTS = (
    positive_df["length_bin"]
    .value_counts()
    .reindex(labels, fill_value=0)
)

CARD_PROPORTIONS = CARD_COUNTS / len(positive_df)

print("\nCARD length distribution:")
for label in labels:
    print(
        f"{label}: "
        f"{CARD_COUNTS[label]} "
        f"({CARD_PROPORTIONS[label] * 100:.2f}%)"
    )


# --------------------------------------------------
# 10. Calculate negative sampling targets
# --------------------------------------------------

targets = {
    label: round(TARGET * CARD_PROPORTIONS[label])
    for label in labels
}

# Correct rounding so the targets sum exactly to TARGET
difference = TARGET - sum(targets.values())
targets["200-299"] += difference

print("\nTarget negative proteins by length:")
for label in labels:
    print(f"{label}: {targets[label]}")
# --------------------------------------------------
# --------------------------------------------------
# 11. Check that every length bin has enough proteins
# --------------------------------------------------

available = (
    negative_df["length_bin"]
    .value_counts()
    .reindex(labels, fill_value=0)
)

print("\nAvailable candidates by length:")
print(available.to_string())

for label in labels:

    if available[label] < targets[label]:

        raise ValueError(
            f"Not enough candidates in length bin {label}: "
            f"need {targets[label]}, "
            f"but only {available[label]} are available."
        )


# --------------------------------------------------
# 12. Randomly sample the negative proteins
# --------------------------------------------------

sampled_groups = []

for label in labels:

    group = negative_df[
        negative_df["length_bin"] == label
    ]

    sampled = group.sample(
        n=targets[label],
        random_state=RANDOM_STATE
    )

    sampled_groups.append(sampled)


negative_class = pd.concat(
    sampled_groups,
    ignore_index=True
)


# --------------------------------------------------
# 13. Final verification
# --------------------------------------------------

print("\nFinal negative dataset:")
print(f"Proteins: {len(negative_class)}")
print(
    f"Unique sequences: "
    f"{negative_class['sequence'].nunique()}"
)

print("\nFinal length distribution:")
print(
    negative_class["length_bin"]
    .value_counts()
    .reindex(labels)
    .to_string()
)


# --------------------------------------------------
# 14. Save
# --------------------------------------------------

output_file = "data/negative_class_Pseudomonas_aeruginosa.csv"

negative_class.to_csv(
    output_file,
    index=False
)

print(f"\nSaved: {output_file}")
