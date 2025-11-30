package writer

import (
	"WriterService/redis_client"
	"context"
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
	ctx := context.Background()

	// Convert data to JSON string
	jsonData, err := json.Marshal(data)
	if err != nil {
		return fmt.Errorf("failed to marshal data to JSON: %w", err)
	}

	// Generate a key from the data (you can customize this logic)
	key := generateKey(data)

	// Write to Redis
	err = rw.client.Set(ctx, key, string(jsonData))
	if err != nil {
		return fmt.Errorf("failed to write to Redis: %w", err)
	}

	log.Printf("Successfully wrote data to Redis with key: %s", key)
	return nil
}

// generateKey generates a Redis key from the data
// You can customize this based on your requirements
func generateKey(data map[string]interface{}) string {
	// Try to use an ID field if present
	if id, ok := data["id"].(string); ok {
		return fmt.Sprintf("data:%s", id)
	}

	// Fallback to a timestamp-based key
	return fmt.Sprintf("data:%d", len(data))
}
