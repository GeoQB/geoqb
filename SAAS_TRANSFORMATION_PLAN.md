# GeoQB SaaS Transformation Plan

**From CLI Tool to Production SaaS Platform**

---

## Executive Summary

**Goal:** Transform GeoQB into a production-ready SaaS platform with modern UI, user management, and cloud deployment on GCP.

**Timeline:** 2 weeks to MVP trial
**Budget:** $50k initial development
**Target:** 100 trial users, 10 paying customers in first month

---

## Current State vs. Target State

### Current State (CLI Tool)
- ❌ No web interface
- ❌ No user authentication
- ❌ No multi-tenancy
- ❌ No payment processing
- ❌ No usage tracking
- ❌ Manual deployment
- ❌ Limited monitoring
- ✅ Strong core functionality

### Target State (SaaS Platform)
- ✅ Modern web UI (React + Tailwind)
- ✅ Email-based authentication
- ✅ Multi-tenant architecture
- ✅ Stripe payment integration
- ✅ Usage metering & quotas
- ✅ Automated CI/CD to GCP
- ✅ Comprehensive monitoring
- ✅ API-first architecture

---

## Phase 1: Foundation (Week 1)

### Day 1-2: Backend API Development

**FastAPI Application Structure:**
```
geoqb-api/
├── app/
│   ├── main.py                 # FastAPI app
│   ├── config.py               # Configuration
│   ├── database.py             # DB setup
│   ├── models/                 # SQLAlchemy models
│   │   ├── user.py
│   │   ├── workspace.py
│   │   ├── layer.py
│   │   └── usage.py
│   ├── schemas/                # Pydantic schemas
│   │   ├── user.py
│   │   ├── layer.py
│   │   └── auth.py
│   ├── api/                    # API routes
│   │   ├── v1/
│   │   │   ├── auth.py         # Login, signup, tokens
│   │   │   ├── layers.py       # Layer CRUD
│   │   │   ├── analysis.py     # Run analysis
│   │   │   ├── workspaces.py   # Workspace management
│   │   │   └── billing.py      # Subscription & usage
│   ├── core/                   # Business logic
│   │   ├── security.py         # JWT, password hashing
│   │   ├── permissions.py      # RBAC
│   │   └── geoqb_engine.py     # GeoQB integration
│   ├── services/               # External integrations
│   │   ├── tigergraph.py
│   │   ├── stripe.py
│   │   └── email.py
│   └── middleware/
│       ├── auth.py
│       ├── rate_limit.py
│       └── usage_tracking.py
├── tests/                      # Test suite
├── alembic/                    # DB migrations
├── Dockerfile
├── requirements.txt
└── docker-compose.yml
```

**Key Endpoints:**

```python
# Authentication
POST   /api/v1/auth/signup
POST   /api/v1/auth/login
POST   /api/v1/auth/refresh
POST   /api/v1/auth/forgot-password
POST   /api/v1/auth/reset-password

# Users
GET    /api/v1/users/me
PATCH  /api/v1/users/me
DELETE /api/v1/users/me

# Workspaces
GET    /api/v1/workspaces
POST   /api/v1/workspaces
GET    /api/v1/workspaces/{id}
PATCH  /api/v1/workspaces/{id}
DELETE /api/v1/workspaces/{id}

# Layers
GET    /api/v1/layers
POST   /api/v1/layers
GET    /api/v1/layers/{id}
PATCH  /api/v1/layers/{id}
DELETE /api/v1/layers/{id}
POST   /api/v1/layers/{id}/ingest
GET    /api/v1/layers/{id}/status

# Analysis
POST   /api/v1/analysis/score-location
POST   /api/v1/analysis/find-optimal-locations
POST   /api/v1/analysis/cluster
GET    /api/v1/analysis/jobs/{id}

# Billing
GET    /api/v1/billing/subscription
POST   /api/v1/billing/subscription
PATCH  /api/v1/billing/subscription
GET    /api/v1/billing/usage
POST   /api/v1/billing/payment-methods
```

