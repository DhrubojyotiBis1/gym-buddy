package redis_client

import (
	"WriterService/config"
	"context"
	"fmt"
	"log"

	"github.com/redis/go-redis/v9"
)

// RedisClient wraps the Redis client
type RedisClient struct {
	client *redis.Client
}

// NewRedisClient creates a new Redis client
func NewRedisClient() (*RedisClient, error) {
	env := config.MustLoad()

	addr := fmt.Sprintf("%s:%s", env.RedisHost, env.RedisPort)
	opts := &redis.Options{
		Addr:     addr,
		Password: env.RedisPassword,
		DB:       env.RedisDB,
	}

	client := redis.NewClient(opts)

	// Test connection
	ctx := context.Background()
	_, err := client.Ping(ctx).Result()
	if err != nil {
		return nil, fmt.Errorf("failed to connect to Redis: %w", err)
	}

	log.Println("Successfully connected to Redis")
	return &RedisClient{client: client}, nil
}

// Set sets a key-value pair in Redis
func (rc *RedisClient) Set(ctx context.Context, key, value string) error {
	return rc.client.Set(ctx, key, value, 0).Err()
}

// Get retrieves a value from Redis
func (rc *RedisClient) Get(ctx context.Context, key string) (string, error) {
	val, err := rc.client.Get(ctx, key).Result()
	if err == redis.Nil {
		return "", fmt.Errorf("key %s does not exist", key)
	}
	return val, err
}

// Close closes the Redis connection
func (rc *RedisClient) Close() error {
	return rc.client.Close()
}
