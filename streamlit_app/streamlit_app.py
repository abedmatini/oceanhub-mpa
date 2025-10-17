#!/usr/bin/env python3
"""
Western Indian Ocean MPA Data Explorer
Interactive Streamlit app with Leaflet maps for Marine Protected Areas
"""

import streamlit as st
import geopandas as gpd
import pandas as pd
import folium
from folium import plugins
from streamlit_folium import st_folium
from pathlib import Path
import warnings

warnings.filterwarnings("ignore")

# Page configuration
st.set_page_config(
    page_title="WIO MPA Explorer",
    page_icon="🌊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS
st.markdown(
    """
    <style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #2c3e50;
        text-align: center;
        padding: 1rem 0;
        background: linear-gradient(120deg, #3498db 0%, #2ecc71 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #7f8c8d;
        text-align: center;
        padding-bottom: 2rem;
    }
    .stat-box {
        background-color: #ecf0f1;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #3498db;
        margin: 1rem 0;
    }
    .stat-number {
        font-size: 2.5rem;
        font-weight: bold;
        color: #2c3e50;
    }
    .stat-label {
        font-size: 1rem;
        color: #7f8c8d;
        text-transform: uppercase;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Base directory
BASE_DIR = Path("/Users/mac/Downloads/MPA Data")

# Dataset paths
DATASETS = {
    "All MPAs": BASE_DIR / "WIOMPAS_All_fin" / "WIOMPAS_All_fin.shp",
    "Local MPAs": BASE_DIR / "WIOMPA_Local_fin" / "WIOMPA_Local_fin.shp",
    "National MPAs": BASE_DIR / "WIOMPA_National_fin" / "WIOMPA_National_fin.shp",
    "LMMAs": BASE_DIR / "wio_lmma_ioc" / "wio_lmma_ioc.shp",
    "IOC MPAs": BASE_DIR / "wio_mpa_ioc" / "wio_mpa_ioc.shp",
    "Mangroves": BASE_DIR
    / "wio_mangrove_gmw2020_africaalbers"
    / "wio_mangrove_gmw2020_africaalbers.shp",
}


@st.cache_data
def load_dataset(dataset_path):
    """Load and cache dataset"""
    try:
        gdf = gpd.read_file(dataset_path)
        # Ensure WGS84 for Leaflet
        if gdf.crs and gdf.crs != "EPSG:4326":
            gdf = gdf.to_crs("EPSG:4326")
        return gdf
    except Exception as e:
        st.error(f"Error loading dataset: {e}")
        return None


def create_folium_map(gdf, dataset_name, color="#3498db"):
    """Create a Folium map with the dataset"""

    # Calculate center
    bounds = gdf.total_bounds
    center_lat = (bounds[1] + bounds[3]) / 2
    center_lon = (bounds[0] + bounds[2]) / 2

    # Create base map
    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=5,
        tiles="OpenStreetMap",
        control_scale=True,
    )

    # Add different tile layers
    folium.TileLayer("CartoDB positron", name="Light Map").add_to(m)
    folium.TileLayer("CartoDB dark_matter", name="Dark Map").add_to(m)
    folium.TileLayer(
        "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
        attr="Esri",
        name="Satellite",
    ).add_to(m)

    # Add features
    feature_group = folium.FeatureGroup(name=dataset_name)

    # Limit features for performance (first 1000)
    display_gdf = gdf.head(1000) if len(gdf) > 1000 else gdf

    for idx, row in display_gdf.iterrows():
        if row.geometry is None or pd.isna(row.geometry):
            continue

        # Create popup content
        popup_html = "<div style='width: 300px;'>"
        popup_html += (
            f"<h4 style='color: #2c3e50; margin-bottom: 10px;'>{dataset_name}</h4>"
        )

        # Add attributes (exclude geometry and limit fields)
        fields_to_show = [col for col in row.index if col != "geometry"][:10]

        for field in fields_to_show:
            value = row[field]
            if pd.notna(value):
                popup_html += f"<b>{field}:</b> {value}<br>"

        popup_html += "</div>"

        popup = folium.Popup(popup_html, max_width=300)

        # Add geometry
        if row.geometry.geom_type in ["Polygon", "MultiPolygon"]:
            folium.GeoJson(
                row.geometry,
                style_function=lambda x, color=color: {
                    "fillColor": color,
                    "color": "#2c3e50",
                    "weight": 1,
                    "fillOpacity": 0.5,
                },
                popup=popup,
            ).add_to(feature_group)
        elif row.geometry.geom_type in ["Point", "MultiPoint"]:
            coords = (
                (row.geometry.y, row.geometry.x)
                if row.geometry.geom_type == "Point"
                else (row.geometry.centroid.y, row.geometry.centroid.x)
            )
            folium.CircleMarker(
                location=coords,
                radius=5,
                color=color,
                fill=True,
                fillColor=color,
                fillOpacity=0.7,
                popup=popup,
            ).add_to(feature_group)

    feature_group.add_to(m)

    # Add layer control
    folium.LayerControl().add_to(m)

    # Add fullscreen button
    plugins.Fullscreen().add_to(m)

    # Add measure control
    plugins.MeasureControl(position="topleft", primary_length_unit="kilometers").add_to(
        m
    )

    # Add minimap
    minimap = plugins.MiniMap(toggle_display=True)
    minimap.add_to(m)

    return m


def landing_page():
    """Display landing page with overview"""

    st.markdown(
        '<h1 class="main-header">🌊 Western Indian Ocean MPA Explorer</h1>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<p class="sub-header">Interactive visualization of Marine Protected Areas in the Western Indian Ocean region</p>',
        unsafe_allow_html=True,
    )

    # Hero image or info
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(
            """
            <div class="stat-box">
                <div class="stat-number">🗺️ 6</div>
                <div class="stat-label">Datasets</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            """
            <div class="stat-box">
                <div class="stat-number">🏝️ 58K+</div>
                <div class="stat-label">Features</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col3:
        st.markdown(
            """
            <div class="stat-box">
                <div class="stat-number">🌍 9</div>
                <div class="stat-label">Countries</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("---")

    # About section
    st.header("📖 About This Explorer")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🎯 Purpose")
        st.write(
            """
        This interactive tool allows you to explore Marine Protected Areas (MPAs) 
        across the Western Indian Ocean region. View spatial data, analyze attributes, 
        and discover patterns in marine conservation efforts.
        """
        )

        st.subheader("📊 Available Datasets")
        st.write(
            """
        - **All MPAs**: Complete collection of 368 MPAs
        - **Local MPAs**: 208 locally managed areas
        - **National MPAs**: 160 nationally managed areas
        - **LMMAs**: 421 Locally Managed Marine Areas
        - **IOC MPAs**: 78 IOC designated areas
        - **Mangroves**: 57,161 mangrove polygons (GMW 2020)
        """
        )

    with col2:
        st.subheader("🗺️ Countries Covered")
        countries = [
            "🇰🇪 Kenya",
            "🇹🇿 Tanzania",
            "🇲🇬 Madagascar",
            "🇿🇦 South Africa",
            "🇲🇿 Mozambique",
            "🇸🇨 Seychelles",
            "🇲🇺 Mauritius",
            "🇰🇲 Comoros",
            "🇫🇷 France (Territories)",
        ]
        for country in countries:
            st.write(f"• {country}")

    st.markdown("---")

    # Quick start
    st.header("🚀 Quick Start")
    st.info(
        """
    **👈 Use the sidebar** to navigate between different sections:
    - **Interactive Maps**: Explore MPAs on interactive Leaflet maps
    - **Data Explorer**: Browse and filter datasets in tabular format
    - **Statistics**: View summary statistics and charts
    - **Download Data**: Access Parquet and CSV exports
    """
    )

    # Sample map preview
    st.header("🗺️ Sample: All MPAs Overview")
    with st.spinner("Loading map preview..."):
        # Load a small sample
        gdf = load_dataset(DATASETS["All MPAs"])
        if gdf is not None:
            # Show only a sample
            sample_gdf = gdf.head(100)
            m = create_folium_map(sample_gdf, "All MPAs (Sample)", color="#3498db")
            st_folium(m, width=1200, height=500)


def interactive_maps():
    """Interactive map viewer"""

    st.header("🗺️ Interactive MPA Maps")

    # Dataset selector
    col1, col2 = st.columns([2, 1])

    with col1:
        selected_dataset = st.selectbox(
            "Select Dataset",
            list(DATASETS.keys()),
            help="Choose which MPA dataset to visualize",
        )

    with col2:
        color = st.color_picker("Pick a color", "#3498db")

    # Load and display
    dataset_path = DATASETS[selected_dataset]

    if not dataset_path.exists():
        st.error(f"Dataset not found: {dataset_path}")
        return

    with st.spinner(f"Loading {selected_dataset}..."):
        gdf = load_dataset(dataset_path)

        if gdf is None:
            st.error("Failed to load dataset")
            return

        # Display stats
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Total Features", f"{len(gdf):,}")

        with col2:
            st.metric("Columns", len(gdf.columns) - 1)

        with col3:
            geom_types = ", ".join(gdf.geometry.type.unique().tolist())
            st.metric("Geometry Types", geom_types)

        with col4:
            if "COUNTRY" in gdf.columns:
                st.metric("Countries", gdf["COUNTRY"].nunique())

        st.markdown("---")

        # Filters
        with st.expander("🔍 Filters & Options", expanded=False):
            filter_col1, filter_col2 = st.columns(2)

            with filter_col1:
                # Country filter
                if "COUNTRY" in gdf.columns:
                    countries = ["All"] + sorted(gdf["COUNTRY"].unique().tolist())
                    selected_country = st.selectbox("Filter by Country", countries)

                    if selected_country != "All":
                        gdf = gdf[gdf["COUNTRY"] == selected_country]
                        st.info(
                            f"Filtered to {len(gdf)} features in {selected_country}"
                        )

            with filter_col2:
                # Max features to display
                max_features = st.slider(
                    "Max features to display",
                    min_value=10,
                    max_value=min(1000, len(gdf)),
                    value=min(500, len(gdf)),
                    step=10,
                    help="Limit features for better performance",
                )

        # Create and display map
        st.subheader(f"Map: {selected_dataset}")

        display_gdf = gdf.head(max_features)
        m = create_folium_map(display_gdf, selected_dataset, color=color)

        st_folium(m, width=1200, height=600)

        # Show data table
        if st.checkbox("Show Data Table", value=False):
            st.subheader("Data Table")
            display_cols = [col for col in display_gdf.columns if col != "geometry"]
            st.dataframe(display_gdf[display_cols].head(100), use_container_width=True)


def data_explorer():
    """Data explorer with filtering and search"""

    st.header("📊 Data Explorer")

    # Dataset selector
    selected_dataset = st.selectbox("Select Dataset", list(DATASETS.keys()))

    dataset_path = DATASETS[selected_dataset]

    if not dataset_path.exists():
        st.error(f"Dataset not found: {dataset_path}")
        return

    with st.spinner(f"Loading {selected_dataset}..."):
        gdf = load_dataset(dataset_path)

        if gdf is None:
            st.error("Failed to load dataset")
            return

        # Remove geometry for table display
        df = gdf.drop(columns=["geometry"])

        # Search and filter
        col1, col2 = st.columns([3, 1])

        with col1:
            search_term = st.text_input("🔍 Search (searches all text columns)", "")

        with col2:
            show_rows = st.number_input(
                "Rows to display", min_value=10, max_value=1000, value=50, step=10
            )

        # Apply search
        if search_term:
            mask = df.astype(str).apply(
                lambda row: row.str.contains(search_term, case=False, na=False).any(),
                axis=1,
            )
            df = df[mask]
            st.info(f"Found {len(df)} matching records")

        # Column selector
        all_columns = df.columns.tolist()
        selected_columns = st.multiselect(
            "Select columns to display (leave empty for all)",
            all_columns,
            default=[],
        )

        if selected_columns:
            df = df[selected_columns]

        # Display table
        st.dataframe(df.head(show_rows), use_container_width=True)

        # Download button
        csv = df.to_csv(index=False)
        st.download_button(
            label="📥 Download as CSV",
            data=csv,
            file_name=f"{selected_dataset.lower().replace(' ', '_')}.csv",
            mime="text/csv",
        )

        # Summary statistics
        if st.checkbox("Show Summary Statistics"):
            st.subheader("Summary Statistics")
            st.write(df.describe())


def statistics():
    """Statistics and charts"""

    st.header("📈 Statistics & Analytics")

    # Load All MPAs dataset
    with st.spinner("Loading data..."):
        gdf = load_dataset(DATASETS["All MPAs"])

        if gdf is None:
            st.error("Failed to load dataset")
            return

        # Country breakdown
        if "COUNTRY" in gdf.columns:
            st.subheader("MPAs by Country")

            country_counts = gdf["COUNTRY"].value_counts()
            st.bar_chart(country_counts)

            # Table view
            st.dataframe(
                pd.DataFrame(
                    {
                        "Country": country_counts.index,
                        "Count": country_counts.values,
                        "Percentage": (country_counts.values / len(gdf) * 100).round(2),
                    }
                ),
                use_container_width=True,
            )

        # Status breakdown
        if "STATUS" in gdf.columns:
            st.subheader("MPAs by Status")

            status_counts = gdf["STATUS"].value_counts()
            st.bar_chart(status_counts)

        # Category breakdown
        if "CATEGORY" in gdf.columns:
            st.subheader("MPAs by Category")

            category_counts = gdf["CATEGORY"].value_counts()
            st.bar_chart(category_counts)

        # Area statistics
        if "AREAKM_ACT" in gdf.columns:
            st.subheader("MPA Area Statistics (km²)")

            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric("Total Area", f"{gdf['AREAKM_ACT'].sum():,.0f} km²")

            with col2:
                st.metric("Average Area", f"{gdf['AREAKM_ACT'].mean():,.2f} km²")

            with col3:
                st.metric("Median Area", f"{gdf['AREAKM_ACT'].median():,.2f} km²")

            with col4:
                st.metric("Largest MPA", f"{gdf['AREAKM_ACT'].max():,.0f} km²")


def downloads():
    """Downloads page"""

    st.header("📥 Download Data")

    st.write(
        """
    Download processed MPA data in various formats for your analysis.
    """
    )

    # Parquet files
    st.subheader("GeoParquet Files (with geometry)")

    parquet_dir = BASE_DIR / "parquet_exports" / "geoparquet"

    if parquet_dir.exists():
        for file in sorted(parquet_dir.glob("*.parquet")):
            size_mb = file.stat().st_size / (1024 * 1024)
            col1, col2, col3 = st.columns([3, 1, 1])

            with col1:
                st.write(f"📦 {file.name}")

            with col2:
                st.write(f"{size_mb:.2f} MB")

            with col3:
                with open(file, "rb") as f:
                    st.download_button(
                        label="Download",
                        data=f,
                        file_name=file.name,
                        mime="application/octet-stream",
                        key=f"geo_{file.name}",
                    )

    # Attribute Parquet files
    st.subheader("Attribute Tables (without geometry)")

    attr_dir = BASE_DIR / "parquet_exports" / "attributes"

    if attr_dir.exists():
        for file in sorted(attr_dir.glob("*.parquet")):
            size_kb = file.stat().st_size / 1024
            col1, col2, col3 = st.columns([3, 1, 1])

            with col1:
                st.write(f"📄 {file.name}")

            with col2:
                st.write(f"{size_kb:.1f} KB")

            with col3:
                with open(file, "rb") as f:
                    st.download_button(
                        label="Download",
                        data=f,
                        file_name=file.name,
                        mime="application/octet-stream",
                        key=f"attr_{file.name}",
                    )


def main():
    """Main app function"""

    # Sidebar navigation
    st.sidebar.title("🧭 Navigation")

    page = st.sidebar.radio(
        "Go to",
        [
            "🏠 Home",
            "🗺️ Interactive Maps",
            "📊 Data Explorer",
            "📈 Statistics",
            "📥 Downloads",
        ],
    )

    st.sidebar.markdown("---")

    st.sidebar.info(
        """
    **About**
    
    Western Indian Ocean Marine Protected Areas data explorer.
    
    **Data Sources:**
    - WIOMPA datasets
    - IOC Marine Spatial Planning
    - Global Mangrove Watch 2020
    """
    )

    # Route to appropriate page
    if page == "🏠 Home":
        landing_page()
    elif page == "🗺️ Interactive Maps":
        interactive_maps()
    elif page == "📊 Data Explorer":
        data_explorer()
    elif page == "📈 Statistics":
        statistics()
    elif page == "📥 Downloads":
        downloads()


if __name__ == "__main__":
    main()
