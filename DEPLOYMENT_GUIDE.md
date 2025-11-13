# GeoQB SaaS Deployment Guide

Complete guide to deploy GeoQB SaaS to Google Cloud Platform (GCP).

## Prerequisites

- GCP account with billing enabled
- `gcloud` CLI installed and configured
- `kubectl` installed
- `terraform` installed
- Docker installed
- GitHub account for CI/CD

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                        Google Cloud Platform                 │
│                                                              │
│  ┌────────────┐         ┌─────────────────┐                │
│  │   Cloud    │         │  GKE Cluster    │                │
│  │  Load      │────────▶│                 │                │
│  │  Balancer  │         │  ┌───────────┐  │                │
│  └────────────┘         │  │ Frontend  │  │                │
│        │                │  │  (Next.js)│  │                │
│        │                │  └───────────┘  │                │
│        │                │  ┌───────────┐  │                │
│        └───────────────▶│  │  Backend  │  │                │
│                         │  │ (FastAPI) │  │                │
│                         │  └───────────┘  │                │
│                         └─────────────────┘                │
│                                 │                           │
│                                 │                           │
│  ┌────────────┐   ┌────────────┐   ┌──────────────┐       │
│  │  Cloud SQL │   │   Redis    │   │    Cloud     │       │
│  │ PostgreSQL │   │ Memorystore│   │   Storage    │       │
│  └────────────┘   └────────────┘   └──────────────┘       │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## Step 1: Set Up GCP Project

```bash
# Set project ID
export PROJECT_ID="your-gcp-project-id"
export REGION="us-central1"

# Create project (if needed)
gcloud projects create $PROJECT_ID --name="GeoQB SaaS"

# Set active project
gcloud config set project $PROJECT_ID

# Enable billing
# (Do this through GCP Console)

# Enable required APIs
gcloud services enable \
  compute.googleapis.com \
  container.googleapis.com \
  sqladmin.googleapis.com \
  redis.googleapis.com \
  cloudresourcemanager.googleapis.com
```

## Step 2: Deploy Infrastructure with Terraform

```bash
cd terraform

# Initialize Terraform
terraform init

# Create terraform.tfvars
cat > terraform.tfvars <<EOF
project_id    = "${PROJECT_ID}"
region        = "us-central1"
environment   = "production"
db_password   = "$(openssl rand -base64 32)"
node_count    = 2
machine_type  = "e2-standard-2"
EOF

# Plan deployment
terraform plan

# Apply infrastructure
terraform apply

# Save outputs
terraform output > ../terraform-outputs.txt
```

This creates:
- VPC network and subnets
- GKE cluster with autoscaling node pool
- Cloud SQL PostgreSQL instance
- Redis Memorystore instance
- Static IP for load balancer
- Cloud Storage bucket for backups

## Step 3: Configure kubectl

```bash
# Get GKE credentials
gcloud container clusters get-credentials geoqb-cluster --region $REGION

# Verify connection
kubectl get nodes
```

## Step 4: Create Kubernetes Secrets

```bash
# Get database connection from Terraform outputs
DB_CONNECTION=$(terraform output -raw postgres_connection)
REDIS_HOST=$(terraform output -raw redis_host)
REDIS_PORT=$(terraform output -raw redis_port)

# Generate secret key
SECRET_KEY=$(openssl rand -base64 32)

# Create secrets
kubectl create secret generic geoqb-secrets \
  --from-literal=database-url="postgresql://geoqb:YOUR_PASSWORD@/geoqb?host=/cloudsql/${DB_CONNECTION}" \
  --from-literal=redis-url="redis://${REDIS_HOST}:${REDIS_PORT}/0" \
  --from-literal=secret-key="${SECRET_KEY}" \
  --from-literal=tigergraph-username="tigergraph" \
  --from-literal=tigergraph-password="YOUR_TIGERGRAPH_PASSWORD" \
  --from-literal=sendgrid-api-key="YOUR_SENDGRID_KEY"

# Create config map
kubectl create configmap geoqb-config \
  --from-literal=tigergraph-host="your-tigergraph-host.com" \
  --from-literal=environment="production"
```

## Step 5: Build and Push Docker Images

```bash
# Configure Docker for GCR
gcloud auth configure-docker gcr.io

# Build and push backend
cd geoqb-api
docker build -t gcr.io/${PROJECT_ID}/geoqb-api:latest .
docker push gcr.io/${PROJECT_ID}/geoqb-api:latest

# Build and push frontend
cd ../geoqb-web
docker build -t gcr.io/${PROJECT_ID}/geoqb-web:latest .
docker push gcr.io/${PROJECT_ID}/geoqb-web:latest
```

## Step 6: Deploy to Kubernetes

```bash
cd ../k8s

# Update PROJECT_ID in deployment files
sed -i "s/PROJECT_ID/${PROJECT_ID}/g" backend-deployment.yaml
sed -i "s/PROJECT_ID/${PROJECT_ID}/g" frontend-deployment.yaml

# Deploy backend
kubectl apply -f backend-deployment.yaml

# Deploy frontend
kubectl apply -f frontend-deployment.yaml

# Deploy ingress
kubectl apply -f ingress.yaml

# Check deployment status
kubectl get deployments
kubectl get pods
kubectl get services
kubectl get ingress
```

## Step 7: Initialize Database

```bash
# Get a backend pod name
BACKEND_POD=$(kubectl get pods -l app=geoqb-api -o jsonpath='{.items[0].metadata.name}')

# Run migrations
kubectl exec -it $BACKEND_POD -- python -c "from app.database import init_db; init_db()"

# Verify database
kubectl exec -it $BACKEND_POD -- python -c "from app.database import SessionLocal; db = SessionLocal(); print('Database OK' if db else 'Database Error')"
```

