package writer

import (
	"WriterService/redis_client"
	"encoding/json"
	"fmt"
	"log"
)

// RedisWriter implements WriterStrategy for writing to Redis
type RedisWriter struct {
	client *redis_client.RedisClient
}

// NewRedisWriter creates a new RedisWriter instance
func NewRedisWriter(client *redis_client.RedisClient) *RedisWriter {
	return &RedisWriter{
		client: client,
	}
}

// Write writes data to Redis
func (rw *RedisWriter) Write(data map[string]interface{}) error {

	// Convert data to JSON string
	jsonData, err := json.Marshal(data)
	if err != nil {
		return fmt.Errorf("failed to marshal data to JSON: %w", err)
	}

	// Generate a key from the data (you can customize this logic)
	key := fmt.Sprintf("convId:%s", data["conversation_id"])
	err = rw.client.AddToSortedSet(key, string(jsonData))
	if err != nil {
		return fmt.Errorf("failed to write to Redis: %w", err)
	}

	log.Printf("Successfully wrote data to Redis with key: %s", key)
	return nil

}
