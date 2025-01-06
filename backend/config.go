package api

import (
	"encoding/json"
	"os"
	"sync"
)

// Config holds the application configuration
type Config struct {
	// Hedera configuration
	HederaAccountID  string `json:"hedera_account_id"`
	HederaPrivateKey string `json:"hedera_private_key"`
	HederaNetwork    string `json:"hedera_network"` // testnet or mainnet

	// API configuration
	Port           string `json:"port"`
	AllowedOrigins string `json:"allowed_origins"`

	// Database configuration
	PostgresURL string `json:"postgres_url"`
	RedisURL    string `json:"redis_url"`

	// WebSocket configuration
	WSPort string `json:"ws_port"`

	// Algorithm service configuration
	AlgoServiceURL string `json:"algo_service_url"`
}

var (
	config *Config
	once   sync.Once
)

// LoadConfig loads configuration from file and environment
func LoadConfig(configPath string) (*Config, error) {
	once.Do(func() {
		config = &Config{}

		// Load from config file if exists
		if configPath != "" {
			if err := loadConfigFile(configPath, config); err != nil {
				return
			}
		}

		// Override with environment variables
		loadEnvVars(config)
	})

	return config, nil
}

// loadConfigFile loads configuration from JSON file
func loadConfigFile(path string, cfg *Config) error {
	file, err := os.ReadFile(path)
	if err != nil {
		return err
	}

	return json.Unmarshal(file, cfg)
}

// loadEnvVars loads configuration from environment variables
func loadEnvVars(cfg *Config) {
	if v := os.Getenv("HEDERA_ACCOUNT_ID"); v != "" {
		cfg.HederaAccountID = v
	}
	if v := os.Getenv("HEDERA_PRIVATE_KEY"); v != "" {
		cfg.HederaPrivateKey = v
	}
	if v := os.Getenv("HEDERA_NETWORK"); v != "" {
		cfg.HederaNetwork = v
	}
	if v := os.Getenv("PORT"); v != "" {
		cfg.Port = v
	}
	if v := os.Getenv("ALLOWED_ORIGINS"); v != "" {
		cfg.AllowedOrigins = v
	}
	if v := os.Getenv("POSTGRES_URL"); v != "" {
		cfg.PostgresURL = v
	}
	if v := os.Getenv("REDIS_URL"); v != "" {
		cfg.RedisURL = v
	}
	if v := os.Getenv("WS_PORT"); v != "" {
		cfg.WSPort = v
	}
	if v := os.Getenv("ALGO_SERVICE_URL"); v != "" {
		cfg.AlgoServiceURL = v
	}
}

// GetConfig returns the current configuration
func GetConfig() *Config {
	if config == nil {
		LoadConfig("")
	}
	return config
}
