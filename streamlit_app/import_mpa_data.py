#!/usr/bin/env python3
"""
MPA Data Import Script
Imports all Western Indian Ocean Marine Protected Area datasets
"""

import os
import geopandas as gpd
import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt
import warnings

warnings.filterwarnings("ignore")

# Set the base directory
BASE_DIR = Path("/Users/mac/Downloads/MPA Data")


def load_shapefile(shapefile_path, dataset_name):
    """
    Load a shapefile and print basic information

    Parameters:
    -----------
    shapefile_path : str or Path
        Path to the .shp file
    dataset_name : str
        Name of the dataset for display

    Returns:
    --------
    GeoDataFrame or None if loading fails
    """
    try:
        print(f"\n{'='*60}")
        print(f"Loading: {dataset_name}")
        print(f"{'='*60}")

        # Read the shapefile
        gdf = gpd.read_file(shapefile_path)

        # Print basic information
        print(f"✓ Successfully loaded {dataset_name}")
        print(f"  - Number of features: {len(gdf)}")
        print(f"  - Geometry type: {gdf.geometry.type.unique().tolist()}")
        print(f"  - CRS: {gdf.crs}")
        print(f"  - Bounds: {gdf.total_bounds}")

        # Print column information
        print(f"\n  Columns ({len(gdf.columns)}):")
        for col in gdf.columns:
            if col != "geometry":
                dtype = gdf[col].dtype
                non_null = gdf[col].notna().sum()
                print(f"    • {col}: {dtype} ({non_null}/{len(gdf)} non-null)")

        # Print sample data (first 3 rows, excluding geometry)
        print(f"\n  Sample data (first 3 rows):")
        display_cols = [col for col in gdf.columns if col != "geometry"]
        if display_cols:
            print(gdf[display_cols].head(3).to_string(index=False, max_cols=5))

        return gdf

    except Exception as e:
        print(f"✗ Error loading {dataset_name}: {str(e)}")
        return None


def main():
    """
    Main function to import all MPA datasets
    """
    print("Western Indian Ocean MPA Data Import Script")
    print("=" * 60)

    # Define all datasets to import
    datasets = {
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

    # Dictionary to store loaded datasets
    loaded_data = {}

    # Load each dataset
    for name, path in datasets.items():
        if path.exists():
            gdf = load_shapefile(path, name)
            if gdf is not None:
                # Store in dictionary with simplified key
                key = name.replace(" ", "_").replace("(", "").replace(")", "").lower()
                loaded_data[key] = gdf
        else:
            print(f"\n✗ File not found: {path}")

    # Summary
    print(f"\n{'='*60}")
    print("IMPORT SUMMARY")
    print(f"{'='*60}")
    print(f"Successfully loaded {len(loaded_data)} out of {len(datasets)} datasets:")
    for key in loaded_data:
        print(f"  ✓ {key}")

    # Optional: Create a simple visualization
    # Disabled to avoid display issues in headless environments
    # if loaded_data:
    #     print("\nCreating visualization...")
    #     create_visualization(loaded_data)

    return loaded_data


def create_visualization(data_dict):
    """
    Create a simple visualization of all loaded datasets

    Parameters:
    -----------
    data_dict : dict
        Dictionary of loaded GeoDataFrames
    """
    try:
        # Count datasets with valid geometries
        valid_datasets = [
            name
            for name, gdf in data_dict.items()
            if gdf is not None and not gdf.geometry.is_empty.all()
        ]

        if not valid_datasets:
            print("No valid geometries to plot")
            return

        # Create subplots
        n_plots = len(valid_datasets)
        cols = min(3, n_plots)
        rows = (n_plots + cols - 1) // cols

        fig, axes = plt.subplots(rows, cols, figsize=(cols * 5, rows * 4))
        if n_plots == 1:
            axes = [axes]
        else:
            axes = axes.flatten() if n_plots > 1 else [axes]

        # Plot each dataset
        for idx, name in enumerate(valid_datasets):
            gdf = data_dict[name]
            ax = axes[idx] if n_plots > 1 else axes[0]

            # Plot with different colors for different geometry types
            if "Point" in gdf.geometry.type.values:
                gdf.plot(ax=ax, markersize=10, color="red", alpha=0.6)
            elif "LineString" in gdf.geometry.type.values:
                gdf.plot(ax=ax, linewidth=1, color="blue", alpha=0.6)
            else:  # Polygons
                gdf.plot(
                    ax=ax,
                    edgecolor="black",
                    facecolor="lightblue",
                    linewidth=0.5,
                    alpha=0.6,
                )

            ax.set_title(name.replace("_", " ").title(), fontsize=10)
            ax.set_xlabel("Longitude", fontsize=8)
            ax.set_ylabel("Latitude", fontsize=8)
            ax.tick_params(labelsize=7)

        # Hide unused subplots
        for idx in range(n_plots, len(axes)):
            axes[idx].set_visible(False)

        plt.suptitle(
            "Western Indian Ocean Marine Protected Areas",
            fontsize=12,
            fontweight="bold",
        )
        plt.tight_layout()

        # Save the figure
        output_path = BASE_DIR / "mpa_overview.png"
        plt.savefig(output_path, dpi=150, bbox_inches="tight")
        print(f"✓ Visualization saved to: {output_path}")

        # Show the plot
        plt.show()

    except Exception as e:
        print(f"Could not create visualization: {e}")


def export_to_csv(data_dict, output_dir=None):
    """
    Export attribute data from all datasets to CSV files

    Parameters:
    -----------
    data_dict : dict
        Dictionary of loaded GeoDataFrames
    output_dir : Path or str
        Directory to save CSV files (default: BASE_DIR / "csv_exports")
    """
    if output_dir is None:
        output_dir = BASE_DIR / "csv_exports"

    output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True)

    print(f"\nExporting to CSV files in: {output_dir}")

    for name, gdf in data_dict.items():
        if gdf is not None:
            # Drop geometry column for CSV export
            df = pd.DataFrame(gdf.drop(columns="geometry"))

            # Save to CSV
            csv_path = output_dir / f"{name}.csv"
            df.to_csv(csv_path, index=False)
            print(f"  ✓ Exported {name} ({len(df)} records) to {csv_path.name}")


