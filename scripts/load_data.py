"""
Load data from CSV files into BigQuery tables.
This script is executed by the CI/CD pipeline.

Learning Notes:
- Uses google-cloud-bigquery library to interact with BigQuery
- Reads configuration from config.yaml
- Handles authentication automatically in GitHub Actions
- Supports schema auto-detection or explicit schema definition
"""

import os
import json
from google.cloud import bigquery
from google.oauth2 import service_account
import yaml


def load_config():
    """Load configuration from config.yaml file."""
    config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'config.yaml')
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)


def get_bigquery_client(config):
    """
    Create and return BigQuery client.
    
    In GitHub Actions: Uses service account from environment variable
    Locally: Uses GOOGLE_APPLICATION_CREDENTIALS environment variable
    """
    # Check if running in GitHub Actions (service account JSON in env var)
    gcp_credentials = os.environ.get('GCP_SERVICE_ACCOUNT_KEY')
    
    if gcp_credentials:
        # Running in GitHub Actions
        print("🔐 Authenticating with service account from environment variable...")
        credentials_info = json.loads(gcp_credentials)
        credentials = service_account.Credentials.from_service_account_info(credentials_info)
        client = bigquery.Client(
            credentials=credentials,
            project=config['gcp_project_id']
        )
    else:
        # Running locally - uses GOOGLE_APPLICATION_CREDENTIALS
        print("🔐 Authenticating with local credentials...")
        client = bigquery.Client(project=config['gcp_project_id'])
    
    return client


def create_dataset_if_not_exists(client, config):
    """Create BigQuery dataset if it doesn't exist."""
    dataset_id = f"{config['gcp_project_id']}.{config['dataset_id']}"
    
    try:
        client.get_dataset(dataset_id)
        print(f"✅ Dataset {dataset_id} already exists")
    except Exception:
        print(f"📦 Creating dataset {dataset_id}...")
        dataset = bigquery.Dataset(dataset_id)
        dataset.location = config['location']
        dataset.description = "Dataset created by CI/CD pipeline"
        client.create_dataset(dataset)
        print(f"✅ Dataset {dataset_id} created successfully")


def load_table_schema(schema_file):
    """Load BigQuery table schema from JSON file."""
    schema_path = os.path.join(
        os.path.dirname(__file__), 
        '..', 
        'data', 
        'schemas', 
        schema_file
    )
    
    with open(schema_path, 'r') as f:
        schema_json = json.load(f)
    
    # Convert JSON schema to BigQuery SchemaField objects
    schema = []
    for field in schema_json:
        schema.append(
            bigquery.SchemaField(
                name=field['name'],
                field_type=field['type'],
                mode=field.get('mode', 'NULLABLE'),
                description=field.get('description', '')
            )
        )
    
    return schema


def load_data_to_bigquery(client, config):
    """Load CSV data into BigQuery table."""
    
    # Define table reference
    table_id = f"{config['gcp_project_id']}.{config['dataset_id']}.{config['table_id']}"
    
    # Load schema
    print(f"📋 Loading schema from {config['schema_file']}...")
    schema = load_table_schema(config['schema_file'])
    
    # Configure load job
    job_config = bigquery.LoadJobConfig(
        source_format=bigquery.SourceFormat.CSV,
        skip_leading_rows=1,  # Skip header row
        schema=schema,
        write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,  # Replace existing data
        # Other options:
        # WRITE_APPEND - add to existing data
        # WRITE_EMPTY - only write if table is empty
    )
    
    # Path to CSV file
    csv_path = os.path.join(
        os.path.dirname(__file__), 
        '..', 
        'data', 
        config['data_file']
    )
    
    print(f"📤 Loading data from {config['data_file']} to {table_id}...")
    
    # Load data
    with open(csv_path, 'rb') as source_file:
        load_job = client.load_table_from_file(
            source_file,
            table_id,
            job_config=job_config
        )
    
    # Wait for job to complete
    load_job.result()
    
    # Get the loaded table
    table = client.get_table(table_id)
    
    print(f"✅ Loaded {table.num_rows} rows into {table_id}")
    print(f"📊 Table size: {table.num_bytes / 1024 / 1024:.2f} MB")
    
    return table


def main():
    """Main execution function."""
    print("=" * 60)
    print("🚀 Starting BigQuery Data Load Process")
    print("=" * 60)
    
    # Load configuration
    print("\n📖 Loading configuration...")
    config = load_config()
    print(f"   Project: {config['gcp_project_id']}")
    print(f"   Dataset: {config['dataset_id']}")
    print(f"   Table: {config['table_id']}")
    print(f"   Location: {config['location']}")
    
    # Create BigQuery client
    client = get_bigquery_client(config)
    
    # Create dataset if needed
    print("\n📦 Checking dataset...")
    create_dataset_if_not_exists(client, config)
    
    # Load data
    print("\n📥 Loading data to BigQuery...")
    table = load_data_to_bigquery(client, config)
    
    print("\n" + "=" * 60)
    print("✅ Data load completed successfully!")
    print("=" * 60)
    
    return 0


if __name__ == "__main__":
    exit(main())
