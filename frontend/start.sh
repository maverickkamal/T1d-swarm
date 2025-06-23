#!/bin/sh

# Get the backend URL from environment variable, default to empty if not set
BACKEND_URL=${BACKEND_URL:-""}

# Create the runtime config file with environment variables
cat > /usr/share/nginx/html/assets/config/runtime-config.json << EOF
{
  "backendUrl": "$BACKEND_URL"
}
EOF

echo "Runtime config created with backend URL: $BACKEND_URL"

# Start nginx
nginx -g 'daemon off;' 