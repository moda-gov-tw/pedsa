FROM node:18.14.2

RUN mkdir -p /app
WORKDIR /app

# Install dependency
COPY package*.json /app/
RUN yarn

# Copy source files to docker inside
COPY . /app

# Start the app
CMD ["yarn", "dev"]
