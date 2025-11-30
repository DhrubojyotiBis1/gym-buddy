package writer

import (
	"WriterService/redis_client"
	"fmt"
	"strings"

	"gorm.io/gorm"
)

// WriterFactory creates the appropriate writer strategy based on the writeIn value
type WriterFactory struct {
	redisWriter *RedisWriter
	dbWriter    *DBWriter
}

// NewWriterFactory creates a new WriterFactory
func NewWriterFactory(redisClient *redis_client.RedisClient, dbPool *gorm.DB) *WriterFactory {
	return &WriterFactory{
		redisWriter: NewRedisWriter(redisClient),
		dbWriter:    NewDBWriter(dbPool),
	}
}

// GetWriter returns the appropriate writer strategy based on writeIn value
func (wf *WriterFactory) GetWriter(writeIn string) (WriterStrategy, error) {
	writeIn = strings.ToLower(strings.TrimSpace(writeIn))

	switch writeIn {
	case "redis":
		return wf.redisWriter, nil
	case "db", "database":
		return wf.dbWriter, nil
	default:
		return nil, fmt.Errorf("unknown writeIn value: %s. Supported values: 'redis', 'db'", writeIn)
	}
}
