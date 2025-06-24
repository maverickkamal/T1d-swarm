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


## 🚀 Quick Start

### Prerequisites

## ✨ Prerequisite

- **Install [Angular CLI](https://angular.dev/tools/cli)**

- **Install [NodeJs](https://nodejs.org/en)**

- **Install [npm](https://docs.npmjs.com/downloading-and-installing-node-js-and-npm)**

- **Install [google-adk (Python)](https://github.com/google/adk-python)** 

- **Install [google-adk (Java)](https://github.com/google/adk-java/)** 


### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/maverickkamal/T1d-swarm.git
   cd frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Configure backend URL**

```bash
npm run serve --backend=http://localhost:8000
```

### Run adk api server

In another terminal run:

```bash
adk api_server --allow_origins=http://localhost:4200 --host=0.0.0.0
```

### Access after first start
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


## 🆘 Support

- **Issues** - Report bugs and request features via GitHub Issues
- **Development** - Check the source code for implementation examples

---

**Built with ❤️ for the T1D community**
