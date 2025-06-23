# Use Node.js for serving (simpler approach)
FROM node:18-alpine

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci

# Copy source code
COPY . .

# Expose port 8080 (Cloud Run default)
EXPOSE 8080

# Set the PORT environment variable for Cloud Run
ENV PORT=8080

# Use the existing npm serve command with backend URL from environment
# The serve script calls set-backend.js which reads from npm_config_backend
CMD npm run serve --backend=$BACKEND_URL -- --host=0.0.0.0 --port=$PORT --disable-host-check