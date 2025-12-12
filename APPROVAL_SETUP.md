# 🔐 Setting Up PR Approvals and Branch Protection

## 📋 Quick Setup Guide

### Step 1: Enable Branch Protection for `main` (PROD)

1. **Go to your repository settings:**
   https://github.com/edlaakhilreddy12/CICD-setup-Big-Query/settings/branches

2. **Click "Add rule" or "Add branch protection rule"**

3. **Configure the rule:**
   - **Branch name pattern:** `main`
   - **✅ Require a pull request before merging**
     - ✅ Require approvals: `1` (or more)
     - ✅ Dismiss stale pull request approvals when new commits are pushed
     - ✅ Require review from Code Owners (optional)
   - **✅ Require status checks to pass before merging**
     - Search and add: `validate` (from your GitHub Actions)
     - This ensures tests pass before merge
   - **✅ Require branches to be up to date before merging**
   - **✅ Include administrators** (if you want rules to apply to you too)
   - **✅ Restrict who can push to matching branches** (optional)
     - Add yourself or specific team members

4. **Click "Create" or "Save changes"**

### Step 2: Enable Branch Protection for `dev` (Optional)

Repeat above steps for `dev` branch if you want approval even for dev deployments.

---

## 🔄 Workflow with Approvals

### Scenario: Making Changes

#### 1. Create Feature Branch from DEV
```bash
git checkout dev
git pull origin dev
git checkout -b feature/add-new-department
```

#### 2. Make Your Changes
```bash
# Edit files
nano data/sample_data.csv

# Commit
git add .
git commit -m "Add new department data"
git push origin feature/add-new-department
```

#### 3. Create Pull Request to DEV
1. Go to: https://github.com/edlaakhilreddy12/CICD-setup-Big-Query/pulls
2. Click "New pull request"
3. **Base:** `dev` ← **Compare:** `feature/add-new-department`
4. Click "Create pull request"
5. Add description of changes
6. **Assign reviewers** (yourself or team members)

#### 4. Review and Approve (DEV)
- Review the changes
- GitHub Actions will run automatically (validation)
- If tests pass and looks good, click "Approve" and "Merge"
- This deploys to `DEV_TEST_CICD_PIPELINE`

#### 5. Test in DEV Environment
```sql
-- Verify changes in DEV
SELECT * FROM `vast-crow-480921-i7.DEV_TEST_CICD_PIPELINE.employees`;
```

#### 6. Create Pull Request to PROD
Once DEV is verified:
1. Go to: https://github.com/edlaakhilreddy12/CICD-setup-Big-Query/pulls
2. Click "New pull request"
3. **Base:** `main` ← **Compare:** `dev`
4. Click "Create pull request"
5. Add description: "Promoting verified changes from DEV to PROD"

#### 7. Approve for PROD Deployment
- **You (or designated admin) must approve**
- GitHub Actions runs validation
- Once approved, click "Merge pull request"
- This deploys to `PROD_TEST_CICD_PIPELINE`

---

## 👥 Adding Team Members as Reviewers

### Option 1: Add Collaborators
1. Go to: https://github.com/edlaakhilreddy12/CICD-setup-Big-Query/settings/access
2. Click "Add people"
3. Enter GitHub username
4. Choose role:
   - **Admin** - Full access
   - **Write** - Can push and review
   - **Read** - View only

### Option 2: Create CODEOWNERS File (Automated Review Assignment)

I'll create a CODEOWNERS file that automatically assigns you:

```bash
# This automatically requests your review on every PR
```

---

## 🛡️ Recommended Settings

### For `main` branch (PRODUCTION):
- ✅ **Require pull request** - Can't push directly
- ✅ **Require 1 approval** - You must approve
- ✅ **Require status checks** - Tests must pass
- ✅ **Restrict who can push** - Only you or specific admins

### For `dev` branch (DEVELOPMENT):
- ✅ **Require pull request** (optional, less strict)
- ⚪ Approval optional (or require 1)
- ✅ **Require status checks** - Tests must pass

---

## 📧 Notification Settings

Make sure you get notified:
1. Go to: https://github.com/settings/notifications
2. **Email notifications:**
   - ✅ Pull requests
   - ✅ Pull request reviews
   - ✅ Comments
3. Or use GitHub mobile app for instant notifications

---

## 🎯 Example Workflow Diagram

```
Developer                    You (Admin)              Production
────────                    ────────────              ──────────

Create feature branch
     │
     ├─▶ Make changes
     │
     ├─▶ Push to GitHub
     │
     ├─▶ Create PR to dev
     │
     └─▶ Request your review ──▶ You review
                                    │
                                    ├─▶ Check changes
                                    │
                                    ├─▶ Run tests
                                    │
                                    └─▶ Approve/Request changes
                                           │
                      ┌────────────────────┘
                      │
                      ├─▶ Merge to dev
                      │
                      ├─▶ Auto-deploy to DEV dataset
                      │
                      ├─▶ Test in DEV
                      │
                      └─▶ Create PR to main
                             │
                             └─▶ You review (REQUIRED) ──▶ Approve
                                                              │
                                                              └─▶ Deploy to PROD
```

---

## 🚀 Quick Commands Reference

### For You (Admin/Reviewer):

```bash
# Fetch latest PRs
gh pr list

# Review a PR
gh pr view 1  # View PR #1
gh pr review 1 --approve -b "Looks good!"
gh pr merge 1  # Merge after approval

# Or use GitHub web interface (easier)
```

### For Team Members:

```bash
# Create feature branch
git checkout dev
git checkout -b feature/my-feature

# Make changes and push
git add .
git commit -m "My changes"
git push origin feature/my-feature

# Create PR via web:
# https://github.com/edlaakhilreddy12/CICD-setup-Big-Query/compare/dev...feature/my-feature
```

---

## ✅ Verification Steps

After setting up branch protection:

1. **Test it:**
   ```bash
   git checkout main
   echo "test" >> test.txt
   git add test.txt
   git commit -m "Test direct push"
   git push origin main
   ```
   
   **Expected:** Should be rejected! Must use PR.

2. **Correct way:**
   ```bash
   git checkout -b test-branch
   git push origin test-branch
   # Then create PR via GitHub web interface
   ```

---

## 📱 Mobile Notifications

Install **GitHub Mobile App**:
- iOS: https://apps.apple.com/app/github/id1477376905
- Android: https://play.google.com/store/apps/details?id=com.github.android

Benefits:
- Get instant PR notifications
- Review and approve PRs from phone
- Merge PRs on the go

---

## 🔒 Security Best Practices

1. **Never push directly to main** - Always use PRs
2. **Always review code** - Even your own changes
3. **Require passing tests** - Don't merge if tests fail
4. **Use meaningful commit messages** - Helps with reviews
5. **Test in DEV first** - Catch issues before PROD
6. **Keep branches up to date** - Merge main into dev regularly

---

## 🎓 Next Steps

1. ✅ Set up branch protection (do this now!)
2. ✅ Test by creating a PR
3. ✅ Add team members if needed
4. ✅ Configure notifications
5. ✅ Create a test PR to verify approval workflow

---

**Ready to set up? Go to:**
https://github.com/edlaakhilreddy12/CICD-setup-Big-Query/settings/branches

Click "Add rule" and follow the steps above!
