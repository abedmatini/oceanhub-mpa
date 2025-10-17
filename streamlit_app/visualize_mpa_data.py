#!/usr/bin/env python3
"""
MPA Data Visualization Script
Creates and saves maps of all Western Indian Ocean Marine Protected Area datasets
"""

import os
import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from pathlib import Path
import warnings

warnings.filterwarnings("ignore")

# Use non-interactive backend to avoid display issues
import matplotlib

matplotlib.use("Agg")

# Set the base directory
BASE_DIR = Path("/Users/mac/Downloads/MPA Data")
OUTPUT_DIR = BASE_DIR / "maps"
OUTPUT_DIR.mkdir(exist_ok=True)

# Datasets to visualize
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


def create_individual_maps():
    """Create individual map for each dataset"""
    print("\n" + "=" * 60)
    print("Creating Individual Dataset Maps")
    print("=" * 60)

    for name, path in DATASETS.items():
        if not path.exists():
            print(f"✗ Skipping {name} - file not found")
            continue

        try:
            print(f"\nProcessing: {name}")
            gdf = gpd.read_file(path)

            # Reproject to WGS84 for consistent visualization
            if gdf.crs and gdf.crs != "EPSG:4326":
                gdf = gdf.to_crs("EPSG:4326")

            # Create figure
            fig, ax = plt.subplots(1, 1, figsize=(14, 10))

            # Plot based on geometry type
            if "Point" in gdf.geometry.type.values:
                gdf.plot(
                    ax=ax, markersize=30, color="#e74c3c", alpha=0.7, edgecolor="black"
                )
            elif "LineString" in gdf.geometry.type.values:
                gdf.plot(ax=ax, linewidth=1.5, color="#3498db", alpha=0.8)
            else:  # Polygons
                gdf.plot(
                    ax=ax,
                    edgecolor="#2c3e50",
                    facecolor="#3498db",
                    linewidth=0.5,
                    alpha=0.6,
                )

            # Styling
            ax.set_title(
                f"{name}\n({len(gdf)} features)", fontsize=16, fontweight="bold", pad=20
            )
            ax.set_xlabel("Longitude", fontsize=12)
            ax.set_ylabel("Latitude", fontsize=12)
            ax.grid(True, alpha=0.3, linestyle="--", linewidth=0.5)
            ax.set_facecolor("#e8f4f8")

            # Add scale info
            bounds = gdf.total_bounds
            info_text = f"Extent: {bounds[0]:.2f}°E to {bounds[2]:.2f}°E, {bounds[1]:.2f}°N to {bounds[3]:.2f}°N"
            ax.text(
                0.5,
                -0.08,
                info_text,
                transform=ax.transAxes,
                ha="center",
                fontsize=9,
                style="italic",
            )

            plt.tight_layout()

            # Save
            filename = name.replace(" ", "_").replace("(", "").replace(")", "").lower()
            output_path = OUTPUT_DIR / f"{filename}.png"
            plt.savefig(output_path, dpi=300, bbox_inches="tight", facecolor="white")
            plt.close()

            print(f"  ✓ Saved: {output_path.name}")

        except Exception as e:
            print(f"  ✗ Error: {e}")


def create_overview_map():
    """Create overview map showing all datasets together"""
    print("\n" + "=" * 60)
    print("Creating Overview Map (All Datasets)")
    print("=" * 60)

    fig, ax = plt.subplots(1, 1, figsize=(16, 12))

    colors = {
        "WIOMPA All MPAs": "#e74c3c",
        "WIOMPA Local MPAs": "#3498db",
        "WIOMPA National MPAs": "#2ecc71",
        "WIO LMMA (Locally Managed Marine Areas)": "#f39c12",
        "WIO MPA IOC": "#9b59b6",
        "WIO Mangroves (GMW 2020)": "#1abc9c",
    }

    legend_patches = []
    datasets_plotted = 0

    for name, path in DATASETS.items():
        if not path.exists():
            continue

        try:
            print(f"  Adding: {name}")
            gdf = gpd.read_file(path)

            # Reproject to WGS84
            if gdf.crs and gdf.crs != "EPSG:4326":
                gdf = gdf.to_crs("EPSG:4326")

            color = colors.get(name, "#34495e")

            # Plot
            if "mangrove" in name.lower():
                # Mangroves - smaller features
                gdf.plot(ax=ax, color=color, alpha=0.4, edgecolor=color, linewidth=0.2)
            else:
                gdf.plot(ax=ax, color=color, alpha=0.5, edgecolor=color, linewidth=0.8)

            # Add to legend
            legend_patches.append(
                mpatches.Patch(color=color, label=f"{name} ({len(gdf)})")
            )
            datasets_plotted += 1

        except Exception as e:
            print(f"  ✗ Error with {name}: {e}")

    # Styling
    ax.set_title(
        "Western Indian Ocean Marine Protected Areas - Overview",
        fontsize=18,
        fontweight="bold",
        pad=20,
    )
    ax.set_xlabel("Longitude", fontsize=14)
    ax.set_ylabel("Latitude", fontsize=14)
    ax.grid(True, alpha=0.3, linestyle="--", linewidth=0.5)
    ax.set_facecolor("#e8f4f8")

    # Legend
    ax.legend(
        handles=legend_patches,
        loc="upper left",
        fontsize=10,
        framealpha=0.95,
        edgecolor="black",
    )

    plt.tight_layout()

    # Save
    output_path = OUTPUT_DIR / "overview_all_datasets.png"
    plt.savefig(output_path, dpi=300, bbox_inches="tight", facecolor="white")
    plt.close()

    print(f"\n✓ Saved overview map: {output_path.name}")
    print(f"  Datasets included: {datasets_plotted}")


