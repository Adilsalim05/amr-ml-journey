from collections import Counter
import pandas as pd


INPUT = "data/ml_dataset.csv"
OUTPUT = "data/kmer_features.csv"

K = 3


def kmer_frequencies(sequence, k=3):
    """
    Convert a protein sequence into k-mer frequency features.
    """

    kmers = [
        sequence[i:i+k]
        for i in range(len(sequence) - k + 1)
    ]

    counts = Counter(kmers)

    total = len(kmers)

    return {
        kmer: count / total
        for kmer, count in counts.items()
    }


# --------------------------------------------------
# 1. Load dataset
# --------------------------------------------------

df = pd.read_csv(INPUT)

print("Proteins:", len(df))


# --------------------------------------------------
# 2. Generate k-mer frequencies
# --------------------------------------------------

feature_rows = []

for sequence in df["sequence"]:

    features = kmer_frequencies(sequence, K)

    feature_rows.append(features)


# --------------------------------------------------
# 3. Convert to dataframe
# --------------------------------------------------

X = pd.DataFrame(feature_rows).fillna(0)


# --------------------------------------------------
# 4. Add identifiers and labels
# --------------------------------------------------

X.insert(
    0,
    "Protein Accession",
    df["Protein Accession"]
)

X["label"] = df["label"].values


# --------------------------------------------------
# 5. Save
# --------------------------------------------------

X.to_csv(OUTPUT, index=False)

print("\nFeature matrix created")
print("Shape:", X.shape)

print("\nClass distribution:")
print(X["label"].value_counts())

print("\nNumber of 3-mer features:", X.shape[1] - 2)

print("\nFirst five features:")
print(X.iloc[:5, :10].to_string(index=False))
