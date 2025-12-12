"""
Quick diagnostic script to test BigQuery connection and permissions.
Run this locally to identify issues before pushing to GitHub.
"""

import os
import json
import sys

def test_environment():
    """Test if environment variable is set."""
    print("=" * 60)
    print("🔍 STEP 1: Checking Environment Variable")
    print("=" * 60)
    
    key = os.environ.get('GCP_SERVICE_ACCOUNT_KEY')
    if not key:
        print("❌ ERROR: GCP_SERVICE_ACCOUNT_KEY environment variable not set")
        print("\nTo fix locally, run:")
        print('export GCP_SERVICE_ACCOUNT_KEY=\'$(cat /path/to/your-service-account-key.json)\'')
        return False
    
    print("✅ Environment variable is set")
    print(f"   Length: {len(key)} characters")
    
    # Try to parse JSON
    try:
        creds = json.loads(key)
        print(f"✅ Valid JSON format")
        print(f"   Project ID: {creds.get('project_id', 'NOT FOUND')}")
        print(f"   Client Email: {creds.get('client_email', 'NOT FOUND')}")
        return True
    except json.JSONDecodeError as e:
        print(f"❌ ERROR: Invalid JSON format")
        print(f"   Error: {e}")
        return False


def test_bigquery_connection():
    """Test BigQuery connection."""
    print("\n" + "=" * 60)
    print("🔍 STEP 2: Testing BigQuery Connection")
    print("=" * 60)
    
    try:
        from google.cloud import bigquery
        from google.oauth2 import service_account
        print("✅ BigQuery library imported successfully")
    except ImportError as e:
        print(f"❌ ERROR: Cannot import BigQuery library")
        print(f"   Error: {e}")
        print("\nTo fix, run:")
        print("pip install google-cloud-bigquery PyYAML")
        return False
    
    # Load config
    try:
        import yaml
        with open('config/config.yaml', 'r') as f:
            config = yaml.safe_load(f)
        print(f"✅ Config loaded")
        print(f"   Project: {config['gcp_project_id']}")
        print(f"   Dataset: {config['dataset_id']}")
    except Exception as e:
        print(f"❌ ERROR: Cannot load config")
        print(f"   Error: {e}")
        return False
    
    # Try to create client
    try:
        gcp_credentials = os.environ.get('GCP_SERVICE_ACCOUNT_KEY')
        credentials_info = json.loads(gcp_credentials)
        credentials = service_account.Credentials.from_service_account_info(credentials_info)
        client = bigquery.Client(
            credentials=credentials,
            project=config['gcp_project_id']
        )
        print("✅ BigQuery client created successfully")
    except Exception as e:
        print(f"❌ ERROR: Cannot create BigQuery client")
        print(f"   Error: {e}")
        return False
    
    # Test API access
    try:
        datasets = list(client.list_datasets())
        print(f"✅ Can access BigQuery API")
        print(f"   Found {len(datasets)} existing datasets")
        for dataset in datasets:
            print(f"     - {dataset.dataset_id}")
    except Exception as e:
        print(f"❌ ERROR: Cannot access BigQuery API")
        print(f"   Error: {e}")
        print("\n   Possible causes:")
        print("   - BigQuery API not enabled")
        print("   - Service account lacks permissions")
        print("   - Invalid project ID")
        return False
    
    # Check if target dataset exists
    dataset_id = f"{config['gcp_project_id']}.{config['dataset_id']}"
    try:
        dataset = client.get_dataset(dataset_id)
        print(f"✅ Target dataset exists: {config['dataset_id']}")
    except Exception:
        print(f"⚠️  Target dataset does not exist: {config['dataset_id']}")
        print(f"   Will be created on first deployment")
    
    return True


def main():
    print("\n🚀 BigQuery CI/CD Pipeline Diagnostic Tool\n")
    
    success = True
    
    # Test 1: Environment
    if not test_environment():
        success = False
    
    # Test 2: BigQuery connection
    if success and not test_bigquery_connection():
        success = False
    
    # Final result
    print("\n" + "=" * 60)
    if success:
        print("✅ ALL TESTS PASSED!")
        print("=" * 60)
        print("\nYour local setup is correct.")
        print("If GitHub Actions is failing, check:")
        print("1. Secret name matches: SVC_BQ_CICD")
        print("2. Secret contains the FULL JSON (including { and })")
        print("3. No extra spaces or formatting in the secret")
    else:
        print("❌ TESTS FAILED")
        print("=" * 60)
        print("\nFix the issues above before deploying to GitHub.")
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
