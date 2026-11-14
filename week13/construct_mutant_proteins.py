from pathlib import Path
from Bio import SeqIO
from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord

genes = {
    "ompR": {"position": 6, "reference": "K", "alternate": "T"},
    "parE": {"position": 504, "reference": "A", "alternate": "V"},
    "yjgA": {"position": 91, "reference": "Q", "alternate": "L"},
}

input_dir = Path("week13/reference_genes")
output_file = Path("week13/mutant_proteins.faa")

records = []

for gene, mutation in genes.items():
    record = SeqIO.read(input_dir / f"{gene}.gb", "genbank")
    cds = next(f for f in record.features if f.type == "CDS")
    wt = cds.qualifiers["translation"][0]

    pos = mutation["position"] - 1
    assert wt[pos] == mutation["reference"]

    mutant = (
        wt[:pos]
        + mutation["alternate"]
        + wt[pos + 1:]
    )

    assert mutant[pos] == mutation["alternate"]
    assert len(mutant) == len(wt)

    records.append(SeqRecord(
        Seq(wt), id=f"{gene}_WT", description="MG1655 reference protein"
    ))
    records.append(SeqRecord(
        Seq(mutant), id=f"{gene}_mutant", description="Computationally constructed protein variant"
    ))

    print(f"{gene}: {wt[pos]}{mutation['position']}{mutant[pos]} | {len(wt)} aa")

# AcrR insertion: p.I16_L17insLD
record = SeqIO.read(input_dir / "acrR.gb", "genbank")
cds = next(f for f in record.features if f.type == "CDS")
wt = cds.qualifiers["translation"][0]

assert wt[15] == "I" and wt[16] == "L"

mutant = wt[:16] + "LD" + wt[16:]

assert mutant[15:19] == "ILDL"
assert len(mutant) == len(wt) + 2

records.append(SeqRecord(
    Seq(wt), id="acrR_WT", description="MG1655 reference protein"
))
records.append(SeqRecord(
    Seq(mutant), id="acrR_mutant", description="Computationally constructed p.I16_L17insLD variant"
))

print(f"acrR: I16_L17insLD | {len(wt)} -> {len(mutant)} aa")

SeqIO.write(records, output_file, "fasta")
print(f"\nSaved {len(records)} sequences to {output_file}")
