# AquaForesee Deployment Guide

This guide covers deployment options for the AquaForesee application in various environments.

## Quick Local Deployment

### Using Docker Compose (Recommended)

```bash
# Clone the repository
git clone <repository-url>
cd aquaforesee

# Start all services
docker-compose up -d

# Access the application
# Frontend: http://localhost:3000
# Backend: http://localhost:8000
# Database: localhost:5432
```

### Manual Setup

```bash
# Run the automated setup script
python setup.py

# Or follow manual steps:
# 1. Setup backend
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# 2. Setup frontend
cd ../frontend
npm install

# 3. Setup database
docker-compose up -d postgres

# 4. Train ML models
cd ../
python ml_models/train_model.py

# 5. Start services
# Terminal 1: Backend
cd backend
python main.py

# Terminal 2: Frontend
cd frontend
npm start
```

## Cloud Deployment

### AWS Deployment

#### Architecture

- **Frontend**: S3 + CloudFront
- **Backend**: ECS Fargate or EC2
- **Database**: RDS PostgreSQL with PostGIS
- **Load Balancer**: Application Load Balancer

#### Step-by-Step AWS Deployment

1. **Database Setup (RDS)**

```bash
# Create RDS PostgreSQL instance
aws rds create-db-instance \
  --db-instance-identifier aquaforesee-db \
  --db-instance-class db.t3.micro \
  --engine postgres \
  --master-username postgres \
  --master-user-password your-password \
  --allocated-storage 20 \
  --vpc-security-group-ids sg-xxxxxxxx
```

2. **Backend Deployment (ECS)**

```dockerfile
# Build and push Docker image
docker build -t aquaforesee-backend ./backend
docker tag aquaforesee-backend:latest your-account.dkr.ecr.region.amazonaws.com/aquaforesee-backend:latest
docker push your-account.dkr.ecr.region.amazonaws.com/aquaforesee-backend:latest
```

3. **Frontend Deployment (S3 + CloudFront)**

```bash
# Build frontend
cd frontend
npm run build

# Deploy to S3
aws s3 sync build/ s3://your-bucket-name --delete

# Create CloudFront distribution
aws cloudfront create-distribution --distribution-config file://cloudfront-config.json
```

### Google Cloud Platform (GCP)

#### Architecture

- **Frontend**: Cloud Storage + Cloud CDN
- **Backend**: Cloud Run or GKE
- **Database**: Cloud SQL PostgreSQL

#### GCP Deployment Commands

```bash
# Enable required APIs
gcloud services enable run.googleapis.com
gcloud services enable sql-component.googleapis.com

# Create Cloud SQL instance
gcloud sql instances create aquaforesee-db \
  --database-version=POSTGRES_13 \
  --tier=db-f1-micro \
  --region=us-central1

# Deploy backend to Cloud Run
gcloud run deploy aquaforesee-backend \
  --image gcr.io/your-project/aquaforesee-backend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

### Azure Deployment

#### Architecture

- **Frontend**: Azure Static Web Apps
- **Backend**: Azure Container Instances or App Service
- **Database**: Azure Database for PostgreSQL

#### Azure Deployment Commands

```bash
# Create resource group
az group create --name aquaforesee-rg --location eastus

# Create PostgreSQL server
az postgres server create \
  --resource-group aquaforesee-rg \
  --name aquaforesee-db \
  --location eastus \
  --admin-user postgres \
  --admin-password your-password \
  --sku-name B_Gen5_1

# Deploy backend to Container Instances
az container create \
  --resource-group aquaforesee-rg \
  --name aquaforesee-backend \
  --image your-registry/aquaforesee-backend:latest \
  --ports 8000 \
  --environment-variables DATABASE_URL=your-connection-string
```

## Kubernetes Deployment

### Prerequisites

- Kubernetes cluster (local or cloud)
- kubectl configured
- Docker images built and pushed to registry

### Deployment Files

#### Backend Deployment

```yaml
# k8s/backend-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: aquaforesee-backend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: aquaforesee-backend
  template:
    metadata:
      labels:
        app: aquaforesee-backend
    spec:
      containers:
        - name: backend
          image: your-registry/aquaforesee-backend:latest
          ports:
            - containerPort: 8000
          env:
            - name: DATABASE_URL
              valueFrom:
                secretKeyRef:
                  name: aquaforesee-secrets
                  key: database-url
---
apiVersion: v1
kind: Service
metadata:
  name: aquaforesee-backend-service
spec:
  selector:
    app: aquaforesee-backend
  ports:
    - port: 8000
      targetPort: 8000
  type: LoadBalancer
