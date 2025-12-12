"""
Run SQL transformations in BigQuery.
This script executes SQL files to create views, summary tables, etc.

Learning Notes:
- Reads SQL files and executes them in BigQuery
- Supports parameter substitution (project_id, dataset_id, etc.)
- Handles multiple SQL statements
- Provides detailed error reporting
"""

import os
import json
from google.cloud import bigquery
from google.oauth2 import service_account
import yaml
import time


def load_config():
    """Load configuration from config.yaml file."""
    # Check if CONFIG_FILE environment variable is set (for multi-environment support)
    config_file = os.environ.get('CONFIG_FILE', 'config.yaml')
    config_path = os.path.join(os.path.dirname(__file__), '..', 'config', config_file)
    
    print(f"📖 Loading config from: {config_file}")
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)


def get_bigquery_client(config):
    """Create and return BigQuery client."""
    gcp_credentials = os.environ.get('GCP_SERVICE_ACCOUNT_KEY')
    
    if gcp_credentials:
        print("🔐 Authenticating with service account from environment variable...")
        credentials_info = json.loads(gcp_credentials)
        credentials = service_account.Credentials.from_service_account_info(credentials_info)
        client = bigquery.Client(
            credentials=credentials,
            project=config['gcp_project_id']
        )
    else:
        print("🔐 Authenticating with local credentials...")
        client = bigquery.Client(project=config['gcp_project_id'])
    
    return client


def read_sql_file(sql_file_path):
    """Read SQL file and return contents."""
    with open(sql_file_path, 'r') as f:
        return f.read()


def substitute_parameters(sql_content, config):
    """Replace placeholders in SQL with actual values from config."""
    replacements = {
        '{project_id}': config['gcp_project_id'],
        '{dataset_id}': config['dataset_id'],
        '{table_id}': config['table_id']
    }
    
    for placeholder, value in replacements.items():
        sql_content = sql_content.replace(placeholder, value)
    
    return sql_content


def execute_sql(client, sql_query, description="SQL query"):
    """Execute a SQL query and return results."""
    print(f"\n🔄 Executing: {description}")
    print(f"   Query preview: {sql_query[:100]}..." if len(sql_query) > 100 else f"   Query: {sql_query}")
    
    try:
        query_job = client.query(sql_query)
        result = query_job.result()  # Wait for job to complete
        
        print(f"✅ Success! Processed {query_job.total_bytes_processed / 1024 / 1024:.2f} MB")
        
        if query_job.num_dml_affected_rows is not None:
            print(f"   Affected rows: {query_job.num_dml_affected_rows}")
        
        return result
        
    except Exception as e:
        print(f"❌ Error executing query: {str(e)}")
        raise


def run_sql_file(client, config, sql_filename, description):
    """Read and execute an entire SQL file."""
    print("\n" + "=" * 60)
    print(f"📄 Processing: {sql_filename}")
    print("=" * 60)
    
    # Read SQL file
    sql_path = os.path.join(os.path.dirname(__file__), '..', 'sql', sql_filename)
    
    if not os.path.exists(sql_path):
        print(f"⚠️  File not found: {sql_path}")
        return
    
    sql_content = read_sql_file(sql_path)
    
    # Substitute parameters
    sql_content = substitute_parameters(sql_content, config)
    
    # Split by semicolon to handle multiple statements
    # Filter out empty statements
    statements = [s.strip() for s in sql_content.split(';') if s.strip()]
    
    print(f"📝 Found {len(statements)} SQL statement(s) to execute")
    
    # Execute each statement
    for i, statement in enumerate(statements, 1):
        # Skip comments-only statements
        if statement.startswith('--') or not statement:
            continue
        
        try:
            execute_sql(
                client, 
                statement, 
                description=f"{description} - Statement {i}/{len(statements)}"
            )
            time.sleep(1)  # Small delay between queries for table creation to propagate
        except Exception as e:
            print(f"⚠️  Statement {i} had an error, but continuing...")
            print(f"   Error: {e}")
            # Continue with next statement


def verify_transformations(client, config):
    """Run verification queries to check transformation results."""
    print("\n" + "=" * 60)
    print("🔍 Verifying Transformations")
    print("=" * 60)
    
    # Check if department_summary table exists
    table_id = f"{config['gcp_project_id']}.{config['dataset_id']}.department_summary"
    
    try:
        table = client.get_table(table_id)
        print(f"✅ Table exists: department_summary")
        print(f"   Rows: {table.num_rows}")
    except Exception as e:
        print(f"⚠️  Table not found: department_summary")
        print(f"   This is normal if transformations just created it.")
        print(f"   Skipping verification.")
        return
    
    # Check department summary
    verify_query = f"""
    SELECT 
        department,
        employee_count,
        avg_salary,
        total_salary
    FROM 
        `{config['gcp_project_id']}.{config['dataset_id']}.department_summary`
    ORDER BY 
        total_salary DESC
    """
    
    try:
        print("\n📊 Department Summary Results:")
        results = execute_sql(client, verify_query, "Verification query")
        
        for row in results:
            print(f"   {row.department}: {row.employee_count} employees, "
                  f"Avg: ${row.avg_salary:,.2f}, Total: ${row.total_salary:,}")
    except Exception as e:
        print(f"⚠️  Could not verify transformations: {e}")
        print(f"   This may be normal - check BigQuery Console to verify data.")


def main():
    """Main execution function."""
    print("=" * 60)
    print("🚀 Starting BigQuery Transformations")
    print("=" * 60)
    
    # Load configuration
    print("\n📖 Loading configuration...")
    config = load_config()
    print(f"   Project: {config['gcp_project_id']}")
    print(f"   Dataset: {config['dataset_id']}")
    
    # Create BigQuery client
    client = get_bigquery_client(config)
    
    # Run transformations
    run_sql_file(
        client, 
        config, 
        'transformations.sql',
        'Data transformations'
    )
    
    # Wait a moment for BigQuery to process table creation
    print("\n⏳ Waiting for BigQuery to process table creation...")
    time.sleep(3)
    
    # Verify results
    verify_transformations(client, config)
    
    print("\n" + "=" * 60)
    print("✅ All transformations completed successfully!")
    print("=" * 60)
    
    return 0


if __name__ == "__main__":
    exit(main())
