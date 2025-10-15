#!/bin/bash

# Quick Kubernetes Deployment Script for Offline Dictionary API
# This script automates the entire deployment process

set -e

echo "🚀 Quick Kubernetes Deployment for Offline Dictionary API"
echo "=================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check prerequisites
print_step "Checking prerequisites..."

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

print_success "Prerequisites check passed"

# Step 1: Build Docker image
print_step "Building Docker image..."
docker build -t murali676/kubernetes_deployment:latest .

if [ $? -eq 0 ]; then
    print_success "Docker image built successfully"
else
    print_error "Failed to build Docker image"
    exit 1
fi

# Step 2: Create namespace
print_step "Creating namespace..."
kubectl apply -f k8s/namespace.yaml
print_success "Namespace created"

# Step 3: Deploy MongoDB
print_step "Deploying MongoDB..."
kubectl apply -f k8s/mongodb-pvc.yaml
kubectl apply -f k8s/mongodb-deployment.yaml

# Wait for MongoDB to be ready
print_step "Waiting for MongoDB to be ready..."
kubectl wait --for=condition=ready pod -l app=mongodb -n offline-dictionary --timeout=300s
print_success "MongoDB is ready"

# Step 4: Deploy application configuration
print_step "Deploying application configuration..."
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/secret.yaml
print_success "Configuration deployed"

# Step 5: Deploy application
print_step "Deploying FastAPI application..."
kubectl apply -f k8s/app-deployment.yaml
kubectl apply -f k8s/app-service-nodeport.yaml

# Wait for application to be ready
print_step "Waiting for application to be ready..."
kubectl wait --for=condition=ready pod -l app=offline-dictionary -n offline-dictionary --timeout=300s
print_success "Application is ready"

# Step 6: Verify deployment
print_step "Verifying deployment..."

# Check pods
echo "📋 Pod Status:"
kubectl get pods -n offline-dictionary

# Check services
echo "📋 Service Status:"
kubectl get services -n offline-dictionary

# Step 7: Test application
print_step "Testing application..."

# Start port forwarding in background
kubectl port-forward service/offline-dictionary-service 8099:8099 -n offline-dictionary &
PORT_FORWARD_PID=$!

# Wait for port forwarding to start
sleep 5

# Test health endpoint
if curl -f http://localhost:8099/health &> /dev/null; then
    print_success "✅ Application is healthy and accessible"
else
    print_warning "⚠️  Application health check failed"
fi

# Clean up port forwarding
kill $PORT_FORWARD_PID 2>/dev/null || true

# Step 8: Display access information
echo ""
echo "🎉 Deployment completed successfully!"
echo "=================================="
echo ""
echo "📱 Access your application:"
echo "1. External access: http://142.93.216.4:30080"
echo "2. Port forward: kubectl port-forward service/offline-dictionary-service 8099:8099 -n offline-dictionary"
echo "3. API documentation: http://142.93.216.4:30080/docs"
echo ""
echo "🔧 Management commands:"
echo "• Check logs: kubectl logs -f deployment/offline-dictionary-app -n offline-dictionary"
echo "• Scale app: kubectl scale deployment offline-dictionary-app --replicas=3 -n offline-dictionary"
echo "• Check status: kubectl get all -n offline-dictionary"
echo ""
echo "🧹 Cleanup:"
echo "• Remove all: kubectl delete namespace offline-dictionary"
echo ""

print_success "Deployment completed! Your FastAPI application is now running on Kubernetes."
