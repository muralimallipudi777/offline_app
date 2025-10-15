# Kubernetes Deployment Guide for Offline Dictionary API

This guide will help you deploy your FastAPI application to Kubernetes on your Ubuntu server.

## Prerequisites

### 1. Install Docker
```bash
# Update package index
sudo apt update

# Install Docker
sudo apt install -y docker.io

# Start and enable Docker
sudo systemctl start docker
sudo systemctl enable docker

# Add your user to docker group
sudo usermod -aG docker $USER
newgrp docker
```

### 2. Install kubectl
```bash
# Download kubectl
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"

# Install kubectl
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl

# Verify installation
kubectl version --client
```

### 3. Install Minikube (for local testing) or set up a Kubernetes cluster
```bash
# Install Minikube
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube

# Start Minikube
minikube start --driver=docker
```

## Step-by-Step Deployment

### Step 1: Build Docker Image

1. **Build the Docker image:**
```bash
# From your project directory
docker build -t offline-dictionary:latest .
```

2. **Test the image locally:**
```bash
# Run with docker-compose for testing
docker-compose up -d

# Test the application
curl http://localhost:8099/health
```

### Step 2: Push to Registry (Optional)

If you have a Docker registry (Docker Hub, AWS ECR, etc.):

```bash
# Tag the image
docker tag offline-dictionary:latest your-registry/offline-dictionary:latest

# Push to registry
docker push your-registry/offline-dictionary:latest
```

### Step 3: Deploy to Kubernetes

1. **Create namespace:**
```bash
kubectl apply -f k8s/namespace.yaml
```

2. **Deploy MongoDB:**
```bash
# Create PVC for MongoDB
kubectl apply -f k8s/mongodb-pvc.yaml

# Deploy MongoDB
kubectl apply -f k8s/mongodb-deployment.yaml
```

3. **Deploy the application:**
```bash
# Create ConfigMap and Secret
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/secret.yaml

# Deploy the application
kubectl apply -f k8s/app-deployment.yaml
kubectl apply -f k8s/app-service.yaml
```

### Step 4: Verify Deployment

1. **Check pods:**
```bash
kubectl get pods -n offline-dictionary
```

2. **Check services:**
```bash
kubectl get services -n offline-dictionary
```

3. **Check logs:**
```bash
kubectl logs -f deployment/offline-dictionary-app -n offline-dictionary
```

### Step 5: Access the Application

1. **Port forwarding (for testing):**
```bash
kubectl port-forward service/offline-dictionary-service 8099:8099 -n offline-dictionary
```

2. **Access the application:**
```bash
curl http://localhost:8099/health
```

## Production Deployment

### 1. Update Image Reference

Edit `k8s/app-deployment.yaml` and update the image:
```yaml
image: your-registry/offline-dictionary:latest
```

### 2. Configure Ingress

Edit `k8s/app-service.yaml` and update the host:
```yaml
spec:
  rules:
  - host: your-domain.com  # Change this to your domain
```

### 3. Set up SSL/TLS

Add SSL configuration to the ingress:
```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: offline-dictionary-ingress
  namespace: offline-dictionary
  annotations:
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
spec:
  tls:
  - hosts:
    - your-domain.com
    secretName: offline-dictionary-tls
```

## Monitoring and Maintenance

### 1. Scale the Application
```bash
kubectl scale deployment offline-dictionary-app --replicas=3 -n offline-dictionary
```

### 2. Update the Application
```bash
# Update the image
kubectl set image deployment/offline-dictionary-app offline-dictionary=your-registry/offline-dictionary:v2.0.0 -n offline-dictionary

# Check rollout status
kubectl rollout status deployment/offline-dictionary-app -n offline-dictionary
```

### 3. Backup MongoDB
```bash
# Create a backup
kubectl exec -it deployment/mongodb -n offline-dictionary -- mongodump --db offline --out /backup

# Copy backup to local machine
kubectl cp offline-dictionary/mongodb-pod:/backup ./mongodb-backup
```

## Troubleshooting

### Common Issues:

1. **Pods not starting:**
```bash
kubectl describe pod <pod-name> -n offline-dictionary
kubectl logs <pod-name> -n offline-dictionary
```

2. **Database connection issues:**
```bash
# Check MongoDB logs
kubectl logs deployment/mongodb -n offline-dictionary

# Test MongoDB connection
kubectl exec -it deployment/mongodb -n offline-dictionary -- mongosh
```

3. **Service not accessible:**
```bash
# Check service endpoints
kubectl get endpoints -n offline-dictionary

# Test service connectivity
kubectl run test-pod --image=busybox -it --rm -- nslookup offline-dictionary-service.offline-dictionary.svc.cluster.local
```

## Security Considerations

1. **Update secrets:**
```bash
# Generate a new secret key
echo -n "your-new-secret-key" | base64

# Update the secret
kubectl edit secret offline-dictionary-secret -n offline-dictionary
```

2. **Network policies:**
Create network policies to restrict traffic between pods.

3. **Resource limits:**
Monitor resource usage and adjust limits as needed.

## Cleanup

To remove the deployment:
```bash
kubectl delete namespace offline-dictionary
```

## Next Steps

1. Set up monitoring with Prometheus and Grafana
2. Configure log aggregation with ELK stack
3. Set up CI/CD pipeline for automated deployments
4. Implement backup strategies for MongoDB
5. Configure alerting for application health