### Day 3-4: Frontend Development

**Tech Stack:**
- **Framework:** Next.js 14 (React + TypeScript)
- **Styling:** Tailwind CSS + shadcn/ui
- **State:** Zustand
- **Data Fetching:** TanStack Query (React Query)
- **Forms:** React Hook Form + Zod
- **Charts:** Recharts + deck.gl
- **Maps:** Mapbox GL JS

**Page Structure:**
```
geoqb-web/
├── app/
│   ├── (auth)/
│   │   ├── login/
│   │   ├── signup/
│   │   └── forgot-password/
│   ├── (dashboard)/
│   │   ├── layout.tsx           # Dashboard shell
│   │   ├── page.tsx             # Overview
│   │   ├── layers/              # Layer management
│   │   ├── analysis/            # Run analyses
│   │   ├── visualizations/      # Maps & charts
│   │   ├── settings/            # Account settings
│   │   └── billing/             # Subscription
│   ├── (marketing)/
│   │   ├── page.tsx             # Landing page
│   │   ├── pricing/
│   │   ├── docs/
│   │   └── about/
│   └── api/                     # API routes (proxies)
├── components/
│   ├── ui/                      # shadcn components
│   ├── maps/                    # Map components
│   ├── forms/                   # Form components
│   └── layouts/                 # Layout components
├── lib/
│   ├── api.ts                   # API client
│   ├── auth.ts                  # Auth helpers
│   └── utils.ts
└── public/
    └── animations/              # Lottie animations
```

**Landing Page Features:**
- Hero with animated background (particles.js or three.js)
- Product demo video/animation
- Feature showcase with icons
- Pricing table
- Social proof (testimonials, logos)
- CTA (Start Free Trial)

### Day 5: Authentication & User Management

**PostgreSQL Schema:**

```sql
-- Users table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    company VARCHAR(255),
    role VARCHAR(50) DEFAULT 'user',
    is_active BOOLEAN DEFAULT true,
    is_verified BOOLEAN DEFAULT false,
    verification_token VARCHAR(255),
    reset_token VARCHAR(255),
    reset_token_expires TIMESTAMP,
    plan VARCHAR(50) DEFAULT 'free',
    trial_ends_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Workspaces table
CREATE TABLE workspaces (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    storage_used_mb INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Layers table
CREATE TABLE layers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID REFERENCES workspaces(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    layer_type VARCHAR(50),
    tags JSONB,
    bbox JSONB,
    resolution INTEGER,
    status VARCHAR(50) DEFAULT 'pending',
    record_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Usage tracking
CREATE TABLE usage_events (
    id BIGSERIAL PRIMARY KEY,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    event_type VARCHAR(50) NOT NULL,
    resource_type VARCHAR(50),
    resource_id UUID,
    quantity INTEGER DEFAULT 1,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- API keys
CREATE TABLE api_keys (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    key_hash VARCHAR(255) NOT NULL,
    name VARCHAR(255),
    last_used_at TIMESTAMP,
    expires_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Subscriptions
CREATE TABLE subscriptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    stripe_customer_id VARCHAR(255),
    stripe_subscription_id VARCHAR(255),
    plan VARCHAR(50) NOT NULL,
    status VARCHAR(50) NOT NULL,
    current_period_start TIMESTAMP,
    current_period_end TIMESTAMP,
    cancel_at_period_end BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## Phase 2: SaaS Features (Week 2)

### Missing SaaS Features Analysis

| Feature | Priority | Status | Implementation |
|---------|----------|--------|----------------|
| **User Management** | CRITICAL | Missing | PostgreSQL + FastAPI |
| **Authentication** | CRITICAL | Missing | JWT + email verification |
| **Multi-tenancy** | CRITICAL | Missing | Workspace isolation |
| **Usage Metering** | HIGH | Missing | Event tracking + quotas |
| **Billing Integration** | HIGH | Missing | Stripe |
| **API Rate Limiting** | HIGH | Missing | Redis + middleware |
| **Web Dashboard** | HIGH | Missing | Next.js UI |
| **Payment Processing** | MEDIUM | Missing | Stripe Checkout |
| **Email Notifications** | MEDIUM | Missing | SendGrid/Postmark |
| **Usage Analytics** | MEDIUM | Missing | PostHog/Mixpanel |
| **Admin Panel** | MEDIUM | Missing | React Admin |
| **Webhooks** | LOW | Missing | FastAPI background tasks |
| **API Keys** | LOW | Missing | UUID tokens |
| **SSO** | LOW | Future | SAML/OAuth |

### Day 6-7: Tier System & Quotas

**Plan Structure:**

```python
# app/models/plans.py
from enum import Enum

