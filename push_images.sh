#!/bin/bash
set -e

BACKEND_IMAGE="owlf/grocery-calculator-backend:latest"
FRONTEND_IMAGE="owlf/grocery-calculator-frontend:latest"

echo "Building backend image..."
docker build -t $BACKEND_IMAGE .

echo "Building frontend image..."
docker build -t $FRONTEND_IMAGE ./frontend

echo "Pushing backend image..."
docker push $BACKEND_IMAGE

echo "Pushing frontend image..."
docker push $FRONTEND_IMAGE

echo "Successfully built and pushed images!"
