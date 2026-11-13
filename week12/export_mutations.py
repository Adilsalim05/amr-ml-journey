import csv
from pathlib import Path
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill
from openpyxl.utils import get_column_letter

vcf = Path("week12/variants/SRR2589044.snpeff.vcf")
out = Path("week12/results")

ann_fields = [
    "Allele", "Annotation", "Impact", "Gene", "Gene_ID",
    "Feature_Type", "Feature_ID", "Transcript_BioType", "Rank",
    "HGVS_c", "HGVS_p", "cDNA_position", "CDS_position",
    "AA_position", "Distance", "Warnings"
]

summary_fields = [
    "CHROM", "POS", "REF", "ALT", "QUAL", "FILTER", "DP",
    "REF_AD", "ALT_AD", "ALT_AF_percent", "Annotation",
    "Impact", "Gene", "Gene_ID", "HGVS_c", "HGVS_p",
    "Annotation_count"
]

summary, all_annotations = [], []
impact_rank = {"HIGH": 0, "MODERATE": 1, "LOW": 2, "MODIFIER": 3}

with vcf.open() as handle:
    for line in handle:
        if line.startswith("#"):
            continue

        fields = line.rstrip("\n").split("\t")
        chrom, pos, _, ref, alt, qual, filt, info = fields[:8]

        format_keys = fields[8].split(":") if len(fields) > 8 else []
        sample_values = fields[9].split(":") if len(fields) > 9 else []
        sample = dict(zip(format_keys, sample_values))

        dp = sample.get("DP", "")
        ad = sample.get("AD", "")
        ad_values = ad.split(",") if ad else []

        ref_ad = int(ad_values[0]) if len(ad_values) > 0 and ad_values[0].isdigit() else None
        alt_ad = int(ad_values[1]) if len(ad_values) > 1 and ad_values[1].isdigit() else None
        total_ad = ref_ad + alt_ad if ref_ad is not None and alt_ad is not None else 0
        af = round(100 * alt_ad / total_ad, 2) if total_ad else None

        info_dict = dict(item.split("=", 1) for item in info.split(";") if "=" in item)
        annotations = [
            dict(zip(ann_fields, (entry.split("|") + [""] * 16)[:16]))
            for entry in info_dict.get("ANN", "").split(",")
            if entry
        ]

        if not annotations:
            print(f"WARNING: No ANN annotation at {chrom}:{pos}")
            continue

        # Select the most severe consequence; prefer intergenic_region
        # when all consequences have MODIFIER impact.
        primary = min(
            annotations,
            key=lambda a: (
                impact_rank.get(a["Impact"], 4),
                0 if a["Annotation"] == "intergenic_region" else 1
            )
        )

        summary.append({
            "CHROM": chrom, "POS": int(pos), "REF": ref, "ALT": alt,
            "QUAL": float(qual), "FILTER": filt, "DP": int(dp) if dp.isdigit() else None,
            "REF_AD": ref_ad, "ALT_AD": alt_ad, "ALT_AF_percent": af,
            "Annotation": primary["Annotation"], "Impact": primary["Impact"],
            "Gene": primary["Gene"], "Gene_ID": primary["Gene_ID"],
            "HGVS_c": primary["HGVS_c"], "HGVS_p": primary["HGVS_p"],
            "Annotation_count": len(annotations)
        })

        for annotation in annotations:
            all_annotations.append({
                "CHROM": chrom, "POS": int(pos), "REF": ref, "ALT": alt,
                **annotation
            })

csv_path = out / "SRR2589044_mutation_annotations.csv"
xlsx_path = out / "SRR2589044_mutation_annotations.xlsx"

with csv_path.open("w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=summary_fields)
    writer.writeheader()
    writer.writerows(summary)

wb = Workbook()
ws = wb.active
ws.title = "Primary variants"
ws.append(summary_fields)

for row in summary:
    ws.append([row[field] for field in summary_fields])

ann_ws = wb.create_sheet("All SnpEff annotations")
all_fields = ["CHROM", "POS", "REF", "ALT"] + ann_fields
ann_ws.append(all_fields)

for row in all_annotations:
    ann_ws.append([row.get(field, "") for field in all_fields])

for sheet in wb.worksheets:
    sheet.freeze_panes = "A2"
    sheet.auto_filter.ref = sheet.dimensions
    for cell in sheet[1]:
        cell.font = Font(bold=True, color="FFFFFF")
        cell.fill = PatternFill("solid", fgColor="365F91")
    for column in sheet.columns:
        width = min(max(len(str(cell.value or "")) for cell in column) + 2, 35)
        sheet.column_dimensions[get_column_letter(column[0].column)].width = width

wb.save(xlsx_path)

print(f"Variants exported: {len(summary)}")
print(f"Individual SnpEff annotations: {len(all_annotations)}")
print(f"CSV:  {csv_path}")
print(f"XLSX: {xlsx_path}")
