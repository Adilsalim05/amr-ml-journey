import pandas as pd


INPUT = "data/mechanism_dataset.csv"


# --------------------------------------------------
# 1. Load data
# --------------------------------------------------

df = pd.read_csv(INPUT)

print("Dataset:", df.shape)


# --------------------------------------------------
# 2. Analyze each mechanism
# --------------------------------------------------

for mechanism, group in df.groupby("Resistance Mechanism"):

    print("\n" + "=" * 70)
    print(mechanism)
    print("=" * 70)

    family_counts = (
        group
        .groupby("AMR Gene Family")
        .size()
        .sort_values(ascending=False)
    )

    print("\nNumber of proteins:", len(group))
    print("Number of gene families:", len(family_counts))

    print(
        "Mean proteins/family:",
        round(family_counts.mean(), 2)
    )

    print(
        "Median proteins/family:",
        round(family_counts.median(), 2)
    )

    print(
        "Largest family:",
        family_counts.iloc[0]
    )

    # --------------------------------------------------
    # Top 10 families
    # --------------------------------------------------

    print("\nTop 10 gene families:")

    print(
        family_counts
        .head(10)
        .to_string()
    )

    # --------------------------------------------------
    # Concentration
    # --------------------------------------------------

    total = len(group)

    top5 = family_counts.head(5).sum()
    top10 = family_counts.head(10).sum()

    print(
        f"\nTop 5 families contain "
        f"{top5}/{total} proteins "
        f"({100 * top5 / total:.1f}%)"
    )

    print(
        f"Top 10 families contain "
        f"{top10}/{total} proteins "
        f"({100 * top10 / total:.1f}%)"
    )
