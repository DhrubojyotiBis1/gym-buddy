# 🚀 API Gateway Service (Production-grade Nginx)

This service is a production-grade API Gateway for microservices, built on Nginx.
It acts as a reverse proxy, load balancer, and rate limiter.

## 🧩 Features
- Reverse proxy for microservices (`AuthenticationService`, `NotificationService`)
- Load balancing (least connections + failover)
- Rate limiting (per-client)
- Circuit breaker–like retry/failover logic
- Security headers and proper timeouts
- Health check endpoint (`/health`)

## 🏗️ Build and Run
```bash
docker build -t api-gateway ./APIGatewayService
docker run -d --name api-gateway --network microservices-network -p 8080:80 api-gateway
