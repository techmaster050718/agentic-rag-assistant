# Deployment Guide

## Local Development
Use Docker Compose to run the entire stack locally:
```bash
./scripts/docker-up.sh
```

## Production
Deploy using Terraform to Google Cloud Platform:
1. Navigate to `infra/terraform`
2. Initialize: `terraform init`
3. Plan: `terraform plan`
4. Apply: `terraform apply`
