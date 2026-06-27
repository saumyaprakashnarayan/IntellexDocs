FROM node:20-alpine AS base

WORKDIR /app

# Installing dependencies as a separate layer means Docker reuses this cached
# layer on subsequent builds as long as package.json hasn't changed, which
# avoids re-downloading all node_modules on every code change
COPY package.json tsconfig.json tailwind.config.ts postcss.config.js ./
RUN npm install

# NEXT_PUBLIC_ variables are baked into the JavaScript bundle during `npm run build`,
# not read at runtime. The value must therefore be injected here as a build ARG
# rather than as a runtime ENV — setting it only in `docker run -e` would be too late.
ARG NEXT_PUBLIC_API_URL=http://localhost:8000
ENV NEXT_PUBLIC_API_URL=${NEXT_PUBLIC_API_URL}

COPY . .
RUN npm run build

EXPOSE 3000
CMD ["npm", "run", "start"]
