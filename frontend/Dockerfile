FROM node:18-alpine
WORKDIR /app
COPY . .
RUN npm install
EXPOSE 8000
RUN npm run build
CMD ["npm", "run", "preview"]
