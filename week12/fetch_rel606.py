from Bio import Entrez, SeqIO

Entrez.email = "adilsaleem105@gmail.com"

handle = Entrez.efetch(
    db="nucleotide",
    id="NC_012967.1",
    rettype="fasta",
    retmode="text"
)

record = SeqIO.read(handle, "fasta")
handle.close()

SeqIO.write(
    record,
    "week12/reference/ecoli_B_REL606.fasta",
    "fasta"
)

print("Reference:", record.id)
print("Length:", len(record.seq))
