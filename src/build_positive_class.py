from Bio import SeqIO
import pandas as pd

FASTA = "data/card/protein_fasta_protein_homolog_model.fasta"
CARD_INDEX = "data/card/aro_index.tsv"
OUTPUT = "data/positive_class.csv"


# ---------------------------------------------------------
# 1. Load CARD protein sequences
# ---------------------------------------------------------

records = list(SeqIO.parse(FASTA, "fasta"))

print("FASTA sequences:", len(records))


# ---------------------------------------------------------
# 2. Load CARD annotation index
# ---------------------------------------------------------

card = pd.read_csv(CARD_INDEX, sep="\t")

print("CARD index rows:", len(card))


# ---------------------------------------------------------
# ---------------------------------------------------------
# 3. Build sequence dataframe
# ---------------------------------------------------------

organisms = []

for r in records:
    description = r.description

    if "[" in description and "]" in description:
        organism = description.split("[")[-1].split("]")[0]
    else:
        organism = None

    organisms.append(organism)

sequence_df = pd.DataFrame({
    "Protein Accession": [r.id.split("|")[1] for r in records],
    "sequence": [str(r.seq) for r in records],
    "CARD Organism": organisms
})

print("\nSequence dataframe:")
print(sequence_df.head().to_string(index=False))

print(
    "Missing CARD organism:",
    sequence_df["CARD Organism"].isna().sum()
)

# ---------------------------------------------------------
# 4. Join sequences to CARD annotations
# ---------------------------------------------------------

merged = sequence_df.merge(
    card,
    on="Protein Accession",
    how="left"
)

print("\nMerged shape:", merged.shape)

unmatched = merged["ARO Accession"].isna().sum()
print("Unmatched annotations:", unmatched)


# ---------------------------------------------------------
# 5. Keep relevant CARD metadata
# ---------------------------------------------------------

metadata_columns = [
    "ARO Accession",
    "Model Name",
    "AMR Gene Family",
    "Drug Class",
    "Resistance Mechanism"
]


# ---------------------------------------------------------
# 6. Aggregate multiple CARD annotations
#
# One protein sequence = one observation.
# If one protein accession has multiple CARD annotations,
# preserve all unique annotations rather than creating
# multiple training observations.
# ---------------------------------------------------------

aggregation_columns = [
    "ARO Accession",
    "Model Name",
    "AMR Gene Family",
    "Drug Class",
    "Resistance Mechanism"
]


positive_df = (
    merged[
        ["Protein Accession", "sequence", "CARD Organism"] + aggregation_columns
    ]
    .groupby(
        ["Protein Accession", "sequence", "CARD Organism"],
        as_index=False
        )
    .agg({
        column: lambda x: "; ".join(
            sorted(set(x.dropna().astype(str)))
        )
        for column in aggregation_columns
    })
)


# ---------------------------------------------------------
# 7. Assign AMR label
#
# Presence in this CARD protein dataset is our operational
# definition of AMR-associated for the positive class.
# ---------------------------------------------------------

positive_df["label"] = 1


# ---------------------------------------------------------
# 8. Report dataset integrity
# ---------------------------------------------------------

print("\nPositive dataset:")
print("Rows before annotation aggregation:", len(merged))
print("Rows after aggregation:", len(positive_df))
print(
    "Duplicate observations removed:",
    len(merged) - len(positive_df)
)
print(
    "Unique protein accessions:",
    positive_df["Protein Accession"].nunique()
)
print(
    "Sequences with missing CARD annotations:",
    positive_df["ARO Accession"].isna().sum()
)


# ---------------------------------------------------------
# 9. Save positive class
# ---------------------------------------------------------

positive_df.to_csv(OUTPUT, index=False)

print("\nSaved:", OUTPUT)
print("Final shape:", positive_df.shape)

print("\nFirst five records:")
print(
    positive_df.head().to_string(index=False)
)
