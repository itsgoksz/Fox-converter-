from dbfread import DBF
import pandas as pd
import json
import os

FRX_FILE = "jwerp/1001/silver.frx"


def process_frx(file_path):
    print(f"Processing {file_path}...")
    df = pd.DataFrame(list(DBF(file_path, load=True, ignore_missing_memofile=True)))

    # Pass 1: Find all bands (OBJTYPE=9)
    bands = []
    current_y = 0.0

    # Mapping of OBJCODE to Band Name
    band_names = {
        0: "Title",
        1: "Page Header",
        2: "Column Header",
        3: "Group Header",
        4: "Detail",
        5: "Group Footer",
        6: "Column Footer",
        7: "Page Footer",
        8: "Summary",
    }

    # Extract bands
    for idx, row in df.iterrows():
        objtype = row.get("OBJTYPE")
        if objtype == 9:
            height = float(row.get("HEIGHT", 0) or 0)
            objcode = row.get("OBJCODE")
            band_name = band_names.get(objcode, f"Band-{objcode}")

            bands.append(
                {
                    "band_id": len(bands),
                    "objcode": objcode,
                    "name": band_name,
                    "start_y": current_y,
                    "height": height,
                    "end_y": current_y + height,
                    "objects": [],
                }
            )
            current_y += height

    # Pass 2: Assign visual objects to bands based on VPOS
    visual_objtypes = [5, 6, 7, 8, 17]
    # 5: Label, 8: Field, 17: Picture, 6/7: Line/Shape

    unassigned = []

    for idx, row in df.iterrows():
        objtype = row.get("OBJTYPE")

        if objtype not in visual_objtypes:
            continue

        vpos = float(row.get("VPOS", 0) or 0)

        name_val = row.get("NAME")
        expr_val = row.get("EXPR")
        
        name_str = "" if pd.isna(name_val) else str(name_val).strip()
        expr_str = "" if pd.isna(expr_val) else str(expr_val).strip()
        
        obj = {
            "record": int(idx),
            "objtype": objtype,
            "objcode": row.get("OBJCODE"),
            "name": name_str,
            "expr": expr_str,
            "vpos_absolute": vpos,
            "hpos": float(row.get("HPOS", 0) or 0),
            "width": float(row.get("WIDTH", 0) or 0),
            "height": float(row.get("HEIGHT", 0) or 0),
            "font": str(row.get("FONTFACE", "")).strip(),
            "fontsize": row.get("FONTSIZE"),
        }

        # Find which band this belongs to
        assigned = False
        for band in bands:
            # We add a tiny buffer for rounding errors in floats
            if band["start_y"] - 1 <= vpos <= band["end_y"] + 1:
                obj["vpos"] = vpos - band["start_y"]
                band["objects"].append(obj)
                assigned = True
                break

        if not assigned:
            # Fallback for objects completely out of bounds (usually page footers pushed down)
            if len(bands) > 0 and vpos > bands[-1]["end_y"]:
                obj["vpos"] = vpos - bands[-1]["start_y"]
                bands[-1]["objects"].append(obj)
            else:
                unassigned.append(obj)

    report = {
        "report_name": os.path.basename(file_path),
        "bands": bands,
        "unassigned_objects": unassigned,
    }

    out_file = "report_definition_banded.json"
    with open(out_file, "w") as f:
        json.dump(report, f, indent=2, default=str)

    print(f"\nSaved {out_file}")
    print("-" * 50)
    for band in bands:
        print(
            f"Band: {band['name']:<15} | Height: {band['height']:<8} | Objects: {len(band['objects'])}"
        )
    print(f"Unassigned: {len(unassigned)}")


if __name__ == "__main__":
    process_frx(FRX_FILE)
