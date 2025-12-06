# -*- coding: utf-8 -*-
"""
Created on Sun Nov  9 16:18:05 2025

@author: User
"""

from elasticsearch import Elasticsearch, helpers
import pandas as pd
import sys

# Configuration
ES_HOST = "http://localhost:9200"
INDEX_NAME = "cv-transcriptions"
CSV_FILE = "../common_voice/cv-valid-dev.csv"


def test_connection(es):
    """Test Elasticsearch connection"""
    print("Testing Elasticsearch connection...")
    try:
        info = es.info()
        print("Connected to Elasticsearch")
        print(f"Cluster: {info['cluster_name']}")
        print(f"Version: {info['version']['number']}")
        return True
    except Exception as e:
        print(f"✗ Connection failed: {e}")
        return False


def create_index(es):
    """Create Elasticsearch index with proper mappings"""
    index_mapping = {
        "mappings": {
            "properties": {
                "filename": {"type": "keyword"},
                "text": {"type": "text"},
                "generated_text": {
                    "type": "text",
                    "fields": {"keyword": {"type": "keyword"}},
                },
                "duration": {"type": "float"},
                "age": {"type": "keyword"},
                "gender": {"type": "keyword"},
                "accent": {"type": "keyword"},
            }
        }
    }

    try:
        # Delete index if it exists
        if es.indices.exists(index=INDEX_NAME):
            es.indices.delete(index=INDEX_NAME)
            print(f"Deleted existing index: {INDEX_NAME}")

        # Create new index
        es.indices.create(index=INDEX_NAME, body=index_mapping)
        print(f"Created index: {INDEX_NAME}")
        return True
    except Exception as e:
        print(f"Error creating index: {e}")
        return False


def generate_docs(df):
    """Generator function to yield documents for bulk indexing"""
    import math
    
    for idx, row in df.iterrows():
        # Handle missing or NaN values for duration (numeric field)
        duration_val = row.get("duration", None)
        if pd.isna(duration_val) or duration_val == '' or (isinstance(duration_val, float) and math.isnan(duration_val)):
            duration_val = None  # Use None instead of NaN
        else:
            try:
                duration_val = float(duration_val)
            except (ValueError, TypeError):
                duration_val = None
        
        # Handle string fields - convert NaN/nan to empty string or None
        def clean_string(value):
            if pd.isna(value) or str(value).lower() == 'nan':
                return ""  # or use None if you prefer
            return str(value)

        doc = {
            "_index": INDEX_NAME,
            "_id": str(idx),
            "_source": {
                "filename": clean_string(row.get("filename", "")),
                "text": clean_string(row.get("text", "")),
                "generated_text": clean_string(row.get("generated_text", "")),
                "duration": duration_val,  # Can be None
                "age": clean_string(row.get("age", "")),
                "gender": clean_string(row.get("gender", "")),
                "accent": clean_string(row.get("accent", "")),
            },
        }
        yield doc


def main():
    print("=" * 50)
    print("Elasticsearch Indexing Script")
    print("=" * 50)

    # Connect to Elasticsearch
    print(f"\n1. Connecting to Elasticsearch at {ES_HOST}...")
    try:
        es = Elasticsearch([ES_HOST], request_timeout=30)
    except Exception as e:
        print(f"Failed to create Elasticsearch client: {e}")
        sys.exit(1)

    # Test connection (using info() instead of ping())
    if not test_connection(es):
        sys.exit(1)

    # Create index
    print(f"\n2. Creating index '{INDEX_NAME}'...")
    if not create_index(es):
        sys.exit(1)

    # Load CSV
    print(f"\n3. Loading CSV from {CSV_FILE}...")
    try:
        df = pd.read_csv(CSV_FILE)
        print(f"Loaded {len(df)} records")

        # Show a sample of the data
        print("\nSample data:")
        print(df.head(2))
        print(f"\nColumns: {list(df.columns)}")

    except FileNotFoundError:
        print(f"CSV file not found: {CSV_FILE}")
        print("Please make sure cv-valid-dev.csv exists in the correct location")
        sys.exit(1)
    except Exception as e:
        print(f"Error loading CSV: {e}")
        sys.exit(1)

    # Bulk index documents
    print("\n4. Indexing documents...")
    try:
        success_count = 0
        error_count = 0
        errors_sample = []  # ADD THIS LINE

        # Use bulk helper with error handling
        for ok, response in helpers.streaming_bulk(
            es,  # This es is from line ~70 where you created the client
            generate_docs(df),
            chunk_size=500,
            request_timeout=60,
            raise_on_error=False,
        ):
            if ok:
                success_count += 1
            else:
                error_count += 1
                # ADD THESE LINES
                if len(errors_sample) < 5:
                    errors_sample.append(response)

            # Show progress every 500 documents
            if (success_count + error_count) % 500 == 0:
                print(f"Progress: {success_count} successful, {error_count} failed")

        print("    Indexing complete!")
        print(f"   Successfully indexed: {success_count}")
        print(f"   Failed: {error_count}")
        
        # ADD THIS SECTION
        if errors_sample:
            print("\n   Sample errors:")
            for i, error in enumerate(errors_sample[:3], 1):
                print(f"   Error {i}: {error}")

    except Exception as e:
        print(f"Error during bulk indexing: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()