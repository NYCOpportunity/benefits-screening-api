# Lambda Deployment Workflow

## Overview
Automated deployment to AWS Lambda when pushing to `prod` or `stg` branches.

## Triggers (Lines 3-7)
- **Push to `prod`** → Deploys to production Lambda
- **Push to `stg`** → Deploys to staging Lambda  
- **PR to `main`** → No deployment (safety measure)

## Global Settings (Lines 9-16)
```yaml
env:
  AWS_REGION: us-east-1
  LAMBDA_FUNCTION_NAME_PROD: benefits-screening-api-prod
  LAMBDA_FUNCTION_NAME_STG: Benefits-Screening-API-stg

permissions:
  contents: read      # Read repo
  id-token: write    # AWS auth
```

## Deployment Jobs

### Production (Lines 41-143)
**Triggers**: Only on push to `prod` branch

**Steps**:
1. **Setup** (Lines 47-61)
   - Checkout code
   - Install Python 3.13
   - Install UV package manager
   - Install production dependencies only

2. **AWS Auth** (Lines 63-86)
   - Debug credentials availability
   - Configure AWS credentials from GitHub secrets

3. **Package** (Lines 88-103)
   - Create package directory
   - Export & install dependencies
   - Copy `src/` folder (preserves structure)
   - Zip everything except test files

4. **Deploy** (Lines 105-122)
   - Upload ZIP to Lambda
   - Update configuration:
     - Handler: `src.main.lambda_handler`
     - Environment: production
     - Memory: 512MB, Timeout: 30s

5. **Verify** (Lines 124-143)
   - Wait for update completion
   - Test with sample payload
   - Fail if errors detected

### Staging (Lines 145-242)
Identical structure but:
- Different Lambda name
- Environment: staging
- Memory: 256MB, Timeout: 60s
- Debug logging enabled

## Key Features
- **Test job commented out** (Lines 19-39) - can be enabled
- **Credential debugging** helps troubleshoot auth issues
- **Automatic testing** after each deployment
- **Environment-specific configs** (memory, timeout, logging)

## Required GitHub Repository Secrets
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`