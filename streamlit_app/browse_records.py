#!/usr/bin/env python3
"""
MPA Data Row-by-Row Browser
Displays each record in a clean tabular format and saves individual record views
"""

import geopandas as gpd
import pandas as pd
from pathlib import Path
import warnings

warnings.filterwarnings("ignore")

# Set the base directory
BASE_DIR = Path("/Users/mac/Downloads/MPA Data")
OUTPUT_DIR = BASE_DIR / "record_views"
OUTPUT_DIR.mkdir(exist_ok=True)

# Datasets to browse
DATASETS = {
    "WIOMPA All MPAs": BASE_DIR / "WIOMPAS_All_fin" / "WIOMPAS_All_fin.shp",
    "WIOMPA Local MPAs": BASE_DIR / "WIOMPA_Local_fin" / "WIOMPA_Local_fin.shp",
    "WIOMPA National MPAs": BASE_DIR
    / "WIOMPA_National_fin"
    / "WIOMPA_National_fin.shp",
    "WIO LMMA (Locally Managed Marine Areas)": BASE_DIR
    / "wio_lmma_ioc"
    / "wio_lmma_ioc.shp",
    "WIO MPA IOC": BASE_DIR / "wio_mpa_ioc" / "wio_mpa_ioc.shp",
    "WIO Mangroves (GMW 2020)": BASE_DIR
    / "wio_mangrove_gmw2020_africaalbers"
    / "wio_mangrove_gmw2020_africaalbers.shp",
}


def format_record(row, index, total_records):
    """Format a single record in a clean tabular layout"""
    lines = []
    lines.append("=" * 80)
    lines.append(f"RECORD {index + 1} of {total_records}")
    lines.append("=" * 80)
    lines.append("")

    # Find the longest field name for alignment
    max_field_length = max(
        len(str(field)) for field in row.index if field != "geometry"
    )

    for field in row.index:
        if field == "geometry":
            # Show geometry info instead of full WKT
            geom = row[field]
            if geom is not None and not pd.isna(geom):
                geom_info = (
                    f"{geom.geom_type} (Area: {geom.area:.6f}, Bounds: {geom.bounds})"
                )
                lines.append(f"{field:<{max_field_length}} : {geom_info}")
            else:
                lines.append(f"{field:<{max_field_length}} : None")
        else:
            value = row[field]
            # Format the value
            if pd.isna(value):
                display_value = "NULL"
            elif isinstance(value, float):
                display_value = f"{value:.6f}"
            else:
                display_value = str(value)

            lines.append(f"{field:<{max_field_length}} : {display_value}")

    lines.append("")
    return "\n".join(lines)


def browse_dataset(name, path, max_records=100):
    """Browse through a dataset and save formatted records"""

    if not path.exists():
        print(f"✗ {name} - file not found")
        return

    try:
        print(f"\n{'='*80}")
        print(f"{name}")
        print(f"{'='*80}")

        # Load dataset
        gdf = gpd.read_file(path)
        total_records = len(gdf)

        print(f"Total records: {total_records}")
        print(f"Displaying first {min(max_records, total_records)} records...")

        # Create dataset-specific output directory
        dataset_dir = (
            OUTPUT_DIR
            / name.replace(" ", "_").replace("(", "").replace(")", "").lower()
        )
        dataset_dir.mkdir(exist_ok=True)

        # Create a combined file with all records
        all_records = []
        all_records.append("=" * 80)
        all_records.append(f"{name} - ALL RECORDS")
        all_records.append(f"Total: {total_records}")
        all_records.append("=" * 80)
        all_records.append("")

        # Display and save each record
        records_to_show = min(max_records, total_records)

        for idx in range(records_to_show):
            row = gdf.iloc[idx]

            # Format the record
            formatted = format_record(row, idx, total_records)

            # Print first 10 to console
            if idx < 10:
                print(f"\n{formatted}")

            # Add to combined file
            all_records.append(formatted)
            all_records.append("\n")

            # Save individual record file (first 20 only to avoid too many files)
            if idx < 20:
                record_file = dataset_dir / f"record_{idx+1:04d}.txt"
                with open(record_file, "w", encoding="utf-8") as f:
                    f.write(formatted)

        # Save combined file
        combined_file = dataset_dir / f"all_records_1_to_{records_to_show}.txt"
        with open(combined_file, "w", encoding="utf-8") as f:
            f.write("\n".join(all_records))

        print(f"\n✓ Saved {records_to_show} records to: {dataset_dir}")
        print(f"  - Individual files: first 20 records")
        print(f"  - Combined file: {combined_file.name}")

        # Create a CSV for easy viewing in spreadsheet apps
        csv_file = dataset_dir / f"{name.replace(' ', '_').lower()}_all_data.csv"
        gdf_no_geom = gdf.drop(columns=["geometry"])
        gdf_no_geom.to_csv(csv_file, index=False)
        print(f"  - CSV export: {csv_file.name}")

        # Create an HTML table view for first 50 records
        html_file = dataset_dir / f"{name.replace(' ', '_').lower()}_preview.html"
        create_html_view(gdf.head(50), name, html_file)
        print(f"  - HTML preview: {html_file.name}")

    except Exception as e:
        print(f"✗ Error browsing {name}: {e}")


