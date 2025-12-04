package main

import (
	"WriterService/config"
	"context"
	"log"
	"net/url"
	"time"

	"github.com/jackc/pgx/v5/pgxpool"
)

func DbLoad() {
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
		log.Println("DB not loaded")
		log.Fatal(err)
	}
	defer pool.Close()
	PrintDBBasics(ctx, pool)
	schema, _ := ListSchemas(ctx, pool)
	log.Println(schema)
	// for _, val := range schema {
	// 	tables, _ := ListTables(ctx, pool, val)
	// 	log.Printf("Tables %s: ", tables)
	// }
	out, _ := ListTablesWithSizes(ctx, pool)
	log.Println(out)
	// size, _ := GetDBSize(ctx, pool)
	// log.Println(size)
	for _, val := range out {
		abcd, _ := LoadTableSchema(ctx, pool, val.Schema, out[0].Table)
		log.Printf("%s - %s", val.Schema, val.Table)
		log.Println(abcd)
		log.Println()
	}

	// var now string
	// err = pool.QueryRow(ctx, "select now()").Scan(&now)
	// if err != nil {
	// 	log.Fatal(err)
	// }
	// log.Println(now)
}

func PrintDBBasics(ctx context.Context, pool *pgxpool.Pool) error {
	var (
		dbName  string
		user    string
		version string
		now     time.Time
	)

	err := pool.QueryRow(ctx, `
		SELECT current_database(), current_user, version(), now()
	`).Scan(&dbName, &user, &version, &now)
	if err != nil {
		return err
	}

	log.Println("Database:", dbName)
	log.Println("User:", user)
	log.Println("Server version:", version)
	log.Println("Server time:", now)
	return nil
}

func ListSchemas(ctx context.Context, pool *pgxpool.Pool) ([]string, error) {
	rows, err := pool.Query(ctx, `
		SELECT schema_name
		FROM information_schema.schemata
		ORDER BY schema_name
	`)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var schemas []string
	for rows.Next() {
		var s string
		if err := rows.Scan(&s); err != nil {
			return nil, err
		}
		schemas = append(schemas, s)
	}
	return schemas, rows.Err()
}

func ListTables(ctx context.Context, pool *pgxpool.Pool, schema string) ([]string, error) {
	query := `
		SELECT table_name
		FROM information_schema.tables
		WHERE table_type = 'BASE TABLE'
		  AND table_schema = COALESCE(NULLIF($1, ''), table_schema)
		  AND table_schema NOT IN ('pg_catalog', 'information_schema')
		ORDER BY table_schema, table_name
	`

	rows, err := pool.Query(ctx, query, schema)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var tables []string
	for rows.Next() {
		var t string
		if err := rows.Scan(&t); err != nil {
			return nil, err
		}
		tables = append(tables, t)
	}
	return tables, rows.Err()
}

func GetDBSize(ctx context.Context, pool *pgxpool.Pool) (string, error) {
	var size string
	err := pool.QueryRow(ctx, `
		SELECT pg_size_pretty(pg_database_size(current_database()))
	`).Scan(&size)
	return size, err
}

type TableMeta struct {
	Schema string
	Table  string
	Size   string
}

func ListTablesWithSizes(ctx context.Context, pool *pgxpool.Pool) ([]TableMeta, error) {
	rows, err := pool.Query(ctx, `
		SELECT schemaname,
		       relname AS table_name,
		       pg_size_pretty(pg_total_relation_size(relid)) AS size
		FROM pg_catalog.pg_statio_user_tables
		ORDER BY pg_total_relation_size(relid) DESC;
	`)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var out []TableMeta
	for rows.Next() {
		var t TableMeta
		if err := rows.Scan(&t.Schema, &t.Table, &t.Size); err != nil {
			return nil, err
		}
		out = append(out, t)
	}
	return out, rows.Err()
}

type ColumnSchema struct {
	Name     string
	DataType string
	Nullable bool
	Default  *string
	IsPK     bool
}

func LoadTableSchema(ctx context.Context, pool *pgxpool.Pool, schema, table string) ([]ColumnSchema, error) {
	rows, err := pool.Query(ctx, `
		SELECT
			c.column_name,
			c.data_type,
			(c.is_nullable = 'YES') AS nullable,
			c.column_default,
			EXISTS (
				SELECT 1
				FROM information_schema.table_constraints tc
				JOIN information_schema.key_column_usage kcu
				  ON tc.constraint_name = kcu.constraint_name
				 AND tc.table_schema = kcu.table_schema
				 AND tc.table_name = kcu.table_name
				WHERE tc.constraint_type = 'PRIMARY KEY'
				  AND tc.table_schema = c.table_schema
				  AND tc.table_name = c.table_name
				  AND kcu.column_name = c.column_name
			) AS is_pk
		FROM information_schema.columns c
		WHERE c.table_schema = $1 AND c.table_name = $2
		ORDER BY c.ordinal_position;
	`, schema, table)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var cols []ColumnSchema
	for rows.Next() {
		var col ColumnSchema
		if err := rows.Scan(&col.Name, &col.DataType, &col.Nullable, &col.Default, &col.IsPK); err != nil {
			return nil, err
		}
		cols = append(cols, col)
	}
	return cols, rows.Err()
}
