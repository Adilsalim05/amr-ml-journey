import os

import pandas as pd
import matplotlib.pyplot as plt

from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    roc_curve,
    roc_auc_score,
    precision_recall_curve,
    average_precision_score
)


# ============================================================
# SETTINGS
# ============================================================

INPUT = "data/kmer_features.csv"
FIGURE_DIR = "figures"

TEST_SIZE = 0.20
RANDOM_STATE = 42


# ============================================================
# 1. Create figure directory
# ============================================================

os.makedirs(FIGURE_DIR, exist_ok=True)


# ============================================================
# 2. Load k-mer feature matrix
# ============================================================

df = pd.read_csv(INPUT)

print("Total proteins:", len(df))


# ============================================================
# 3. Separate features and labels
# ============================================================

X = df.drop(columns=["Protein Accession", "label"])
y = df["label"]


# ============================================================
# 4. Train/test split
# ============================================================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=TEST_SIZE,
    random_state=RANDOM_STATE,
    stratify=y
)

print("Training proteins:", len(X_train))
print("Test proteins:", len(X_test))


# ============================================================
# 5. Create models
# ============================================================

logistic_model = LogisticRegression(
    max_iter=1000,
    random_state=RANDOM_STATE
)

random_forest_model = RandomForestClassifier(
    n_estimators=200,
    random_state=RANDOM_STATE,
    n_jobs=-1
)


# ============================================================
# 6. Train models
# ============================================================

print("\nTraining Logistic Regression...")
logistic_model.fit(X_train, y_train)

print("Training Random Forest...")
random_forest_model.fit(X_train, y_train)

print("Both models trained successfully.")


# ============================================================
# 7. Generate predictions
# ============================================================

# Logistic Regression
lr_pred = logistic_model.predict(X_test)
lr_probability = logistic_model.predict_proba(X_test)[:, 1]

# Random Forest
rf_pred = random_forest_model.predict(X_test)
rf_probability = random_forest_model.predict_proba(X_test)[:, 1]


# ============================================================
# 8. Calculate performance metrics
# ============================================================

models = {
    "Logistic Regression": (lr_pred, lr_probability),
    "Random Forest": (rf_pred, rf_probability)
}

performance = []

for name, (predictions, probabilities) in models.items():

    performance.append({
        "Model": name,
        "Accuracy": accuracy_score(y_test, predictions),
        "Precision": precision_score(y_test, predictions),
        "Recall": recall_score(y_test, predictions),
        "F1": f1_score(y_test, predictions),
        "ROC_AUC": roc_auc_score(y_test, probabilities),
        "Average_Precision": average_precision_score(
            y_test,
            probabilities
        )
    })

performance_df = pd.DataFrame(performance)

print("\nModel performance:")
print(
    performance_df.round(3).to_string(index=False)
)


# ============================================================
# FIGURE 1
# Confusion matrices
# ============================================================

fig, axes = plt.subplots(1, 2, figsize=(10, 4))

for ax, (name, (predictions, _)) in zip(
    axes,
    models.items()
):

    cm = confusion_matrix(y_test, predictions)

    ax.imshow(cm)

    ax.set_title(name)

    ax.set_xlabel("Predicted")
    ax.set_ylabel("Actual")

    ax.set_xticks([0, 1])
    ax.set_yticks([0, 1])

    ax.set_xticklabels(["Non-AMR", "AMR"])
    ax.set_yticklabels(["Non-AMR", "AMR"])

    for i in range(2):
        for j in range(2):

            ax.text(
                j,
                i,
                cm[i, j],
                ha="center",
                va="center"
            )

plt.tight_layout()

plt.savefig(
    f"{FIGURE_DIR}/confusion_matrices.png",
    dpi=300,
    bbox_inches="tight"
)

plt.close()

print("\nSaved: figures/confusion_matrices.png")


# ============================================================
# FIGURE 2
# ROC curves
# ============================================================

plt.figure(figsize=(7, 6))

for name, (_, probabilities) in models.items():

    fpr, tpr, _ = roc_curve(
        y_test,
        probabilities
    )

    auc = roc_auc_score(
        y_test,
        probabilities
    )

    plt.plot(
        fpr,
        tpr,
        label=f"{name} (AUC = {auc:.3f})"
    )

plt.plot(
    [0, 1],
    [0, 1],
    linestyle="--"
)

plt.xlabel("False Positive Rate")
plt.ylabel("True Positive Rate")

plt.title("ROC Curve")

plt.legend()

plt.tight_layout()

plt.savefig(
    f"{FIGURE_DIR}/roc_comparison.png",
    dpi=300,
    bbox_inches="tight"
)

plt.close()

print("Saved: figures/roc_comparison.png")


# ============================================================
# FIGURE 3
# Precision-Recall curves
# ============================================================

plt.figure(figsize=(7, 6))

