import pandas as pd
import numpy as np

from sklearn.model_selection import StratifiedGroupKFold
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix
)


FEATURE_FILE = "data/mechanism_kmer_features.csv"
MECHANISM_FILE = "data/mechanism_dataset.csv"

N_SPLITS = 5
RANDOM_STATE = 42


# --------------------------------------------------
# 1. Load data
# --------------------------------------------------

features = pd.read_csv(FEATURE_FILE)

mechanisms = pd.read_csv(
    MECHANISM_FILE,
    usecols=[
        "Protein Accession",
        "AMR Gene Family",
        "Resistance Mechanism"
    ]
)


# --------------------------------------------------
# 2. Merge features with annotations
# --------------------------------------------------

df = features.merge(
    mechanisms,
    on="Protein Accession",
    how="inner"
)


# --------------------------------------------------
# 3. Exclude target replacement
# --------------------------------------------------

df = df[
    df["Resistance Mechanism"]
    != "antibiotic target replacement"
].copy()


print("Dataset:", df.shape)

print("\nMechanism distribution:")
print(
    df["Resistance Mechanism"]
    .value_counts()
)


# --------------------------------------------------
# 4. Prepare X, y, and groups
# --------------------------------------------------

exclude_columns = [
    "Protein Accession",
    "label",
    "AMR Gene Family",
    "Resistance Mechanism"
]

X = df.drop(columns=exclude_columns)

y = df["label"]

groups = df["AMR Gene Family"]


# --------------------------------------------------
# 5. Create StratifiedGroupKFold
# --------------------------------------------------

cv = StratifiedGroupKFold(
    n_splits=N_SPLITS,
    shuffle=True,
    random_state=RANDOM_STATE
)


# --------------------------------------------------
# 6. Cross-validation
# --------------------------------------------------

results = []

labels = sorted(y.unique())


for fold, (train_idx, test_idx) in enumerate(
    cv.split(X, y, groups),
    start=1
):

    X_train = X.iloc[train_idx]
    X_test = X.iloc[test_idx]

    y_train = y.iloc[train_idx]
    y_test = y.iloc[test_idx]

    train_groups = set(groups.iloc[train_idx])
    test_groups = set(groups.iloc[test_idx])

    overlap = train_groups & test_groups

    print("\n" + "=" * 60)
    print(f"FOLD {fold}")
    print("=" * 60)

    print("Training proteins:", len(train_idx))
    print("Validation proteins:", len(test_idx))

    print("\nTraining classes:")
    print(y_train.value_counts().sort_index())

    print("\nValidation classes:")
    print(y_test.value_counts().sort_index())

    print(
        "\nGene-family overlap:",
        len(overlap)
    )

    if len(overlap) == 0:
        print("PASS: No family leakage.")
    else:
        print("WARNING: Family leakage detected!")


    # --------------------------------------------------
    # 7. Train model
    # --------------------------------------------------

    model = LogisticRegression(
        max_iter=1000,
        random_state=RANDOM_STATE,
        class_weight="balanced"
    )

    model.fit(X_train, y_train)


    # --------------------------------------------------
    # 8. Predict
    # --------------------------------------------------

    predictions = model.predict(X_test)


    # --------------------------------------------------
    # 9. Evaluate
    # --------------------------------------------------

    accuracy = accuracy_score(
        y_test,
        predictions
    )

    balanced_accuracy = balanced_accuracy_score(
        y_test,
        predictions
    )

    precision = precision_score(
        y_test,
        predictions,
        average="macro",
        zero_division=0
    )

    recall = recall_score(
        y_test,
        predictions,
        average="macro",
        zero_division=0
    )

    f1 = f1_score(
        y_test,
        predictions,
        average="macro",
        zero_division=0
    )


    print("\nPerformance:")

    print(
        f"Accuracy:           {accuracy:.3f}"
    )

    print(
        f"Balanced accuracy:  {balanced_accuracy:.3f}"
    )

    print(
        f"Macro precision:    {precision:.3f}"
    )

    print(
        f"Macro recall:       {recall:.3f}"
    )

    print(
        f"Macro F1:           {f1:.3f}"
    )


    # --------------------------------------------------
    # 10. Confusion matrix
    # --------------------------------------------------

    cm = confusion_matrix(
        y_test,
        predictions,
        labels=labels
    )

    print("\nConfusion matrix:")

    print(cm)


    results.append({
        "fold": fold,
        "accuracy": accuracy,
        "balanced_accuracy": balanced_accuracy,
        "macro_precision": precision,
        "macro_recall": recall,
        "macro_f1": f1
    })


# --------------------------------------------------
# 11. Overall results
# --------------------------------------------------

results_df = pd.DataFrame(results)

print("\n" + "=" * 60)
print("CROSS-VALIDATION SUMMARY")
print("=" * 60)

print(results_df.to_string(index=False))


print("\nMean performance:")

for column in [
    "accuracy",
    "balanced_accuracy",
    "macro_precision",
    "macro_recall",
    "macro_f1"
]:

    print(
        f"{column}: "
        f"{results_df[column].mean():.3f} "
        f"+/- "
        f"{results_df[column].std():.3f}"
    )
