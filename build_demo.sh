#!/bin/bash
# Build and test demo Docker image

set -e

echo "================================"
echo "Building Demo Docker Image"
echo "================================"

# Build the image
echo "Step 1: Building Docker image..."
docker build -t youth-checkin-demo:latest .

echo ""
echo "Step 2: Starting demo container..."
docker-compose --profile demo up -d

echo ""
echo "Step 3: Waiting for services to start..."
sleep 10

echo ""
echo "Step 4: Checking demo-app health..."
docker-compose --profile demo logs demo-app | tail -20

echo ""
echo "Step 5: Testing database setup..."
docker-compose --profile demo exec demo-app python test_demo.py

echo ""
echo "================================"
echo "✓ Demo Build Complete!"
echo "================================"
echo ""
echo "Access the demo at: http://localhost:5000"
echo ""
echo "Login credentials:"
echo "  Password: demo123"
echo ""
echo "Test phone numbers:"
echo "  555-0101 (Johnson - 2 kids)"
echo "  555-0102 (Smith - 1 kid)"
echo "  555-0103 (Williams - 2 kids)"
echo "  555-0105 (Garcia - 3 kids)"
echo ""
echo "To stop the demo:"
echo "  docker-compose --profile demo down"
echo ""
