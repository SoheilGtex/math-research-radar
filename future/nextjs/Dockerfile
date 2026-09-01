FROM node:20-alpine

WORKDIR /app

# Install dependencies first (leverage Docker cache)
COPY package*.json ./
RUN npm install

# The rest of the code will be mapped via volume mapping in docker-compose
COPY . .

EXPOSE 3000

# Start Next.js in development mode
CMD ["npm", "run", "dev"]