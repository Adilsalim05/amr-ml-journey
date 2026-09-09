import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split


MECHANISM_FILE = "data/mechanism_dataset.csv"

TEST_SIZE = 0.20
N_TRIALS = 1000


# --------------------------------------------------
# 1. Load only the columns needed for split search
# --------------------------------------------------

df = pd.read_csv(
    MECHANISM_FILE,
    usecols=[
        "Protein Accession",
        "AMR Gene Family",
        "Resistance Mechanism",
        "label"
    ]
)

print("Mechanism dataset:", df.shape)


# --------------------------------------------------
# 2. Keep mechanisms with enough gene families
# --------------------------------------------------

valid_mechanisms = []

for mechanism, group in df.groupby("Resistance Mechanism"):

    n_families = group["AMR Gene Family"].nunique()

    if n_families >= 5:
        valid_mechanisms.append(mechanism)
    else:
        print(
            f"Skipping {mechanism}: "
            f"only {n_families} gene families."
        )

df = df[
    df["Resistance Mechanism"].isin(valid_mechanisms)
].copy()


# --------------------------------------------------
# 3. Pre-calculate families for each mechanism
# --------------------------------------------------

mechanism_families = {
    mechanism: group["AMR Gene Family"].unique()
    for mechanism, group
    in df.groupby("Resistance Mechanism")
}


# --------------------------------------------------
# 4. Search for a good family-level split
# --------------------------------------------------

best_score = -np.inf
best_split = None


for trial in range(N_TRIALS):

    train_family_sets = {}
    test_family_sets = {}

    for mechanism, families in mechanism_families.items():

        train_families, test_families = train_test_split(
            families,
            test_size=TEST_SIZE,
            random_state=trial
        )

        train_family_sets[mechanism] = set(train_families)
        test_family_sets[mechanism] = set(test_families)


    # ----------------------------------------------
    # Count test proteins without making huge
    # DataFrame copies
    # ----------------------------------------------

    test_counts = []

    for mechanism, group in df.groupby(
        "Resistance Mechanism"
    ):

        test_families = test_family_sets[mechanism]

        n_test = group[
            group["AMR Gene Family"].isin(test_families)
        ].shape[0]

        test_counts.append(n_test)


    # We want the smallest test class to be
    # as large as possible.

    score = min(test_counts)

    if score > best_score:

        best_score = score

        best_split = (
            train_family_sets,
            test_family_sets
        )


# --------------------------------------------------
# 5. Construct final split
# --------------------------------------------------

train_family_sets, test_family_sets = best_split

train_mask = []
test_mask = []

for idx, row in df.iterrows():

    mechanism = row["Resistance Mechanism"]
    family = row["AMR Gene Family"]

    if family in train_family_sets[mechanism]:
        train_mask.append(True)
        test_mask.append(False)

    else:
        train_mask.append(False)
        test_mask.append(True)


train = df[np.array(train_mask)]
test = df[np.array(test_mask)]


# --------------------------------------------------
# 6. Report results
# --------------------------------------------------

print("\n=== BEST FAMILY-AWARE SPLIT ===")

print("\nTraining proteins:", len(train))
print("Test proteins:", len(test))

print("\nTraining classes:")
print(train["label"].value_counts().sort_index())

print("\nTest classes:")
print(test["label"].value_counts().sort_index())


print("\n=== MECHANISM BREAKDOWN ===")

for mechanism in sorted(
    df["Resistance Mechanism"].unique()
):

    tr = train[
        train["Resistance Mechanism"] == mechanism
    ]

    te = test[
        test["Resistance Mechanism"] == mechanism
    ]

    print(f"\n{mechanism}")

    print(
        "  Train families:",
        tr["AMR Gene Family"].nunique()
    )

    print(
        "  Test families: ",
        te["AMR Gene Family"].nunique()
    )

    print(
        "  Train proteins:",
        len(tr)
    )

    print(
        "  Test proteins: ",
        len(te)
    )


# --------------------------------------------------
# 7. Verify no family leakage
# --------------------------------------------------

overlap = (
    set(train["AMR Gene Family"])
    &
    set(test["AMR Gene Family"])
)

print(
    "\nGene families shared between train and test:",
    len(overlap)
)

if len(overlap) == 0:
    print("PASS: No gene-family overlap.")
else:
    print("WARNING: Gene-family overlap detected.")
