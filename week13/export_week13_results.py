import pandas as pd

OUTPUT = "week13/week13_complete_analysis.xlsx"

# Load existing protein analysis workbook
original = pd.read_excel(
    "week13/mutation_analysis.xlsx",
    sheet_name=None
)

# Model performance
performance = pd.DataFrame({
    "Metric": ["Accuracy", "Precision", "Recall", "F1-score"],
    "Value": [0.933, 0.990, 0.875, 0.929]
})

confusion_matrix = pd.DataFrame(
    [[214, 2], [27, 189]],
    index=["Actual non-AMR", "Actual AMR"],
    columns=["Predicted non-AMR", "Predicted AMR"]
)

# Top 20 Random Forest features
top_features = pd.DataFrame({
    "3-mer": [
        "KTG", "ALR", "YGN", "TFK", "RDT",
        "STF", "IPG", "VGW", "SDN", "GPL",
        "DTT", "TGS", "GYG", "SIG", "FWL",
        "TTG", "DER", "FGY", "AAN", "GWE"
    ],
    "Importance": [
        0.015285, 0.007810, 0.007339, 0.006794, 0.006739,
        0.006343, 0.005939, 0.005810, 0.005104, 0.004987,
        0.004726, 0.004373, 0.004233, 0.003908, 0.003908,
        0.003815, 0.003778, 0.003651, 0.003651, 0.003645
    ]
})

# Unseen feature documentation
unseen = pd.DataFrame({
    "Protein": ["parE_WT", "parE_mutant"],
    "Unseen_3mer": ["WCY", "WCY"],
    "Count": [1, 1],
    "Note": [
        "Feature absent from Week 5 training vocabulary; omitted from model input.",
        "Feature absent from Week 5 training vocabulary; omitted from model input."
    ]
})

notes = pd.DataFrame({
    "Topic": [
        "Prediction interpretation",
        "Model scope",
        "Training performance",
        "Feature limitation",
        "Biological limitation",
        "Sequence provenance"
    ],
    "Note": [
        "Probabilities are classifier outputs, not probabilities of clinical resistance.",
        "The model distinguishes AMR-associated proteins from non-AMR proteins.",
        "Performance was reproduced using the original random stratified split; this is not external validation.",
        "WCY was absent from the training feature vocabulary and was omitted for both ParE sequences.",
        "Predictions do not demonstrate that mutations alter protein function or norfloxacin resistance.",
        "Mutant sequences were computationally constructed from reported protein changes, not independently sequenced."
    ]
})

# Export all results
with pd.ExcelWriter(OUTPUT, engine="openpyxl") as writer:

    for sheet_name, data in original.items():
        data.to_excel(writer, sheet_name=sheet_name, index=False)

    pd.read_csv("week13/manuscript_mutations.csv").to_excel(
        writer, sheet_name="Manuscript_mutations", index=False
    )

    pd.read_csv("week13/wt_mutant_predictions.csv").to_excel(
        writer, sheet_name="ML_predictions", index=False
    )

    performance.to_excel(
        writer, sheet_name="Model_performance", index=False
    )

    confusion_matrix.to_excel(
        writer, sheet_name="Confusion_matrix"
    )

    top_features.to_excel(
        writer, sheet_name="Top_3mer_features", index=False
    )

    unseen.to_excel(
        writer, sheet_name="Unseen_3mers", index=False
    )

    notes.to_excel(
        writer, sheet_name="Interpretation_notes", index=False
    )

print("Workbook created:", OUTPUT)
print("Sheets:", list(original.keys()) + [
    "Manuscript_mutations",
    "ML_predictions",
    "Model_performance",
    "Confusion_matrix",
    "Top_3mer_features",
    "Unseen_3mers",
    "Interpretation_notes"
])
