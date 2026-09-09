import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report
)


INPUT = "data/mechanism_kmer_features.csv"

TEST_SIZE = 0.20
RANDOM_STATE = 42


# --------------------------------------------------
# 1. Load k-mer feature matrix
# --------------------------------------------------

df = pd.read_csv(INPUT)

print("Total proteins:", len(df))


# --------------------------------------------------
# 2. Separate features and labels
# --------------------------------------------------

X = df.drop(columns=["Protein Accession", "label"])
y = df["label"]


# --------------------------------------------------
# 3. Train/test split
# --------------------------------------------------

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=TEST_SIZE,
    random_state=RANDOM_STATE,
    stratify=y
)


# --------------------------------------------------
# 4. Train logistic regression
# --------------------------------------------------
model = LogisticRegression(
    max_iter=1000,
    random_state=RANDOM_STATE,
    class_weight="balanced"
)
model.fit(X_train, y_train)

print("\nModel trained successfully.")


# --------------------------------------------------
# 5. Predictions
# --------------------------------------------------

y_train_pred = model.predict(X_train)
y_test_pred = model.predict(X_test)


# --------------------------------------------------
# 6. Overall performance
# --------------------------------------------------

test_accuracy = accuracy_score(y_test, y_test_pred)
test_balanced_accuracy = balanced_accuracy_score(y_test, y_test_pred)

test_precision = precision_score(
    y_test,
    y_test_pred,
    average="macro",
    zero_division=0
)

test_recall = recall_score(
    y_test,
    y_test_pred,
    average="macro",
    zero_division=0
)

test_f1 = f1_score(
    y_test,
    y_test_pred,
    average="macro",
    zero_division=0
)


print("\n=== TEST PERFORMANCE ===")
print(f"Accuracy:           {test_accuracy:.3f}")
print(f"Balanced accuracy:  {test_balanced_accuracy:.3f}")
print(f"Macro precision:    {test_precision:.3f}")
print(f"Macro recall:       {test_recall:.3f}")
print(f"Macro F1:            {test_f1:.3f}")


# --------------------------------------------------
# 7. Per-class performance
# --------------------------------------------------

class_names = {
    0: "antibiotic inactivation",
    1: "antibiotic target alteration",
    2: "antibiotic efflux",
    3: "antibiotic target protection",
    4: "antibiotic target replacement"
}

print("\n=== PER-CLASS PERFORMANCE ===")

report = classification_report(
    y_test,
    y_test_pred,
    labels=[0, 1, 2, 3, 4],
    target_names=[class_names[i] for i in range(5)],
    zero_division=0
)

print(report)


# --------------------------------------------------
# 8. Confusion matrix
# --------------------------------------------------

cm = confusion_matrix(
    y_test,
    y_test_pred,
    labels=[0, 1, 2, 3, 4]
)

print("\n=== CONFUSION MATRIX ===")
print(cm)

print("\nClass order:")
for i in range(5):
    print(f"{i}: {class_names[i]}")