class Plan(str, Enum):
    FREE = "free"
    PROFESSIONAL = "professional"
    BUSINESS = "business"
    ENTERPRISE = "enterprise"

PLAN_LIMITS = {
    Plan.FREE: {
        "layers": 3,
        "queries_per_month": 100,
        "api_calls_per_month": 1000,
        "storage_mb": 100,
        "concurrent_analyses": 1,
        "data_retention_days": 7,
    },
    Plan.PROFESSIONAL: {
        "layers": 25,
        "queries_per_month": 10000,
        "api_calls_per_month": 100000,
        "storage_mb": 10000,
        "concurrent_analyses": 5,
        "data_retention_days": 90,
    },
    Plan.BUSINESS: {
        "layers": 100,
        "queries_per_month": 100000,
        "api_calls_per_month": 1000000,
        "storage_mb": 100000,
        "concurrent_analyses": 20,
        "data_retention_days": 365,
    },
    Plan.ENTERPRISE: {
        "layers": -1,  # Unlimited
        "queries_per_month": -1,
        "api_calls_per_month": -1,
        "storage_mb": -1,
        "concurrent_analyses": -1,
        "data_retention_days": -1,
    }
}

PLAN_PRICES = {
    Plan.FREE: 0,
    Plan.PROFESSIONAL: 99,  # per month
    Plan.BUSINESS: 499,
    Plan.ENTERPRISE: None,  # Custom pricing
}
```

### Day 8-9: Testing Strategy

**Test Coverage Goals:**
- Unit tests: 90%+
- Integration tests: 80%+
- E2E tests: Critical user flows
- Load tests: 1000 concurrent users

**Test Structure:**

```
tests/
├── unit/
│   ├── test_auth.py
│   ├── test_layers.py
│   ├── test_permissions.py
│   └── test_usage_tracking.py
├── integration/
│   ├── test_api_endpoints.py
│   ├── test_database.py
│   └── test_tigergraph.py
├── e2e/
│   ├── test_signup_flow.py
│   ├── test_layer_creation.py
│   ├── test_analysis_flow.py
│   └── test_billing_flow.py
├── load/
│   ├── locustfile.py
│   └── k6_script.js
└── fixtures/
    └── test_data.py
