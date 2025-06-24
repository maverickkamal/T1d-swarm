# ADK Web - T1D Analysis Dashboard

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![Angular](https://img.shields.io/badge/Angular-17+-red.svg?logo=angular)](https://angular.io)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0+-blue.svg?logo=typescript)](https://www.typescriptlang.org)

> **A modern Angular web application for real-time T1D (Type 1 Diabetes) analysis with live progress tracking and agent orchestration.**

## 🌟 Features

- **🎯 T1D Scenario Analysis** - Run comprehensive Type 1 Diabetes scenarios with AI agents
- **📊 Real-time Progress Tracking** - Live SSE-based progress updates with nested agent visualization  
- **🔄 Agent Orchestration** - Multi-agent system with refinement loops and verification
- **📈 Risk Forecasting** - Glycemic risk analysis with confidence scoring
- **🔍 Verification System** - Built-in forecast verification and confidence checking
- **📱 Responsive Design** - Modern Material Design UI that works on all devices
- **🎨 Dark Theme** - Sleek dark mode interface optimized for extended use

## 🏗️ Architecture

### Frontend (Angular 17+)
- **Progress Tracking System** - Real-time SSE connection with auto-reconnection
- **Agent Status Visualization** - Hierarchical progress display with nested agents
- **Material Design Components** - Clean, modern UI components
- **Reactive State Management** - RxJS-based reactive programming

### Backend Integration
- **SSE Endpoints** - Server-Sent Events for real-time progress updates
- **REST API** - RESTful endpoints for scenario execution and data retrieval
- **Agent System** - Multi-agent orchestration with progress tracking

## 🚀 Quick Start

### Prerequisites

- **Node.js** (v18+ recommended)
- **Angular CLI** (v17+)
- **Compatible Backend** - Python/FastAPI or similar with SSE support

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd adk-web
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Configure backend URL**
   Update the backend URL in your environment files if needed:
   ```typescript
   // src/env/environment.ts
   export const environment = {
     production: false,
     apiUrl: 'http://localhost:8080'
   };
   ```

4. **Start the development server**
   ```bash
   npm start
   # or
   ng serve
   ```

5. **Access the application**
   Open your browser to `http://localhost:4200`

## 🎯 Usage

### Running T1D Analysis

1. **Select a Scenario** - Choose from predefined T1D scenarios
2. **Customize Input** (optional) - Add custom parameters for personalized analysis
3. **Execute Analysis** - Click "Run Scenario" to start the agent orchestration
4. **Monitor Progress** - Watch real-time progress with detailed agent status
5. **Review Results** - Analyze risk forecasts, verification results, and insights

### Progress Tracking Features

The built-in progress tracking system provides:

- **Overall Progress Bar** - Shows completion percentage across all agents
- **Agent Hierarchy** - Visualizes nested agent relationships
- **Real-time Updates** - Live status changes via Server-Sent Events
- **Connection Status** - Visual indicators for SSE connection health
- **Auto-completion** - Automatic cleanup when analysis completes

## 🛠️ Development

### Project Structure

```
src/
├── app/
│   ├── components/
│   │   ├── chat/              # Main chat/scenario interface
│   │   ├── progress/          # Real-time progress tracking
│   │   ├── artifact-tab/      # Results and artifacts
│   │   └── ...
│   ├── core/
│   │   ├── models/            # TypeScript interfaces
│   │   └── services/          # Angular services
│   └── assets/                # Static assets
```

### Key Components

- **`ChatComponent`** - Main interface for scenario selection and execution
- **`ProgressComponent`** - Real-time progress tracking with SSE integration
- **`ProgressService`** - Service handling SSE connections and state management
- **Agent Services** - Backend communication for scenario execution

### Build Commands

```bash
# Development server
npm start

# Production build
npm run build

# Run tests
npm test

# Run linting
npm run lint
```

## 🔧 Configuration

### Backend Integration

Ensure your backend provides these endpoints:

- **`POST /get-scenario/`** - Execute T1D scenarios
  ```json
  {
    "scenario_id": "string",
    "session_id": "string", 
    "custom_text": "string (optional)"
  }
  ```

- **`GET /progress/{session_id}`** - SSE endpoint for progress tracking
  ```json
  {
    "session_id": "string",
    "agent_name": "string",
    "event_type": "agent_start|agent_complete|agent_error",
    "timestamp": "ISO string",
    "parent_agent": "string (optional)"
  }
  ```

### Environment Configuration

Create environment files for different deployment stages:

```typescript
// src/env/environment.prod.ts
export const environment = {
  production: true,
  apiUrl: 'https://your-production-api.com'
};
```

## 🎨 Customization

### Theming

The application uses Angular Material with custom theming. Colors are defined in:
- `_theme-colors.scss` - Main theme variables
- `src/styles.scss` - Global styles

### Agent Display Names

Customize agent display names in the progress service:

```typescript
// src/app/core/services/progress.service.ts
const displayNames = {
  'T1dInsightOrchestratorAgent': '🎯 T1D Insight Orchestrator',
  'GlycemicRiskForecasterAgent': '📈 Glycemic Risk Forecaster',
  // Add your custom agent names
};
```

## 📊 Progress Tracking Integration

For detailed integration instructions, see [`sse_integration.md`](sse_integration.md) which includes:

- Complete setup guide
- Backend integration requirements  
- Customization options
- Troubleshooting tips

## 🧪 Testing

### Unit Tests
```bash
npm test
```

### E2E Tests
```bash
npm run e2e
```

### Debug Mode
Enable debug mode for progress tracking:
```html
<app-progress [sessionId]="sessionId" [debug]="true"></app-progress>
```

## 🚀 Deployment

### Production Build
```bash
npm run build --prod
```

### Docker Deployment
```dockerfile
FROM node:18-alpine as build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build --prod

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

## 🤝 Contributing

We welcome contributions! Please read our contributing guidelines:

1. **Fork the repository**
2. **Create a feature branch** (`git checkout -b feature/amazing-feature`)
3. **Commit your changes** (`git commit -m 'Add amazing feature'`)
4. **Push to the branch** (`git push origin feature/amazing-feature`)
5. **Open a Pull Request**

### Development Guidelines

- Follow Angular style guide
- Write unit tests for new features
- Use semantic commit messages
- Update documentation as needed

## 📄 License

This project is licensed under the Apache 2.0 License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Issues** - Report bugs and request features via GitHub Issues
- **Documentation** - See [`sse_integration.md`](sse_integration.md) for detailed integration guide
- **Development** - Check the source code for implementation examples

---

**Built with ❤️ for the T1D community**
