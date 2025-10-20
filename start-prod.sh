#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m' # No Color

echo -e "${CYAN}🎬 Vigen AI - Starting Production Environment${NC}"
echo -e "${CYAN}==============================================${NC}"

# Check if Docker is running
echo -e "${YELLOW}🔍 Checking Docker status...${NC}"

if ! docker ps >/dev/null 2>&1; then
    echo -e "${RED}❌ Docker is not running. Please start Docker first.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Docker is running${NC}"

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo -e "${RED}❌ .env file is required for production${NC}"
    echo -e "${YELLOW}Please create .env file with your production configuration${NC}"
    exit 1
fi

# Confirmation for production deployment
echo -e "${YELLOW}⚠️  You are about to start the PRODUCTION environment${NC}"
echo -e "${YELLOW}Make sure your .env file contains production-ready configuration${NC}"
echo -e "${RED}Press Ctrl+C to cancel, or any key to continue...${NC}"
read -n 1 -s

# Start production environment
echo -e "${YELLOW}🚀 Starting production services...${NC}"

if docker-compose up -d --build; then
    echo ""
    echo -e "${GREEN}✅ Production environment started successfully!${NC}"
    echo ""
    echo -e "${CYAN}🌐 Access URLs:${NC}"
    echo -e "   ${WHITE}Frontend:  http://localhost:3000${NC}"
    echo -e "   ${WHITE}Backend:   http://localhost:8000${NC}"
    echo -e "   ${WHITE}Crew API:  http://localhost:8001${NC}"
    echo ""
    echo -e "${CYAN}📋 Management commands:${NC}"
    echo -e "   ${WHITE}View logs:     docker-compose logs -f${NC}"
    echo -e "   ${WHITE}Stop services: docker-compose down${NC}"
    echo -e "   ${WHITE}Or use:        make prod-logs${NC}"
    echo -e "   ${WHITE}Or use:        make prod-down${NC}"
    echo ""
    
    # Wait for services to be ready
    echo -e "${YELLOW}⏳ Waiting for services to start...${NC}"
    sleep 15
    
    # Check service health
    echo -e "${YELLOW}🏥 Checking service health...${NC}"
    
    if curl -f http://localhost:8000/health >/dev/null 2>&1; then
        echo -e "${GREEN}✅ Backend is healthy${NC}"
    else
        echo -e "${YELLOW}⚠️  Backend health check failed - may still be starting${NC}"
    fi
    
    if curl -f http://localhost:8001/health >/dev/null 2>&1; then
        echo -e "${GREEN}✅ Crew API is healthy${NC}"
    else
        echo -e "${YELLOW}⚠️  Crew API health check failed - may still be starting${NC}"
    fi
    
    if curl -f http://localhost:3000 >/dev/null 2>&1; then
        echo -e "${GREEN}✅ Frontend is healthy${NC}"
    else
        echo -e "${YELLOW}⚠️  Frontend health check failed - may still be starting${NC}"
    fi
    
    echo ""
    echo -e "${GREEN}🎉 Production environment is ready!${NC}"
    echo ""
    echo -e "${YELLOW}🔐 Security reminders:${NC}"
    echo -e "   ${WHITE}- Ensure your SECRET_KEY is strong and secure${NC}"
    echo -e "   ${WHITE}- Verify AWS credentials have minimal required permissions${NC}"
    echo -e "   ${WHITE}- Monitor logs for any security issues${NC}"
    echo -e "   ${WHITE}- Set up proper SSL/TLS termination if serving publicly${NC}"
    
else
    echo -e "${RED}❌ Failed to start production environment${NC}"
    exit 1
fi