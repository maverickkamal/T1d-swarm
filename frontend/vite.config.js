import { defineConfig } from 'vite';

export default defineConfig({
  server: {
    host: '0.0.0.0',
    port: 8080,
    allowedHosts: [
      'localhost',
      '.us-central1.run.app',
      'adk-frontend-993662266913.us-central1.run.app'
    ]
  }
}); 