from Bio.SeqUtils.ProtParam import ProteinAnalysis
import pandas as pd


def physicochemical_features(sequence):
    sequence = sequence.upper().replace("*", "")

    valid_aas = set("ACDEFGHIKLMNPQRSTVWY")

    if not set(sequence).issubset(valid_aas):
        return None

    analysis = ProteinAnalysis(sequence)

    return {
        "molecular_weight": analysis.molecular_weight(),
        "isoelectric_point": analysis.isoelectric_point(),
        "instability_index": analysis.instability_index(),
        "aromaticity": analysis.aromaticity(),
        "gravy": analysis.gravy(),
        "helix_fraction": analysis.secondary_structure_fraction()[0],
        "turn_fraction": analysis.secondary_structure_fraction()[1],
        "sheet_fraction": analysis.secondary_structure_fraction()[2],
    }


def build_physicochemical_matrix(sequences):
    rows = []

    for seq in sequences:
        features = physicochemical_features(seq)
        rows.append(features if features else {})

    return pd.DataFrame(rows)
