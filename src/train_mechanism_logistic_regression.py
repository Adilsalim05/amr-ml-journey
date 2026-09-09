import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression


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

print("\nTraining class distribution:")
print(y_train.value_counts().sort_index())

print("\nTest class distribution:")
print(y_test.value_counts().sort_index())


# --------------------------------------------------
# 4. Create multinomial logistic regression model
# --------------------------------------------------

model = LogisticRegression(
    max_iter=1000,
    random_state=RANDOM_STATE
)


# --------------------------------------------------
# 5. Train model
# --------------------------------------------------

model.fit(X_train, y_train)

print("\nModel trained successfully.")


# --------------------------------------------------
# 6. Make predictions
# --------------------------------------------------

y_train_pred = model.predict(X_train)
y_test_pred = model.predict(X_test)

y_test_probability = model.predict_proba(X_test)


# --------------------------------------------------
# 7. Show a few predictions
# --------------------------------------------------

results = pd.DataFrame({
    "actual": y_test.values,
    "predicted": y_test_pred
})

print("\nFirst 10 test predictions:")
print(results.head(10).to_string(index=False))


# --------------------------------------------------
# 8. Show probability information
# --------------------------------------------------

print("\nProbability matrix shape:")
print(y_test_probability.shape)

print("\nClasses:")
print(model.classes_)

print("\nFirst test protein probabilities:")
print(y_test_probability[0])
