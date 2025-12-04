package db

import (
	"WriterService/config"
	"context"
	"log"
	"net/url"

	"github.com/jackc/pgx/v5/pgxpool"
)

// Pool wraps the pgxpool.Pool for easier usage
type Pool struct {
	*pgxpool.Pool
}

var globalPool *Pool

// InitDB initializes the database connection pool
func InitDB() (*Pool, error) {
	ctx := context.Background()
	envVar := config.MustLoad()
	u := &url.URL{
		Scheme: "postgres",
		User:   url.UserPassword(envVar.DbUserName, envVar.DbPassword),
		Host:   envVar.DbHost,
		Path:   envVar.DbName,
	}

	pool, err := pgxpool.New(ctx, u.String())
	if err != nil {
		return nil, err
	}

	// Test connection
	var dbName string
	err = pool.QueryRow(ctx, "SELECT current_database()").Scan(&dbName)
	if err != nil {
		pool.Close()
		return nil, err
	}

	log.Printf("Successfully connected to database: %s", dbName)

	globalPool = &Pool{Pool: pool}
	return globalPool, nil
}

// GetPool returns the global database pool
func GetPool() *Pool {
	return globalPool
}

// Close closes the database connection pool
func (p *Pool) Close() {
	if p != nil && p.Pool != nil {
		p.Pool.Close()
	}
}
