# Google Cloud Run Deployment Setup

This guide will help you set up Google Cloud Run deployment for the Taksha Flow backend using GitHub Actions.

## Prerequisites

- Google Cloud Platform (GCP) account
- GitHub repository with admin access
- `gcloud` CLI installed (optional, for local setup)

## Step 1: Set Up Google Cloud Project

### 1.1 Create or Select a Project

```bash
# Create a new project
gcloud projects create YOUR_PROJECT_ID --name="Taksha Flow"

# Or list existing projects
gcloud projects list

# Set the project
gcloud config set project YOUR_PROJECT_ID
```

### 1.2 Enable Required APIs

```bash
# Enable Cloud Run API
gcloud services enable run.googleapis.com

# Enable Artifact Registry API (for Docker images)
gcloud services enable artifactregistry.googleapis.com

# Enable Cloud Build API
gcloud services enable cloudbuild.googleapis.com
```

## Step 2: Create Artifact Registry Repository

```bash
# Create a Docker repository in Artifact Registry
gcloud artifacts repositories create taksha-flow \
  --repository-format=docker \
  --location=us-central1 \
  --description="Taksha Flow Docker images"

# Verify the repository was created
gcloud artifacts repositories list
```

## Step 3: Create Service Account

### 3.1 Create the Service Account

```bash
# Create service account
gcloud iam service-accounts create github-actions \
  --display-name="GitHub Actions Deployment" \
  --description="Service account for GitHub Actions to deploy to Cloud Run"
```

### 3.2 Grant Required Permissions

```bash
# Set your project ID
export PROJECT_ID="YOUR_PROJECT_ID"
export SA_EMAIL="github-actions@${PROJECT_ID}.iam.gserviceaccount.com"

# Grant Cloud Run Admin role
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/run.admin"

# Grant Service Account User role (required to deploy as the default compute service account)
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/iam.serviceAccountUser"

# Grant Artifact Registry Writer role
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/artifactregistry.writer"

# Grant Storage Admin role (for Cloud Build)
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/storage.admin"
```

### 3.3 Create and Download Service Account Key

```bash
# Create key and download as JSON
gcloud iam service-accounts keys create github-actions-key.json \
  --iam-account="${SA_EMAIL}"

# Display the key (you'll need this for GitHub secrets)
cat github-actions-key.json
```

**IMPORTANT:** Keep this JSON file secure! It contains credentials to access your GCP project.

## Step 4: Configure GitHub Secrets

Go to your GitHub repository and add the following secrets:

**Settings → Secrets and variables → Actions → New repository secret**

### Required Secrets

| Secret Name | Description | Example/Notes |
|------------|-------------|---------------|
| `GCP_PROJECT_ID` | Your Google Cloud Project ID | `my-project-123456` |
| `GCP_SA_KEY` | Service account JSON key | Paste the entire content of `github-actions-key.json` |
| `GCP_REGION` | Cloud Run deployment region | `us-central1` (optional, defaults to `us-central1`) |

### How to Add Secrets

1. Navigate to: `https://github.com/YOUR_USERNAME/YOUR_REPO/settings/secrets/actions`
2. Click "New repository secret"
3. For `GCP_SA_KEY`:
   - Name: `GCP_SA_KEY`
   - Value: Paste the **entire contents** of the `github-actions-key.json` file
4. For `GCP_PROJECT_ID`:
   - Name: `GCP_PROJECT_ID`
   - Value: Your project ID (e.g., `taksha-flow-prod`)
5. For `GCP_REGION` (optional):
   - Name: `GCP_REGION`
   - Value: `us-central1` or your preferred region

## Step 5: Deploy Your Application

### Option 1: Deploy Using Tags (Recommended)

```bash
# For production release
git tag backend-v1.0.0
git push origin backend-v1.0.0

# For beta release
git tag backend-v1.0.0.beta.1
git push origin backend-v1.0.0.beta.1

# For alpha release
git tag backend-v1.0.0.alpha.1
git push origin backend-v1.0.0.alpha.1

# For release candidate
git tag backend-v1.0.0.rc.1
git push origin backend-v1.0.0.rc.1
```

### Option 2: Manual Deployment via GitHub Actions

1. Go to: `https://github.com/YOUR_USERNAME/YOUR_REPO/actions`
2. Select "Deploy Backend to Google Cloud Run" workflow
3. Click "Run workflow"
4. Enter the tag (e.g., `backend-v1.0.0`)
5. Click "Run workflow"

## Step 6: Verify Deployment

After the GitHub Action completes:

1. Check the workflow summary for the service URL
2. Visit the URL to verify the deployment
3. Check health endpoint: `https://YOUR_SERVICE_URL/health`

### View in Google Cloud Console

