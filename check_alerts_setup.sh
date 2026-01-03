#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  GJ_POS Alerts Service Setup Check${NC}"
echo -e "${BLUE}========================================${NC}\n"

# Check if .env file exists
if [ ! -f "backend/.env" ]; then
    echo -e "${RED}✗ .env file not found!${NC}"
    echo "  Create it with: cp backend/.env.example backend/.env"
    exit 1
fi

echo -e "${GREEN}✓ .env file found${NC}\n"

# Check Python requirements
echo -e "${YELLOW}Checking Python packages...${NC}"

cd backend

# Check for requests package
python3 -c "import requests" 2>/dev/null
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ requests package installed${NC}"
else
    echo -e "${RED}✗ requests package not installed${NC}"
    echo "  Install with: pip install requests"
fi

# Check for twilio package
python3 -c "import twilio" 2>/dev/null
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ twilio package installed${NC}"
else
    echo -e "${YELLOW}⚠ twilio package not installed (optional for WhatsApp)${NC}"
    echo "  Install with: pip install twilio"
fi

echo ""

# Check .env configurations
echo -e "${YELLOW}Checking service configurations in .env...${NC}"

FAST2SMS_KEY=$(grep "FAST2SMS_API_KEY=" backend/.env | cut -d'=' -f2 | tr -d ' ')
TWILIO_SID=$(grep "TWILIO_ACCOUNT_SID=" backend/.env | cut -d'=' -f2 | tr -d ' ')
TWILIO_TOKEN=$(grep "TWILIO_AUTH_TOKEN=" backend/.env | cut -d'=' -f2 | tr -d ' ')

if [ -z "$FAST2SMS_KEY" ]; then
    echo -e "${YELLOW}⚠ Fast2SMS API Key not configured${NC}"
else
    echo -e "${GREEN}✓ Fast2SMS API Key configured${NC}"
fi

if [ -z "$TWILIO_SID" ]; then
    echo -e "${YELLOW}⚠ Twilio Account SID not configured${NC}"
else
    echo -e "${GREEN}✓ Twilio Account SID configured${NC}"
fi

if [ -z "$TWILIO_TOKEN" ]; then
    echo -e "${YELLOW}⚠ Twilio Auth Token not configured${NC}"
else
    echo -e "${GREEN}✓ Twilio Auth Token configured${NC}"
fi

echo ""

# Summary
echo -e "${BLUE}========================================${NC}"
echo -e "${YELLOW}Setup Summary:${NC}"

if [ -z "$FAST2SMS_KEY" ] && [ -z "$TWILIO_SID" ]; then
    echo -e "${YELLOW}⚠ No external services configured${NC}"
    echo ""
    echo -e "${BLUE}To enable message sending:${NC}"
    echo ""
    echo -e "${GREEN}Option 1: Fast2SMS (SMS only)${NC}"
    echo "  1. Sign up: https://www.fast2sms.com/"
    echo "  2. Copy API Key from dashboard"
    echo "  3. Edit backend/.env and set FAST2SMS_API_KEY=your_key"
    echo ""
    echo -e "${GREEN}Option 2: Twilio WhatsApp (WhatsApp only, FREE)${NC}"
    echo "  1. Go to: https://www.twilio.com/console/sms/whatsapp/learn"
    echo "  2. Copy Account SID and Auth Token"
    echo "  3. Edit backend/.env and set:"
    echo "     TWILIO_ACCOUNT_SID=your_sid"
    echo "     TWILIO_AUTH_TOKEN=your_token"
    echo ""
    echo -e "${GREEN}Email${NC}: Already works (no setup needed)"
else
    echo -e "${GREEN}✓ At least one service is configured!${NC}"
    echo ""
    echo "Restart your backend and test sending a message:"
    echo "1. python app.py"
    echo "2. Go to Alerts page"
    echo "3. Send a test message"
fi

echo ""
echo -e "${BLUE}More info:${NC}"
echo "  - Detailed guide: FREE_ALERTS_SETUP.md"
echo "  - Quick start: QUICK_SETUP_ALERTS.md"
echo -e "${BLUE}========================================${NC}"
