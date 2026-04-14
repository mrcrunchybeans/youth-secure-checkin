#!/bin/bash
# Build and test demo Docker image

set -e

CYAN='\033[0;36m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
GRAY='\033[0;37m'
NC='\033[0m'

echo -e "${CYAN}================================${NC}"
echo -e "${CYAN}Building Demo Docker Image${NC}"
echo -e "${CYAN}================================${NC}"

# Build the image
echo -e "${YELLOW}Step 1: Building Docker image...${NC}"
docker build -t youth-checkin-demo:latest .

echo -e "${YELLOW}Step 2: Starting demo container...${NC}"
docker compose --profile demo up -d

echo -e "${YELLOW}Step 3: Waiting for services to start...${NC}"
sleep 10

echo -e "${YELLOW}Step 4: Checking demo-app health...${NC}"
docker compose --profile demo logs demo-app --tail 20

echo -e "${YELLOW}Step 5: Testing database setup...${NC}"
docker compose --profile demo exec demo-app python test_demo.py

echo ""
echo -e "${GREEN}================================${NC}"
echo -e "${GREEN}✓ Demo Build Complete!${NC}"
echo -e "${GREEN}================================${NC}"
echo ""
echo "Access the demo at: http://localhost:5000"
echo ""
echo "Login credentials:"
echo -e "  ${GRAY}Password: demo123${NC}"
echo ""
echo "Test phone numbers:"
echo -e "  ${GRAY}555-0101 (Johnson - 2 kids)${NC}"
echo -e "  ${GRAY}555-0102 (Smith - 1 kid)${NC}"
echo -e "  ${GRAY}555-0103 (Williams - 2 kids)${NC}"
echo -e "  ${GRAY}555-0105 (Garcia - 3 kids)${NC}"
echo ""
echo "To stop the demo:"
echo -e "  ${GRAY}docker compose --profile demo down${NC}"
echo ""
