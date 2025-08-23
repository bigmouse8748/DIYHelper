# DIY Smart Assistant V2 Frontend

# Build stage
FROM node:20-alpine AS builder

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci --production=false

# Copy source code
COPY . .

# Set build environment variable for API endpoint
ARG VITE_API_URL=http://localhost:8000
ENV VITE_API_URL=$VITE_API_URL

# Build the application
RUN npm run build

# Production stage
FROM nginx:alpine

# Copy built files from builder stage
COPY --from=builder /app/dist /usr/share/nginx/html

# Create nginx configuration
RUN echo 'server {' > /etc/nginx/conf.d/default.conf && \
    echo '  listen 80;' >> /etc/nginx/conf.d/default.conf && \
    echo '  server_name _;' >> /etc/nginx/conf.d/default.conf && \
    echo '  root /usr/share/nginx/html;' >> /etc/nginx/conf.d/default.conf && \
    echo '  index index.html;' >> /etc/nginx/conf.d/default.conf && \
    echo '  try_files $uri $uri/ /index.html;' >> /etc/nginx/conf.d/default.conf && \
    echo '  location /api/ {' >> /etc/nginx/conf.d/default.conf && \
    echo '    return 404;' >> /etc/nginx/conf.d/default.conf && \
    echo '  }' >> /etc/nginx/conf.d/default.conf && \
    echo '  location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {' >> /etc/nginx/conf.d/default.conf && \
    echo '    expires 1y;' >> /etc/nginx/conf.d/default.conf && \
    echo '    add_header Cache-Control "public, immutable";' >> /etc/nginx/conf.d/default.conf && \
    echo '  }' >> /etc/nginx/conf.d/default.conf && \
    echo '}' >> /etc/nginx/conf.d/default.conf

# Expose port
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD wget --no-verbose --tries=1 --spider http://localhost || exit 1

# Start nginx
CMD ["nginx", "-g", "daemon off;"]