#!/bin/bash

# Build and Push Docker Image to Docker Hub
# This script builds the Docker image and pushes it to your Docker Hub repository

set -e

echo "🐳 Building and Pushing Docker Image to Docker Hub"
echo "================================================"

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

# Configuration
DOCKER_REPO="murali676/kubernetes_deployment"
IMAGE_TAG="latest"

# Check if Docker is running
if ! docker info &> /dev/null; then
    print_error "Docker is not running. Please start Docker first."
    exit 1
fi

# Check if user is logged in to Docker Hub
if ! docker info | grep -q "Username"; then
    print_warning "You may need to login to Docker Hub first."
    echo "Run: docker login"
    read -p "Press Enter to continue after logging in..."
fi

# Step 1: Build Docker image
print_step "Building Docker image..."
docker build -t ${DOCKER_REPO}:${IMAGE_TAG} .

if [ $? -eq 0 ]; then
    print_success "Docker image built successfully"
else
    print_error "Failed to build Docker image"
    exit 1
fi

# Step 2: Test the image locally (optional)
read -p "Do you want to test the image locally before pushing? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    print_step "Testing image locally..."
    docker run -d --name test-app -p 8099:8099 ${DOCKER_REPO}:${IMAGE_TAG}
    sleep 5
    
    # Test health endpoint
    if curl -f http://localhost:8099/health &> /dev/null; then
        print_success "Local test successful"
    else
        print_warning "Local test failed, but continuing with push..."
    fi
    
    # Clean up test container
    docker stop test-app
    docker rm test-app
fi

# Step 3: Push to Docker Hub
print_step "Pushing image to Docker Hub..."
docker push ${DOCKER_REPO}:${IMAGE_TAG}

if [ $? -eq 0 ]; then
    print_success "Image pushed successfully to Docker Hub"
else
    print_error "Failed to push image to Docker Hub"
    exit 1
fi

# Step 4: Display information
echo ""
print_success "🎉 Image successfully pushed to Docker Hub!"
echo "=============================================="
echo ""
echo "📦 Image Details:"
echo "• Repository: ${DOCKER_REPO}"
echo "• Tag: ${IMAGE_TAG}"
echo "• Full name: ${DOCKER_REPO}:${IMAGE_TAG}"
echo ""
echo "🔗 Docker Hub URL:"
echo "https://hub.docker.com/r/${DOCKER_REPO}"
echo ""
echo "🚀 Next Steps:"
echo "1. Deploy to Kubernetes using the updated manifests"
echo "2. Run: ./scripts/quick-deploy.sh"
echo "3. Or manually: kubectl apply -f k8s/"
echo ""

print_success "Your Docker image is now available on Docker Hub!"
