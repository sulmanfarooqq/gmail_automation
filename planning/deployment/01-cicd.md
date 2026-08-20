# Deployment & CI/CD Architecture

## Infrastructure as Code

### Terraform (Infrastructure)
```
terraform/
├── main.tf                 # Provider, backend
├── variables.tf
├── outputs.tf
├── modules/
│   ├── vps/                # Hetzner/Contabo server
│   ├── dns/                # Cloudflare/Namecheap records
│   ├── monitoring/         # Prometheus, Grafana, Loki
│   ├── object-storage/     # MinIO (or S3-compatible)
│   └── kubernetes/         # k3s cluster (Phase 2+)
└── environments/
    ├── dev/
    ├── staging/
    └── prod/
```

### Ansible (Configuration)
```
ansible/
├── inventory/
│   ├── dev.yml
│   ├── staging.yml
│   └── prod.yml
├── playbooks/
│   ├── bootstrap.yml       # Initial server setup
│   ├── mailu.yml           # Mail stack deployment
│   ├── application.yml     # App stack deployment
│   ├── ai-engine.yml       # AI service deployment
│   └── monitoring.yml      # Monitoring stack
├── roles/
│   ├── common/
│   ├── docker/
│   ├── traefik/
│   ├── mailu/
│   ├── postgres/
│   ├── redis/
│   ├── minio/
│   └── nodejs/
└── vault.yml               # Encrypted secrets
```

## Container Images

### Multi-stage Dockerfiles

**apps/webmail/Dockerfile**
```dockerfile
# Builder
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# Runner
FROM node:20-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production
COPY --from=builder /app/public ./public
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static
EXPOSE 3000
CMD ["node", "server.js"]
```

**ai-engine/Dockerfile**
```dockerfile
FROM python:3.11-slim AS builder
WORKDIR /app
COPY pyproject.toml poetry.lock ./
RUN pip install poetry && poetry export -f requirements.txt -o requirements.txt

FROM python:3.11-slim
WORKDIR /app
COPY --from=builder /app/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Image Building (GitHub Actions)
```yaml
# .github/workflows/docker.yml
jobs:
  build-webmail:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: docker/setup-buildx-action@v3
      - uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      - uses: docker/build-push-action@v5
        with:
          context: ./apps/webmail
          push: true
          tags: ghcr.io/org/webmail:${{ github.sha }},ghcr.io/org/webmail:latest
          cache-from: type=gha
          cache-to: type=gha,mode=max
  
  build-ai-engine:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: docker/setup-buildx-action@v3
      - uses: docker/login-action@v3
      - uses: docker/build-push-action@v5
        with:
          context: ./ai-engine
          push: true
          tags: ghcr.io/org/ai-engine:${{ github.sha }}
```

## Deployment Architecture

### Development (Docker Compose)
```
docker-compose.yml          # Full stack local
docker-compose.override.yml # Local overrides (ports, volumes)
```

### Staging/Production (k3s + ArgoCD)

```
┌─────────────────────────────────────────────────────────────┐
│                      GitHub (GitOps Repo)                    │
│  manifests/                                                 │
│  ├── base/              # Common K8s manifests              │
│  │   ├── namespace.yaml                                        │
│  │   ├── network-policies.yaml                               │
│  │   ├── rbac.yaml                                           │
│  │   └── sealed-secrets.yaml                                 │
│  ├── overlays/                                                  │
│  │   ├── dev/                                                 │
│  │   ├── staging/                                             │
│  │   └── prod/                                                │
│  └── applications/      # ArgoCD Application CRs              │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                      ArgoCD (GitOps Controller)              │
│  - Watches Git repo                                          │
│  - Syncs desired state to cluster                            │
│  - Auto-heal, rollback, history                              │
│  - RBAC, SSO, audit                                          │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                      k3s Cluster (3 nodes)                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │  Control     │  │  Worker 1    │  │  Worker 2    │       │
│  │  Plane       │  │  (apps)      │  │  (apps)      │       │
│  │              │  │              │  │              │       │
│  │  ArgoCD      │  │  Webmail x3  │  │  AI Engine x2│       │
│  │  Traefik     │  │  Admin x2    │  │  Worker x2   │       │
│  │  Cert-Manager│  │  Client x2   │  │  CronJobs    │       │
│  │  Prometheus  │  │  Postgres    │  │  Redis       │       │
│  │  Grafana     │  │  MinIO       │  │  MinIO       │       │
│  │  Loki        │  │              │  │              │       │
│  └──────────────┘  └──────────────┘  └──────────────┘       │
└─────────────────────────────────────────────────────────────┘
```

### Kubernetes Manifests (Kustomize)

**base/deployment.yaml**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: webmail
  labels:
    app: webmail
spec:
  replicas: 3
  selector:
    matchLabels:
      app: webmail
  template:
    metadata:
      labels:
        app: webmail
      annotations:
        prometheus.io/scrape: "true"
        prometheus.io/port: "3000"
    spec:
      securityContext:
        runAsNonRoot: true
        runAsUser: 1000
        fsGroup: 1000
      containers:
      - name: webmail
        image: ghcr.io/org/webmail:latest
        ports:
        - containerPort: 3000
        envFrom:
        - configMapRef:
            name: webmail-config
        - secretRef:
            name: webmail-secrets
        resources:
          requests:
            memory: "256Mi"
            cpu: "100m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 3000
          initialDelaySeconds: 10
          periodSeconds: 30
        readinessProbe:
          httpGet:
            path: /ready
            port: 3000
          initialDelaySeconds: 5
          periodSeconds: 10
```

**overlays/prod/kustomization.yaml**
```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
resources:
- ../../base
patches:
- patch: |-
    apiVersion: apps/v1
    kind: Deployment
    metadata:
      name: webmail
    spec:
      replicas: 5
images:
- name: ghcr.io/org/webmail
  newTag: v1.2.3  # Updated by CI
configMapGenerator:
- name: webmail-config
  literals:
  - NODE_ENV=production
  - LOG_LEVEL=info
secretGenerator:
- name: webmail-secrets
  envs:
  - .env.prod  # Not in git, mounted by ArgoCD
```

## CI/CD Pipeline

### GitHub Actions Workflow
```yaml
# .github/workflows/ci.yml
name: CI

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 20, cache: 'npm' }
      - run: npm ci
      - run: npm run lint
      - run: npm run typecheck
      - run: npm run format:check

  test-unit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 20, cache: 'npm' }
      - uses: actions/setup-python@v5
        with: { python-version: '3.11', cache: 'pip' }
      - run: npm ci && npm run test:unit
      - run: pip install -e ./ai-engine &
