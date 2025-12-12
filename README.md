# CI/CD Pipeline: GitHub to BigQuery

A simple automated pipeline that deploys data and transformations to Google BigQuery using GitHub Actions.

## 📋 What This Does

- **Automatically loads data** to BigQuery when you push to GitHub
- **Runs SQL transformations** to create reports
- **Supports two environments**: Development (`dev` branch) and Production (`main` branch)

## 🏗️ Project Structure

```
CICD-setup-Big-Query/
├── .github/workflows/
│   └── bigquery-deploy.yml    # GitHub Actions workflow
├── config/
│   ├── config-dev.yaml        # Dev environment settings
│   └── config-prod.yaml       # Prod environment settings
├── data/
│   ├── sample_data.csv        # Employee data
│   └── schemas/
│       └── table_schema.json  # BigQuery table schema
├── scripts/
│   ├── load_data.py           # Loads CSV to BigQuery
│   └── run_transformations.py # Runs SQL transformations
├── sql/
│   ├── create_tables.sql      # Creates tables
│   └── transformations.sql    # Business logic queries
└── requirements.txt           # Python dependencies
```

## 🚀 How It Works

1. **Push code** to GitHub (to `dev` or `main` branch)
2. **GitHub Actions triggers** automatically
3. **Pipeline runs**:
   - Creates BigQuery tables
   - Loads sample data
   - Runs transformations
   - Verifies results

## ⚙️ Setup (One-Time)

### 1. Google Cloud Setup
- Create a GCP project
- Enable BigQuery API
- Create a service account with BigQuery Admin role
- Download service account JSON key

### 2. GitHub Setup
- Go to your repo → Settings → Secrets and variables → Actions
- Add secret: `SVC_BQ_CICD` with your service account JSON content

### 3. Update Config Files
Edit `config/config-dev.yaml` and `config/config-prod.yaml`:
```yaml
gcp_project_id: "your-project-id"
dataset_id: "your-dataset-name"
location: "us-central1"
```

## 🌿 Working with Branches

### Development
```bash
git checkout dev
# Make changes to data, SQL, or scripts
git add .
git commit -m "Your message"
git push origin dev
```
→ Deploys to **DEV_TEST_CICD_PIPELINE** dataset

### Production
```bash
git checkout main
git merge dev
git push origin main
```
→ Deploys to **PROD_TEST_CICD_PIPELINE** dataset

## 📊 What Gets Created in BigQuery

**Tables:**
- `employees` - Raw employee data
- `department_summary` - Aggregated report by department
- `high_performers` - Employees with salary > $65,000

## 🔍 View Results

After pipeline runs successfully:
1. Go to [BigQuery Console](https://console.cloud.google.com/bigquery)
2. Select your project
3. View datasets: `DEV_TEST_CICD_PIPELINE` or `PROD_TEST_CICD_PIPELINE`
4. Query the tables

## 📝 Sample Query
```sql
SELECT * FROM `your-project.PROD_TEST_CICD_PIPELINE.department_summary`
ORDER BY avg_salary DESC;
```

## 🛠️ Troubleshooting

**Pipeline fails?**
- Check GitHub Actions logs: Go to repo → Actions tab
- Verify secret `SVC_BQ_CICD` is set correctly
- Ensure config files have correct project ID

**Tables not appearing?**
- BigQuery can take a few seconds to show new tables
- Check the pipeline logs for errors

## 📚 Key Files Explained

| File | Purpose |
|------|---------|
| `bigquery-deploy.yml` | Defines the automated workflow |
| `config-dev.yaml` | Points to dev environment |
| `config-prod.yaml` | Points to prod environment |
| `load_data.py` | Uploads CSV data to BigQuery |
| `run_transformations.py` | Executes SQL transformations |
| `create_tables.sql` | Defines table structure |
| `transformations.sql` | Business logic for reports |

## 🎯 Next Steps

1. Modify `sample_data.csv` with your own data
2. Update `transformations.sql` for your business logic
3. Push to `dev` branch to test
4. Merge to `main` when ready for production

---

**GCP Project**: vast-crow-480921-i7  
**Repository**: [CICD-setup-Big-Query](https://github.com/edlaakhilreddy12/CICD-setup-Big-Query)
