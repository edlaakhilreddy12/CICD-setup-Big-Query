# 🔄 Multi-Environment CI/CD Workflow Guide

## 📚 Overview

This project uses a **two-environment** setup:
- **DEV (Development)**: For testing changes safely
- **PROD (Production)**: For stable, production-ready code

## 🌲 Branch Strategy

```
main (PROD)
  │
  └─── dev (DEV)
         │
         └─── feature branches
```

### Branches:
- **`main`** → Production environment → `PROD_TEST_CICD_PIPELINE` dataset
- **`dev`** → Development environment → `DEV_TEST_CICD_PIPELINE` dataset

## 🚀 Typical Workflow

### Step 1: Make Changes in DEV Branch

```bash
# Switch to dev branch (or create it)
git checkout -b dev

# Make your changes (edit data, SQL, scripts, etc.)
# ...

# Commit your changes
git add .
git commit -m "Add new employee data"

# Push to dev branch (triggers DEV deployment)
git push origin dev
```

**This deploys to:** `DEV_TEST_CICD_PIPELINE` dataset in BigQuery

### Step 2: Test in DEV

1. Go to GitHub Actions and verify deployment succeeded
2. Check BigQuery development dataset:
   ```sql
   SELECT * FROM `vast-crow-480921-i7.DEV_TEST_CICD_PIPELINE.employees`;
   ```
3. Verify data looks correct
4. Test queries and transformations

### Step 3: Promote to PROD

Once you're confident the changes work:

```bash
# Switch to main branch
git checkout main

# Merge dev into main
git merge dev

# Push to main (triggers PROD deployment)
git push origin main
```

**This deploys to:** `PROD_TEST_CICD_PIPELINE` dataset in BigQuery

## 📊 Environment Configurations

### Development (dev branch)
- **Config file:** `config/config-dev.yaml`
- **Dataset:** `DEV_TEST_CICD_PIPELINE`
- **Purpose:** Testing and experimentation

### Production (main branch)
- **Config file:** `config/config-prod.yaml`
- **Dataset:** `PROD_TEST_CICD_PIPELINE`
- **Purpose:** Stable, production data

## 🔧 Setup Instructions

### 1. Create the DEV branch

```bash
cd "/Users/akhilreddy/Documents/CICD pipeline/CICD-setup-Big-Query"

# Create and switch to dev branch
git checkout -b dev

# Push to create remote dev branch
git push -u origin dev
```

### 2. Configure Branch Protection (Optional but Recommended)

Go to: https://github.com/edlaakhilreddy12/CICD-setup-Big-Query/settings/branches

**For `main` branch:**
- ✅ Require pull request before merging
- ✅ Require status checks to pass (so dev must deploy successfully first)

This ensures you can't accidentally push broken code to production!

## 📝 Making Changes

### Option A: Direct to DEV (Quick Changes)

```bash
git checkout dev
# Make changes
git add .
git commit -m "Update data"
git push origin dev
# → Deploys to DEV automatically
```

### Option B: Feature Branch → DEV → PROD (Recommended)

```bash
# Create feature branch from dev
git checkout dev
git checkout -b feature/new-department

# Make changes
# ...

# Commit changes
git add .
git commit -m "Add new department data"

# Push feature branch
git push origin feature/new-department

# Create Pull Request: feature/new-department → dev
# Review, approve, merge
# → Deploys to DEV automatically

# Then create Pull Request: dev → main
# Review, approve, merge
# → Deploys to PROD automatically
```

## 🎯 What Happens When You Push

### Push to `dev` branch:
```
Push → GitHub Actions → Deploy → DEV_TEST_CICD_PIPELINE
```

### Push to `main` branch:
```
Push → GitHub Actions → Deploy → PROD_TEST_CICD_PIPELINE
```

## 📋 Verification

### After DEV Deployment:
```sql
-- Check DEV data
SELECT COUNT(*) FROM `vast-crow-480921-i7.DEV_TEST_CICD_PIPELINE.employees`;
SELECT * FROM `vast-crow-480921-i7.DEV_TEST_CICD_PIPELINE.department_summary`;
```

### After PROD Deployment:
```sql
-- Check PROD data
SELECT COUNT(*) FROM `vast-crow-480921-i7.PROD_TEST_CICD_PIPELINE.employees`;
SELECT * FROM `vast-crow-480921-i7.PROD_TEST_CICD_PIPELINE.department_summary`;
```

## 🔒 Best Practices

1. **Always test in DEV first**
   - Never push directly to main
   - Validate all changes in DEV environment

2. **Use Pull Requests**
   - Create PR from dev → main
   - Review changes before merging
   - Ensures code quality

3. **Keep environments in sync**
   - Regularly merge main back to dev
   - Prevents divergence

4. **Document changes**
   - Write clear commit messages
   - Update documentation as needed

## 🚨 Emergency Rollback

If something goes wrong in PROD:

```bash
# Option 1: Revert the commit
git checkout main
git revert HEAD
git push origin main

# Option 2: Reset to previous commit
git checkout main
git reset --hard HEAD~1
git push origin main --force

# Option 3: Restore from DEV
git checkout main
git merge dev --strategy-option theirs
git push origin main
```

## 📊 Monitoring

Monitor deployments at:
- **All runs:** https://github.com/edlaakhilreddy12/CICD-setup-Big-Query/actions
- **Dev deployments:** Filter by `dev` branch
- **Prod deployments:** Filter by `main` branch

## 🎓 Quick Reference

```bash
# Create dev branch (one-time setup)
git checkout -b dev
git push -u origin dev

# Work on dev
git checkout dev
# make changes
git add .
git commit -m "Your message"
git push origin dev

# Promote to prod
git checkout main
git merge dev
git push origin main

# Sync main changes back to dev
git checkout dev
git merge main
git push origin dev
```

## ✅ Checklist for First Setup

- [ ] Create `dev` branch
- [ ] Push initial commit to `dev`
- [ ] Verify DEV deployment works
- [ ] Check `DEV_TEST_CICD_PIPELINE` dataset exists
- [ ] Merge to `main` when ready
- [ ] Verify PROD deployment works
- [ ] Check `PROD_TEST_CICD_PIPELINE` dataset exists
- [ ] Set up branch protection rules (optional)

---

**You're now ready to use the dev/prod workflow!** 🎉
