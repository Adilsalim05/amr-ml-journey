
from Bio import Entrez, SeqIO
from Bio.SeqRecord import SeqRecord
from Bio.SeqFeature import SeqFeature, FeatureLocation
from pathlib import Path
import time

Entrez.email = "adilsaleem105@gmail.com"

genes = ["acrR", "parE", "ompR", "yjgA"]
accession = "NC_000913.3"

output_dir = Path("week13/reference_genes")
output_dir.mkdir(parents=True, exist_ok=True)

print(f"Fetching reference chromosome {accession}...")

with Entrez.efetch(
    db="nuccore",
    id=accession,
    rettype="gbwithparts",
    retmode="text"
) as handle:
    genome = SeqIO.read(handle, "genbank")

print(f"Reference chromosome: {len(genome.seq)} bp")

for gene in genes:

    print(f"\nProcessing {gene}...")

    cds_features = [
        feature for feature in genome.features
        if feature.type == "CDS"
        and feature.qualifiers.get("gene", [""])[0] == gene
    ]

    if len(cds_features) != 1:
        raise ValueError(
            f"Expected one CDS for {gene}, found {len(cds_features)}"
        )

    cds = cds_features[0]

    # Extract CDS in coding orientation, including reverse-strand genes
    cds_sequence = cds.extract(genome.seq)

    official_translation = cds.qualifiers["translation"][0]

    # Independently translate the extracted CDS
    manual_translation = str(cds_sequence.translate(to_stop=True))

    if manual_translation != official_translation:
        raise ValueError(f"Translation mismatch for {gene}")

    # Create an individual GenBank record for the extracted CDS
    gene_record = SeqRecord(
        cds_sequence,
        id=gene,
        name=gene,
        description=cds.qualifiers.get("product", [gene])[0]
    )

    gene_record.annotations["molecule_type"] = "DNA"

    gene_record.features = [
        SeqFeature(
            FeatureLocation(0, len(cds_sequence), strand=1),
            type="CDS",
            qualifiers=cds.qualifiers
        )
    ]

    output_file = output_dir / f"{gene}.gb"
    SeqIO.write(gene_record, output_file, "genbank")

    print(f"Gene: {gene}")
    print(f"CDS length: {len(cds_sequence)} bp")
    print(f"Protein length: {len(official_translation)} aa")
    print(f"Translation verified: YES")
    print(f"Saved: {output_file}")

    time.sleep(0.4)

print("\nAll four genes processed successfully.")

