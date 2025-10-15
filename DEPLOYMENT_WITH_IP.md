# Kubernetes Deployment with IP Address (142.93.216.4)

This guide shows how to deploy your FastAPI application to Kubernetes using your server IP address `142.93.216.4`.

## Prerequisites

Make sure you have:
- Kubernetes cluster running on your server (IP: 142.93.216.4)
- Docker installed and running
- kubectl configured to access your cluster

## Step 1: Build and Push Docker Image

```bash
# Login to Docker Hub
docker login

# Build and push image
docker build -t murali676/kubernetes_deployment:latest .
docker push murali676/kubernetes_deployment:latest
```

## Step 2: Deploy to Kubernetes

### Option A: Using NodePort (Recommended for IP access)

```bash
# Deploy all components
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/mongodb-pvc.yaml
kubectl apply -f k8s/mongodb-deployment.yaml
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/secret.yaml
kubectl apply -f k8s/app-deployment.yaml

# Use NodePort service for external access
kubectl apply -f k8s/app-service-nodeport.yaml
```

### Option B: Using LoadBalancer (If supported by your cloud provider)

```bash
# Deploy all components
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/mongodb-pvc.yaml
kubectl apply -f k8s/mongodb-deployment.yaml
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/secret.yaml
kubectl apply -f k8s/app-deployment.yaml

# Use LoadBalancer service
kubectl apply -f k8s/app-service-loadbalancer.yaml
```

### Option C: Using Ingress with IP

```bash
# Deploy all components
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/mongodb-pvc.yaml
kubectl apply -f k8s/mongodb-deployment.yaml
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/secret.yaml
kubectl apply -f k8s/app-deployment.yaml

# Install NGINX Ingress Controller
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.8.2/deploy/static/provider/cloud/deploy.yaml

# Deploy with ingress
kubectl apply -f k8s/app-service.yaml
```

## Step 3: Access Your Application

### Using NodePort (Port 30080)
```bash
# Check service status
kubectl get services -n offline-dictionary

# Access your application
curl http://142.93.216.4:30080/health
curl http://142.93.216.4:30080/docs
```

### Using LoadBalancer
```bash
# Check external IP
kubectl get services -n offline-dictionary

# Access your application (replace EXTERNAL-IP with actual IP)
curl http://EXTERNAL-IP:8099/health
curl http://EXTERNAL-IP:8099/docs
```

### Using Ingress
```bash
# Access your application
curl http://142.93.216.4/health
curl http://142.93.216.4/docs
```

## Step 4: Verify Deployment

```bash
# Check all resources
kubectl get all -n offline-dictionary

# Check pods
kubectl get pods -n offline-dictionary

# Check services
kubectl get services -n offline-dictionary

# Check logs
kubectl logs -f deployment/offline-dictionary-app -n offline-dictionary
```

## Step 5: Firewall Configuration

Make sure your server firewall allows traffic on the required ports:

```bash
# For NodePort (port 30080)
sudo ufw allow 30080

# For LoadBalancer (port 8099)
sudo ufw allow 8099

# For Ingress (port 80)
sudo ufw allow 80
sudo ufw allow 443
```

## Step 6: Test Your Application

### Health Check
```bash
curl http://142.93.216.4:30080/health
```

### API Documentation
```bash
# Open in browser
http://142.93.216.4:30080/docs
```

### API Endpoints
```bash
# Root endpoint
curl http://142.93.216.4:30080/

# Health check
curl http://142.93.216.4:30080/health

# API documentation
curl http://142.93.216.4:30080/docs
```

## Troubleshooting

### Check Service Status
```bash
kubectl get services -n offline-dictionary
kubectl describe service offline-dictionary-service -n offline-dictionary
```

### Check Pod Logs
```bash
kubectl logs -f deployment/offline-dictionary-app -n offline-dictionary
```

### Check Ingress Status (if using ingress)
```bash
kubectl get ingress -n offline-dictionary
kubectl describe ingress offline-dictionary-ingress -n offline-dictionary
```

### Port Forward for Testing
```bash
# Port forward for local testing
kubectl port-forward service/offline-dictionary-service 8099:8099 -n offline-dictionary

# Test locally
curl http://localhost:8099/health
```

## Quick Commands Summary

```bash
# Deploy everything
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/mongodb-pvc.yaml
kubectl apply -f k8s/mongodb-deployment.yaml
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/secret.yaml
kubectl apply -f k8s/app-deployment.yaml
kubectl apply -f k8s/app-service-nodeport.yaml

# Check status
kubectl get all -n offline-dictionary

# Access application
curl http://142.93.216.4:30080/health
```

## Cleanup

```bash
# Remove everything
kubectl delete namespace offline-dictionary
```

Your FastAPI application will be accessible at:
- **NodePort**: http://142.93.216.4:30080
- **LoadBalancer**: http://EXTERNAL-IP:8099
- **Ingress**: http://142.93.216.4
