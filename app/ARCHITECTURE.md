# 🏗️ Vigen AI - Architecture Documentation

## 📋 Table of Contents
- [System Overview](#system-overview)
- [Architecture Patterns](#architecture-patterns)
- [Component Architecture](#component-architecture)
- [Data Flow](#data-flow)
- [Security Architecture](#security-architecture)
- [Deployment Architecture](#deployment-architecture)
- [API Design](#api-design)
- [Database Schema](#database-schema)
- [Performance Considerations](#performance-considerations)
- [Scalability Strategy](#scalability-strategy)

## 🎯 System Overview

Vigen AI is a modern web application that leverages AI to generate professional video advertisements. The system follows a **microservices architecture** with clear separation of concerns between frontend, backend, AI processing, and data storage layers.

### High-Level Architecture

```mermaid
graph TB
    subgraph "Client Layer"
        WEB[Web Browser]
        MOBILE[Mobile Browser]
    end
    
    subgraph "CDN/Static Hosting"
        S3_STATIC[S3 Static Website]
        CF[CloudFront CDN]
    end
    
    subgraph "Application Layer"
        FE[React Frontend]
        BE[FastAPI Backend]
        CREW[Crew AI Service]
    end
    
    subgraph "Data Layer"
        DDB[DynamoDB]
        S3[S3 Storage]
    end
    
    subgraph "External Services"
        AWS[AWS Services]
        AI[AI Models]
    end
    
    WEB --> CF
    MOBILE --> CF
    CF --> S3_STATIC
    S3_STATIC --> FE
    FE --> BE
    BE --> CREW
    BE --> DDB
    BE --> S3
    CREW --> AI
    CREW --> S3
```

## 🔧 Architecture Patterns

### 1. **Layered Architecture**

```
┌─────────────────────────────────────────┐
│           Presentation Layer            │
│    (React Components, State Management) │
├─────────────────────────────────────────┤
│             Service Layer               │
│     (API Services, Business Logic)     │
├─────────────────────────────────────────┤
│            Controller Layer             │
│        (FastAPI Routes, Validation)     │
├─────────────────────────────────────────┤
│             Business Layer              │
│       (Domain Models, Use Cases)       │
├─────────────────────────────────────────┤
│             Data Access Layer           │
│    (DynamoDB Service, S3 Service)      │
└─────────────────────────────────────────┘
```

### 2. **Event-Driven Architecture**
- **Polling-based Updates**: Frontend polls backend for status updates
- **Async Processing**: AI video generation runs asynchronously
- **State Synchronization**: Real-time progress tracking across components

### 3. **RESTful API Design**
- **Resource-based URLs**: `/ads/{id}`, `/auth/login`
- **HTTP Verbs**: GET, POST, PUT, DELETE
- **Standardized Responses**: Consistent JSON structure
- **Status Codes**: Proper HTTP status code usage

## 🧩 Component Architecture

### Frontend Architecture (React + Vite)

```mermaid
graph TD
    subgraph "React Application"
        APP[App.jsx]
        ROUTER[React Router]
        
        subgraph "Pages"
            DASH[Dashboard]
            CREATE[CreateAd]
            PROGRESS[AdProgress] 
            VIDEO[VideoDetail]
            AUTH[Auth Pages]
        end
        
        subgraph "Components"
            HEADER[Header]
            SKELETON[SkeletonLoader]
            COMMON[Common Components]
        end
        
        subgraph "Services"
            API[API Layer]
            AD_SVC[Ad Service]
            AUTH_SVC[Auth Service]
        end
        
        subgraph "State Management"
            ZUSTAND[Zustand Store]
            AUTH_STORE[Auth Store]
        end
    end
    
    APP --> ROUTER
    ROUTER --> DASH
    ROUTER --> CREATE
    ROUTER --> PROGRESS
    ROUTER --> VIDEO
    ROUTER --> AUTH
    
    DASH --> HEADER
    CREATE --> HEADER
    PROGRESS --> HEADER
    VIDEO --> HEADER
    
    DASH --> SKELETON
    PROGRESS --> SKELETON
    
    API --> AD_SVC
    API --> AUTH_SVC
    
    ZUSTAND --> AUTH_STORE
```

### Backend Architecture (FastAPI)

```mermaid
graph TD
    subgraph "FastAPI Application"
        MAIN[main.py]
        
        subgraph "Routes"
            AUTH_R[Auth Routes]
            ADS_R[Ads Routes]
        end
        
        subgraph "Services"
            AUTH_S[Auth Service]
            S3_S[S3 Service]
            DDB_S[DynamoDB Service]
        end
        
        subgraph "Models"
            USER_M[User Model]
            AD_M[Advertisement Model]
        end
        
        subgraph "Schemas"
            AUTH_SCH[Auth Schemas]
            AD_SCH[Ad Schemas]
        end
        
        subgraph "Utils"
            RATE_L[Rate Limiter]
            CONFIG[Configuration]
        end
    end
    
    MAIN --> AUTH_R
    MAIN --> ADS_R
    
    AUTH_R --> AUTH_S
    ADS_R --> S3_S
    ADS_R --> DDB_S
    
    AUTH_S --> USER_M
    ADS_R --> AD_M
    
    AUTH_R --> AUTH_SCH
    ADS_R --> AD_SCH
    
    AUTH_R --> RATE_L
    ADS_R --> RATE_L
    
    MAIN --> CONFIG
```

## 🔄 Data Flow

### Video Generation Workflow

```mermaid
sequenceDiagram
    participant User
    participant Frontend
    participant Backend
    participant CrewAI
    participant S3
    participant DynamoDB
    
    User->>Frontend: Create Ad Request
    Frontend->>Backend: POST /ads
    Backend->>DynamoDB: Store Ad Record
    Backend->>CrewAI: Trigger Generation
    Backend->>Frontend: Return Run ID
    
    Frontend->>Backend: Poll Status (GET /ads/{id}/status)
    Backend->>CrewAI: Check Progress
    CrewAI->>Backend: Progress Update
    Backend->>Frontend: Progress Data
    
    Note over CrewAI: AI Processing Pipeline
    CrewAI->>CrewAI: Script Generation
    CrewAI->>CrewAI: Script Review
    CrewAI->>CrewAI: Video Creation
    CrewAI->>CrewAI: Audio Production
    CrewAI->>CrewAI: Final Editing
    
    CrewAI->>S3: Upload Final Video
    CrewAI->>Backend: Generation Complete
    Backend->>DynamoDB: Update Ad Status
    
    Frontend->>Backend: Get Video URL
    Backend->>S3: Generate Presigned URL
    S3->>Backend: Return URL
    Backend->>Frontend: Video URL
    Frontend->>User: Display Video
```

### Authentication Flow

```mermaid
sequenceDiagram
    participant User
    participant Frontend
    participant Backend
    participant DynamoDB
    
    User->>Frontend: Login Request
    Frontend->>Backend: POST /auth/login
    Backend->>DynamoDB: Verify Credentials
    DynamoDB->>Backend: User Data
    Backend->>Backend: Generate JWT Tokens
    Backend->>Frontend: Access + Refresh Token
    Frontend->>Frontend: Store Tokens
    
    Note over Frontend: Token Refresh Process
    Frontend->>Backend: API Request (Expired Token)
    Backend->>Frontend: 401 Unauthorized
    Frontend->>Backend: POST /auth/refresh
    Backend->>Backend: Verify Refresh Token
    Backend->>Frontend: New Access Token
    Frontend->>Backend: Retry Original Request
```

## 🔐 Security Architecture

### Authentication & Authorization

```mermaid
graph TD
    subgraph "Security Layers"
        CORS[CORS Protection]
        RATE[Rate Limiting]
        JWT[JWT Validation]
        AUTHOR[Authorization]
        INPUT[Input Validation]
        S3_SEC[S3 Security]
    end
    
    subgraph "Authentication Flow"
        LOGIN[Login Endpoint]
        REGISTER[Register Endpoint]
        REFRESH[Refresh Token]
        VERIFY[Token Verification]
    end
    
    subgraph "Authorization Controls"
        USER_ISO[User Isolation]
        RESOURCE[Resource Ownership]
        PRESIGNED[Presigned URLs]
    end
    
    CORS --> RATE
    RATE --> JWT
    JWT --> AUTHOR
    AUTHOR --> INPUT
    INPUT --> S3_SEC
    
    LOGIN --> VERIFY
    REGISTER --> VERIFY
    REFRESH --> VERIFY
    
    VERIFY --> USER_ISO
    USER_ISO --> RESOURCE
    RESOURCE --> PRESIGNED
```

### Security Measures

1. **Rate Limiting**
   ```python
   # Authentication endpoints: 3-5 requests per 5 minutes
   @rate_limit(max_requests=5, window_seconds=300)
   
   # Status polling: 15 requests per second
   @rate_limit(max_requests=15, window_seconds=1)
   
   # General operations: 10-30 requests per minute
   @rate_limit(max_requests=20, window_seconds=60)
   ```

2. **JWT Security**
   - Access tokens: 24-hour expiration
   - Refresh tokens: 7-day expiration
   - Secure token storage in frontend
   - Automatic token refresh

3. **S3 Security**
   - Presigned URLs with 15-minute expiration
   - User-specific path validation
   - File type restrictions
   - Object existence verification

4. **Input Validation**
   - Pydantic schema validation
   - SQL injection prevention
   - XSS protection
   - Path traversal prevention

## 🚀 Deployment Architecture

### Development Environment

```mermaid
graph TD
    subgraph "Development Stack"
        DEV_FE[Vite Dev Server<br/>:3000]
        DEV_BE[FastAPI Dev<br/>:8000]
        DEV_CREW[Crew AI<br/>:8001]
    end
    
    subgraph "Local Services"
        LOCAL_DB[Local DynamoDB]
        LOCAL_S3[LocalStack S3]
    end
    
    subgraph "External Services"  
        AWS_DDB[AWS DynamoDB]
        AWS_S3[AWS S3]
    end
    
    DEV_FE --> DEV_BE
    DEV_BE --> DEV_CREW
    DEV_BE --> LOCAL_DB
    DEV_BE --> LOCAL_S3
    DEV_BE --> AWS_DDB
    DEV_BE --> AWS_S3
```

### Production Environment

```mermaid
graph TD
    subgraph "Client Access"
        USERS[Users]
        CDN[CloudFront CDN]
    end
    
    subgraph "Static Hosting"
        S3_STATIC[S3 Static Website]
    end
    
    subgraph "Application Tier"
        ALB[Application Load Balancer]
        ECS[ECS Containers]
        BE_INST[Backend Instances]
    end
    
    subgraph "Data Tier"
        DDB_PROD[DynamoDB]
        S3_PROD[S3 Storage]
    end
    
    subgraph "AI Processing"
        CREW_PROD[Crew AI Service]
        AI_MODELS[AI Models]
    end
    
    USERS --> CDN
    CDN --> S3_STATIC
    S3_STATIC --> ALB
    ALB --> ECS
    ECS --> BE_INST
    BE_INST --> DDB_PROD
    BE_INST --> S3_PROD
    BE_INST --> CREW_PROD
    CREW_PROD --> AI_MODELS
```

### Docker Architecture

```dockerfile
# Multi-stage build for frontend
FROM node:18-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
```

```dockerfile
# Backend container
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 📡 API Design

### RESTful Endpoints

```yaml
# Authentication API
/auth:
  /register:
    POST: Register new user
  /login:
    POST: User login
  /refresh:
    POST: Refresh access token
  /me:
    GET: Get current user info

# Advertisement API  
/ads:
  /:
    GET: List user ads
    POST: Create new ad
  /{run_id}:
    GET: Get specific ad
    PUT: Update ad
  /{run_id}/status:
    GET: Get generation status (polling)
  /{run_id}/video-url:
    GET: Get presigned video URL
```

### Response Schemas

```python
# Advertisement Response
class AdvertisementResponse(BaseModel):
    run_id: str
    name: str
    desc: str
    status: AdvStatus
    final_video_uri: Optional[str]
    created_at: datetime
    updated_at: datetime

# Status Response
class AdvertisementStatusResponse(BaseModel):
    run_id: str
    status: AdvStatus
    crew_status: Optional[dict]  # Full crew API status

# Error Response
class ErrorResponse(BaseModel):
    detail: str
    error_code: Optional[str]
    timestamp: datetime
```

## 🗄️ Database Schema

### DynamoDB Tables

#### Users Table
```python
{
    "user_id": "uuid",           # Partition Key
    "email": "string",           # Unique
    "full_name": "string",
    "role": "string",
    "password_hash": "string",
    "created_at": "timestamp",
    "updated_at": "timestamp"
}
```

#### Advertisements Table
```python
{
    "user_id": "string",         # Partition Key
    "run_id": "string",          # Sort Key
    "name": "string",
    "desc": "string", 
    "status": "string",          # ENUM: IN_PROGRESS, GENERATED, FAILED
    "final_video_uri": "string", # S3 URI
    "created_at": "timestamp",
    "updated_at": "timestamp"
}

# Global Secondary Index (GSI)
"status-index": {
    "partition_key": "status",
    "sort_key": "created_at"
}
```

### Data Access Patterns

```python
# Get user's advertisements
query(
    KeyConditionExpression=Key('user_id').eq(user_id)
)

# Get specific advertisement
get_item(
    Key={'user_id': user_id, 'run_id': run_id}
)

# Query by status (using GSI)
query(
    IndexName='status-index',
    KeyConditionExpression=Key('status').eq('GENERATED')
)
```

## ⚡ Performance Considerations

### Frontend Optimizations

1. **Code Splitting**
   ```javascript
   // Vite automatic code splitting
   manualChunks: {
     vendor: ['react', 'react-dom', 'react-router-dom'],
     ui: ['lucide-react', '@radix-ui/react-dialog']
   }
   ```

2. **Lazy Loading**
   ```javascript
   const VideoDetail = lazy(() => import('./pages/VideoDetail'));
   const CreateAd = lazy(() => import('./pages/CreateAd'));
   ```

3. **State Management**
   - Zustand for minimal state management
   - Local state for component-specific data
   - Efficient re-rendering with React patterns

### Backend Optimizations

1. **Database Queries**
   - DynamoDB single-table design
   - Efficient access patterns
   - Minimal data fetching

2. **Caching Strategy**
   ```python
   # Presigned URL caching
   @lru_cache(maxsize=1000)
   def generate_presigned_url(object_key: str) -> str:
       return s3_service.generate_presigned_download_url(object_key)
   ```

3. **Rate Limiting**
   - In-memory sliding window
   - User-specific and IP-based limits
   - Configurable thresholds

### S3 Optimizations

1. **CloudFront Integration**
   - Global content delivery
   - Edge caching
   - Custom error pages for SPA routing

2. **Presigned URLs**
   - Short expiration times (15 minutes)
   - Path validation
   - Object existence checks

## 📈 Scalability Strategy

### Horizontal Scaling

```mermaid
graph TD
    subgraph "Load Balancing"
        ALB[Application Load Balancer]
        TG[Target Groups]
    end
    
    subgraph "Application Scaling"
        ASG[Auto Scaling Group]
        INST1[Backend Instance 1]
        INST2[Backend Instance 2]
        INST3[Backend Instance N]
    end
    
    subgraph "Data Scaling"
        DDB_SCALE[DynamoDB Auto Scaling]
        S3_SCALE[S3 Unlimited Storage]
    end
    
    ALB --> TG
    TG --> ASG
    ASG --> INST1
    ASG --> INST2
    ASG --> INST3
    
    INST1 --> DDB_SCALE
    INST2 --> DDB_SCALE
    INST3 --> DDB_SCALE
    
    INST1 --> S3_SCALE
    INST2 --> S3_SCALE
    INST3 --> S3_SCALE
```

### Microservices Evolution

```mermaid
graph TD
    subgraph "Current Monolithic Structure"
        MONO[FastAPI Monolith]
    end
    
    subgraph "Future Microservices"
        AUTH_MS[Auth Microservice]
        AD_MS[Advertisement Microservice]
        MEDIA_MS[Media Processing Service]
        NOTIFY_MS[Notification Service]
    end
    
    subgraph "Service Mesh"
        ISTIO[Istio Service Mesh]
        GATEWAY[API Gateway]
    end
    
    MONO --> AUTH_MS
    MONO --> AD_MS
    MONO --> MEDIA_MS
    MONO --> NOTIFY_MS
    
    GATEWAY --> AUTH_MS
    GATEWAY --> AD_MS
    GATEWAY --> MEDIA_MS
    GATEWAY --> NOTIFY_MS
    
    ISTIO --> GATEWAY
```

### Caching Strategy

```mermaid
graph TD
    subgraph "Caching Layers"
        CDN[CloudFront CDN]
        REDIS[Redis Cache]
        APP_CACHE[Application Cache]
    end
    
    subgraph "Cache Types"
        STATIC[Static Assets]
        API_RESP[API Responses]
        USER_SESS[User Sessions]
        PRESIGNED[Presigned URLs]
    end
    
    CDN --> STATIC
    REDIS --> API_RESP
    REDIS --> USER_SESS
    APP_CACHE --> PRESIGNED
```

## 🔍 Monitoring & Observability

### Logging Strategy

```python
# Structured JSON logging
logger.info("Generated presigned URL", extra={
    "user_id": current_user.email,
    "ad_id": run_id,
    "s3_key": key,
    "expiration": 900,
    "timestamp": datetime.utcnow().isoformat()
})
```

### Health Checks

```python
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow(),
        "version": "1.0.0",
        "services": {
            "database": await check_dynamodb(),
            "storage": await check_s3(),
            "crew_ai": await check_crew_service()
        }
    }
```

### Metrics Collection

- **Application Metrics**: Request rates, response times, error rates
- **Business Metrics**: Ad creation rates, completion rates, user engagement
- **Infrastructure Metrics**: CPU, memory, disk usage, network I/O
- **Custom Metrics**: Rate limiting hits, S3 operations, DynamoDB usage

---

This architecture documentation provides a comprehensive overview of the Vigen AI platform's technical implementation, design decisions, and scalability considerations. The system is designed to be maintainable, scalable, and secure while delivering a high-quality user experience.