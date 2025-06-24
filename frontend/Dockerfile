# Multi-stage build for production
FROM node:18-alpine AS build

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci

# Copy source code
COPY . .

# Create runtime config with hardcoded backend (correct location and format)
RUN mkdir -p src/assets/config && echo '{ "backendUrl": "https://t1d-swarm-993662266913.us-central1.run.app" }' > src/assets/config/runtime-config.json

# Build for production
RUN npm run build:prod

# Production stage with nginx
FROM nginx:alpine
COPY nginx.conf /etc/nginx/nginx.conf
COPY --from=build /app/dist/agent_framework_web/browser/ /usr/share/nginx/html

# Expose port 8080
EXPOSE 8080
ENV PORT=8080

# Start nginx
CMD ["nginx", "-g", "daemon off;"]