# 🌊 Western Indian Ocean MPA Explorer

Interactive Streamlit web application for exploring Marine Protected Areas in the Western Indian Ocean region.

## Features

- **🏠 Landing Page**: Overview and introduction to the datasets
- **🗺️ Interactive Maps**: Leaflet-based interactive maps with:
  - Multiple basemap options (OpenStreetMap, Satellite, Light/Dark themes)
  - Clickable features with detailed popups
  - Fullscreen mode
  - Distance measurement tools
  - Minimap for navigation
  - Country and feature filtering
- **📊 Data Explorer**: Browse, search, and filter datasets in tabular format
- **📈 Statistics**: Visual analytics and charts of MPA distributions
- **📥 Downloads**: Access to processed Parquet and CSV files

## Quick Start

### 1. Install Dependencies

```bash
cd "/Users/mac/Downloads/MPA Data"
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Run the App

```bash
streamlit run streamlit_app.py
```

The app will automatically open in your default browser at `http://localhost:8501`

## App Structure

### Navigation

Use the sidebar to navigate between:

1. **Home** - Landing page with overview and sample map
2. **Interactive Maps** - Full-featured map viewer with filters
3. **Data Explorer** - Table view with search and column selection
4. **Statistics** - Charts and analytics dashboard
5. **Downloads** - Access to Parquet/CSV exports

### Datasets Available

- **All MPAs** (368 features) - Complete MPA collection
- **Local MPAs** (208 features) - Locally managed areas
- **National MPAs** (160 features) - Nationally managed areas
- **LMMAs** (421 features) - Locally Managed Marine Areas
- **IOC MPAs** (78 features) - IOC designated areas
- **Mangroves** (57,161 features) - Global Mangrove Watch 2020

## Interactive Map Features

### Controls

- **Zoom**: Mouse wheel or +/- buttons
- **Pan**: Click and drag
- **Basemap**: Layer control in top-right corner
- **Fullscreen**: Expand to full screen
- **Measure**: Measure distances and areas
- **Minimap**: Overview map in bottom-right

### Filters

- Filter by country (for datasets with country information)
- Limit number of features displayed for performance
- Custom color picker for map features

### Popups

Click on any feature to view:
- MPA name
- Country
- Status
- Category
- Area
- Year established
- Management information
- And more...

## Data Explorer Features

- **Search**: Full-text search across all columns
- **Column Selection**: Choose which columns to display
- **CSV Export**: Download filtered results
- **Summary Statistics**: View numeric column statistics

## Statistics Dashboard

View analytics including:
- MPAs by country (bar chart + table)
- Status breakdown
- Category distribution
- Area statistics (total, average, median, max)

## Performance Tips

1. **Large Datasets**: The Mangroves dataset has 57K+ features
   - Use the feature limit slider to display fewer features
   - Filter by country to reduce data

2. **Browser Performance**: 
   - Use Chrome or Firefox for best performance
   - Close other browser tabs if maps are slow

3. **Data Loading**: 
   - First load may take a few seconds
   - Data is cached after initial load

## Customization

### Change Map Colors

Use the color picker in the Interactive Maps section to customize feature colors.

### Adjust Display Limits

Use the "Max features to display" slider to control how many features render on the map.

### Select Basemap

Choose from:
- OpenStreetMap (default)
- Light Map (CartoDB Positron)
- Dark Map (CartoDB Dark Matter)
- Satellite Imagery (ESRI)

## Troubleshooting

### Port Already in Use

If port 8501 is in use:

```bash
streamlit run streamlit_app.py --server.port 8502
```

### Map Not Displaying

1. Check internet connection (basemaps require internet)
2. Try refreshing the page
3. Clear browser cache

### Data Not Loading

1. Ensure shapefiles are in correct directories
2. Check file permissions
3. Verify virtual environment is activated

## Technical Details

### Tech Stack

- **Frontend**: Streamlit
- **Maps**: Folium (Leaflet.js wrapper)
- **GIS**: GeoPandas, Shapely
- **Data**: Pandas, PyArrow

### Data Flow

1. Shapefiles loaded with GeoPandas
2. Reprojected to WGS84 (EPSG:4326) for Leaflet
3. Cached for performance
4. Rendered as GeoJSON on Folium maps

### File Locations

- **Shapefiles**: Various subdirectories in MPA Data/
- **Parquet exports**: `parquet_exports/`
- **Maps (images)**: `maps/`
- **Attribute summaries**: `attribute_summaries/`
- **Record views**: `record_views/`

## Data Sources

- WIOMPA (Western Indian Ocean Marine Protected Areas)
- IOC Marine Spatial Planning Initiative
- Global Mangrove Watch 2020

## License

Data provided for research and conservation purposes.

## Support

For issues or questions, refer to the dataset documentation or contact the data providers.

