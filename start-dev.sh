#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m' # No Color

echo -e "${CYAN}🎬 Vigen AI - Starting Development Environment${NC}"
echo -e "${CYAN}=============================================${NC}"

# Check if Docker is running
echo -e "${YELLOW}🔍 Checking Docker status...${NC}"

if ! docker ps >/dev/null 2>&1; then
    echo -e "${RED}❌ Docker is not running. Please start Docker first.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Docker is running${NC}"

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚠️  .env file not found${NC}"
    
    if [ -f ".env.example" ]; then
        echo -e "${YELLOW}📋 Copying .env.example to .env...${NC}"
        cp .env.example .env
        echo -e "${GREEN}✅ Created .env file${NC}"
        echo -e "${RED}📝 IMPORTANT: Edit .env file with your AWS credentials before continuing!${NC}"
        echo -e "${YELLOW}Press any key to continue after editing .env...${NC}"
        read -n 1 -s
    else
        echo -e "${RED}❌ No .env.example file found${NC}"
        exit 1
    fi
fi

# Start development environment
echo -e "${YELLOW}🚀 Starting development services...${NC}"

if docker-compose -f docker-compose.dev.yml up -d; then
    echo ""
    echo -e "${GREEN}✅ Development environment started successfully!${NC}"
    echo ""
    echo -e "${CYAN}🌐 Access URLs:${NC}"
    echo -e "   ${WHITE}Frontend:  http://localhost:3000${NC}"
    echo -e "   ${WHITE}Backend:   http://localhost:8000${NC}"
    echo -e "   ${WHITE}Crew API:  http://localhost:8001${NC}"
    echo -e "   ${WHITE}API Docs:  http://localhost:8000/docs${NC}"
    echo ""
    echo -e "${CYAN}📋 Useful commands:${NC}"
    echo -e "   ${WHITE}View logs:     docker-compose -f docker-compose.dev.yml logs -f${NC}"
    echo -e "   ${WHITE}Stop services: docker-compose -f docker-compose.dev.yml down${NC}"
    echo -e "   ${WHITE}Or use:        make dev-logs${NC}"
    echo -e "   ${WHITE}Or use:        make dev-down${NC}"
    echo ""
    
    # Wait for services to be ready
    echo -e "${YELLOW}⏳ Waiting for services to start...${NC}"
    sleep 10
    
    # Check service health
    echo -e "${YELLOW}🏥 Checking service health...${NC}"
    
    if curl -f http://localhost:8000/health >/dev/null 2>&1; then
        echo -e "${GREEN}✅ Backend is healthy${NC}"
    else
        echo -e "${YELLOW}⚠️  Backend may still be starting up...${NC}"
    fi
    
    if curl -f http://localhost:8001/health >/dev/null 2>&1; then
        echo -e "${GREEN}✅ Crew API is healthy${NC}"
    else
        echo -e "${YELLOW}⚠️  Crew API may still be starting up...${NC}"
    fi
    
    if curl -f http://localhost:3000 >/dev/null 2>&1; then
        echo -e "${GREEN}✅ Frontend is healthy${NC}"
    else
        echo -e "${YELLOW}⚠️  Frontend may still be starting up...${NC}"
    fi
    
    echo ""
    echo -e "${GREEN}🎉 Development environment is ready!${NC}"
    echo -e "${CYAN}You can now open http://localhost:3000 in your browser${NC}"
    
else
    echo -e "${RED}❌ Failed to start development environment${NC}"
    exit 1
fi