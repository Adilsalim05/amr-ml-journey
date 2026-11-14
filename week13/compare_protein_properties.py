import pandas as pd
from Bio import SeqIO
from Bio.SeqUtils.ProtParam import ProteinAnalysis
from pathlib import Path

input_file = Path("week13/mutant_proteins.faa")
output_file = Path("week13/protein_properties.csv")

records = list(SeqIO.parse(input_file, "fasta"))
results = []

for record in records:
    sequence = str(record.seq)
    analysis = ProteinAnalysis(sequence)

    results.append({
        "protein": record.id,
        "length_aa": len(sequence),
        "molecular_weight_Da": analysis.molecular_weight(),
        "theoretical_pI": analysis.isoelectric_point(),
        "GRAVY": analysis.gravy(),
        "instability_index": analysis.instability_index(),
        "aromaticity": analysis.aromaticity()
    })

df = pd.DataFrame(results)
df.to_csv(output_file, index=False, float_format="%.4f")

print(df.to_string(index=False))
print(f"\nSaved results to {output_file}")
