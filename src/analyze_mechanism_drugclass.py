import pandas as pd


INPUT = "data/mechanism_dataset.csv"


# --------------------------------------------------
# 1. Load data
# --------------------------------------------------

df = pd.read_csv(INPUT)

print("Dataset:", df.shape)


# --------------------------------------------------
# 2. Exclude rare mechanisms used only outside
#    the main classifier
# --------------------------------------------------

df = df[
    ~df["Resistance Mechanism"].isin([
        "antibiotic target replacement"
    ])
].copy()


# --------------------------------------------------
# 3. Analyze each mechanism
# --------------------------------------------------

for mechanism, group in df.groupby("Resistance Mechanism"):

    print("\n" + "=" * 70)
    print(mechanism)
    print("=" * 70)

    drug_counts = (
        group["Drug Class"]
        .value_counts()
    )

    print(
        "\nNumber of drug classes:",
        len(drug_counts)
    )

    print(
        "Number of proteins:",
        len(group)
    )

    print("\nTop 10 drug classes:")

    print(
        drug_counts
        .head(10)
        .to_string()
    )

    top5 = drug_counts.head(5).sum()
    total = len(group)

    print(
        f"\nTop 5 drug classes contain "
        f"{top5}/{total} proteins "
        f"({100 * top5 / total:.1f}%)"
    )


# --------------------------------------------------
# 4. Mechanism × Drug Class table
# --------------------------------------------------

print("\n" + "=" * 70)
print("MECHANISM × DRUG CLASS")
print("=" * 70)

table = pd.crosstab(
    df["Resistance Mechanism"],
    df["Drug Class"]
)

print("\nTable shape:", table.shape)

print("\nMechanism × Drug Class counts:")
print(table)
