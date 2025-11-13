# GeoQB SaaS Implementation Guide

**Quick Reference for Building the Production Platform**

This guide provides immediate next steps and code templates for implementing the full SaaS platform.

---

## 🚀 Quick Start (2-Week Sprint)

### Day 1: Project Setup

```bash
# 1. Create project structure
cd /home/user/geoqb
mkdir -p {geoqb-api,geoqb-web,terraform,.github/workflows}

# 2. Initialize backend
cd geoqb-api
python3 -m venv venv
source venv/bin/activate
pip install fastapi[all] sqlalchemy alembic python-jose[cryptography] passlib[bcrypt] python-multipart stripe sendgrid redis

# 3. Initialize frontend
cd ../geoqb-web
npx create-next-app@latest . --typescript --tailwind --app --no-src-dir
npm install @tanstack/react-query zustand framer-motion mapbox-gl recharts shadcn-ui

# 4. Setup GCP
gcloud init
gcloud config set project geoqb-prod
gcloud services enable container.googleapis.com sqladmin.googleapis.com redis.googleapis.com

# 5. Setup Terraform
cd ../terraform
terraform init
```

---

## 📁 Critical File Templates

### 1. Backend API Entry Point

**File:** `geoqb-api/app/main.py`

```python
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
import os

# Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# FastAPI app
app = FastAPI(
    title="GeoQB API",
    description="Spatial Knowledge Graph Platform",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://geoqb.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")

# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Auth utilities
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise credentials_exception
    return user

# Routes
from app.api.v1 import auth, layers, analysis, billing

app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(layers.router, prefix="/api/v1/layers", tags=["layers"])
app.include_router(analysis.router, prefix="/api/v1/analysis", tags=["analysis"])
app.include_router(billing.router, prefix="/api/v1/billing", tags=["billing"])

@app.get("/")
def root():
    return {"message": "GeoQB API", "version": "1.0.0", "status": "operational"}

@app.get("/health")
def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

---

### 2. Authentication Endpoints

**File:** `geoqb-api/app/api/v1/auth.py`

```python
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from app.database import get_db
from app.models import User
from app.main import get_password_hash, verify_password, create_access_token
import uuid

router = APIRouter()

class UserSignup(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    company: str = None

class UserResponse(BaseModel):
    id: str
    email: str
    full_name: str
    company: str
    plan: str
    created_at: str

@router.post("/signup", response_model=UserResponse)
async def signup(user_data: UserSignup, db: Session = Depends(get_db)):
    # Check if user exists
    existing = db.query(User).filter(User.email == user_data.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Create user
    user = User(
        id=str(uuid.uuid4()),
        email=user_data.email,
        password_hash=get_password_hash(user_data.password),
        full_name=user_data.full_name,
        company=user_data.company,
        plan="free"
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # Send verification email (TODO)

    return user

@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer", "user": user}

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    return current_user
```

---

### 3. Database Models

**File:** `geoqb-api/app/models.py`

```python
from sqlalchemy import Column, String, Integer, Boolean, DateTime, JSON, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255))
    company = Column(String(255))
    role = Column(String(50), default="user")
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    plan = Column(String(50), default="free")
    trial_ends_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    workspaces = relationship("Workspace", back_populates="user")
    usage_events = relationship("UsageEvent", back_populates="user")

class Workspace(Base):
    __tablename__ = "workspaces"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"))
    name = Column(String(255), nullable=False)
    description = Column(Text)
    storage_used_mb = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="workspaces")
    layers = relationship("Layer", back_populates="workspace")

class Layer(Base):
    __tablename__ = "layers"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    workspace_id = Column(String, ForeignKey("workspaces.id", ondelete="CASCADE"))
    name = Column(String(255), nullable=False)
    layer_type = Column(String(50))
    tags = Column(JSON)
    bbox = Column(JSON)
    resolution = Column(Integer)
    status = Column(String(50), default="pending")
    record_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    workspace = relationship("Workspace", back_populates="layers")

