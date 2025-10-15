# Kubernetes Deployment Steps for Offline Dictionary API

This guide will walk you through deploying your FastAPI application to Kubernetes step by step.

## Prerequisites

### 1. Install Required Tools on Ubuntu Server

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
sudo apt install -y docker.io
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker $USER
newgrp docker

# Install kubectl
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl
kubectl version --client

# Install Minikube (for local cluster) OR use existing Kubernetes cluster
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube
```

## Step 1: Start Kubernetes Cluster

### Option A: Using Minikube (Local Development)
```bash
# Start Minikube
minikube start --driver=docker

# Verify cluster is running
kubectl get nodes
```

### Option B: Using Existing Kubernetes Cluster
```bash
# If you have an existing cluster, verify connection
kubectl cluster-info
kubectl get nodes
```

## Step 2: Build and Push Docker Image

```bash
# Navigate to your project directory
cd /path/to/your/offline-dictionary

# Login to Docker Hub (if not already logged in)
docker login

# Build the Docker image
docker build -t murali676/kubernetes_deployment:latest .

# Push to Docker Hub
docker push murali676/kubernetes_deployment:latest

# Verify the image was created and pushed
docker images | grep kubernetes_deployment
```

### Alternative: Use the automated script
```bash
# Make script executable
chmod +x scripts/build-and-push.sh

# Run the build and push script
./scripts/build-and-push.sh
```

## Step 3: Test Docker Image Locally (Optional)

```bash
# Test the image with docker-compose
docker-compose up -d

# Check if application is running
curl http://localhost:8099/health

# Stop the test
docker-compose down
```

## Step 4: Deploy to Kubernetes

### 4.1 Create Namespace
```bash
kubectl apply -f k8s/namespace.yaml
kubectl get namespaces
```

### 4.2 Deploy MongoDB
```bash
# Create persistent volume claim for MongoDB
kubectl apply -f k8s/mongodb-pvc.yaml

# Deploy MongoDB
kubectl apply -f k8s/mongodb-deployment.yaml

# Wait for MongoDB to be ready
kubectl wait --for=condition=ready pod -l app=mongodb -n offline-dictionary --timeout=300s

# Check MongoDB status
kubectl get pods -n offline-dictionary
kubectl get services -n offline-dictionary
```

### 4.3 Deploy Application Configuration
```bash
# Create ConfigMap
kubectl apply -f k8s/configmap.yaml

# Create Secret
kubectl apply -f k8s/secret.yaml

# Verify configuration
kubectl get configmap -n offline-dictionary
kubectl get secret -n offline-dictionary
```

### 4.4 Deploy FastAPI Application
```bash
# Deploy the application
kubectl apply -f k8s/app-deployment.yaml

# Deploy the service
kubectl apply -f k8s/app-service.yaml

# Wait for application to be ready
kubectl wait --for=condition=ready pod -l app=offline-dictionary -n offline-dictionary --timeout=300s
```

## Step 5: Verify Deployment

### 5.1 Check Pod Status
```bash
# Check all pods
kubectl get pods -n offline-dictionary

# Check pod details
kubectl describe pods -n offline-dictionary

# Check pod logs
kubectl logs -f deployment/offline-dictionary-app -n offline-dictionary
```

### 5.2 Check Services
```bash
# Check services
kubectl get services -n offline-dictionary

# Check service details
kubectl describe service offline-dictionary-service -n offline-dictionary
```

### 5.3 Test Application
```bash
# Port forward to access the application
kubectl port-forward service/offline-dictionary-service 8099:8099 -n offline-dictionary &

# Test the application
curl http://localhost:8099/health
curl http://localhost:8099/

# Test API documentation
curl http://localhost:8099/docs
```

## Step 6: Access Application

### 6.1 Using Port Forward (Development)
```bash
# Port forward in background
kubectl port-forward service/offline-dictionary-service 8099:8099 -n offline-dictionary &

# Access application
# Open browser: http://localhost:8099
# API docs: http://localhost:8099/docs
```

### 6.2 Using Ingress (Production)
```bash
# Deploy ingress controller (if not already installed)
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.8.2/deploy/static/provider/cloud/deploy.yaml

# Update ingress with your domain
# Edit k8s/app-service.yaml and update the host
kubectl apply -f k8s/app-service.yaml

# Check ingress
kubectl get ingress -n offline-dictionary
```

## Step 7: Monitoring and Management

### 7.1 Check Application Health
```bash
# Check pod health
kubectl get pods -n offline-dictionary -o wide