```

#### Frontend Deployment

```yaml
# k8s/frontend-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: aquaforesee-frontend
spec:
  replicas: 2
  selector:
    matchLabels:
      app: aquaforesee-frontend
  template:
    metadata:
      labels:
        app: aquaforesee-frontend
    spec:
      containers:
        - name: frontend
          image: your-registry/aquaforesee-frontend:latest
          ports:
            - containerPort: 3000
---
apiVersion: v1
kind: Service
metadata:
  name: aquaforesee-frontend-service
spec:
  selector:
    app: aquaforesee-frontend
  ports:
    - port: 80
      targetPort: 3000
  type: LoadBalancer
```

#### Database Deployment

```yaml
# k8s/postgres-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: postgres
spec:
  replicas: 1
  selector:
    matchLabels:
      app: postgres
  template:
    metadata:
      labels:
        app: postgres
    spec:
      containers:
        - name: postgres
          image: postgis/postgis:15-3.3
          env:
            - name: POSTGRES_DB
              value: aquaforesee
            - name: POSTGRES_USER
              value: postgres
            - name: POSTGRES_PASSWORD
              valueFrom:
                secretKeyRef:
                  name: aquaforesee-secrets
                  key: postgres-password
          ports:
            - containerPort: 5432
          volumeMounts:
            - name: postgres-storage
              mountPath: /var/lib/postgresql/data
      volumes:
        - name: postgres-storage
          persistentVolumeClaim:
            claimName: postgres-pvc
---
apiVersion: v1
kind: Service
metadata:
  name: postgres-service
spec:
  selector:
    app: postgres
  ports:
    - port: 5432
      targetPort: 5432
```

### Deploy to Kubernetes

```bash
# Create secrets
kubectl create secret generic aquaforesee-secrets \
  --from-literal=database-url="postgresql://postgres:password@postgres-service:5432/aquaforesee" \
  --from-literal=postgres-password="your-password"

# Apply deployments
kubectl apply -f k8s/postgres-deployment.yaml
kubectl apply -f k8s/backend-deployment.yaml
kubectl apply -f k8s/frontend-deployment.yaml

# Check status
kubectl get pods
kubectl get services
```

## Production Considerations

### Security

- Use HTTPS/TLS certificates
- Implement proper authentication and authorization
- Set up API rate limiting
- Use secrets management for sensitive data
- Enable CORS properly
- Implement input validation and sanitization

### Performance

- Set up CDN for static assets
- Implement caching strategies
- Use connection pooling for database
- Optimize Docker images
- Set up horizontal pod autoscaling (K8s)

### Monitoring and Logging

- Set up application monitoring (Prometheus, Grafana)
- Implement centralized logging (ELK stack)
- Set up health checks and alerts
- Monitor database performance
- Track API response times

### Backup and Recovery

- Set up automated database backups
- Implement disaster recovery procedures
- Test backup restoration regularly
- Document recovery procedures

### Environment Variables

#### Production Environment Variables

```bash
# Backend
DATABASE_URL=postgresql://user:password@host:5432/aquaforesee
API_HOST=0.0.0.0
API_PORT=8000
LOG_LEVEL=INFO
SECRET_KEY=your-production-secret-key

# Frontend
REACT_APP_API_URL=https://api.yourdomain.com
REACT_APP_ENVIRONMENT=production
```

### SSL/TLS Configuration

#### Nginx Configuration

```nginx
server {
    listen 443 ssl;
    server_name yourdomain.com;

    ssl_certificate /path/to/certificate.crt;
    ssl_certificate_key /path/to/private.key;

    location / {
        proxy_pass http://frontend:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /api {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## Troubleshooting

### Common Issues

1. **Database Connection Issues**

   - Check connection string format
   - Verify network connectivity
   - Ensure PostGIS extension is installed

2. **CORS Issues**

   - Verify CORS settings in backend
   - Check frontend API URL configuration

3. **Memory Issues**

   - Increase container memory limits
   - Optimize ML model loading

4. **Performance Issues**
   - Check database query performance
   - Monitor API response times
   - Optimize frontend bundle size

### Health Checks

```bash
# Backend health check
curl http://localhost:8000/

# Database connectivity
curl http://localhost:8000/api/regions

# Frontend accessibility
curl http://localhost:3000/
```

## Scaling Considerations

### Horizontal Scaling

- Use load balancers for multiple backend instances
- Implement session management for stateless backends
- Use CDN for frontend static assets
- Consider database read replicas

### Vertical Scaling

- Monitor resource usage
- Adjust container resource limits
- Optimize database configuration
- Tune ML model performance

This deployment guide provides comprehensive options for deploying AquaForesee in various environments, from local development to production cloud deployments.