```

### Day 10-12: GCP Deployment

**Architecture:**

```
┌─────────────────────────────────────────────────────┐
│                   Google Cloud Platform              │
│                                                       │
│  ┌──────────────────────────────────────────────┐  │
│  │     Cloud Load Balancer (HTTPS)              │  │
│  └──────────────────┬───────────────────────────┘  │
│                     │                                │
│  ┌──────────────────▼───────────────────────────┐  │
│  │     Cloud CDN (Static assets)                │  │
│  └──────────────────────────────────────────────┘  │
│                     │                                │
│  ┌──────────────────▼───────────────────────────┐  │
│  │     GKE Cluster (Kubernetes)                 │  │
│  │  ┌───────────────────────────────────────┐  │  │
│  │  │  Frontend (Next.js)                   │  │  │
│  │  │  - 3 replicas                         │  │  │
│  │  │  - HPA (2-10 pods)                    │  │  │
│  │  └───────────────────────────────────────┘  │  │
│  │  ┌───────────────────────────────────────┐  │  │
│  │  │  Backend API (FastAPI)                │  │  │
│  │  │  - 5 replicas                         │  │  │
│  │  │  - HPA (3-20 pods)                    │  │  │
│  │  └───────────────────────────────────────┘  │  │
│  │  ┌───────────────────────────────────────┐  │  │
│  │  │  Worker (Celery)                      │  │  │
│  │  │  - 3 replicas                         │  │  │
│  │  │  - HPA (2-10 pods)                    │  │  │
│  │  └───────────────────────────────────────┘  │  │
│  └──────────────────────────────────────────────┘  │
│                     │                                │
│  ┌──────────────────▼───────────────────────────┐  │
│  │     Cloud SQL (PostgreSQL)                   │  │
│  │     - HA configuration                       │  │
│  │     - Automatic backups                      │  │
│  └──────────────────────────────────────────────┘  │
│                     │                                │
│  ┌──────────────────▼───────────────────────────┐  │
│  │     Cloud Memorystore (Redis)                │  │
│  │     - Session storage                        │  │
│  │     - Rate limiting                          │  │
│  │     - Caching                                │  │
│  └──────────────────────────────────────────────┘  │
│                     │                                │
│  ┌──────────────────▼───────────────────────────┐  │
│  │     Cloud Storage (GCS)                      │  │
│  │     - User uploads                           │  │
│  │     - Generated files                        │  │
│  │     - Backups                                │  │
│  └──────────────────────────────────────────────┘  │
│                                                       │
│  ┌──────────────────────────────────────────────┐  │
│  │     Cloud Monitoring & Logging               │  │
│  │     - Metrics                                │  │
│  │     - Logs                                   │  │
│  │     - Alerts                                 │  │
│  └──────────────────────────────────────────────┘  │
└───────────────────────────────────────────────────────┘
                        │
                        ▼
              ┌──────────────────┐
              │  TigerGraph      │
              │  Cloud           │
              └──────────────────┘
```

### Day 13-14: CI/CD Implementation

**GitHub Actions Workflow:**

```yaml
# .github/workflows/deploy.yml
name: Deploy to GCP

on:
  push:
    branches: [main, staging]
  pull_request:
    branches: [main]

env:
  GCP_PROJECT_ID: geoqb-prod
  GKE_CLUSTER: geoqb-cluster
  GKE_ZONE: us-central1-a

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -r requirements-test.txt

      - name: Run tests
        run: |
          pytest --cov=app --cov-report=xml

      - name: Upload coverage
        uses: codecov/codecov-action@v3

  build:
    needs: test
    runs-on: ubuntu-latest
    if: github.event_name == 'push'

    steps:
      - uses: actions/checkout@v3

      - name: Set up Cloud SDK
        uses: google-github-actions/setup-gcloud@v1
        with:
          service_account_key: ${{ secrets.GCP_SA_KEY }}
          project_id: ${{ env.GCP_PROJECT_ID }}

      - name: Configure Docker
        run: gcloud auth configure-docker

      - name: Build images
        run: |
          docker build -t gcr.io/$GCP_PROJECT_ID/geoqb-api:$GITHUB_SHA ./api
          docker build -t gcr.io/$GCP_PROJECT_ID/geoqb-web:$GITHUB_SHA ./web

      - name: Push images
        run: |
          docker push gcr.io/$GCP_PROJECT_ID/geoqb-api:$GITHUB_SHA
          docker push gcr.io/$GCP_PROJECT_ID/geoqb-web:$GITHUB_SHA

  deploy:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'

    steps:
      - uses: actions/checkout@v3

      - name: Set up Cloud SDK
        uses: google-github-actions/setup-gcloud@v1
        with:
          service_account_key: ${{ secrets.GCP_SA_KEY }}
          project_id: ${{ env.GCP_PROJECT_ID }}

      - name: Get GKE credentials
        run: |
          gcloud container clusters get-credentials $GKE_CLUSTER \
            --zone $GKE_ZONE

      - name: Deploy to GKE
        run: |
          kubectl set image deployment/geoqb-api \
            geoqb-api=gcr.io/$GCP_PROJECT_ID/geoqb-api:$GITHUB_SHA
          kubectl set image deployment/geoqb-web \
            geoqb-web=gcr.io/$GCP_PROJECT_ID/geoqb-web:$GITHUB_SHA
          kubectl rollout status deployment/geoqb-api
          kubectl rollout status deployment/geoqb-web

      - name: Notify deployment
        uses: 8398a7/action-slack@v3
        with:
          status: ${{ job.status }}
          text: 'Deployment to production completed'
          webhook_url: ${{ secrets.SLACK_WEBHOOK }}
