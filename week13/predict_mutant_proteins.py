from collections import Counter
import joblib
import pandas as pd

MODEL_FILE = "week13/week5_random_forest.joblib"
FASTA_FILE = "week13/mutant_proteins.faa"
OUTPUT_FILE = "week13/wt_mutant_predictions.csv"

# 1. Load saved model and training feature columns
saved = joblib.load(MODEL_FILE)
model = saved["model"]
feature_columns = saved["feature_columns"]

print("Model loaded.")
print("Expected features:", len(feature_columns))


# 2. Read FASTA sequences
sequences = {}
current_id = None

with open(FASTA_FILE) as handle:
    for line in handle:
        line = line.strip()

        if not line:
            continue

        if line.startswith(">"):
            current_id = line[1:].split()[0]
            if current_id in sequences:
                raise ValueError(f"Duplicate FASTA ID: {current_id}")
            sequences[current_id] = ""
        else:
            if current_id is None:
                raise ValueError("Sequence found before FASTA header.")
            sequences[current_id] += line.upper()

expected_ids = {
    "ompR_WT", "ompR_mutant",
    "parE_WT", "parE_mutant",
    "yjgA_WT", "yjgA_mutant",
    "acrR_WT", "acrR_mutant"
}

if set(sequences) != expected_ids:
    raise ValueError(
        f"Unexpected FASTA IDs. Found: {sorted(sequences)}"
    )

print("Sequences loaded:", len(sequences))


# 3. Convert each protein into normalized 3-mer frequencies
feature_rows = []
metadata = []

for protein_id, sequence in sequences.items():

    if len(sequence) < 3:
        raise ValueError(f"Sequence too short: {protein_id}")

    kmers = [
        sequence[i:i+3]
        for i in range(len(sequence) - 2)
    ]

    counts = Counter(kmers)
    total = len(kmers)

    frequencies = {
        kmer: count / total
        for kmer, count in counts.items()
    }

    unseen = set(frequencies) - set(feature_columns)

    # Align exactly to the Week 5 training feature columns
    row = {
        feature: frequencies.get(feature, 0.0)
        for feature in feature_columns
    }

    feature_rows.append(row)

    metadata.append({
        "protein_id": protein_id,
        "length_aa": len(sequence),
        "total_3mers": total,
        "unseen_3mer_types": len(unseen)
    })


# 4. Build feature matrix in exact training-column order
X = pd.DataFrame(feature_rows, columns=feature_columns)

if X.shape[1] != len(feature_columns):
    raise ValueError("Feature dimension mismatch.")

if not X.columns.tolist() == feature_columns:
    raise ValueError("Feature-column order mismatch.")

print("Prediction matrix shape:", X.shape)
print("Minimum feature sum:", X.sum(axis=1).min())
print("Maximum feature sum:", X.sum(axis=1).max())


# 5. Generate predictions and probabilities
predictions = model.predict(X)
probabilities = model.predict_proba(X)

amr_index = list(model.classes_).index(1)
non_amr_index = list(model.classes_).index(0)

# 6. Assemble results
results = pd.DataFrame(metadata)
results["predicted_label"] = predictions
results["probability_non_AMR"] = probabilities[:, non_amr_index]
results["probability_AMR"] = probabilities[:, amr_index]

results.to_csv(OUTPUT_FILE, index=False)

print("\nPredictions:")
print(results.to_string(index=False))

print("\nResults saved to:", OUTPUT_FILE)
