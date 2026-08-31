import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix
)


INPUT = "data/kmer_features.csv"

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
# 3. Split into training and test sets
# --------------------------------------------------

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=TEST_SIZE,
    random_state=RANDOM_STATE,
    stratify=y
)

print("\nTraining proteins:", len(X_train))
print("Test proteins:", len(X_test))


# --------------------------------------------------
# 4. Create logistic regression model
# --------------------------------------------------

model = LogisticRegression(
    max_iter=1000,
    random_state=RANDOM_STATE
)


# --------------------------------------------------
# 5. Train the model
# --------------------------------------------------

model.fit(X_train, y_train)

print("\nModel trained successfully.")


# --------------------------------------------------
# 6. Make predictions on training and test sets
# --------------------------------------------------

y_train_pred = model.predict(X_train)
y_test_pred = model.predict(X_test)

y_test_probability = model.predict_proba(X_test)[:, 1]


# --------------------------------------------------
# 7. Show a few test predictions
# --------------------------------------------------

results = pd.DataFrame({
    "actual": y_test.values,
    "predicted": y_test_pred,
    "AMR_probability": y_test_probability
})

print("\nFirst 10 test predictions:")
print(results.head(10).to_string(index=False))


# --------------------------------------------------
# 8. Calculate training performance
# --------------------------------------------------

train_accuracy = accuracy_score(y_train, y_train_pred)
train_precision = precision_score(y_train, y_train_pred)
train_recall = recall_score(y_train, y_train_pred)
train_f1 = f1_score(y_train, y_train_pred)


# --------------------------------------------------
# 9. Calculate test performance
# --------------------------------------------------

test_accuracy = accuracy_score(y_test, y_test_pred)
test_precision = precision_score(y_test, y_test_pred)
test_recall = recall_score(y_test, y_test_pred)
test_f1 = f1_score(y_test, y_test_pred)


# --------------------------------------------------
# 10. Display training performance
# --------------------------------------------------

print("\nTraining performance:")
print(f"Accuracy:  {train_accuracy:.3f}")
print(f"Precision: {train_precision:.3f}")
print(f"Recall:    {train_recall:.3f}")
print(f"F1 score:  {train_f1:.3f}")


# --------------------------------------------------
# 11. Display test performance
# --------------------------------------------------

print("\nTest performance:")
print(f"Accuracy:  {test_accuracy:.3f}")
print(f"Precision: {test_precision:.3f}")
print(f"Recall:    {test_recall:.3f}")
print(f"F1 score:  {test_f1:.3f}")


# --------------------------------------------------
# 12. Calculate performance gaps
# --------------------------------------------------

accuracy_gap = train_accuracy - test_accuracy
precision_gap = train_precision - test_precision
recall_gap = train_recall - test_recall
f1_gap = train_f1 - test_f1


# --------------------------------------------------
# 13. Display training-test performance gaps
# --------------------------------------------------

print("\nTraining - Test performance gap:")
print(f"Accuracy gap:  {accuracy_gap:.3f}")
print(f"Precision gap: {precision_gap:.3f}")
print(f"Recall gap:    {recall_gap:.3f}")
print(f"F1 gap:        {f1_gap:.3f}")


# --------------------------------------------------
# 14. Test confusion matrix
# --------------------------------------------------

cm = confusion_matrix(y_test, y_test_pred)

print("\nTest confusion matrix:")
print(cm)
