package redis_client

import (
	"WriterService/config"
	"context"
	"fmt"
	"log"
	"time"

	"github.com/redis/go-redis/v9"
)

// RedisClient wraps the Redis client
type RedisClient struct {
	client *redis.Client
	cancel context.CancelFunc
	ctx    context.Context
}

// NewRedisClient creates a new Redis client
func NewRedisClient(ctx context.Context) (*RedisClient, error) {
	env := config.MustLoad()

	addr := fmt.Sprintf("%s:%s", env.RedisHost, env.RedisPort)
	opts := &redis.Options{
		Addr:     addr,
		Password: env.RedisPassword,
		DB:       env.RedisDB,
	}

	client := redis.NewClient(opts)

	// Test connection
	childCtx, cancel := context.WithCancel(ctx)
	_, err := client.Ping(childCtx).Result()
	if err != nil {
		cancel()
		return nil, fmt.Errorf("failed to connect to Redis: %w", err)
	}

	log.Println("Successfully connected to Redis")
	return &RedisClient{client: client, ctx: childCtx, cancel: cancel}, nil
}

// Set sets a key-value pair in Redis
func (rc *RedisClient) AddToSortedSet(key, value string) error {

	if err := rc.client.ZAdd(rc.ctx, key, redis.Z{
		Score:  float64(time.Now().Unix()),
		Member: value,
	}).Err(); err != nil {
		return fmt.Errorf("ZAdd: %w", err)
	}
	if err := rc.trimSortedSet(key, 5); err != nil {
		return fmt.Errorf("trimSortedSet: %w", err)
	}
	return nil
}

func (rc *RedisClient) trimSortedSet(key string, max int64) error {
	n, err := rc.client.ZCard(rc.ctx, key).Result()
	if err != nil {
		return err
	}
	if n <= max {
		return nil
	}

	toRemove := n - max                                                // number of oldest we must drop
	return rc.client.ZRemRangeByRank(rc.ctx, key, 0, toRemove-1).Err() // lowest scores first
}

// Get retrieves a value from Redis
func (rc *RedisClient) Get(key string) ([]string, error) {
	vals, err := rc.client.ZRevRange(rc.ctx, key, 0, 4).Result()
	if err != nil {
		return nil, fmt.Errorf("ZRevRange: %w", err)
	}
	return vals, nil
}

// Close closes the Redis connection
func (rc *RedisClient) Close() error {
	rc.cancel()
	return rc.client.Close()
}