class UsageEvent(Base):
    __tablename__ = "usage_events"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"))
    event_type = Column(String(50), nullable=False)
    resource_type = Column(String(50))
    resource_id = Column(String)
    quantity = Column(Integer, default=1)
    metadata = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="usage_events")
```

---

### 4. Frontend Landing Page

**File:** `geoqb-web/app/page.tsx`

```typescript
'use client';

import { motion } from 'framer-motion';
import Link from 'link';
import { Sparkles, Layers, Zap, Globe } from 'lucide-react';

export default function HomePage() {
  return (
    <main className="min-h-screen bg-gradient-to-br from-gray-900 via-blue-900 to-gray-900">
      {/* Hero Section */}
      <section className="relative min-h-screen flex items-center justify-center overflow-hidden">
        {/* Animated Background */}
        <div className="absolute inset-0">
          <div className="absolute inset-0 bg-[url('/grid.svg')] opacity-20" />
          {/* Particle animation here */}
        </div>

        {/* Content */}
        <div className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-32 text-center">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
          >
            <h1 className="text-5xl md:text-7xl font-bold text-white mb-6">
              Build Spatial Knowledge Graphs{' '}
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-cyan-400">
                in Minutes
              </span>
            </h1>

            <p className="text-xl md:text-2xl text-gray-300 mb-12 max-w-3xl mx-auto">
              Multi-layer geospatial analysis powered by graph AI.
              From data to insights, faster than ever before.
            </p>

            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link href="/signup">
                <motion.button
                  className="px-8 py-4 bg-gradient-to-r from-blue-500 to-cyan-500 text-white rounded-lg font-semibold text-lg hover:shadow-2xl transition-shadow"
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                >
                  Start Free Trial
                </motion.button>
              </Link>

              <motion.button
                className="px-8 py-4 bg-white/10 backdrop-blur-lg text-white rounded-lg font-semibold text-lg border border-white/20 hover:bg-white/20 transition-colors"
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
              >
                Watch Demo
              </motion.button>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 bg-gray-900">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <motion.div
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            transition={{ duration: 0.6 }}
            className="text-center mb-16"
          >
            <h2 className="text-4xl font-bold text-white mb-4">
              Everything You Need
            </h2>
            <p className="text-xl text-gray-400">
              Powerful features for spatial analysis at any scale
            </p>
          </motion.div>

          <div className="grid md:grid-cols-3 gap-8">
            {[
              {
                icon: Layers,
                title: 'Multi-Layer Analysis',
                description: 'Combine data from OpenStreetMap, demographics, and custom sources in a unified graph'
              },
              {
                icon: Sparkles,
                title: 'Graph Machine Learning',
                description: 'Discover patterns with Node2Vec, clustering, and community detection algorithms'
              },
              {
                icon: Zap,
                title: 'Real-Time Streaming',
                description: 'Process live sensor data and events with Apache Kafka integration'
              },
            ].map((feature, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.2 }}
                className="p-8 bg-white/5 backdrop-blur-lg rounded-xl border border-white/10 hover:border-white/20 transition-colors"
              >
                <feature.icon className="w-12 h-12 text-blue-400 mb-4" />
                <h3 className="text-2xl font-semibold text-white mb-2">
                  {feature.title}
                </h3>
                <p className="text-gray-400">
                  {feature.description}
                </p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Pricing Section */}
      <section className="py-20 bg-gray-800">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-white mb-4">
              Simple, Transparent Pricing
            </h2>
            <p className="text-xl text-gray-400">
              Start free, scale as you grow
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            {[
              { name: 'Free', price: '$0', features: ['3 layers', '100 queries/month', 'Community support'] },
              { name: 'Professional', price: '$99', features: ['25 layers', '10k queries/month', 'Email support', 'API access'] },
              { name: 'Business', price: '$499', features: ['100 layers', '100k queries/month', 'Priority support', 'Custom integrations'] },
            ].map((plan, index) => (
              <motion.div
                key={index}
                whileHover={{ scale: 1.05 }}
                className="p-8 bg-white/5 backdrop-blur-lg rounded-xl border border-white/10"
              >
                <h3 className="text-2xl font-bold text-white mb-2">{plan.name}</h3>
                <p className="text-4xl font-bold text-blue-400 mb-6">
                  {plan.price}<span className="text-sm text-gray-400">/month</span>
                </p>
                <ul className="space-y-3 mb-8">
                  {plan.features.map((feature, i) => (
                    <li key={i} className="text-gray-300 flex items-center">
                      <svg className="w-5 h-5 mr-2 text-green-400" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                      </svg>
                      {feature}
                    </li>
                  ))}
                </ul>
                <button className="w-full py-3 bg-blue-500 text-white rounded-lg font-semibold hover:bg-blue-600 transition-colors">
                  Get Started
                </button>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-gradient-to-r from-blue-600 to-cyan-600">
        <div className="max-w-4xl mx-auto text-center px-4">
          <h2 className="text-4xl font-bold text-white mb-6">
            Ready to Get Started?
          </h2>
          <p className="text-xl text-white/90 mb-8">
            Join hundreds of developers building spatial knowledge graphs
          </p>
          <Link href="/signup">
            <motion.button
              className="px-12 py-4 bg-white text-blue-600 rounded-lg font-bold text-lg hover:shadow-2xl transition-shadow"
              whileHover={{ scale: 1.05 }}
            >
              Start Your Free Trial
            </motion.button>
          </Link>
        </div>
      </section>
    </main>
  );
}
```

---

### 5. Docker Configuration

**File:** `geoqb-api/Dockerfile`

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create non-root user
RUN useradd -m -u 1000 geoqb && chown -R geoqb:geoqb /app
USER geoqb

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

### 6. CI/CD Workflow

**File:** `.github/workflows/deploy-gcp.yml`

```yaml
name: Deploy to GCP

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

env:
  GCP_PROJECT_ID: geoqb-prod
  GKE_CLUSTER: geoqb-cluster
  GKE_ZONE: us-central1-a
  IMAGE: geoqb-api

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
          cd geoqb-api
          pip install -r requirements.txt
          pip install pytest pytest-cov httpx

      - name: Run tests
        run: |
          cd geoqb-api
          pytest --cov=app tests/

  build-and-deploy:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'

    steps:
      - uses: actions/checkout@v3

      - name: Setup Cloud SDK
        uses: google-github-actions/setup-gcloud@v1
        with:
          service_account_key: ${{ secrets.GCP_SA_KEY }}
          project_id: ${{ env.GCP_PROJECT_ID }}

      - name: Configure Docker
        run: gcloud auth configure-docker

      - name: Build
        run: |
          cd geoqb-api
          docker build -t gcr.io/$GCP_PROJECT_ID/$IMAGE:$GITHUB_SHA .

      - name: Push
        run: docker push gcr.io/$GCP_PROJECT_ID/$IMAGE:$GITHUB_SHA

      - name: Get GKE credentials
        run: |
          gcloud container clusters get-credentials $GKE_CLUSTER \
            --zone $GKE_ZONE

      - name: Deploy
        run: |
          kubectl set image deployment/geoqb-api \
            geoqb-api=gcr.io/$GCP_PROJECT_ID/$IMAGE:$GITHUB_SHA
          kubectl rollout status deployment/geoqb-api
```

---

### 7. Test Suite

**File:** `geoqb-api/tests/test_auth.py`

```python
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import Base, engine, SessionLocal
from app.models import User

client = TestClient(app)

# Setup test database
@pytest.fixture(scope="module")
def test_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

def test_signup(test_db):
    response = client.post(
        "/api/v1/auth/signup",
        json={
            "email": "test@example.com",
            "password": "testpassword123",
            "full_name": "Test User"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"
    assert "id" in data

def test_login(test_db):
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "test@example.com",
            "password": "testpassword123"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_get_current_user(test_db):
    # Login first
    login_response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "test@example.com",
            "password": "testpassword123"
        }
    )
    token = login_response.json()["access_token"]

    # Get user info
    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"
```

---

## 🚀 Deployment Steps

### 1. Setup GCP Project

```bash
# Create project
gcloud projects create geoqb-prod --name="GeoQB Production"
gcloud config set project geoqb-prod

# Enable APIs
gcloud services enable \
  container.googleapis.com \
  sqladmin.googleapis.com \
  redis.googleapis.com \
  storage-api.googleapis.com

# Create GKE cluster
gcloud container clusters create geoqb-cluster \
  --zone us-central1-a \
  --num-nodes 3 \
  --machine-type n2-standard-4 \
  --enable-autoscaling \
  --min-nodes 3 \
  --max-nodes 10

# Create Cloud SQL instance
gcloud sql instances create geoqb-db \
  --database-version=POSTGRES_15 \
  --tier=db-custom-4-15360 \
  --region=us-central1 \
  --backup-start-time=03:00

# Create database
gcloud sql databases create geoqb --instance=geoqb-db

# Create Redis instance
gcloud redis instances create geoqb-cache \
  --size=5 \
  --region=us-central1 \
  --redis-version=redis_7_0
```

### 2. Deploy Application

```bash
# Build and push Docker image
cd geoqb-api
docker build -t gcr.io/geoqb-prod/geoqb-api:latest .
docker push gcr.io/geoqb-prod/geoqb-api:latest

# Apply Kubernetes manifests
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/secrets.yaml
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
kubectl apply -f k8s/ingress.yaml

# Check deployment
kubectl get pods -n geoqb
kubectl logs -f deployment/geoqb-api -n geoqb
```

### 3. Setup Domain & SSL

```bash
# Reserve static IP
gcloud compute addresses create geoqb-ip \
  --global

# Get IP address
gcloud compute addresses describe geoqb-ip \
  --global \
  --format="get(address)"

# Point DNS A record to this IP

# SSL certificate (auto-provisioned by GKE Ingress)
# or use cert-manager
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml
```

---

## 📊 Monitoring Setup

### Prometheus + Grafana

```bash
# Install Prometheus
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm install prometheus prometheus-community/kube-prometheus-stack

# Access Grafana
kubectl port-forward svc/prometheus-grafana 3000:80

# Login: admin / prom-operator
```

### Cloud Monitoring

```bash
# Enable Cloud Monitoring
gcloud services enable monitoring.googleapis.com

# Create alert policy
gcloud alpha monitoring policies create \
  --notification-channels=EMAIL_CHANNEL_ID \
  --display-name="API Error Rate" \
  --condition-display-name="Error rate > 5%" \
  --condition-threshold-value=0.05
```

---

## 🔐 Security Checklist

- [ ] Change all default passwords
- [ ] Setup secrets in GCP Secret Manager
- [ ] Enable Cloud Armor (DDoS protection)
- [ ] Configure VPC with private subnets
- [ ] Enable audit logging
- [ ] Setup IAM roles properly
- [ ] Enable binary authorization
- [ ] Configure network policies
- [ ] Setup backup and disaster recovery
- [ ] Run security scan (GCP Security Command Center)

---

## 📈 Success Metrics

Track these KPIs:

**Technical:**
- API response time (p95 < 200ms)
- Error rate (< 0.1%)
- Uptime (> 99.9%)
- Test coverage (> 90%)

**Business:**
- Signups per day
- Activation rate (first layer created)
- Conversion rate (trial → paid)
- Monthly recurring revenue (MRR)
- Customer acquisition cost (CAC)

---

## 🆘 Support

**Issues:**
- GitHub Issues: https://github.com/GeoQB/geoqb/issues
- Email: support@geoqb.com

**Documentation:**
- API Docs: https://api.geoqb.com/docs
- User Guide: https://docs.geoqb.com

---

**Last Updated:** 2024
**Status:** Implementation Ready
**Timeline:** 2 weeks to production
