# Build stage
FROM node:18-alpine as builder

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy application
COPY . .

# Build-time environment variables for Vite
ARG VITE_API_URL=http://localhost:8080/api
ENV VITE_API_URL=${VITE_API_URL}

RUN cp .env.example .env || true

# Build
RUN npm run build


# Production stage
FROM node:18-alpine

WORKDIR /app

# Copy package files so serve can resolve file metadata when needed
COPY package*.json ./

# Install serve to run the static site
RUN npm install -g serve

# Copy built app from builder
COPY --from=builder /app/dist ./dist

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD node -e "require('http').get('http://127.0.0.1:3001', res => { process.exit(res.statusCode === 200 ? 0 : 1); }).on('error', () => process.exit(1));"

# Expose port
EXPOSE 3001

# Run app
CMD ["serve", "-s", "dist", "-l", "3001"]
