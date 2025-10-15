#!/bin/bash

# Kubernetes Deployment Script for Offline Dictionary API

set -e

echo "🚀 Starting deployment of Offline Dictionary API to Kubernetes..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if kubectl is installed
if ! command -v kubectl &> /dev/null; then
    print_error "kubectl is not installed. Please install kubectl first."
    exit 1
fi

# Check if Docker is running
if ! docker info &> /dev/null; then
    print_error "Docker is not running. Please start Docker first."
    exit 1
fi

# Build Docker image
print_status "Building Docker image..."
docker build -t murali676/kubernetes_deployment:latest .

if [ $? -eq 0 ]; then
    print_status "Docker image built successfully"
else
    print_error "Failed to build Docker image"
    exit 1
fi

# Test the image locally (optional)
read -p "Do you want to test the image locally first? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    print_status "Testing image locally..."
    docker run -d --name test-app -p 8099:8099 murali676/kubernetes_deployment:latest
    sleep 5
    
    # Test health endpoint
    if curl -f http://localhost:8099/health &> /dev/null; then
        print_status "Local test successful"
    else
        print_warning "Local test failed, but continuing with deployment..."
    fi
    
    # Clean up test container
    docker stop test-app
    docker rm test-app
fi

# Deploy to Kubernetes
print_status "Deploying to Kubernetes..."

# Create namespace
kubectl apply -f k8s/namespace.yaml
print_status "Namespace created"

# Deploy MongoDB
kubectl apply -f k8s/mongodb-pvc.yaml
kubectl apply -f k8s/mongodb-deployment.yaml
print_status "MongoDB deployed"

# Wait for MongoDB to be ready
print_status "Waiting for MongoDB to be ready..."
kubectl wait --for=condition=ready pod -l app=mongodb -n offline-dictionary --timeout=300s

# Deploy application
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/secret.yaml
kubectl apply -f k8s/app-deployment.yaml
kubectl apply -f k8s/app-service.yaml
print_status "Application deployed"

# Wait for application to be ready
print_status "Waiting for application to be ready..."
kubectl wait --for=condition=ready pod -l app=offline-dictionary -n offline-dictionary --timeout=300s

# Check deployment status
print_status "Checking deployment status..."
kubectl get pods -n offline-dictionary
kubectl get services -n offline-dictionary

# Test the application
print_status "Testing application health..."
kubectl port-forward service/offline-dictionary-service 8099:8099 -n offline-dictionary &
PORT_FORWARD_PID=$!

# Wait a moment for port forwarding to start
sleep 5

if curl -f http://localhost:8099/health &> /dev/null; then
    print_status "✅ Application is healthy and accessible"
else
    print_warning "⚠️  Application health check failed"
fi

# Clean up port forwarding
kill $PORT_FORWARD_PID 2>/dev/null || true

print_status "🎉 Deployment completed successfully!"
print_status "To access your application:"
print_status "1. kubectl port-forward service/offline-dictionary-service 8099:8099 -n offline-dictionary"
print_status "2. Open http://localhost:8099 in your browser"
print_status "3. API documentation: http://localhost:8099/docs"

print_status "To check logs:"
print_status "kubectl logs -f deployment/offline-dictionary-app -n offline-dictionary"

print_status "To scale the application:"
print_status "kubectl scale deployment offline-dictionary-app --replicas=3 -n offline-dictionary"
