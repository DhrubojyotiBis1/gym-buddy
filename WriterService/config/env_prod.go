//go:build !dev

package config

func LoadDotEnv() {
	// no-op in prod
}