## Step 8: Configure DNS

```bash
# Get load balancer IP
LB_IP=$(kubectl get ingress geoqb-ingress -o jsonpath='{.status.loadBalancer.ingress[0].ip}')

echo "Configure your DNS:"
echo "  geoqb.io        A    $LB_IP"
echo "  www.geoqb.io    A    $LB_IP"
echo "  api.geoqb.io    A    $LB_IP"
```

Add these A records to your DNS provider.

## Step 9: Set Up CI/CD with GitHub Actions

```bash
# Create service account for GitHub Actions
gcloud iam service-accounts create github-actions \
  --display-name="GitHub Actions"

# Grant necessary permissions
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:github-actions@${PROJECT_ID}.iam.gserviceaccount.com" \
  --role="roles/container.developer"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:github-actions@${PROJECT_ID}.iam.gserviceaccount.com" \
  --role="roles/storage.admin"

# Create key
gcloud iam service-accounts keys create github-actions-key.json \
  --iam-account=github-actions@${PROJECT_ID}.iam.gserviceaccount.com

# Add secrets to GitHub repository:
# - GCP_PROJECT_ID: your-project-id
# - GCP_SA_KEY: contents of github-actions-key.json
# - GKE_CLUSTER_NAME: geoqb-cluster
# - GKE_CLUSTER_ZONE: us-central1

# Delete local key file
rm github-actions-key.json
```

## Step 10: Verify Deployment

```bash
# Check all pods are running
kubectl get pods

# Check services
kubectl get services

# Check ingress
kubectl get ingress

# Test API endpoint
curl https://api.geoqb.io/health

# Test frontend
curl https://geoqb.io

# View logs
kubectl logs -l app=geoqb-api --tail=50
kubectl logs -l app=geoqb-web --tail=50
```

## Monitoring and Maintenance

### View Logs

```bash
# API logs
kubectl logs -l app=geoqb-api -f

# Frontend logs
kubectl logs -l app=geoqb-web -f
```

### Scale Deployment

```bash
# Manual scaling
kubectl scale deployment geoqb-api --replicas=5

# Auto-scaling is configured via HPA (HorizontalPodAutoscaler)
kubectl get hpa
```

### Update Deployment

```bash
# After pushing new image
kubectl set image deployment/geoqb-api geoqb-api=gcr.io/${PROJECT_ID}/geoqb-api:new-tag
kubectl rollout status deployment/geoqb-api

# Rollback if needed
kubectl rollout undo deployment/geoqb-api
```

### Database Backup

```bash
# Export database
gcloud sql export sql geoqb-postgres gs://${PROJECT_ID}-geoqb-backups/backup-$(date +%Y%m%d).sql \
  --database=geoqb
```

## Cost Optimization

### Development/Staging Environment

```hcl
# terraform.tfvars for dev
preemptible   = true      # Use cheaper preemptible nodes
node_count    = 1         # Fewer nodes
machine_type  = "e2-micro" # Smaller instances
redis_tier    = "BASIC"   # Basic Redis
db_tier       = "db-f1-micro" # Smallest database
```

### Production Environment

```hcl
# terraform.tfvars for prod
preemptible   = false     # Reliable nodes
node_count    = 2         # Minimum for HA
machine_type  = "e2-standard-2"
redis_tier    = "STANDARD_HA" # High availability
db_tier       = "db-custom-2-7680" # Dedicated resources
```

## Troubleshooting

### Pods not starting

```bash
kubectl describe pod <pod-name>
kubectl logs <pod-name>
```

### Database connection issues

```bash
# Check Cloud SQL proxy
kubectl get pods -l app=cloudsql-proxy

# Test connection from pod
kubectl exec -it <backend-pod> -- python -c "from app.database import SessionLocal; SessionLocal()"
```

### Ingress not working

```bash
# Check ingress status
kubectl describe ingress geoqb-ingress

# Wait for certificate provisioning (can take 15+ minutes)
kubectl describe managedcertificate geoqb-cert
```

## Security Checklist

- [ ] Change all default passwords
- [ ] Enable Cloud Armor for DDoS protection
- [ ] Set up Cloud IAM policies
- [ ] Enable GKE binary authorization
- [ ] Configure network policies
- [ ] Set up audit logging
- [ ] Enable Secret Manager instead of Kubernetes secrets
- [ ] Configure SSL/TLS certificates
- [ ] Set up Cloud KMS for encryption keys
- [ ] Enable VPC Service Controls

## Estimated Costs

**Minimum configuration (dev/testing):**
- GKE: ~$150/month (2 e2-micro nodes)
- Cloud SQL: ~$25/month (db-f1-micro)
- Redis: ~$35/month (1GB basic)
- Networking: ~$20/month
- **Total: ~$230/month**

**Production configuration:**
- GKE: ~$300/month (2 e2-standard-2 nodes)
- Cloud SQL: ~$200/month (db-custom-2-7680)
- Redis: ~$100/month (5GB standard-ha)
- Networking: ~$50/month
- **Total: ~$650/month**

## Next Steps

1. Set up monitoring with Cloud Monitoring/Prometheus
2. Configure alerts for critical metrics
3. Set up log aggregation
4. Implement backup and disaster recovery
5. Set up staging environment
6. Configure CDN for frontend assets
7. Implement rate limiting
8. Set up health checks and uptime monitoring

## Support

For issues or questions:
- Check logs: `kubectl logs -l app=geoqb-api`
- View GCP Console for infrastructure issues
- Review GitHub Actions for CI/CD issues
- Contact: support@geoqb.io
