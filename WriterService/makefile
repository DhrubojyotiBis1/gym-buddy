.PHONY: build run docker-build docker-run test

build:
	go build -o bin/service main.go

run:
	PORT=8006 go run main.go

test:
	go test ./...

docker-build:
	docker build -t writer-service:latest .

docker-run:
	docker run -p 8006:8006 writer-service:latest