def create_html_view(gdf, dataset_name, output_file):
    """Create an HTML table view of the data"""

    # Drop geometry for HTML display
    df = gdf.drop(columns=["geometry"]) if "geometry" in gdf.columns else gdf

    html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>{dataset_name} - Data Preview</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 20px;
            background-color: #f5f5f5;
        }}
        h1 {{
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
        }}
        .info {{
            background-color: #ecf0f1;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 20px;
        }}
        table {{
            border-collapse: collapse;
            width: 100%;
            background-color: white;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        th {{
            background-color: #3498db;
            color: white;
            padding: 12px;
            text-align: left;
            font-weight: bold;
            position: sticky;
            top: 0;
        }}
        td {{
            padding: 10px;
            border-bottom: 1px solid #ddd;
        }}
        tr:hover {{
            background-color: #f5f5f5;
        }}
        tr:nth-child(even) {{
            background-color: #fafafa;
        }}
        .null {{
            color: #999;
            font-style: italic;
        }}
        .record-num {{
            background-color: #e8f4f8;
            font-weight: bold;
            color: #2980b9;
        }}
    </style>
</head>
<body>
    <h1>{dataset_name}</h1>
    <div class="info">
        <strong>Total Records:</strong> {len(gdf)}<br>
        <strong>Columns:</strong> {len(df.columns)}<br>
        <strong>Showing:</strong> First {min(50, len(gdf))} records
    </div>
    <table>
        <thead>
            <tr>
                <th>#</th>
"""

    # Add column headers
    for col in df.columns:
        html_content += f"                <th>{col}</th>\n"

    html_content += """            </tr>
        </thead>
        <tbody>
"""

    # Add data rows
    for idx, row in df.iterrows():
        html_content += f"            <tr>\n"
        html_content += f'                <td class="record-num">{idx + 1}</td>\n'

        for col in df.columns:
            value = row[col]
            if pd.isna(value):
                html_content += f'                <td class="null">NULL</td>\n'
            else:
                # Format numbers nicely
                if isinstance(value, float):
                    formatted_value = f"{value:.4f}"
                else:
                    formatted_value = str(value)
                html_content += f"                <td>{formatted_value}</td>\n"

        html_content += "            </tr>\n"

    html_content += """        </tbody>
    </table>
</body>
</html>
"""

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(html_content)


def main():
    """Main function"""
    print("\n" + "=" * 80)
    print("MPA DATA ROW-BY-ROW BROWSER")
    print("=" * 80)
    print(f"Output directory: {OUTPUT_DIR}")
    print("\nThis will create formatted views of each dataset's records.")
    print("=" * 80)

    # Browse each dataset
    for name, path in DATASETS.items():
        browse_dataset(name, path, max_records=100)

    # Final summary
    print(f"\n{'='*80}")
    print("BROWSING COMPLETE")
    print(f"{'='*80}")

    saved_dirs = [d for d in OUTPUT_DIR.iterdir() if d.is_dir()]
    print(f"\n✓ Created record views for {len(saved_dirs)} datasets")
    print(f"\nOutput directories:")
    for d in sorted(saved_dirs):
        num_files = (
            len(list(d.glob("*.txt")))
            + len(list(d.glob("*.csv")))
            + len(list(d.glob("*.html")))
        )
        print(f"  • {d.name}/ ({num_files} files)")

    print(f"\n{'='*80}")
    print("How to use the outputs:")
    print("=" * 80)
    print("1. Individual TXT files: View single records in detail")
    print("2. Combined TXT files: Browse multiple records in sequence")
    print("3. CSV files: Open in Excel/Sheets for spreadsheet analysis")
    print("4. HTML files: Open in browser for interactive table view")
    print("=" * 80)


if __name__ == "__main__":
    main()
