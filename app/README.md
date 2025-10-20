# 🎬 Vigen AI - Video Generation Platform

![Vigen AI Logo](frontend/public/favicon.svg)

> **📋 Note**: This is the web application component. For complete setup including AI video generation, see the [root README](../README.md) which provides unified Docker orchestration for the entire platform.

**Vigen AI** is a cutting-edge AI-powered video advertisement generation platform that creates professional-quality video ads in minutes. Transform your product descriptions into compelling video content with our advanced AI workflow.

## ✨ Features

### 🎯 **Core Capabilities**
- **AI-Powered Script Generation** - Automatically creates compelling ad scripts from product descriptions
- **Real-time Video Generation** - Creates professional video content with AI
- **Dynamic Audio Production** - Generates voiceovers and background music
- **Intelligent Editing** - Automated video editing and post-processing
- **Progress Tracking** - Real-time monitoring of video generation workflow
- **Secure Media Storage** - S3-based video storage with presigned URLs

### 🔐 **Security & Performance**
- **JWT Authentication** - Secure user authentication with refresh tokens
- **Rate Limiting** - Intelligent API rate limiting with user-specific and IP-based controls
- **Input Validation** - Comprehensive data validation and sanitization
- **Audit Logging** - Complete activity tracking and monitoring
- **CORS Protection** - Configurable cross-origin resource sharing

### 🎨 **User Experience**
- **Modern UI/UX** - Dark theme with gradient accents and smooth animations
- **Responsive Design** - Works seamlessly across desktop and mobile devices
- **Real-time Updates** - Live progress tracking with polling-based status updates
- **Error Handling** - Graceful error handling with user-friendly messages
- **Accessibility** - Keyboard navigation and screen reader support

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- AWS Account (for S3 and DynamoDB)
- Node.js 18+ (for local development)
- Python 3.11+ (for local development)

### Environment Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/kamal-teja/Vigen.git
   cd Vigen
   ```

2. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Required Environment Variables**
   ```env
   # JWT Configuration
   SECRET_KEY=your-super-secret-key-here
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=1440
   
   # AWS Configuration
   AWS_ACCESS_KEY_ID=your-aws-access-key
   AWS_SECRET_ACCESS_KEY=your-aws-secret-key
   AWS_REGION=us-east-1
   S3_BUCKET_NAME=your-s3-bucket-name
   
   # DynamoDB Tables
   USERS_TABLE=vigen-users
   ADVERTISEMENTS_TABLE=vigen-advertisements
   
   # Crew AI Endpoint (video generation service)
   CREW_ENDPOINT_URL=http://your-crew-service:8001
   
   # CORS Origins
   CORS_ORIGINS=http://localhost:3000,https://yourdomain.com
   ```

### 🐳 Docker Deployment

#### Development Mode
```bash
# Start development environment
make dev
# Note: Docker commands should now be run from the root directory
# Use the root-level docker-compose files for full application setup

# View logs
make dev-logs
```

#### Production Mode
```bash
# Start production environment
make prod
# Note: Docker commands should now be run from the root directory
# Use the root-level docker-compose files for full application setup

# View logs
make prod-logs
```

### 🛠️ Local Development

#### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

## 📚 API Documentation

### Authentication Endpoints
- `POST /auth/register` - User registration
- `POST /auth/login` - User login
- `POST /auth/refresh` - Refresh access token
- `GET /auth/me` - Get current user info

### Advertisement Endpoints
- `POST /ads` - Create new advertisement
- `GET /ads` - List user advertisements
- `GET /ads/{run_id}` - Get specific advertisement
- `PUT /ads/{run_id}` - Update advertisement
- `GET /ads/{run_id}/status` - Get generation status (polling endpoint)
- `GET /ads/{run_id}/video-url` - Get presigned video URL

### Rate Limits
- **Authentication**: 3-5 requests per 5 minutes
- **Status Polling**: 15 requests per second
- **General Operations**: 10-30 requests per minute
- **Video URL Generation**: 10 requests per minute

## 🏗️ Architecture

### Tech Stack
- **Frontend**: React 18, Vite, Tailwind CSS, Zustand
- **Backend**: FastAPI, Python 3.11, Pydantic
- **Database**: AWS DynamoDB
- **Storage**: AWS S3
- **Authentication**: JWT with refresh tokens
- **Deployment**: Docker, Docker Compose

### Key Components
- **Video Generation Workflow**: 5-step AI pipeline
- **Real-time Progress Tracking**: WebSocket-style polling
- **Secure File Access**: S3 presigned URLs with validation
- **State Management**: Zustand for frontend state
- **API Rate Limiting**: Custom rate limiter with sliding windows

## 🔄 Video Generation Workflow

1. **Script Generation** - AI creates compelling ad script
2. **Script Review** - Optimization and quality assurance  
3. **Video Creation** - AI generates video content
4. **Audio Production** - Voiceover and music creation
5. **Final Editing** - Post-processing and final output

## 📱 Frontend Pages

- **Dashboard** - Overview of all video ads and statistics
- **Create Ad** - Form to create new video advertisements
- **Ad Progress** - Real-time progress tracking during generation
- **Video Detail** - View completed videos with playback
- **Auth Pages** - Login and registration

## 🔧 Configuration

### Docker Environment
```yaml
# docker-compose.yml
services:
  backend:
    build: ./backend
    ports: ["8000:8000"]
    environment:
      - SECRET_KEY=${SECRET_KEY}
      - AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID}
      # ... other env vars
  
  frontend:
    build: ./frontend
    ports: ["3000:80"]
    environment:
      - VITE_API_URL=http://localhost:8000
```

### Frontend Build Configuration
```javascript
// vite.config.js
export default defineConfig({
  plugins: [react()],
  build: {
    outDir: 'dist',
    sourcemap: false,
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['react', 'react-dom', 'react-router-dom'],
          ui: ['lucide-react', '@radix-ui/react-dialog']
        }
      }
    }
  }
})
```

## 🚀 Deployment Options

### Static S3 Deployment
```bash
# Build for production
cd frontend
npm run build:prod

# Deploy to S3 (using AWS CLI)
aws s3 sync dist/ s3://your-bucket-name/ --delete

# Or use the deployment script
./deploy.ps1
```

### Production Environment Variables
```env
# Frontend (.env.production)
VITE_API_URL=https://api.yourdomain.com

# Backend (.env)
DEBUG=False
CORS_ORIGINS=https://yourdomain.com
```

## 🧪 Testing

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend  
npm test

# End-to-end tests
npm run test:e2e
```

## 📊 Monitoring & Logging

- **Application Logs**: Structured JSON logging
- **Rate Limiting**: Request tracking and blocking
- **Health Checks**: Docker health check endpoints
- **Error Tracking**: Comprehensive error handling

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📞 Support

- **Documentation**: [Architecture Guide](ARCHITECTURE.md)
- **Issues**: [GitHub Issues](https://github.com/kamal-teja/Vigen/issues)
- **Email**: support@vigenai.com

## 🙏 Acknowledgments

- **FastAPI** - Modern Python web framework
- **React** - Frontend library
- **Tailwind CSS** - Utility-first CSS framework
- **Lucide Icons** - Beautiful icon set
- **AWS Services** - Cloud infrastructure

---

**Built with ❤️ by the Vigen AI Team**

*Transform your ideas into compelling video content with the power of AI*