```

---

## UI/UX Design System

### Design Principles

1. **Clean & Modern**: Minimal clutter, generous whitespace
2. **Data-First**: Visualizations take center stage
3. **Fast**: Optimistic updates, skeleton loaders
4. **Accessible**: WCAG 2.1 AA compliance
5. **Mobile-Friendly**: Responsive design

### Color Palette

```css
/* Primary Colors */
--primary-50: #fff7ed;
--primary-500: #ff6b35;  /* TigerGraph Orange */
--primary-900: #7c2d12;

/* Secondary */
--secondary-500: #004e89;  /* Deep Blue */
--secondary-900: #001a33;

/* Accent */
--accent-500: #00d9ff;  /* Bright Cyan */

/* Neutrals */
--gray-50: #f9fafb;
--gray-500: #6b7280;
--gray-900: #111827;

/* Semantic */
--success: #10b981;
--warning: #f59e0b;
--error: #ef4444;
--info: #3b82f6;
```

### Component Library (shadcn/ui)

**Core Components:**
- Button (primary, secondary, ghost, link)
- Input, Textarea, Select
- Card, Dialog, Sheet
- Tabs, Accordion
- Table, Pagination
- Toast, Alert
- Badge, Avatar
- Dropdown Menu
- Command Palette (⌘K)

**Custom Components:**
- LayerCard (visual layer preview)
- MapViewer (interactive Mapbox)
- AnalysisResults (charts + insights)
- UsageMetrics (progress bars)
- PricingCard (tier selection)

### Key Screens

#### 1. Landing Page
```
[Hero Section with animated particles]
  - Headline: "Build Spatial Knowledge Graphs in Minutes"
  - Subheadline: "Multi-layer geospatial analysis powered by graph AI"
  - CTA: "Start Free Trial" | "Watch Demo"
  - Product screenshot/video

[Features Grid - 3 columns]
  - Multi-Layer Analysis
  - Graph Machine Learning
  - Real-Time Streaming

[How It Works - 3 steps]
  1. Define Layers
  2. Run Analysis
  3. Get Insights

[Pricing Table]
  Free | Professional | Business | Enterprise

[Social Proof]
  - Customer logos
  - Testimonials

[CTA Footer]
  - "Ready to Get Started?"
```

#### 2. Dashboard
```
[Top Nav]
  Logo | Search | Notifications | Profile

[Sidebar]
  - Overview
  - Layers
  - Analysis
  - Visualizations
  - Settings
  - Billing

[Main Content]
  [Stats Cards Row]
    Total Layers | Active Analyses | API Calls | Storage Used

  [Recent Activity]
    Timeline of layer creations, analyses run

  [Quick Actions]
    + Create Layer | Run Analysis | View Map
```

#### 3. Layer Creation
```
[Step 1: Define Layer]
  Name: [input]
  Type: [select: Amenity, Highway, Building, etc.]
  Tags: [key-value pairs]

