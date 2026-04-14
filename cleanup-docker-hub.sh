#!/bin/bash
# Docker Hub Tag Cleanup Script
# Deletes specified tags from Docker Hub repository

set -e

CYAN='\033[0;36m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

# Defaults
USERNAME="${1:-crunchybeans}"
REPOSITORY="${2:-youth-secure-checkin}"
TOKEN="${3:-}"
TAGS_TO_DELETE="${4:-v1}"

echo -e "${CYAN}🧹 Docker Hub Tag Cleanup Tool${NC}"
echo -e "${CYAN}================================${NC}"
echo ""

# Check if token is provided
if [ -z "$TOKEN" ]; then
    echo -e "${RED}❌ Error: Docker Hub API token is required${NC}"
    echo ""
    echo -e "${YELLOW}To get your token:${NC}"
    echo -e "${YELLOW}1. Go to: https://hub.docker.com/settings/security${NC}"
    echo -e "${YELLOW}2. Click 'New Access Token'${NC}"
    echo -e "${YELLOW}3. Give it a name (e.g., 'cleanup-script')${NC}"
    echo -e "${YELLOW}4. Set permissions to 'Read, Write, Delete'${NC}"
    echo -e "${YELLOW}5. Copy the token and pass it as the third argument${NC}"
    echo ""
    echo -e "${CYAN}Usage: ./cleanup-docker-hub.sh [username] [repository] <token> [tags]${NC}"
    echo -e "${CYAN}Example: ./cleanup-docker-hub.sh crunchybeans youth-secure-checkin your-token-here 'v1 v2'${NC}"
    exit 1
fi

echo "Repository: ${USERNAME}/${REPOSITORY}"
echo "Tags to delete: ${TAGS_TO_DELETE}"
echo ""

# Confirm deletion
read -p "Are you sure you want to delete these tags? (yes/no): " CONFIRM
if [ "$CONFIRM" != "yes" ]; then
    echo -e "${YELLOW}❌ Cancelled${NC}"
    exit 0
fi

echo ""
echo -e "${GREEN}Starting cleanup...${NC}"
echo ""

# Delete each tag
SUCCESS_COUNT=0
FAIL_COUNT=0

for TAG in $TAGS_TO_DELETE; do
    echo -n "🗑️  Deleting tag: ${TAG}..."

    URI="https://hub.docker.com/v2/repositories/${USERNAME}/${REPOSITORY}/tags/${TAG}/"

    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" -X DELETE \
        -H "Authorization: Bearer ${TOKEN}" \
        "$URI")

    if [ "$HTTP_CODE" = "204" ] || [ "$HTTP_CODE" = "200" ]; then
        echo -e " ${GREEN}✅ Deleted${NC}"
        SUCCESS_COUNT=$((SUCCESS_COUNT + 1))
    else
        echo -e " ${RED}❌ Failed (HTTP ${HTTP_CODE})${NC}"
        FAIL_COUNT=$((FAIL_COUNT + 1))
    fi
done

echo ""
echo -e "${CYAN}================================${NC}"
echo -e "${GREEN}✅ Successfully deleted: ${SUCCESS_COUNT}${NC}"
echo -e "${RED}❌ Failed: ${FAIL_COUNT}${NC}"
echo ""

if [ "$FAIL_COUNT" -eq 0 ]; then
    echo -e "${GREEN}🎉 All tags cleaned up successfully!${NC}"
else
    echo -e "${YELLOW}⚠️  Some tags failed to delete. Check errors above.${NC}"
fi

echo ""
echo -e "${CYAN}View your Docker Hub repository:${NC}"
echo -e "${BLUE}https://hub.docker.com/r/${USERNAME}/${REPOSITORY}/tags${NC}"
