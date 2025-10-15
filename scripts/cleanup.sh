#!/bin/bash

# Cleanup Script for Offline Dictionary API

set -e

echo "🧹 Cleaning up Offline Dictionary API deployment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

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
    print_error "kubectl is not installed."
    exit 1
fi

# Confirm deletion
read -p "Are you sure you want to delete the entire offline-dictionary namespace? This will remove all data! (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    print_status "Cleanup cancelled."
    exit 0
fi

# Delete the namespace (this will delete everything in the namespace)
print_status "Deleting offline-dictionary namespace..."
kubectl delete namespace offline-dictionary

if [ $? -eq 0 ]; then
    print_status "✅ Namespace deleted successfully"
else
    print_warning "⚠️  Namespace deletion may have failed or namespace may not exist"
fi

# Clean up Docker images (optional)
read -p "Do you want to remove the Docker image as well? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    print_status "Removing Docker image..."
    docker rmi offline-dictionary:latest 2>/dev/null || print_warning "Docker image not found or already removed"
fi

print_status "🎉 Cleanup completed!"
print_status "All resources have been removed from Kubernetes."
