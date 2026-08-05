# src/load_card_data.py
import json
import pandas as pd

def load_card_dataframe(json_path="data/card/card.json"):
    with open(json_path) as f:
        card = json.load(f)

    records = []
    for key, entry in card.items():
        if key.startswith("_") or not isinstance(entry, dict):
            continue
        records.append({
            "aro_accession": entry.get("ARO_accession"),
            "model_name": entry.get("model_name"),
            "model_type": entry.get("model_type"),
        })
    return pd.DataFrame(records)

if __name__ == "__main__":
    df = load_card_dataframe()
    print(df.shape)
    print(df.head())
