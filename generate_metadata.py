import os
import json
import argparse
from collections import Counter


def scan_directory(folder_path, recursive=True):
    total_files = 0
    dbf_tables_found = 0
    extension_counts = Counter()
    files_list = []

    # Normalize the path to its absolute representation
    abs_folder_path = os.path.abspath(folder_path)

    if not os.path.exists(abs_folder_path):
        print(f"Error: The path '{abs_folder_path}' does not exist.")
        return None

    if recursive:
        # Recursive directory scan using os.walk
        for root, _, files in os.walk(abs_folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                if os.path.islink(file_path):
                    continue
                try:
                    size_bytes = os.path.getsize(file_path)
                except OSError:
                    # Skip files that cannot be accessed
                    continue

                _, ext = os.path.splitext(file)
                upper_ext = ext.upper()

                total_files += 1
                if upper_ext == ".DBF":
                    dbf_tables_found += 1

                extension_counts[upper_ext] += 1
                files_list.append(
                    {
                        "name": file,
                        "extension": upper_ext,
                        "size_bytes": size_bytes,
                        "path": file_path,
                    }
                )
    else:
        # Single-level directory scan using os.listdir
        for file in os.listdir(abs_folder_path):
            file_path = os.path.join(abs_folder_path, file)
            if os.path.isfile(file_path) and not os.path.islink(file_path):
                try:
                    size_bytes = os.path.getsize(file_path)
                except OSError:
                    continue

                _, ext = os.path.splitext(file)
                upper_ext = ext.upper()

                total_files += 1
                if upper_ext == ".DBF":
                    dbf_tables_found += 1

                extension_counts[upper_ext] += 1
                files_list.append(
                    {
                        "name": file,
                        "extension": upper_ext,
                        "size_bytes": size_bytes,
                        "path": file_path,
                    }
                )

    # Sort the files list alphabetically by filename for clean output
    files_list.sort(key=lambda x: x["name"].lower())

    # Sort extension summary by count descending (optional, matching your sample)
    sorted_extensions = dict(
        sorted(extension_counts.items(), key=lambda item: item[1], reverse=True)
    )

    metadata = {
        "scan_info": {
            "folder": abs_folder_path,
            "total_files": total_files,
            "dbf_tables_found": dbf_tables_found,
        },
        "extension_summary": sorted_extensions,
        "files": files_list,
    }

    return metadata


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate directory metadata JSON.")
    parser.add_argument("folder", help="Path to the directory to scan")
    parser.add_argument(
        "-o",
        "--output",
        help="Output JSON file path (prints to console if not specified)",
    )
    parser.add_argument(
        "--non-recursive",
        action="store_true",
        help="Scan only the immediate folder (no subdirectories)",
    )

    args = parser.parse_args()

    result = scan_directory(args.folder, recursive=not args.non_recursive)

    if result:
        # json.dumps handles path backslash escaping automatically
        formatted_json = json.dumps(result, indent=4)

        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(formatted_json)
            print(f"Metadata written successfully to {args.output}")
        else:
            print(formatted_json)
