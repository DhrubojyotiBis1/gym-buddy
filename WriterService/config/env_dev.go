//go:build dev

package config

import "github.com/joho/godotenv"

func LoadDotEnv() {
	_ = godotenv.Load()
}
