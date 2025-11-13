# GeoQB Deployment Guide

Complete guide for deploying GeoQB in various environments with best practices and recommended improvements.

---

## Table of Contents

1. [Current Deployment Model](#current-deployment-model)
2. [Development Environment](#development-environment)
3. [Production Deployment](#production-deployment)
4. [Docker Deployment](#docker-deployment-new)
5. [Kubernetes Deployment](#kubernetes-deployment-new)
6. [Cloud Platform Deployment](#cloud-platform-deployment)
7. [CI/CD Pipeline](#cicd-pipeline)
8. [Monitoring & Operations](#monitoring--operations)
9. [Disaster Recovery](#disaster-recovery)
10. [Deployment Improvements](#deployment-improvements)

---

## Current Deployment Model

### Architecture

**Type:** Developer Workstation / Single-Server Deployment

**Components:**
- **Application**: Python CLI tools running locally
- **Database**: TigerGraph Cloud (SaaS)
- **Streaming**: Confluent Cloud (SaaS)
- **Storage**: Local filesystem + Optional S3

**Pros:**
- Simple setup for researchers and data scientists
- No infrastructure management required
- Direct access to TigerGraph Cloud
- Low operational overhead

**Cons:**
- Not suitable for production multi-user scenarios
- No high availability
- No scalability
- Security limitations (credentials in files)

---

## Development Environment

### Prerequisites

- **Python:** 3.7 or higher
- **Operating System:** macOS, Linux, or Windows WSL
- **Memory:** Minimum 8GB RAM (16GB recommended)
- **Storage:** Minimum 10GB free space for workspace
- **Network:** Internet connection for cloud services

### External Services Required

1. **TigerGraph Cloud Account**
   - Free tier: https://tgcloud.io/
   - Create graph database application
   - Note credentials for configuration

2. **Confluent Cloud Account** (Optional)
   - For Kafka streaming features
   - Free tier available

3. **AWS/S3 Account** (Optional)
   - For S3 storage features
   - Tebi.io alternative supported

### Step-by-Step Setup

#### 1. Clone Repository

```bash
git clone https://github.com/GeoQB/geoqb.git
cd geoqb/pyGeoQB
```

#### 2. Create Virtual Environment

```bash
# Using bootstrap script (recommended)
./script/bootstrap.sh env1

# Or manually
python3 -m venv env1
source env1/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

#### 3. Create Workspace Directory

```bash
# Create workspace
mkdir -p ~/geoqb-workspace/{raw,stage,md,dumps,graph_layers}

# Or clone playground repository
git clone https://github.com/GeoQB/geoqb-playground.git ~/geoqb-workspace
```

#### 4. Configure Environment

Create `env/env.sh`:

```bash
#!/bin/bash

# Activate virtual environment
source $1/bin/activate

### WORKSPACE
export GEOQB_WORKSPACE="$HOME/geoqb-workspace/"

### OSM Data Sources
export overpass_endpoint="https://overpass.kumi.systems/api/interpreter"
export sophox_endpoint="https://sophox.org:443/sparql"

### TigerGraph Cloud
export TG_URL="https://your-instance.i.tgcloud.io/"
export TG_SECRET="your-secret"
export TG_PASSWORD="your-password"
export TG_USERNAME="your-username"

### Tebi S3 (Optional)
export aws_access_key_id="your-access-key"
export aws_secret_access_key="your-secret-key"
export s3_endpoint_url="https://s3.tebi.io"

### SOLID Pod (Optional)
export SOLID_IDP="https://solidcommunity.net"
export SOLID_POD_ENDPOINT="https://your-pod.solidcommunity.net"
export SOLID_USERNAME="your-username"
export SOLID_PASSWORD="your-password"

### Confluent Cloud Kafka (Optional)
export bootstrap_servers="your-cluster.confluent.cloud:9092"
export security_protocol="SASL_SSL"
export sasl_mechanisms="PLAIN"
export sasl_username="your-api-key"
export sasl_password="your-api-secret"

### Schema Registry (Optional)
export schema_registry_url="https://your-sr.confluent.cloud"
export basic_auth_credentials_source="USER_INFO"
export basic_auth_user_info="your-sr-key:your-sr-secret"
```

**Security Note:** Never commit `env.sh` to version control!

#### 5. Initialize Database Schema

```bash
source env/env.sh env1
python examples/test_szenario_0.py
```

This creates the graph schema in TigerGraph.

#### 6. Setup CLI Aliases

```bash
source script/set_aliases.sh env1

# Now you can use:
# gqws - Workspace management
# gql - Layer management
# gqblend - Data blending
```

#### 7. Verify Installation

```bash
# Test workspace
gqws init
gqws ls

# Test database connection
python -c "
from geoanalysis.geoqb import GeoQbTG
import os
tg = GeoQbTG(
    host=os.getenv('TG_URL'),
    username=os.getenv('TG_USERNAME'),
    password=os.getenv('TG_PASSWORD')
)
print('Connected:', tg.test_connection())
"
```

### Development Workflow

```bash
# 1. Activate environment
source env/env.sh env1

# 2. Create layer
gql create hospitals --tags amenity=hospital --bbox 50.0,8.0,51.0,9.0 --resolution 9

# 3. Ingest data
gql ingest hospitals

# 4. Run analysis
python examples/test_szenario_2_graph_analysis.py

# 5. Extract results
gql extract hospitals --output $GEOQB_WORKSPACE/graph_layers/
```

---

## Production Deployment

### Requirements

**Compute:**
- **CPU:** 4+ cores
- **Memory:** 16GB+ RAM
- **Storage:** 100GB+ SSD
- **Network:** 100 Mbps+

**Software:**
- Python 3.9+
- systemd (Linux) or equivalent process manager
- Nginx or Apache for reverse proxy (if API mode)
- PostgreSQL (for user management in multi-tenant deployments)

### Production Setup

#### 1. Create Service User

```bash
sudo useradd -r -s /bin/bash -d /opt/geoqb geoqb
sudo mkdir -p /opt/geoqb /var/log/geoqb /var/lib/geoqb
sudo chown -R geoqb:geoqb /opt/geoqb /var/log/geoqb /var/lib/geoqb
```

#### 2. Install Application

```bash
sudo su - geoqb
cd /opt/geoqb
git clone https://github.com/GeoQB/geoqb.git
cd geoqb/pyGeoQB

# Create production virtual environment
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

#### 3. Configure Secrets (using systemd environment file)

```bash
# /etc/geoqb/env
GEOQB_WORKSPACE=/var/lib/geoqb/workspace
TG_URL=https://your-instance.i.tgcloud.io/
TG_USERNAME=produser
TG_PASSWORD_FILE=/etc/geoqb/secrets/tg_password
```

#### 4. Create systemd Service

```ini
# /etc/systemd/system/geoqb-worker.service
[Unit]
Description=GeoQB Worker Service
After=network.target

[Service]
Type=simple
User=geoqb
Group=geoqb
WorkingDirectory=/opt/geoqb/geoqb/pyGeoQB
EnvironmentFile=/etc/geoqb/env

# Read secrets from files
ExecStartPre=/bin/sh -c 'export TG_PASSWORD=$(cat $TG_PASSWORD_FILE)'

ExecStart=/opt/geoqb/geoqb/pyGeoQB/venv/bin/python \
    examples/worker.py

Restart=on-failure
RestartSec=10

# Security hardening
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/var/lib/geoqb /var/log/geoqb

# Resource limits
MemoryMax=4G
CPUQuota=200%

[Install]
WantedBy=multi-user.target
```

#### 5. Enable and Start Service

```bash
sudo systemctl daemon-reload
sudo systemctl enable geoqb-worker
sudo systemctl start geoqb-worker
sudo systemctl status geoqb-worker
```

#### 6. Setup Log Rotation

```bash
# /etc/logrotate.d/geoqb
/var/log/geoqb/*.log {
    daily
    rotate 30
    compress
    delaycompress
    notifempty
    create 0640 geoqb geoqb
    sharedscripts
    postrotate
        systemctl reload geoqb-worker > /dev/null 2>&1 || true
    endscript
}
```

### Production Security Checklist

- [ ] Use secrets manager (Vault, AWS Secrets Manager)
- [ ] Enable firewall (only allow necessary ports)
- [ ] Configure SELinux/AppArmor
- [ ] Enable audit logging
- [ ] Set up intrusion detection (fail2ban, OSSEC)
- [ ] Configure TLS for all external connections
- [ ] Implement rate limiting
- [ ] Set up monitoring and alerting
- [ ] Configure automatic security updates
- [ ] Implement backup and disaster recovery
- [ ] Document runbooks and procedures

---

## Docker Deployment (NEW)

### Dockerfile

```dockerfile
# Dockerfile
FROM python:3.9-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Create app user
RUN useradd -m -u 1000 geoqb

# Set working directory
WORKDIR /app

# Copy requirements
COPY pyGeoQB/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY pyGeoQB/ .

# Create workspace directory
RUN mkdir -p /workspace && chown geoqb:geoqb /workspace

# Switch to non-root user
USER geoqb

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV GEOQB_WORKSPACE=/workspace

# Expose port (if running API server)
EXPOSE 8000

# Default command
CMD ["python", "examples/worker.py"]
```

### Docker Compose

```yaml
# docker-compose.yml
version: '3.8'

services:
  geoqb:
    build:
      context: .
      dockerfile: Dockerfile
    image: geoqb:latest
    container_name: geoqb
    restart: unless-stopped

    environment:
      - GEOQB_WORKSPACE=/workspace
      - TG_URL=${TG_URL}
      - TG_USERNAME=${TG_USERNAME}
      - TG_PASSWORD=${TG_PASSWORD}
      - overpass_endpoint=https://overpass.kumi.systems/api/interpreter
      - sophox_endpoint=https://sophox.org:443/sparql

    volumes:
      - geoqb-workspace:/workspace
      - geoqb-logs:/app/logs

    networks:
      - geoqb-network

    # Resource limits
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 4G
        reservations:
          cpus: '1'
          memory: 2G

    # Health check
    healthcheck:
      test: ["CMD", "python", "-c", "import sys; sys.exit(0)"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Optional: Nginx reverse proxy
  nginx:
    image: nginx:alpine
    container_name: geoqb-nginx
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    networks:
      - geoqb-network
    depends_on:
      - geoqb

volumes:
  geoqb-workspace:
  geoqb-logs:

networks:
  geoqb-network:
    driver: bridge
```

### Build and Run

```bash
# Build image
docker build -t geoqb:latest .

# Run with docker-compose
docker-compose up -d

# View logs
docker-compose logs -f geoqb

# Execute commands in container
docker-compose exec geoqb gqws ls

# Stop services
docker-compose down
```

### Docker Security Best Practices

```dockerfile
# Production Dockerfile with security hardening
FROM python:3.9-slim AS builder

# Build dependencies
WORKDIR /build
COPY pyGeoQB/requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /build/wheels -r requirements.txt

# Runtime image
FROM python:3.9-slim

# Security: Install security updates
RUN apt-get update && apt-get upgrade -y \
    && apt-get install -y --no-install-recommends \
        ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user with specific UID
RUN groupadd -r geoqb -g 1000 && \
    useradd -r -g geoqb -u 1000 -m -s /sbin/nologin geoqb

WORKDIR /app

# Copy wheels from builder
COPY --from=builder /build/wheels /wheels
RUN pip install --no-cache /wheels/*

# Copy application
COPY --chown=geoqb:geoqb pyGeoQB/ .

# Set up workspace
RUN mkdir -p /workspace && chown geoqb:geoqb /workspace

# Drop to non-root user
USER geoqb

# Security: Read-only root filesystem
# (requires volumes for /workspace and /tmp)
VOLUME ["/workspace", "/tmp"]

ENV PYTHONUNBUFFERED=1
ENV GEOQB_WORKSPACE=/workspace

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import sys; sys.exit(0)"

CMD ["python", "examples/worker.py"]
```

---

## Kubernetes Deployment (NEW)

### Namespace

```yaml
# k8s/namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: geoqb
  labels:
    name: geoqb
```

### ConfigMap

```yaml
# k8s/configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: geoqb-config
  namespace: geoqb
data:
  overpass_endpoint: "https://overpass.kumi.systems/api/interpreter"
  sophox_endpoint: "https://sophox.org:443/sparql"
  GEOQB_WORKSPACE: "/workspace"
```

### Secrets

```yaml
# k8s/secrets.yaml
apiVersion: v1
kind: Secret
metadata:
  name: geoqb-secrets
  namespace: geoqb
type: Opaque
stringData:
  TG_URL: "https://your-instance.i.tgcloud.io/"
  TG_USERNAME: "your-username"
  TG_PASSWORD: "your-password"
  KAFKA_SASL_USERNAME: "your-kafka-user"
  KAFKA_SASL_PASSWORD: "your-kafka-password"
```

### PersistentVolumeClaim

```yaml
# k8s/pvc.yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: geoqb-workspace
  namespace: geoqb
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 100Gi
  storageClassName: fast-ssd  # Adjust to your storage class
```

### Deployment

```yaml
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: geoqb-worker
  namespace: geoqb
  labels:
    app: geoqb
    component: worker
spec:
  replicas: 3
  selector:
    matchLabels:
      app: geoqb
      component: worker
  template:
    metadata:
      labels:
        app: geoqb
        component: worker
    spec:
      securityContext:
        runAsNonRoot: true
        runAsUser: 1000
        fsGroup: 1000

      containers:
      - name: geoqb
        image: geoqb:latest
        imagePullPolicy: Always

        envFrom:
        - configMapRef:
            name: geoqb-config
        - secretRef:
            name: geoqb-secrets

        resources:
          requests:
            memory: "2Gi"
            cpu: "1000m"
          limits:
            memory: "4Gi"
            cpu: "2000m"

        volumeMounts:
        - name: workspace
          mountPath: /workspace

        livenessProbe:
          exec:
            command:
            - python
            - -c
            - "import sys; sys.exit(0)"
          initialDelaySeconds: 30
          periodSeconds: 30

        readinessProbe:
          exec:
            command:
            - python
            - -c
            - "import sys; sys.exit(0)"
          initialDelaySeconds: 10
          periodSeconds: 10

      volumes:
      - name: workspace
        persistentVolumeClaim:
          claimName: geoqb-workspace

      # Spread pods across nodes
      affinity:
        podAntiAffinity:
          preferredDuringSchedulingIgnoredDuringExecution:
          - weight: 100
            podAffinityTerm:
              labelSelector:
                matchExpressions:
                - key: app
                  operator: In
                  values:
                  - geoqb
              topologyKey: kubernetes.io/hostname
```

### Service

```yaml
# k8s/service.yaml
apiVersion: v1
kind: Service
metadata:
  name: geoqb-service
  namespace: geoqb
spec:
  type: ClusterIP
  selector:
    app: geoqb
    component: worker
  ports:
  - port: 8000
    targetPort: 8000
    protocol: TCP
    name: http
```

### Ingress

```yaml
# k8s/ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: geoqb-ingress
  namespace: geoqb
  annotations:
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
    nginx.ingress.kubernetes.io/rate-limit: "100"
spec:
  ingressClassName: nginx
  tls:
  - hosts:
    - api.geoqb.example.com
    secretName: geoqb-tls
  rules:
  - host: api.geoqb.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: geoqb-service
            port:
              number: 8000
```

### HorizontalPodAutoscaler

```yaml
# k8s/hpa.yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: geoqb-hpa
  namespace: geoqb
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: geoqb-worker
  minReplicas: 3
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

### Deploy to Kubernetes

```bash
# Apply all resources
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/secrets.yaml
kubectl apply -f k8s/pvc.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
kubectl apply -f k8s/ingress.yaml
kubectl apply -f k8s/hpa.yaml

# Check status
kubectl get all -n geoqb

# View logs
kubectl logs -f -n geoqb deployment/geoqb-worker

# Scale manually
kubectl scale deployment/geoqb-worker --replicas=5 -n geoqb
```

---

## Cloud Platform Deployment

### AWS Deployment

#### Architecture

```
┌─────────────────────────────────────────────────────────┐
│                      AWS Cloud                          │
│                                                          │
│  ┌────────────────────────────────────────────────┐    │
│  │              VPC (10.0.0.0/16)                 │    │
│  │                                                 │    │
│  │  ┌──────────────────┐  ┌──────────────────┐   │    │
│  │  │  Public Subnet   │  │  Private Subnet  │   │    │
│  │  │                  │  │                  │   │    │
│  │  │  ┌────────────┐  │  │  ┌────────────┐ │   │    │
│  │  │  │ ALB        │  │  │  │ ECS Tasks  │ │   │    │
│  │  │  │            │  │  │  │  (GeoQB)   │ │   │    │
│  │  │  └────────────┘  │  │  └────────────┘ │   │    │
│  │  │                  │  │                  │   │    │
│  │  └──────────────────┘  └──────────────────┘   │    │
│  │                                                 │    │
│  └────────────────────────────────────────────────┘    │
│                                                          │
│  ┌──────────────┐  ┌──────────────┐  ┌─────────────┐  │
│  │     RDS      │  │     S3       │  │   Secrets   │  │
│  │  (Metadata)  │  │ (Workspace)  │  │   Manager   │  │
│  └──────────────┘  └──────────────┘  └─────────────┘  │
└─────────────────────────────────────────────────────────┘
                            │
                            ▼
                  ┌──────────────────┐
                  │  TigerGraph Cloud│
                  │  Confluent Cloud │
                  └──────────────────┘
```

#### Terraform Configuration

```hcl
# terraform/main.tf
terraform {
  required_version = ">= 1.0"

  backend "s3" {
    bucket = "geoqb-terraform-state"
    key    = "prod/terraform.tfstate"
    region = "us-east-1"
  }

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

# VPC
module "vpc" {
  source = "terraform-aws-modules/vpc/aws"

  name = "geoqb-vpc"
  cidr = "10.0.0.0/16"

  azs             = ["us-east-1a", "us-east-1b", "us-east-1c"]
  private_subnets = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
  public_subnets  = ["10.0.101.0/24", "10.0.102.0/24", "10.0.103.0/24"]

  enable_nat_gateway = true
  single_nat_gateway = false

  tags = {
    Project = "GeoQB"
    Environment = var.environment
  }
}

# ECS Cluster
resource "aws_ecs_cluster" "main" {
  name = "geoqb-cluster"

  setting {
    name  = "containerInsights"
    value = "enabled"
  }
}

# ECS Task Definition
resource "aws_ecs_task_definition" "geoqb" {
  family                   = "geoqb"
  requires_compatibilities = ["FARGATE"]
  network_mode            = "awsvpc"
  cpu                     = "2048"
  memory                  = "4096"
  execution_role_arn      = aws_iam_role.ecs_execution.arn
  task_role_arn           = aws_iam_role.ecs_task.arn

  container_definitions = jsonencode([{
    name      = "geoqb"
    image     = "${aws_ecr_repository.geoqb.repository_url}:latest"
    essential = true

    environment = [
      {
        name  = "GEOQB_WORKSPACE"
        value = "/workspace"
      }
    ]

    secrets = [
      {
        name      = "TG_PASSWORD"
        valueFrom = aws_secretsmanager_secret.tg_password.arn
      }
    ]

    logConfiguration = {
      logDriver = "awslogs"
      options = {
        "awslogs-group"         = aws_cloudwatch_log_group.geoqb.name
        "awslogs-region"        = var.aws_region
        "awslogs-stream-prefix" = "ecs"
      }
    }
  }])
}

# ECS Service
resource "aws_ecs_service" "geoqb" {
  name            = "geoqb-service"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.geoqb.arn
  desired_count   = 3
  launch_type     = "FARGATE"

  network_configuration {
    subnets         = module.vpc.private_subnets
    security_groups = [aws_security_group.ecs_tasks.id]
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.geoqb.arn
    container_name   = "geoqb"
    container_port   = 8000
  }
}

# S3 Bucket for Workspace
resource "aws_s3_bucket" "workspace" {
  bucket = "geoqb-workspace-${var.environment}"

  tags = {
    Name = "GeoQB Workspace"
    Environment = var.environment
  }
}

resource "aws_s3_bucket_versioning" "workspace" {
  bucket = aws_s3_bucket.workspace.id

  versioning_configuration {
    status = "Enabled"
  }
}

# Secrets Manager
resource "aws_secretsmanager_secret" "tg_password" {
  name = "geoqb/tigergraph/password"
}

# CloudWatch Log Group
resource "aws_cloudwatch_log_group" "geoqb" {
  name              = "/ecs/geoqb"
  retention_in_days = 30
}
```

### Azure Deployment

```bash
# Azure Container Instances deployment
az group create --name geoqb-rg --location eastus

az container create \
  --resource-group geoqb-rg \
  --name geoqb \
  --image geoqb:latest \
  --cpu 2 \
  --memory 4 \
  --environment-variables \
    GEOQB_WORKSPACE=/workspace \
  --secure-environment-variables \
    TG_PASSWORD=$TG_PASSWORD \
  --azure-file-volume-account-name mystorageaccount \
  --azure-file-volume-account-key $STORAGE_KEY \
  --azure-file-volume-share-name geoqb-workspace \
  --azure-file-volume-mount-path /workspace
```

### Google Cloud Platform

```bash
# Google Cloud Run deployment
gcloud run deploy geoqb \
  --image gcr.io/project-id/geoqb:latest \
  --platform managed \
  --region us-central1 \
  --memory 4Gi \
  --cpu 2 \
  --set-env-vars GEOQB_WORKSPACE=/workspace \
  --set-secrets TG_PASSWORD=geoqb-tg-password:latest \
  --allow-unauthenticated
```

---

## CI/CD Pipeline

### GitHub Actions Workflow

```yaml
# .github/workflows/deploy.yml
name: Build and Deploy

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

env:
  DOCKER_REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'

      - name: Install dependencies
        run: |
          cd pyGeoQB
          pip install -r requirements.txt
          pip install pytest pytest-cov

      - name: Run tests
        run: |
          cd pyGeoQB
          pytest --cov=geoanalysis test/

      - name: Upload coverage
        uses: codecov/codecov-action@v3

  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Run Bandit
        run: |
          pip install bandit
          bandit -r pyGeoQB/geoanalysis

      - name: Run Safety
        run: |
          pip install safety
          safety check

  build:
    needs: [test, security]
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write

    steps:
      - uses: actions/checkout@v3

      - name: Log in to Container Registry
        uses: docker/login-action@v2
        with:
          registry: ${{ env.DOCKER_REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Extract metadata
        id: meta
        uses: docker/metadata-action@v4
        with:
          images: ${{ env.DOCKER_REGISTRY }}/${{ env.IMAGE_NAME }}

      - name: Build and push Docker image
        uses: docker/build-push-action@v4
        with:
          context: .
          push: ${{ github.event_name != 'pull_request' }}
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}

  deploy:
    needs: build
    runs-on: ubuntu-latest
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'

    steps:
      - uses: actions/checkout@v3

      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v2
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: us-east-1

      - name: Deploy to ECS
        run: |
          # Update ECS service with new task definition
          aws ecs update-service \
            --cluster geoqb-cluster \
            --service geoqb-service \
            --force-new-deployment
```

---

## Monitoring & Operations

### Prometheus Metrics

```python
# geoqb/monitoring/prometheus.py
from prometheus_client import Counter, Histogram, Gauge, start_http_server

# Define metrics
layer_operations = Counter(
    'geoqb_layer_operations_total',
    'Total layer operations',
    ['operation', 'status']
)

query_duration = Histogram(
    'geoqb_query_duration_seconds',
    'Query execution time',
    ['query_type']
)

active_layers = Gauge(
    'geoqb_active_layers',
    'Number of active layers'
)

# Start metrics server
start_http_server(9090)
```

### Grafana Dashboard

```json
{
  "dashboard": {
    "title": "GeoQB Operations",
    "panels": [
      {
        "title": "Layer Operations Rate",
        "targets": [
          {
            "expr": "rate(geoqb_layer_operations_total[5m])"
          }
        ]
      },
      {
        "title": "Query Duration (p95)",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, geoqb_query_duration_seconds)"
          }
        ]
      }
    ]
  }
}
```

### Health Checks

```python
# geoqb/monitoring/health.py
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/health')
def health():
    """Health check endpoint."""
    checks = {
        'tigergraph': check_tigergraph(),
        'kafka': check_kafka(),
        'workspace': check_workspace()
    }

    all_healthy = all(checks.values())
    status_code = 200 if all_healthy else 503

    return jsonify({
        'status': 'healthy' if all_healthy else 'unhealthy',
        'checks': checks
    }), status_code
```

---

## Disaster Recovery

### Backup Strategy

```bash
#!/bin/bash
# script/backup.sh

# Backup TigerGraph
python <<EOF
from geoanalysis.geoqb import GeoQbTG
import os

tg = GeoQbTG(...)
tg.export_all_layers('/backups/graph_$(date +%Y%m%d).json')
EOF

# Backup workspace to S3
aws s3 sync $GEOQB_WORKSPACE s3://geoqb-backups/workspace/$(date +%Y%m%d)/

# Backup metadata
tar -czf /backups/metadata_$(date +%Y%m%d).tar.gz \
    $GEOQB_WORKSPACE/md/

# Retain backups for 30 days
find /backups -name "*.tar.gz" -mtime +30 -delete
```

### Recovery Procedures

```bash
# Restore from backup
DATE=20240101

# Restore workspace
aws s3 sync s3://geoqb-backups/workspace/$DATE/ $GEOQB_WORKSPACE/

# Restore graph
python examples/restore_graph.py /backups/graph_$DATE.json

# Verify integrity
gqws ls
gql ls
```

---

## Deployment Improvements

### High Priority Improvements

#### 1. Add Docker Support

**Status:** Not implemented
**Benefit:** Consistent deployments, easier scaling
**Effort:** Medium
**Timeline:** 2 weeks

**Implementation:**
- Create Dockerfile (see Docker section above)
- Add docker-compose.yml for local development
- Document Docker deployment procedures

#### 2. Implement Secrets Management

**Status:** Credentials in plain text files
**Benefit:** Critical security improvement
**Effort:** Medium
**Timeline:** 1 week

**Implementation:**
- Integrate HashiCorp Vault or AWS Secrets Manager
- Migrate credentials from env.sh
- Update documentation

#### 3. Add Health Check Endpoints

**Status:** No health checks
**Benefit:** Better monitoring and auto-scaling
**Effort:** Low
**Timeline:** 3 days

**Implementation:**
- Add Flask/FastAPI health endpoint
- Check TigerGraph connectivity
- Check workspace accessibility

#### 4. Implement Logging Infrastructure

**Status:** Console logging only
**Benefit:** Better debugging and audit trail
**Effort:** Medium
**Timeline:** 1 week

**Implementation:**
- Add structured JSON logging
- Integrate with ELK or Cloudwatch
- Add log aggregation

#### 5. Create Helm Charts

**Status:** No Kubernetes packaging
**Benefit:** Easy Kubernetes deployments
**Effort:** Medium
**Timeline:** 1 week

**Implementation:**
- Create Helm chart template
- Parameterize configurations
- Publish to chart repository

### Medium Priority Improvements

#### 6. Add Blue-Green Deployment

**Benefit:** Zero-downtime deployments
**Effort:** High
**Timeline:** 2 weeks

#### 7. Implement Circuit Breakers

**Benefit:** Better resilience to external failures
**Effort:** Medium
**Timeline:** 1 week

#### 8. Add Performance Testing

**Benefit:** Identify bottlenecks
**Effort:** Medium
**Timeline:** 1 week

#### 9. Create Runbooks

**Benefit:** Faster incident response
**Effort:** Low
**Timeline:** 3 days

#### 10. Setup Multi-Region Deployment

**Benefit:** High availability and disaster recovery
**Effort:** High
**Timeline:** 3 weeks

---

## Deployment Checklist

### Pre-Deployment

- [ ] Code review completed
- [ ] Tests passing
- [ ] Security scan completed
- [ ] Documentation updated
- [ ] Backup taken
- [ ] Rollback plan documented

### Deployment

- [ ] Deploy to staging environment
- [ ] Run smoke tests
- [ ] Deploy to production
- [ ] Monitor logs and metrics
- [ ] Verify health checks

### Post-Deployment

- [ ] Verify functionality
- [ ] Check error rates
- [ ] Monitor resource usage
- [ ] Update status page
- [ ] Send deployment notification

---

## Troubleshooting

### Common Issues

**Issue: Connection to TigerGraph fails**
```bash
# Check connectivity
curl -I $TG_URL

# Verify credentials
python -c "from geoanalysis.geoqb import GeoQbTG; \
    tg = GeoQbTG(...); print(tg.test_connection())"
```

**Issue: Out of memory**
```bash
# Check memory usage
free -h

# Reduce batch size in code
# or increase instance size
```

**Issue: Workspace permission errors**
```bash
# Fix permissions
sudo chown -R geoqb:geoqb $GEOQB_WORKSPACE
chmod 755 $GEOQB_WORKSPACE
```

---

**Document Version:** 1.0
**Last Updated:** 2024
**Maintained By:** GeoQB DevOps Team