```bash
# List all Cloud Run services
gcloud run services list --platform=managed

# Get service details
gcloud run services describe taksha-flow-backend \
  --platform=managed \
  --region=us-central1

# View logs
gcloud run services logs read taksha-flow-backend \
  --platform=managed \
  --region=us-central1
```

## Service Naming Convention

The workflow creates different services based on release type:

- **Production**: `taksha-flow-backend`
- **Beta**: `taksha-flow-backend-beta`
- **Alpha**: `taksha-flow-backend-alpha`
- **RC**: `taksha-flow-backend-rc`

## Environment Variables

The deployment automatically sets these environment variables:

- `VERSION`: The version from the tag (e.g., `1.0.0`)
- `ENVIRONMENT`: Either `production` or `staging`

### Adding Additional Environment Variables

Edit the workflow file `.github/workflows/deploy-backend-cloudrun.yml` and add to the `gcloud run deploy` command:

```yaml
--set-env-vars "YOUR_VAR_NAME=value" \
```

Or use secrets:

```yaml
--set-env-vars "DATABASE_URL=${{ secrets.DATABASE_URL }}" \
```

## Resource Configuration

Current settings (can be modified in the workflow):

- **Memory**: 512Mi
- **CPU**: 1
- **Min Instances**: 0 (scales to zero)
- **Max Instances**: 1
- **Timeout**: 300 seconds
- **Port**: 8080

### Modify Resources

Edit `.github/workflows/deploy-backend-cloudrun.yml` and change:

```yaml
--memory 512Mi \
--cpu 1 \
--min-instances 0 \
--max-instances 1 \
```

## Troubleshooting

### Common Issues

1. **Permission Denied Errors**
   - Verify service account has all required roles
   - Check that `GCP_SA_KEY` secret is correctly formatted JSON

2. **Artifact Registry Not Found**
   - Ensure you created the `taksha-flow` repository
   - Check the region matches

3. **Build Failures**
   - Verify `Dockerfile` is at repository root
   - Check that all dependencies are in `requirements.txt`
   - Review build logs in GitHub Actions

4. **Deployment Timeout**
   - Increase timeout in workflow: `--timeout 600`
   - Check application startup time

5. **Health Check Fails**
   - Ensure your FastAPI app has a `/health` endpoint
   - Check Cloud Run logs: `gcloud run services logs read SERVICE_NAME`

### Debug Commands

```bash
# View Cloud Run service details
gcloud run services describe taksha-flow-backend \
  --platform=managed \
  --region=us-central1 \
  --format=yaml

# View recent logs
gcloud run services logs read taksha-flow-backend \
  --platform=managed \
  --region=us-central1 \
  --limit=50

# Test the service
curl https://YOUR_SERVICE_URL/health
```

## Security Best Practices

1. **Never commit the service account JSON key to Git**
2. **Rotate service account keys regularly** (every 90 days)
3. **Use least privilege**: Only grant necessary permissions
4. **Enable Cloud Audit Logs** for compliance
5. **Use Secret Manager** for sensitive environment variables

### Using Secret Manager (Optional)

```bash
# Create a secret
echo -n "my-secret-value" | gcloud secrets create my-secret --data-file=-

# Grant service account access
gcloud secrets add-iam-policy-binding my-secret \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/secretmanager.secretAccessor"

# Reference in Cloud Run
--set-secrets="MY_SECRET=my-secret:latest"
```

## Cost Optimization

Cloud Run pricing:

- **Free tier**: 2 million requests/month
- **Charges**: CPU, memory, and requests beyond free tier
- **Scaling to zero**: No charges when not in use

Tips:

1. Use `min-instances: 0` to scale to zero
2. Right-size memory and CPU
3. Optimize application startup time
4. Use caching where possible

## Cleanup

To remove all resources:

```bash
# Delete Cloud Run service
gcloud run services delete taksha-flow-backend \
  --platform=managed \
  --region=us-central1

# Delete Artifact Registry repository
gcloud artifacts repositories delete taksha-flow \
  --location=us-central1

# Delete service account
gcloud iam service-accounts delete ${SA_EMAIL}
```

## Next Steps

- Set up custom domain: [Cloud Run Custom Domains](https://cloud.google.com/run/docs/mapping-custom-domains)
- Configure Cloud CDN for global performance
- Set up monitoring and alerting with Cloud Monitoring
- Implement CI/CD testing before deployment
- Add database connections (Cloud SQL, Firestore, etc.)

## Resources

- [Cloud Run Documentation](https://cloud.google.com/run/docs)
- [Artifact Registry Documentation](https://cloud.google.com/artifact-registry/docs)
- [GitHub Actions for GCP](https://github.com/google-github-actions)
- [Cloud Run Pricing](https://cloud.google.com/run/pricing)
