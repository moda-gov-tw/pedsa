#FROM node:18.14.2
ARG IMPORT_IMAGE
FROM $IMPORT_IMAGE

ENV PORT 3000

RUN mkdir -p /app
WORKDIR /app

# Install dependency
COPY package*.json /app/
RUN yarn

# Copy source files to docker inside
COPY . /app

# Build app
EXPOSE 3000
RUN yarn build

# Execute yarn build (only docker run or docker-compose up will execute CMD)
CMD ["yarn", "build", "/app"]

# Start the app (only docker run or docker-compose up will execute CMD)
CMD ["yarn", "start", "/app"]