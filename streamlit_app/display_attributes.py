#!/usr/bin/env python3
"""
MPA Data Attribute Display Script
Displays detailed attribute information for each dataset and saves to text files
"""

import geopandas as gpd
import pandas as pd
from pathlib import Path
import warnings

warnings.filterwarnings("ignore")

# Set the base directory
BASE_DIR = Path("/Users/mac/Downloads/MPA Data")
OUTPUT_DIR = BASE_DIR / "attribute_summaries"
OUTPUT_DIR.mkdir(exist_ok=True)

# Datasets to analyze
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


def analyze_dataset(name, path):
    """Analyze and display detailed attributes for a dataset"""

    if not path.exists():
        print(f"✗ {name} - file not found")
        return None

    try:
        print(f"\n{'='*80}")
        print(f"{name}")
        print(f"{'='*80}")

        # Load dataset
        gdf = gpd.read_file(path)

        # Create output report
        report_lines = []
        report_lines.append("=" * 80)
        report_lines.append(f"{name}")
        report_lines.append("=" * 80)
        report_lines.append(f"\nFile: {path}")
        report_lines.append(f"Number of Features: {len(gdf)}")
        report_lines.append(f"Geometry Types: {gdf.geometry.type.unique().tolist()}")
        report_lines.append(f"CRS: {gdf.crs}")
        report_lines.append(f"Bounds: {gdf.total_bounds}")

        # Column information
        report_lines.append(f"\n{'='*80}")
        report_lines.append(f"COLUMNS ({len(gdf.columns)})")
        report_lines.append(f"{'='*80}\n")

        print(f"\nColumns ({len(gdf.columns)}):")
        print(f"{'-'*80}")

        for col in gdf.columns:
            if col == "geometry":
                continue

            dtype = gdf[col].dtype
            non_null = gdf[col].notna().sum()
            null_count = gdf[col].isna().sum()
            unique_count = gdf[col].nunique()

            col_info = f"• {col}"
            col_info += f"\n  Type: {dtype}"
            col_info += (
                f"\n  Non-null: {non_null}/{len(gdf)} ({100*non_null/len(gdf):.1f}%)"
            )
            col_info += f"\n  Null: {null_count}"
            col_info += f"\n  Unique values: {unique_count}"

            # For numeric columns, show statistics
            if pd.api.types.is_numeric_dtype(gdf[col]):
                if non_null > 0:
                    col_info += f"\n  Min: {gdf[col].min()}"
                    col_info += f"\n  Max: {gdf[col].max()}"
                    col_info += f"\n  Mean: {gdf[col].mean():.2f}"
                    col_info += f"\n  Median: {gdf[col].median():.2f}"

            # For categorical columns, show value counts (top 10)
            elif pd.api.types.is_object_dtype(gdf[col]) and unique_count <= 50:
                value_counts = gdf[col].value_counts().head(10)
                col_info += f"\n  Top values:"
                for val, count in value_counts.items():
                    col_info += f"\n    - {val}: {count} ({100*count/len(gdf):.1f}%)"

            # Sample values (first 5 non-null)
            sample_values = gdf[col].dropna().head(5).tolist()
            if sample_values:
                col_info += f"\n  Sample values: {sample_values[:3]}"

            print(col_info)
            print(f"{'-'*80}")

            report_lines.append(col_info)
            report_lines.append("-" * 80)

        # Data preview
        report_lines.append(f"\n{'='*80}")
        report_lines.append("DATA PREVIEW (First 10 rows)")
        report_lines.append(f"{'='*80}\n")

        print(f"\nData Preview (first 10 rows):")
        display_cols = [col for col in gdf.columns if col != "geometry"]
        preview = gdf[display_cols].head(10).to_string(max_cols=None, max_colwidth=50)
        print(preview)
        report_lines.append(preview)

        # Summary statistics for numeric columns
        numeric_cols = gdf.select_dtypes(include=["number"]).columns.tolist()
        if "geometry" in numeric_cols:
            numeric_cols.remove("geometry")

        if numeric_cols:
            report_lines.append(f"\n{'='*80}")
            report_lines.append("NUMERIC COLUMN STATISTICS")
            report_lines.append(f"{'='*80}\n")

            print(f"\nNumeric Column Statistics:")
            stats = gdf[numeric_cols].describe().to_string()
            print(stats)
            report_lines.append(stats)

        # Missing data summary
        report_lines.append(f"\n{'='*80}")
        report_lines.append("MISSING DATA SUMMARY")
        report_lines.append(f"{'='*80}\n")

        print(f"\nMissing Data Summary:")
        missing_data = []
        for col in gdf.columns:
            if col != "geometry":
                null_count = gdf[col].isna().sum()
                null_pct = 100 * null_count / len(gdf)
                if null_count > 0:
                    missing_data.append(f"{col}: {null_count} ({null_pct:.1f}%)")

        if missing_data:
            missing_str = "\n".join(missing_data)
            print(missing_str)
            report_lines.append(missing_str)
        else:
            print("No missing data!")
            report_lines.append("No missing data!")

        # Save report to file
        filename = name.replace(" ", "_").replace("(", "").replace(")", "").lower()
        output_path = OUTPUT_DIR / f"{filename}_attributes.txt"

        with open(output_path, "w", encoding="utf-8") as f:
            f.write("\n".join(report_lines))

        print(f"\n✓ Saved detailed report to: {output_path.name}")

        return gdf

    except Exception as e:
        print(f"✗ Error analyzing {name}: {e}")
        return None


