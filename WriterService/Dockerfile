# ---------- build stage ----------
    FROM golang:1.23-alpine AS builder

    WORKDIR /app
    
    # Faster caching
    COPY go.mod go.sum ./
    RUN go mod download
    
    COPY . .
    
    # Produce a static binary
    RUN CGO_ENABLED=0 GOOS=linux go build -o service
    
    # ---------- runtime stage ----------
    FROM alpine:3.20
    
    WORKDIR /app
    
    # Add CA certs for HTTPS calls if needed
    RUN apk add --no-cache ca-certificates
    
    COPY --from=builder /app/service .
    
    EXPOSE 8006
    ENV PORT=8006
    
    CMD ["./service"]
    