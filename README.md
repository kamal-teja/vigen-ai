# 🎬 Vigen AI - Complete Video Advertisement Generation Platform

A comprehensive AI-powered video advertisement generation platform combining a modern web application with advanced AI video generation capabilities.

## 📁 Repository Structure

This repository contains two main components:

### 🎨 **App** - Frontend & Backend Web Application
- **Location**: `./app/`
- **Description**: Complete web application with React frontend and FastAPI backend
- **Purpose**: User interface for creating and managing video advertisements
- **Documentation**: [App README](./app/README.md) | [Architecture](./app/ARCHITECTURE.md)

### 🤖 **Crew-API** - AI Video Generation Engine  
- **Location**: `./crew-api/`
- **Description**: CrewAI-powered backend service for AI video generation
- **Purpose**: Core AI processing pipeline for generating professional video content
- **Documentation**: [Crew-API README](./crew-api/README.md)

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- AWS Account (S3, DynamoDB, Bedrock, Polly, MediaConvert)
- Node.js 18+ (for local development)
- Python 3.11+ (for local development)

### 1. Environment Setup

```bash
# Clone the repository
git clone <repository-url>
cd -Advertisement-video-generation

# Setup environment files
cp crew-api/.env.example .env
# Edit .env with your AWS configurations
```

### 2. Start the Complete Platform

#### Option A: Using Docker Compose (Recommended)
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f
```

#### Option B: Start Individual Components

**Start the Web Application (Frontend + Backend):**
```bash
# Start just the web app services
make app
# Frontend: http://localhost:3000
# Backend: http://localhost:8000
```

**Start the AI Video Generation Service:**
```bash
# Start just the AI engine
make crew
# API: http://localhost:8001
```

## ✨ Key Features

### Web Application (App)
- 🎯 Modern React frontend with dark theme
- 🔐 JWT-based authentication system  
- 📊 Real-time progress tracking
- 🎨 Responsive design for all devices
- 🛡️ Rate limiting and security features

### AI Engine (Crew-API)
- 🤖 Multi-agent AI workflow using CrewAI
- 📝 Intelligent script generation with Claude 3.7
- 🎬 Video generation using Amazon Nova Reel
- 🖼️ Scene image creation with Nova Canvas
- 🔊 Voice-over generation with Amazon Polly
- ✂️ Automated video editing with MediaConvert

## 🏗️ Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Web Frontend  │────│  FastAPI Backend│────│   CrewAI Engine │
│   (React/Vite)  │    │   (App Service) │    │ (Video Gen API) │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │  AWS Services   │
                    │ S3│DDB│Bedrock  │
                    │ Polly│MediaConv │
                    └─────────────────┘
```

## 🔧 Configuration

### Required Environment Variables

```bash
# AWS Configuration
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
S3_BUCKET=your-s3-bucket

# Database
USERS_TABLE=adgen-users
ADVERTISEMENTS_TABLE=adgen-advertisements
DDB_TABLE=vigen_status_table

# AI Models
BEDROCK_SCRIPT_MODEL_ID=us.anthropic.claude-3-7-sonnet-20250219-v1:0
BEDROCK_VIDEO_MODEL_ID=amazon.nova-reel-v1:1
BEDROCK_IMAGE_MODEL_ID=amazon.nova-canvas-v1:0

# Security
SECRET_KEY=your-secret-key
CORS_ORIGINS=http://localhost:3000
```

## 🐳 Docker Services

| Service | Port | Description |
|---------|------|-------------|
| Frontend | 3000 | React web application |
| Backend API | 8000 | FastAPI user management service |
| Crew API | 8001 | AI video generation service |

## 📖 Documentation

- **App Documentation**: [./app/README.md](./app/README.md)
- **Architecture Guide**: [./app/ARCHITECTURE.md](./app/ARCHITECTURE.md)  
- **Crew-API Documentation**: [./crew-api/README.md](./crew-api/README.md)

## 🧪 Development

### Running Tests
```bash
# All tests
make test

# App tests only
make test-app

# Crew-API tests only  
make test-crew
```

### Local Development
```bash
# Full development environment
make dev

# Individual services
make app          # Just web app
make crew         # Just AI engine
make frontend     # Just frontend
make backend      # Just backend
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes in the appropriate subfolder (`app/` or `crew-api/`)
4. Test your changes
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🔗 Related Links

- [AWS Bedrock Documentation](https://docs.aws.amazon.com/bedrock/)
- [CrewAI Documentation](https://docs.crewai.com/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)