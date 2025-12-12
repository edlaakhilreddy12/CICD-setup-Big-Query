# 🏛️ Pipeline Architecture

## System Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         DEVELOPER                                │
│                                                                   │
│  Make changes to:                                                │
│  • data/sample_data.csv                                          │
│  • sql/*.sql                                                     │
│  • scripts/*.py                                                  │
│  • config/*.yaml                                                 │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     │ git push origin dev/main
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│                         GITHUB                                   │
│                                                                   │
│  Repository: CICD-setup-Big-Query                                │
│  Branches:                                                       │
│  • dev  → Triggers DEV deployment                               │
│  • main → Triggers PROD deployment                              │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     │ Webhook trigger
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│                    GITHUB ACTIONS                                │
│                                                                   │
│  Workflow: bigquery-deploy.yml                                   │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  Step 1: Checkout Code                                   │   │
│  │  • Clone repository                                      │   │
│  │  • Detect branch (dev or main)                          │   │
│  └─────────────────────────────────────────────────────────┘   │
│                         │                                        │
│                         ▼                                        │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  Step 2: Setup Environment                               │   │
│  │  • Install Python 3.10                                   │   │
│  │  • Install dependencies (google-cloud-bigquery, PyYAML) │   │
│  │  • Authenticate with GCP service account                │   │
│  └─────────────────────────────────────────────────────────┘   │
│                         │                                        │
│                         ▼                                        │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  Step 3: Validate                                        │   │
│  │  • Check required files exist                           │   │
│  │  • Verify config files are valid                        │   │
│  └─────────────────────────────────────────────────────────┘   │
│                         │                                        │
│                         ▼                                        │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  Step 4: Deploy                                          │   │
│  │  • Create tables (create_tables.sql)                    │   │
│  │  • Load data (load_data.py)                             │   │
│  │  • Run transformations (run_transformations.py)         │   │
│  └─────────────────────────────────────────────────────────┘   │
│                         │                                        │
│                         ▼                                        │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  Step 5: Verify                                          │   │
│  │  • Check tables exist                                    │   │
│  │  • Run test queries                                      │   │
│  │  • Validate data loaded correctly                       │   │
│  └─────────────────────────────────────────────────────────┘   │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     │ API calls with service account
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│                   GOOGLE CLOUD (BigQuery)                        │
│                                                                   │
│  Project: vast-crow-480921-i7                                    │
│                                                                   │
│  ┌──────────────────────────┐  ┌──────────────────────────┐    │
│  │   DEV Environment        │  │   PROD Environment       │    │
│  │                          │  │                          │    │
│  │  Dataset:                │  │  Dataset:                │    │
│  │  DEV_TEST_CICD_PIPELINE  │  │  PROD_TEST_CICD_PIPELINE │    │
│  │                          │  │                          │    │
│  │  Tables:                 │  │  Tables:                 │    │
│  │  • employees             │  │  • employees             │    │
│  │  • department_summary    │  │  • department_summary    │    │
│  │  • high_performers       │  │  • high_performers       │    │
│  └──────────────────────────┘  └──────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
```

## Environment Routing

| Branch | Config File | BigQuery Dataset |
|--------|-------------|------------------|
| `dev` | `config-dev.yaml` | `DEV_TEST_CICD_PIPELINE` |
| `main` | `config-prod.yaml` | `PROD_TEST_CICD_PIPELINE` |

## Authentication Flow

```
GitHub Secret (SVC_BQ_CICD)
         │
         │ Contains service account JSON
         ▼
GitHub Actions Runner
         │
         │ Authenticates
         ▼
Google Cloud BigQuery API
         │
         │ Performs operations
         ▼
   BigQuery Datasets
```

## Pipeline Execution Steps

```
1. CREATE TABLES
   ├─ Read: sql/create_tables.sql
   ├─ Execute: CREATE TABLE IF NOT EXISTS employees
   └─ Result: Empty table structure ready

2. LOAD DATA
   ├─ Read: data/sample_data.csv
   ├─ Read: data/schemas/table_schema.json
   ├─ Execute: load_data.py
   └─ Result: Data inserted into employees table

3. TRANSFORM DATA
   ├─ Read: sql/transformations.sql
   ├─ Execute: run_transformations.py
   ├─ Create: department_summary (aggregation)
   ├─ Create: high_performers (filter)
   └─ Result: Business reports generated

4. VERIFY
   ├─ Query: SELECT COUNT(*) FROM employees
   ├─ Query: SELECT COUNT(*) FROM department_summary
   └─ Result: Validation passed ✓
```

## Data Flow

```
CSV File (sample_data.csv)
         │
         │ 10 employee records
         ▼
 BigQuery: employees table
         │
         │ SQL transformations
         ▼
    ┌────────┴────────┐
    ▼                 ▼
department_summary  high_performers
    │                 │
    │ 4 departments   │ 5 high earners
    ▼                 ▼
   Ready for analysis
```

## Key Components

### 1. GitHub Actions Workflow
- **File**: `.github/workflows/bigquery-deploy.yml`
- **Trigger**: Push to `dev` or `main` branch
- **Runtime**: ~2-3 minutes per run

### 2. Python Scripts
- **load_data.py**: Handles CSV → BigQuery upload
- **run_transformations.py**: Executes SQL and verifies results

### 3. Configuration
- **config-dev.yaml**: Development environment settings
- **config-prod.yaml**: Production environment settings

### 4. SQL Files
- **create_tables.sql**: DDL for table creation
- **transformations.sql**: DML for data transformation

## Security

```
Service Account Key
         │
         │ Stored as GitHub Secret
         │ (encrypted at rest)
         ▼
Only accessible during
  workflow execution
         │
         │ Never exposed in logs
         ▼
Temporary credentials
   (expires after job)
```

## Best Practices Implemented

✅ **Separate environments** - Dev and Prod isolated  
✅ **Automated validation** - Checks before deployment  
✅ **Idempotent operations** - Safe to run multiple times  
✅ **Error handling** - Graceful failures with logs  
✅ **Secure secrets** - No credentials in code  
✅ **Version controlled** - All changes tracked in Git

---

**Last Updated**: December 2025
