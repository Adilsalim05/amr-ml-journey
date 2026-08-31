import pandas as pd
from sklearn.model_selection import train_test_split


INPUT = "data/kmer_features.csv"

RANDOM_STATE = 42
TEST_SIZE = 0.20


# --------------------------------------------------
# 1. Load k-mer feature matrix
# --------------------------------------------------

df = pd.read_csv(INPUT)

print("Total proteins:", len(df))


# --------------------------------------------------
# 2. Separate identifiers, features, and labels
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
# 4. Report split
# --------------------------------------------------

print("\nTraining proteins:", len(X_train))
print("Test proteins:", len(X_test))

print("\nTraining class distribution:")
print(y_train.value_counts())

print("\nTest class distribution:")
print(y_test.value_counts())
