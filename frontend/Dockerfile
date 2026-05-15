# Build stage
FROM node:18-alpine as builder

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy application
COPY . .

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
    CMD wget --no-verbose --tries=1 --spider http://127.0.0.1:3000/ || exit 1

# Expose port
EXPOSE 3000

# Run app
CMD ["serve", "-s", "dist", "-l", "3000"]
