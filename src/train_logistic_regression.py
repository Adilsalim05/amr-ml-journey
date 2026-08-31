import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression


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
# 6. Make predictions on the test set
# --------------------------------------------------

y_pred = model.predict(X_test)

y_probability = model.predict_proba(X_test)[:, 1]


# --------------------------------------------------
# 7. Show a few predictions
# --------------------------------------------------

results = pd.DataFrame({
    "actual": y_test.values,
    "predicted": y_pred,
    "AMR_probability": y_probability
})

print("\nFirst 10 test predictions:")
print(results.head(10).to_string(index=False))
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix
)


# --------------------------------------------------
# 8. Evaluate model
# --------------------------------------------------

accuracy = accuracy_score(y_test, y_pred)
precision = precision_score(y_test, y_pred)
recall = recall_score(y_test, y_pred)
f1 = f1_score(y_test, y_pred)

print("\nModel performance:")
print(f"Accuracy:  {accuracy:.3f}")
print(f"Precision: {precision:.3f}")
print(f"Recall:    {recall:.3f}")
print(f"F1 score:  {f1:.3f}")


# --------------------------------------------------
# 9. Confusion matrix
# --------------------------------------------------

cm = confusion_matrix(y_test, y_pred)

print("\nConfusion matrix:")
print(cm)