[Step 2: Set Bounds]
  [Interactive map for bbox selection]
  OR
  [City/region autocomplete]

[Step 3: Configure]
  Resolution: [6, 9, 12]
  Data Source: [OSM Overpass, Sophox, Custom]

[Step 4: Review & Create]
  Preview of configuration
  Estimated records
  [Create Layer button]
```

#### 4. Analysis View
```
[Analysis Configuration Panel - Left]
  Layer Selection: [multi-select]
  Weights: [sliders per layer]
  Analysis Type: [dropdown]
  Advanced Options: [collapsible]
  [Run Analysis button]

[Results Panel - Right]
  [Map View - interactive]
  [Charts - accessibility scores, clusters]
  [Table - top locations]
  [Export - CSV, PDF, API]
```

---

## Technical Implementation Details

### Backend Stack

**Core:**
- **FastAPI** 0.104+
- **PostgreSQL** 15
- **SQLAlchemy** 2.0 (async)
- **Alembic** (migrations)
- **Redis** (caching, sessions)

**Auth:**
- **python-jose** (JWT)
- **passlib** (password hashing)
- **python-multipart** (file uploads)

**Integrations:**
- **pyTigerGraph** (graph database)
- **stripe** (payments)
- **sendgrid** (emails)
- **boto3** (GCS via S3 API)

**Testing:**
- **pytest** + **pytest-asyncio**
- **httpx** (async testing)
- **faker** (test data)
- **locust** (load testing)

### Frontend Stack

**Framework:**
- **Next.js** 14 (App Router)
- **React** 18
- **TypeScript** 5

**UI:**
- **Tailwind CSS** 3
- **shadcn/ui** components
- **Framer Motion** (animations)
- **Lucide Icons**

**State & Data:**
- **Zustand** (state management)
- **TanStack Query** (server state)
- **Zod** (validation)
- **React Hook Form** (forms)

**Visualization:**
- **Mapbox GL JS** (maps)
- **deck.gl** (3D visualization)
- **Recharts** (charts)
- **D3.js** (custom viz)

---

## Deployment Configuration

### Terraform Infrastructure

```hcl
# terraform/main.tf
terraform {
  required_version = ">= 1.0"

  backend "gcs" {
    bucket = "geoqb-terraform-state"
    prefix = "prod"
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

# GKE Cluster
resource "google_container_cluster" "primary" {
  name     = "geoqb-cluster"
  location = var.region

  initial_node_count       = 3
  remove_default_node_pool = true

  workload_identity_config {
    workload_pool = "${var.project_id}.svc.id.goog"
  }
}

resource "google_container_node_pool" "primary" {
  name       = "primary-pool"
  cluster    = google_container_cluster.primary.name
  node_count = 3

  autoscaling {
    min_node_count = 3
    max_node_count = 10
  }

  node_config {
    machine_type = "n2-standard-4"

    oauth_scopes = [
      "https://www.googleapis.com/auth/cloud-platform"
    ]

    labels = {
      environment = "production"
    }
  }
}

# Cloud SQL
resource "google_sql_database_instance" "main" {
  name             = "geoqb-db"
  database_version = "POSTGRES_15"
  region           = var.region

  settings {
    tier = "db-custom-4-15360"

    backup_configuration {
      enabled = true
      start_time = "03:00"
    }

    ip_configuration {
      ipv4_enabled = false
      private_network = google_compute_network.vpc.id
    }
  }
}

# Cloud Storage
resource "google_storage_bucket" "user_data" {
  name     = "${var.project_id}-user-data"
  location = var.region

  lifecycle_rule {
    condition {
      age = 90
    }
    action {
      type          = "SetStorageClass"
      storage_class = "NEARLINE"
    }
  }
}

# Cloud Memorystore (Redis)
resource "google_redis_instance" "cache" {
  name           = "geoqb-cache"
  tier           = "STANDARD_HA"
  memory_size_gb = 5
  region         = var.region
}
```

### Kubernetes Manifests

```yaml
# k8s/api-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: geoqb-api
  namespace: geoqb
spec:
  replicas: 5
  selector:
    matchLabels:
      app: geoqb-api
  template:
    metadata:
      labels:
        app: geoqb-api
    spec:
      containers:
      - name: api
        image: gcr.io/geoqb-prod/geoqb-api:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: geoqb-secrets
              key: database-url
        - name: REDIS_URL
          valueFrom:
            secretKeyRef:
              name: geoqb-secrets
              key: redis-url
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "2000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: geoqb-api-hpa
  namespace: geoqb
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: geoqb-api
  minReplicas: 3
  maxReplicas: 20
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

---

## Cost Estimates

### GCP Monthly Costs (Production)

| Service | Configuration | Monthly Cost |
|---------|---------------|--------------|
| GKE Cluster | 3-10 n2-standard-4 nodes | $400-1,200 |
| Cloud SQL | db-custom-4-15360 HA | $600 |
| Cloud Memorystore | 5GB Standard HA | $150 |
| Cloud Storage | 100GB + egress | $50 |
| Load Balancer | HTTPS | $20 |
| Cloud CDN | 1TB egress | $100 |
| Monitoring & Logging | Standard | $50 |
| **Total** | | **$1,370-2,170/month** |

### Third-Party Services

| Service | Plan | Monthly Cost |
|---------|------|--------------|
| Stripe | Payment processing | 2.9% + $0.30/txn |
| SendGrid | Email (50k/month) | $15 |
| TigerGraph Cloud | Shared instance | $0-500 |
| Mapbox | Maps (200k views) | $0-500 |
| PostHog | Analytics | $0 (self-hosted) |
| **Total** | | **$15-1,015/month** |

**Grand Total:** $1,385-3,185/month

**Break-even:** ~50 Professional users or ~10 Business users

---

## Success Metrics

### Week 1 Goals
- ✅ Backend API functional (all endpoints)
- ✅ Authentication working
- ✅ Database schema deployed
- ✅ Basic frontend UI
- ✅ Landing page live

### Week 2 Goals
- ✅ Full user flows working
- ✅ Payment integration complete
- ✅ GCP deployment automated
- ✅ 90%+ test coverage
- ✅ 100 trial signups

### Month 1 Goals
- 500 signups
- 50 active users (WAU)
- 10 paying customers
- $500 MRR
- <5% churn

---

## Risk Mitigation

### Technical Risks

| Risk | Mitigation |
|------|------------|
| TigerGraph downtime | Implement retry logic, circuit breakers |
| Data loss | Automated backups, replication |
| Security breach | Penetration testing, bug bounty |
| Performance issues | Load testing, CDN, caching |
| Cost overruns | Budget alerts, auto-scaling limits |

### Business Risks

| Risk | Mitigation |
|------|------------|
| Low adoption | Marketing campaign, free tier |
| High churn | Onboarding optimization, support |
| Competition | Focus on differentiators (graph ML) |
| Pricing too high/low | A/B testing, customer surveys |

---

## Next Steps

**Immediate (This Week):**
1. Review and approve this plan
2. Setup GCP project
3. Initialize git repositories (api, web, infra)
4. Begin backend API development
5. Design final UI mockups

**Week 1:**
6. Complete backend API
7. Build frontend components
8. Setup CI/CD pipeline
9. Deploy staging environment
10. Begin testing

**Week 2:**
11. Complete all user flows
12. Stripe integration
13. Production deployment
14. Soft launch to beta users
15. Collect feedback and iterate

---

**Status:** Ready to Begin
**Timeline:** 2 weeks to MVP
**Budget:** $50k initial + $2-3k/month operating
**Team:** 2 full-stack developers + 1 designer