# Check resource usage
kubectl top pods -n offline-dictionary

# Check events
kubectl get events -n offline-dictionary --sort-by='.lastTimestamp'
```

### 7.2 Scale Application
```bash
# Scale to 3 replicas
kubectl scale deployment offline-dictionary-app --replicas=3 -n offline-dictionary

# Check scaling
kubectl get deployment offline-dictionary-app -n offline-dictionary
```

### 7.3 Update Application
```bash
# Update image
kubectl set image deployment/offline-dictionary-app offline-dictionary=offline-dictionary:v2.0.0 -n offline-dictionary

# Check rollout status
kubectl rollout status deployment/offline-dictionary-app -n offline-dictionary

# Rollback if needed
kubectl rollout undo deployment/offline-dictionary-app -n offline-dictionary
```

## Step 8: Troubleshooting

### 8.1 Common Issues

#### Pods Not Starting
```bash
# Check pod status
kubectl get pods -n offline-dictionary

# Check pod logs
kubectl logs <pod-name> -n offline-dictionary

# Check pod description
kubectl describe pod <pod-name> -n offline-dictionary
```

#### Database Connection Issues
```bash
# Check MongoDB logs
kubectl logs deployment/mongodb -n offline-dictionary

# Test MongoDB connection
kubectl exec -it deployment/mongodb -n offline-dictionary -- mongosh

# Check MongoDB service
kubectl get service mongodb-service -n offline-dictionary
```

#### Service Not Accessible
```bash
# Check service endpoints
kubectl get endpoints -n offline-dictionary

# Test service connectivity
kubectl run test-pod --image=busybox -it --rm -- nslookup offline-dictionary-service.offline-dictionary.svc.cluster.local
```

### 8.2 Debug Commands
```bash
# Get all resources
kubectl get all -n offline-dictionary

# Check persistent volumes
kubectl get pv,pvc -n offline-dictionary

# Check configmaps and secrets
kubectl get configmap,secret -n offline-dictionary

# Check ingress
kubectl get ingress -n offline-dictionary
```

## Step 9: Cleanup (Optional)

### 9.1 Remove Application
```bash
# Delete the entire namespace (removes everything)
kubectl delete namespace offline-dictionary

# Or delete individual resources
kubectl delete -f k8s/app-service.yaml
kubectl delete -f k8s/app-deployment.yaml
kubectl delete -f k8s/mongodb-deployment.yaml
kubectl delete -f k8s/mongodb-pvc.yaml
kubectl delete -f k8s/configmap.yaml
kubectl delete -f k8s/secret.yaml
kubectl delete -f k8s/namespace.yaml
```

### 9.2 Stop Minikube (if using)
```bash
# Stop Minikube
minikube stop

# Delete Minikube cluster
minikube delete
```

## Step 10: Production Considerations

### 10.1 Security
```bash
# Update secrets with proper values
kubectl edit secret offline-dictionary-secret -n offline-dictionary

# Generate new secret key
echo -n "your-new-secret-key" | base64
```

### 10.2 Resource Management
```bash
# Check resource usage
kubectl top nodes
kubectl top pods -n offline-dictionary

# Adjust resource limits in k8s/app-deployment.yaml if needed
```

### 10.3 Backup
```bash
# Backup MongoDB data
kubectl exec -it deployment/mongodb -n offline-dictionary -- mongodump --db offline --out /backup

# Copy backup to local machine
kubectl cp offline-dictionary/mongodb-pod:/backup ./mongodb-backup
```

## Quick Reference Commands

```bash
# Check everything
kubectl get all -n offline-dictionary

# Access application
kubectl port-forward service/offline-dictionary-service 8099:8099 -n offline-dictionary

# View logs
kubectl logs -f deployment/offline-dictionary-app -n offline-dictionary

# Scale application
kubectl scale deployment offline-dictionary-app --replicas=3 -n offline-dictionary

# Update application
kubectl set image deployment/offline-dictionary-app offline-dictionary=offline-dictionary:latest -n offline-dictionary
```

## Success Indicators

✅ **Pods are running**: `kubectl get pods -n offline-dictionary` shows all pods as "Running"  
✅ **Services are available**: `kubectl get services -n offline-dictionary` shows services  
✅ **Application responds**: `curl http://localhost:8099/health` returns healthy status  
✅ **Database connected**: Application logs show successful database connection  
✅ **API accessible**: `curl http://localhost:8099/docs` returns API documentation  

Your FastAPI application is now successfully deployed on Kubernetes! 🎉
