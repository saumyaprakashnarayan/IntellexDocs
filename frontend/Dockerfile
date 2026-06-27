FROM node:20-alpine

WORKDIR /app

COPY package.json tsconfig.json tailwind.config.ts postcss.config.js ./
RUN npm install

COPY . .
RUN npm run build

EXPOSE 3000
CMD ["npm", "run", "start"]
