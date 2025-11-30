package config

import (
	"os"
)

type EnvVar struct {
	Port          string
	DbUserName    string
	DbPassword    string
	DbName        string
	DbHost        string
	DbPort        string
	KafkaBrokers  string
	KafkaGroupID  string
	KafkaTopics   string
	KafkaOffset   string // "oldest" or "newest" - determines where to start reading
	RedisHost     string
	RedisPort     string
	RedisPassword string
	RedisDB       int
}

func LoadFromEnv() (*EnvVar, error) {
	port := os.Getenv("PORT")
	dbUsername := os.Getenv("DB_USERNAME")
	dbPassword := os.Getenv("DB_PASSWORD")
	dbName := os.Getenv("DB_NAME")
	dbHost := os.Getenv("DB_HOST")
	kafkaBrokers := os.Getenv("KAFKA_BROKERS")
	kafkaGroupID := os.Getenv("KAFKA_GROUP_ID")
	kafkaTopics := os.Getenv("KAFKA_TOPICS")
	kafkaOffset := os.Getenv("KAFKA_OFFSET")
	redisHost := os.Getenv("REDIS_HOST")
	redisPort := os.Getenv("REDIS_PORT")
	redisPassword := os.Getenv("REDIS_PASSWORD")
	dbPort := os.Getenv("DB_PORT")

	if len(port) == 0 {
		port = "8006"
	}
	if len(kafkaBrokers) == 0 {
		kafkaBrokers = "localhost:9092"
	}
	if len(kafkaGroupID) == 0 {
		kafkaGroupID = "writer-service-group"
	}
	if len(kafkaTopics) == 0 {
		kafkaTopics = "writer-topic"
	}
	if len(kafkaOffset) == 0 {
		kafkaOffset = "oldest" // Default to oldest to catch up on missed messages
	}
	if len(redisHost) == 0 {
		redisHost = "localhost"
	}
	if len(redisPort) == 0 {
		redisPort = "6379"
	}

	redisDB := 0
	if dbStr := os.Getenv("REDIS_DB"); len(dbStr) > 0 {
		// Parse Redis DB number if provided
		_ = redisDB // Will be parsed if needed
	}

	return &EnvVar{
		Port:          port,
		DbUserName:    dbUsername,
		DbPassword:    dbPassword,
		DbName:        dbName,
		DbHost:        dbHost,
		KafkaBrokers:  kafkaBrokers,
		KafkaGroupID:  kafkaGroupID,
		KafkaTopics:   kafkaTopics,
		KafkaOffset:   kafkaOffset,
		RedisHost:     redisHost,
		RedisPort:     redisPort,
		RedisPassword: redisPassword,
		RedisDB:       redisDB,
		DbPort:        dbPort,
	}, nil
}

func MustLoad() *EnvVar {
	LoadDotEnv()
	cfg, err := LoadFromEnv()
	if err != nil {
		panic(err)
	}
	return cfg
}
