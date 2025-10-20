# Ad Video Generator - Frontend

React frontend for the Ad Video Generator application.

## Development (Docker-only)

This frontend is intended to be run inside a development container via Docker Compose. Local npm install and running the dev server on the host is not supported as the primary development workflow.

Quick Docker development steps (from repository root):

1. Copy example env and edit if necessary:

```powershell
cp .env.docker .env
notepad .env
```

2. Start the frontend together with the backend and other services:

```powershell
docker-compose -f docker-compose.dev.yml up -d frontend
```

3. Follow frontend logs if needed:

```powershell
docker-compose -f docker-compose.dev.yml logs -f frontend
```

The dev frontend will be available at http://localhost:3000 and will proxy API calls to the backend container.

## Project Structure

```
frontend/
├── src/
│   ├── pages/           # Page components
│   │   ├── Login.jsx
│   │   ├── Register.jsx
│   │   ├── Dashboard.jsx
│   │   ├── CreateBrand.jsx
│   │   └── CreateAd.jsx
│   ├── services/        # API services
│   │   ├── authService.js
│   │   ├── brandService.js
│   │   └── adService.js
│   ├── store/           # State management
│   │   └── authStore.js
│   ├── lib/             # Utilities
│   │   └── api.js
│   ├── App.jsx
│   ├── main.jsx
│   └── index.css
├── package.json
├── vite.config.js
├── tailwind.config.js
└── .env.example
```

## Available Scripts

When running inside a container these scripts are available as usual (e.g. `npm run dev`, `npm run build`). To run them locally you may run the commands inside the frontend container or use the provided scripts that wrap Docker commands.

## Features

- JWT authentication with auto-refresh
- Brand management with file uploads
- Ad creation with multiple formats
- Responsive design with Tailwind CSS
- State management with Zustand
- Client-side routing with React Router
