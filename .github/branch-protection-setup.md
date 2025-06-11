# GitHub Branch Protection Setup

## Steps to Protect Main Branch:

1. Go to: **Settings** → **Branches** → **Add rule**

2. **Branch name pattern**: `main`

3. **Enable these settings**:
   - ✅ **Require a pull request before merging**
     - ✅ Require approvals: 1
     - ✅ Dismiss stale reviews when new commits are pushed
   - ✅ **Require status checks to pass before merging**
     - ✅ Require branches to be up to date before merging
     - Add status checks: `ci-cd` (from your GitHub Actions)
   - ✅ **Require conversation resolution before merging**
   - ✅ **Include administrators** (prevents you from bypassing rules)

4. **Save changes**

## Result:
- ❌ No direct pushes to `main` allowed
- ✅ Only PR merges allowed
- ✅ CI/CD must pass before merge
- ✅ Code review required 