FROM node:22-alpine AS base

# Install libc6-compat for compatibility with Alpine Linux
RUN apk add --no-cache libc6-compat
WORKDIR /app

# Stage 1: Install dependencies
FROM base AS deps
WORKDIR /app
COPY package.json package-lock.json* ./
RUN npm ci

# Stage 2: Development stage for live containerized development
FROM base AS dev
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
ENV NODE_ENV=development \
    PORT=3000 \
    HOSTNAME="0.0.0.0"
EXPOSE 3000
CMD ["npm", "run", "dev"]

# Stage 3: Builder stage for compiling Next.js standalone output
FROM base AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .

ENV NEXT_TELEMETRY_DISABLED=1 \
    NODE_ENV=production

RUN npm run build

# Stage 4: Production runner stage
FROM base AS runner
WORKDIR /app

ENV NODE_ENV=production \
    PORT=3000 \
    HOSTNAME="0.0.0.0" \
    NEXT_TELEMETRY_DISABLED=1

RUN addgroup --system --gid 1001 nodejs \
    && adduser --system --uid 1001 nextjs

# Create cache directory with correct ownership
RUN mkdir -p .next \
    && chown -R nextjs:nodejs .next

# Copy standalone output and static assets from builder
COPY --from=builder --chown=nextjs:nodejs /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs

EXPOSE 3000

CMD ["node", "server.js"]