def clean_column_names(gdf):
    """
    Clean column names to be BigQuery compatible.
    - Remove special characters (commas, spaces, etc.)
    - Replace with underscores
    - Convert to lowercase
    - Ensure names start with letter or underscore
    """
    new_columns = {}
    for col in gdf.columns:
        if col == "geometry":
            continue
        # Replace special chars with underscore, remove extra spaces
        clean_name = col.strip()
        clean_name = clean_name.replace(",", "")
        clean_name = clean_name.replace(" ", "_")
        clean_name = clean_name.replace("-", "_")
        clean_name = clean_name.replace("(", "")
        clean_name = clean_name.replace(")", "")
        clean_name = clean_name.replace(":", "")
        clean_name = clean_name.replace("/", "_")
        clean_name = clean_name.replace(".", "_")
        # Remove multiple underscores
        while "__" in clean_name:
            clean_name = clean_name.replace("__", "_")
        # Remove leading/trailing underscores
        clean_name = clean_name.strip("_")
        # Convert to lowercase
        clean_name = clean_name.lower()
        # Ensure starts with letter or underscore
        if clean_name and clean_name[0].isdigit():
            clean_name = f"col_{clean_name}"
        new_columns[col] = clean_name
    
    return gdf.rename(columns=new_columns)


def export_to_parquet(
    data_dict, output_dir=None, write_geoparquet=True, write_attributes=True
):
    """
    Export datasets to Parquet formats.
    - GeoParquet: preserves geometries and CRS
    - Attributes Parquet: attribute-only tables without geometry

    Parameters:
    -----------
    data_dict : dict
        Dictionary of loaded GeoDataFrames
    output_dir : Path or str
        Base directory to save Parquet files (default: BASE_DIR / "parquet_exports")
    write_geoparquet : bool
        Whether to write GeoParquet files
    write_attributes : bool
        Whether to write attribute-only Parquet files
    """
    if output_dir is None:
        output_dir = BASE_DIR / "parquet_exports"

    output_dir = Path(output_dir)
    geoparquet_dir = output_dir / "geoparquet"
    attributes_dir = output_dir / "attributes"

    if write_geoparquet:
        geoparquet_dir.mkdir(parents=True, exist_ok=True)
    if write_attributes:
        attributes_dir.mkdir(parents=True, exist_ok=True)

    print(f"\nExporting to Parquet files in: {output_dir}")

    for name, gdf in data_dict.items():
        if gdf is None or gdf.empty:
            print(f"  • Skipping {name} (no data)")
            continue

        # Clean column names for BigQuery compatibility
        gdf_clean = clean_column_names(gdf.copy())
        
        # Fix invalid geometries (self-intersections, etc.) using buffer(0)
        print(f"  • Validating geometries for {name}...")
        invalid_count = (~gdf_clean.geometry.is_valid).sum()
        if invalid_count > 0:
            print(f"    - Found {invalid_count} invalid geometries, repairing...")
            gdf_clean['geometry'] = gdf_clean.geometry.buffer(0)
        
        # Reproject to WGS84 (EPSG:4326) for BigQuery compatibility
        # BigQuery only supports OGC:CRS84 which is essentially WGS84
        if gdf_clean.crs and gdf_clean.crs != "EPSG:4326":
            gdf_clean = gdf_clean.to_crs("EPSG:4326")

        if write_geoparquet:
            gpq_path = geoparquet_dir / f"{name}.parquet"
            # GeoPandas writes GeoParquet when using pyarrow under the hood
            gdf_clean.to_parquet(gpq_path, index=False)
            print(f"  ✓ Wrote GeoParquet: {gpq_path.name} ({len(gdf_clean)} records)")

        if write_attributes:
            df = pd.DataFrame(gdf_clean.drop(columns="geometry"))
            apq_path = attributes_dir / f"{name}.parquet"
            df.to_parquet(apq_path, index=False)
            print(f"  ✓ Wrote Attributes Parquet: {apq_path.name} ({len(df)} records)")


if __name__ == "__main__":
    # Load all datasets
    loaded_datasets = main()

    # Export to Parquet by default (GeoParquet and attribute-only Parquet)
    export_to_parquet(loaded_datasets)

    # Optional: Export to CSV
    # export_to_csv(loaded_datasets)

    # The loaded_datasets dictionary now contains all your data
    # You can access individual datasets like:
    # wiompa_all = loaded_datasets.get('wiompa_all_mpas')
    # wiompa_local = loaded_datasets.get('wiompa_local_mpas')
    # etc.
