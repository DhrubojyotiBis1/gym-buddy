# APIGatewayService/Dockerfile
FROM nginx:1.25-alpine

# Copy configs
COPY nginx.conf /etc/nginx/nginx.conf
COPY default.conf /etc/nginx/conf.d/default.conf
COPY conf.d/ /etc/nginx/conf.d/

# Expose HTTP port
EXPOSE 80

# Run in foreground
CMD ["nginx", "-g", "daemon off;"]

