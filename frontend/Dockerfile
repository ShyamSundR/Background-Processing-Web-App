# Multi-stage Dockerfile for React frontend

# Development stage
FROM node:18-alpine AS development

# Set working directory
WORKDIR /app

# Copy package files first for better caching
COPY package*.json ./

# Install dependencies
RUN npm install --production=false

# Copy source code
COPY . .

# Create non-root user for security
RUN addgroup -g 1001 -S nodejs && \
    adduser -S reactuser -u 1001

# Change ownership to non-root user
RUN chown -R reactuser:nodejs /app
USER reactuser

# Expose port
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:3000 || exit 1

# Start development server
CMD ["npm", "start"]

# Production build stage 
FROM node:18-alpine AS build

WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
RUN npm run build

# Production serve stage
FROM nginx:alpine AS production

# Copy build files to nginx
COPY --from=build /app/build /usr/share/nginx/html


# Expose port
EXPOSE 80

# Start nginx
CMD ["nginx", "-g", "daemon off;"]