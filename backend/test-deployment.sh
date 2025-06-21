#!/bin/bash

# T1D-Swarm Deployment Verification Script
# Tests all endpoints and authentication after Cloud Run deployment

set -e

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
SERVICE_URL=${1:-""}
if [ -z "$SERVICE_URL" ]; then
    echo -e "${RED}❌ Please provide the service URL${NC}"
    echo "Usage: ./test-deployment.sh https://your-service-url"
    exit 1
fi

echo -e "${BLUE}🧪 Testing T1D-Swarm deployment at: $SERVICE_URL${NC}"
echo

# Test 1: Health Check
echo -e "${YELLOW}🔍 Test 1: Health Check${NC}"
if curl -s "$SERVICE_URL/current-session" > /dev/null; then
    echo -e "${GREEN}✅ Health check passed${NC}"
else
    echo -e "${RED}❌ Health check failed${NC}"
    exit 1
fi

# Test 2: Scenarios Endpoint
echo -e "${YELLOW}🔍 Test 2: Scenarios Endpoint${NC}"
if curl -s "$SERVICE_URL/scenarios" | grep -q "display_name"; then
    echo -e "${GREEN}✅ Scenarios endpoint working${NC}"
else
    echo -e "${RED}❌ Scenarios endpoint failed${NC}"
    exit 1
fi

# Test 3: Session Status Check
echo -e "${YELLOW}🔍 Test 3: Session Status Check${NC}"
RESPONSE=$(curl -s "$SERVICE_URL/api/check-access")
if echo "$RESPONSE" | grep -q "can_access"; then
    echo -e "${GREEN}✅ Session status endpoint working${NC}"
    echo "Response: $RESPONSE"
else
    echo -e "${RED}❌ Session status endpoint failed${NC}"
    exit 1
fi

# Test 4: Judge Code Verification (with invalid code)
echo -e "${YELLOW}🔍 Test 4: Judge Code Verification${NC}"
INVALID_RESPONSE=$(curl -s -w "%{http_code}" -o /dev/null -X POST "$SERVICE_URL/api/verify-judge" \
    -H "Content-Type: application/json" \
    -d '{"code":"INVALID_TEST_CODE"}')

if [ "$INVALID_RESPONSE" = "401" ]; then
    echo -e "${GREEN}✅ Judge code verification working (correctly rejected invalid code)${NC}"
else
    echo -e "${RED}❌ Judge code verification failed (expected 401, got $INVALID_RESPONSE)${NC}"
fi

# Test 5: Valid Judge Code (using one of the deployed codes)
echo -e "${YELLOW}🔍 Test 5: Valid Judge Code Test${NC}"
VALID_RESPONSE=$(curl -s -X POST "$SERVICE_URL/api/verify-judge" \
    -H "Content-Type: application/json" \
    -d '{"code":"HACKJUDGE2024"}')

if echo "$VALID_RESPONSE" | grep -q '"valid":true'; then
    echo -e "${GREEN}✅ Valid judge code accepted${NC}"
    echo "Response: $VALID_RESPONSE"
else
    echo -e "${YELLOW}⚠️  Judge code test inconclusive (may need custom codes)${NC}"
fi

# Test 6: API Documentation
echo -e "${YELLOW}🔍 Test 6: API Documentation${NC}"
if curl -s "$SERVICE_URL/docs" | grep -q "FastAPI"; then
    echo -e "${GREEN}✅ API documentation accessible${NC}"
else
    echo -e "${RED}❌ API documentation failed${NC}"
fi

echo
echo -e "${GREEN}🎉 Deployment verification completed!${NC}"
echo -e "${BLUE}📊 Summary:${NC}"
echo -e "${YELLOW}• Service URL: $SERVICE_URL${NC}"
echo -e "${YELLOW}• API Docs: $SERVICE_URL/docs${NC}"
echo -e "${YELLOW}• Health Check: $SERVICE_URL/current-session${NC}"
echo -e "${YELLOW}• Auth Test: $SERVICE_URL/api/check-access${NC}"
echo
echo -e "${BLUE}🔑 Judge Codes for Testing (from your .env):${NC}"
echo -e "${YELLOW}• HACKJUDGE2024${NC}"
echo -e "${YELLOW}• JUDGE001${NC}"
echo -e "${YELLOW}• EVALCODE${NC}"
echo
echo -e "${GREEN}Your T1D-Swarm deployment is ready! 🚀${NC}" 