for name, (_, probabilities) in models.items():

    precision, recall, _ = precision_recall_curve(
        y_test,
        probabilities
    )

    ap = average_precision_score(
        y_test,
        probabilities
    )

    plt.plot(
        recall,
        precision,
        label=f"{name} (AP = {ap:.3f})"
    )

plt.xlabel("Recall")
plt.ylabel("Precision")

plt.title("Precision-Recall Curve")

plt.legend()

plt.tight_layout()

plt.savefig(
    f"{FIGURE_DIR}/precision_recall_comparison.png",
    dpi=300,
    bbox_inches="tight"
)

plt.close()

print(
    "Saved: figures/precision_recall_comparison.png"
)


# ============================================================
# FIGURE 4
# Training vs test performance
# ============================================================

training_performance = []
test_performance = []

for name, model in [
    ("Logistic Regression", logistic_model),
    ("Random Forest", random_forest_model)
]:

    # Training predictions
    train_pred = model.predict(X_train)

    # Test predictions
    test_pred = model.predict(X_test)

    training_performance.append({
        "Model": name,
        "Accuracy": accuracy_score(
            y_train,
            train_pred
        ),
        "Precision": precision_score(
            y_train,
            train_pred
        ),
        "Recall": recall_score(
            y_train,
            train_pred
        ),
        "F1": f1_score(
            y_train,
            train_pred
        )
    })

    test_performance.append({
        "Model": name,
        "Accuracy": accuracy_score(
            y_test,
            test_pred
        ),
        "Precision": precision_score(
            y_test,
            test_pred
        ),
        "Recall": recall_score(
            y_test,
            test_pred
        ),
        "F1": f1_score(
            y_test,
            test_pred
        )
    })


train_df = pd.DataFrame(training_performance)
test_df = pd.DataFrame(test_performance)


metrics = [
    "Accuracy",
    "Precision",
    "Recall",
    "F1"
]

x = range(len(metrics))

plt.figure(figsize=(8, 6))

for i, model_name in enumerate(
    ["Logistic Regression", "Random Forest"]
):

    train_values = train_df[
        train_df["Model"] == model_name
    ][metrics].values[0]

    test_values = test_df[
        test_df["Model"] == model_name
    ][metrics].values[0]

    plt.plot(
        x,
        train_values,
        marker="o",
        label=f"{model_name} - Train"
    )

    plt.plot(
        x,
        test_values,
        marker="x",
        linestyle="--",
        label=f"{model_name} - Test"
    )

plt.xticks(
    list(x),
    metrics
)

plt.ylim(0, 1.05)

plt.ylabel("Score")

plt.title("Training vs Test Performance")

plt.legend()

plt.tight_layout()

plt.savefig(
    f"{FIGURE_DIR}/training_vs_test_performance.png",
    dpi=300,
    bbox_inches="tight"
)

plt.close()

print(
    "Saved: figures/training_vs_test_performance.png"
)


# ============================================================
# FIGURE 5
# Random Forest feature importance
# ============================================================

feature_importance = pd.DataFrame({
    "kmer": X.columns,
    "importance": random_forest_model.feature_importances_
})

feature_importance = feature_importance.sort_values(
    "importance",
    ascending=False
)

top_features = feature_importance.head(20)

plt.figure(figsize=(8, 7))

plt.barh(
    top_features["kmer"][::-1],
    top_features["importance"][::-1]
)

plt.xlabel("Feature Importance")

plt.ylabel("3-mer")

plt.title("Top 20 Random Forest 3-mer Features")

plt.tight_layout()

plt.savefig(
    f"{FIGURE_DIR}/random_forest_top20_features.png",
    dpi=300,
    bbox_inches="tight"
)

plt.close()

print(
    "Saved: figures/random_forest_top20_features.png"
)


# ============================================================
# FIGURE 6
# Prediction probability distributions
# ============================================================

plt.figure(figsize=(8, 6))

plt.hist(
    lr_probability[y_test.values == 0],
    bins=20,
    alpha=0.5,
    label="LR Non-AMR"
)

plt.hist(
    lr_probability[y_test.values == 1],
    bins=20,
    alpha=0.5,
    label="LR AMR"
)

plt.hist(
    rf_probability[y_test.values == 0],
    bins=20,
    alpha=0.5,
    label="RF Non-AMR"
)

plt.hist(
    rf_probability[y_test.values == 1],
    bins=20,
    alpha=0.5,
    label="RF AMR"
)

plt.xlabel("Predicted AMR Probability")

plt.ylabel("Number of Proteins")

plt.title("Prediction Probability Distributions")

plt.legend()

plt.tight_layout()

plt.savefig(
    f"{FIGURE_DIR}/prediction_probability_distributions.png",
    dpi=300,
    bbox_inches="tight"
)

plt.close()

print(
    "Saved: figures/prediction_probability_distributions.png"
)


# ============================================================
# 9. Save performance table
# ============================================================

performance_df.to_csv(
    f"{FIGURE_DIR}/model_performance.csv",
    index=False
)

print(
    "\nSaved: figures/model_performance.csv"
)

print("\nAll figures generated successfully.")