def create_country_breakdown():
    """Create maps showing MPAs by country"""
    print("\n" + "=" * 60)
    print("Creating Country Breakdown Maps")
    print("=" * 60)

    # Load the main MPA dataset
    mpa_path = DATASETS["WIOMPA All MPAs"]
    if not mpa_path.exists():
        print("✗ Main MPA dataset not found")
        return

    try:
        gdf = gpd.read_file(mpa_path)

        # Reproject to WGS84
        if gdf.crs and gdf.crs != "EPSG:4326":
            gdf = gdf.to_crs("EPSG:4326")

        # Check if COUNTRY column exists
        if "COUNTRY" not in gdf.columns:
            print("✗ COUNTRY column not found")
            return

        countries = gdf["COUNTRY"].unique()
        print(f"Found {len(countries)} countries")

        # Create grid of subplots
        n_countries = len(countries)
        cols = 3
        rows = (n_countries + cols - 1) // cols

        fig, axes = plt.subplots(rows, cols, figsize=(18, rows * 4))
        axes = axes.flatten() if n_countries > 1 else [axes]

        for idx, country in enumerate(sorted(countries)):
            country_data = gdf[gdf["COUNTRY"] == country]
            ax = axes[idx]

            country_data.plot(
                ax=ax,
                edgecolor="#2c3e50",
                facecolor="#3498db",
                linewidth=0.5,
                alpha=0.7,
            )

            ax.set_title(
                f"{country}\n({len(country_data)} MPAs)", fontsize=11, fontweight="bold"
            )
            ax.set_xlabel("Longitude", fontsize=8)
            ax.set_ylabel("Latitude", fontsize=8)
            ax.tick_params(labelsize=7)
            ax.grid(True, alpha=0.3, linestyle="--", linewidth=0.5)
            ax.set_facecolor("#e8f4f8")

        # Hide unused subplots
        for idx in range(n_countries, len(axes)):
            axes[idx].set_visible(False)

        plt.suptitle(
            "Marine Protected Areas by Country",
            fontsize=16,
            fontweight="bold",
            y=0.995,
        )
        plt.tight_layout()

        # Save
        output_path = OUTPUT_DIR / "mpas_by_country.png"
        plt.savefig(output_path, dpi=300, bbox_inches="tight", facecolor="white")
        plt.close()

        print(f"✓ Saved country breakdown: {output_path.name}")

    except Exception as e:
        print(f"✗ Error creating country breakdown: {e}")


def main():
    """Main function to create all visualizations"""
    print("\n" + "=" * 60)
    print("MPA DATA VISUALIZATION SCRIPT")
    print("=" * 60)
    print(f"Output directory: {OUTPUT_DIR}")

    # Create all visualizations
    create_individual_maps()
    create_overview_map()
    create_country_breakdown()

    # Summary
    print("\n" + "=" * 60)
    print("VISUALIZATION COMPLETE")
    print("=" * 60)

    saved_files = list(OUTPUT_DIR.glob("*.png"))
    print(f"\n✓ Created {len(saved_files)} maps in: {OUTPUT_DIR}")
    print("\nSaved maps:")
    for f in sorted(saved_files):
        size_mb = f.stat().st_size / (1024 * 1024)
        print(f"  • {f.name} ({size_mb:.2f} MB)")


if __name__ == "__main__":
    main()
