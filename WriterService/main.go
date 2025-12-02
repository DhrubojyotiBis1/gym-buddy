package main

import (
	"WriterService/config"
	"WriterService/db"
	"WriterService/kafka"
	"WriterService/redis_client"
	"WriterService/writer"
	"context"
	"log"
	"os"
	"os/signal"
	"strings"
	"syscall"
)

func main() {
	rootCtx, stop := signal.NotifyContext(context.Background(),
		os.Interrupt,
		syscall.SIGTERM,
	)
	defer stop()
	env := config.MustLoad()

	// Initialize database connection
	dbPool, err := db.InitTable()
	if err != nil {
		log.Fatalf("Failed to initialize database: %v", err)
	}
	defer dbPool.CloseDb()

	// Initialize Redis client
	redisClient, err := redis_client.NewRedisClient(rootCtx)
	if err != nil {
		log.Fatalf("Failed to initialize Redis client: %v", err)
	}
	defer redisClient.Close()

	// Create writer factory with strategy pattern
	writerFactory := writer.NewWriterFactory(redisClient, dbPool.Pool)

	// Initialize Kafka consumer
	topics := strings.Split(env.KafkaTopics, ",")
	for i, topic := range topics {
		topics[i] = strings.TrimSpace(topic)
	}

	kafkaConsumer, err := kafka.NewConsumer(writerFactory, rootCtx)
	if err != nil {
		log.Fatalf("Failed to initialize Kafka consumer: %v", err)
	}
	defer kafkaConsumer.Stop()

	// Start consuming from Kafka
	if err := kafkaConsumer.Start(topics); err != nil {
		log.Fatalf("Failed to start Kafka consumer: %v", err)
	}

	log.Printf("Kafka consumer started, consuming from topics: %v", topics)
	log.Println("Consumer started, waiting for shutdown signal...")

	<-rootCtx.Done() // wait for SIGTERM/SIGINT

	log.Println("Shutting down")
	kafkaConsumer.Stop()
}
