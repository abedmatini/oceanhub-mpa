#!/bin/zsh
#
# Upload MPA Parquet data to GCS and load into BigQuery
# Usage: ./upload_to_bigquery.sh PROJECT_ID BUCKET_NAME DATASET_NAME
#

set -e

# Check arguments
if [ "$#" -ne 3 ]; then
    echo "Usage: $0 PROJECT_ID BUCKET_NAME DATASET_NAME"
    echo "Example: $0 my-project my-mpa-bucket mpa_data"
    exit 1
fi

PROJECT_ID=$1
BUCKET_NAME=$2
DATASET_NAME=$3
GCS_PATH="gs://${BUCKET_NAME}/mpa_data"

echo "=========================================="
echo "MPA Data Upload to BigQuery"
echo "=========================================="
echo "Project: ${PROJECT_ID}"
echo "Bucket: ${BUCKET_NAME}"
echo "Dataset: ${DATASET_NAME}"
echo "=========================================="

# Set project
echo "\n[1/4] Setting GCP project..."
gcloud config set project ${PROJECT_ID}

# Create bucket if it doesn't exist
echo "\n[2/4] Checking/creating GCS bucket..."
if ! gsutil ls -b gs://${BUCKET_NAME} &>/dev/null; then
    echo "Creating bucket ${BUCKET_NAME}..."
    gsutil mb -p ${PROJECT_ID} gs://${BUCKET_NAME}
else
    echo "Bucket ${BUCKET_NAME} already exists"
fi

# Upload GeoParquet files to GCS
echo "\n[3/4] Uploading Parquet files to GCS..."
gsutil -m cp parquet_exports/geoparquet/*.parquet ${GCS_PATH}/geoparquet/
gsutil -m cp parquet_exports/attributes/*.parquet ${GCS_PATH}/attributes/

echo "✓ Files uploaded to ${GCS_PATH}"

# Create BigQuery dataset if it doesn't exist
echo "\n[4/4] Creating BigQuery dataset and loading tables..."
bq mk --dataset --location=US ${PROJECT_ID}:${DATASET_NAME} 2>/dev/null || echo "Dataset already exists"

# Load each GeoParquet file into BigQuery
echo "\nLoading GeoParquet tables (with geometry)..."
for file in parquet_exports/geoparquet/*.parquet; do
    filename=$(basename "$file" .parquet)
    table_id="${PROJECT_ID}:${DATASET_NAME}.${filename}"
    gcs_uri="${GCS_PATH}/geoparquet/$(basename $file)"
    
    echo "  Loading ${filename}..."
    
    # Try to load, continue on error
    if bq load --replace \
        --source_format=PARQUET \
        --autodetect \
        ${table_id} \
        ${gcs_uri} 2>&1; then
        echo "  ✓ ${filename}"
    else
        echo "  ✗ ${filename} - FAILED (likely invalid geometry, check attributes table)"
    fi
done

# Load attribute-only tables
echo "\nLoading attribute tables (without geometry)..."
for file in parquet_exports/attributes/*.parquet; do
    filename=$(basename "$file" .parquet)
    table_id="${PROJECT_ID}:${DATASET_NAME}.${filename}_attrs"
    gcs_uri="${GCS_PATH}/attributes/$(basename $file)"
    
    echo "  Loading ${filename}_attrs..."
    bq load --replace \
        --source_format=PARQUET \
        --autodetect \
        ${table_id} \
        ${gcs_uri}
    
    echo "  ✓ ${filename}_attrs"
done

echo "\n=========================================="
echo "✓ SUCCESS - All data loaded!"
echo "=========================================="
echo "\nBigQuery Dataset: ${PROJECT_ID}:${DATASET_NAME}"
echo "\nTables created:"
echo "  GeoParquet (with geometry):"
bq ls ${DATASET_NAME} | grep -v "_attrs" | grep -v "tableId"
echo "\n  Attributes only:"
bq ls ${DATASET_NAME} | grep "_attrs"

echo "\n=========================================="
echo "Next Steps for Looker:"
echo "=========================================="
echo "1. Go to Looker: https://looker.cloud.google.com"
echo "2. Add BigQuery connection to: ${PROJECT_ID}"
echo "3. Create a new LookML model for dataset: ${DATASET_NAME}"
echo "4. For maps, use the geometry columns from GeoParquet tables"
echo "=========================================="