def create_combined_summary():
    """Create a combined summary of all datasets"""
    print(f"\n{'='*80}")
    print("CREATING COMBINED SUMMARY")
    print(f"{'='*80}")

    summary_lines = []
    summary_lines.append("=" * 80)
    summary_lines.append("WESTERN INDIAN OCEAN MPA DATASETS - COMBINED SUMMARY")
    summary_lines.append("=" * 80)
    summary_lines.append("")

    for name, path in DATASETS.items():
        if not path.exists():
            continue

        try:
            gdf = gpd.read_file(path)

            summary_lines.append(f"\n{name}")
            summary_lines.append("-" * 80)
            summary_lines.append(f"Features: {len(gdf)}")
            summary_lines.append(
                f"Columns: {len(gdf.columns) - 1} (excluding geometry)"
            )
            summary_lines.append(
                f"Geometry Types: {gdf.geometry.type.unique().tolist()}"
            )
            summary_lines.append(f"CRS: {gdf.crs}")

            # List all columns
            cols = [col for col in gdf.columns if col != "geometry"]
            summary_lines.append(f"Attributes: {', '.join(cols)}")

        except Exception as e:
            summary_lines.append(f"Error: {e}")

    # Save combined summary
    output_path = OUTPUT_DIR / "00_combined_summary.txt"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(summary_lines))

    print(f"✓ Saved combined summary to: {output_path.name}")


def main():
    """Main function"""
    print("\n" + "=" * 80)
    print("MPA DATA ATTRIBUTE ANALYSIS")
    print("=" * 80)
    print(f"Output directory: {OUTPUT_DIR}")

    # Analyze each dataset
    for name, path in DATASETS.items():
        analyze_dataset(name, path)

    # Create combined summary
    create_combined_summary()

    # Final summary
    print(f"\n{'='*80}")
    print("ANALYSIS COMPLETE")
    print(f"{'='*80}")

    saved_files = list(OUTPUT_DIR.glob("*.txt"))
    print(f"\n✓ Created {len(saved_files)} attribute reports in: {OUTPUT_DIR}")
    print("\nSaved reports:")
    for f in sorted(saved_files):
        size_kb = f.stat().st_size / 1024
        print(f"  • {f.name} ({size_kb:.1f} KB)")


if __name__ == "__main__":
    main()
