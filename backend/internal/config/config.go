package config

import (
	"encoding/json"
	"fmt"
	"os"
)

// Config holds application configuration
type Config struct {
	Port         string `json:"port"`
	DatabasePath string `json:"database_path"`
	LogLevel     string `json:"log_level"`
	Environment  string `json:"environment"`
}

// LoadConfig loads configuration from a JSON file
func LoadConfig(path string) (*Config, error) {
	file, err := os.Open(path)
	if err != nil {
		return nil, fmt.Errorf("error opening config file: %v", err)
	}
	defer file.Close()

	var config Config
	decoder := json.NewDecoder(file)
	if err := decoder.Decode(&config); err != nil {
		return nil, fmt.Errorf("error decoding config: %v", err)
	}

	if err := validateConfig(&config); err != nil {
		return nil, fmt.Errorf("invalid configuration: %v", err)
	}

	return &config, nil
}

// validateConfig checks if the configuration is valid
func validateConfig(config *Config) error {
	if config.Port == "" {
		config.Port = "8080" // Default port
	}

	if config.DatabasePath == "" {
		config.DatabasePath = "babel.db" // Default database path
	}

	if config.LogLevel == "" {
		config.LogLevel = "info" // Default log level
	}

	if config.Environment == "" {
		config.Environment = "development" // Default environment
	}

	return nil
}

// GetEnvironment returns the current environment
func (c *Config) GetEnvironment() string {
	return c.Environment
}

// IsDevelopment checks if the current environment is development
func (c *Config) IsDevelopment() bool {
	return c.Environment == "development"
}

// IsProduction checks if the current environment is production
func (c *Config) IsProduction() bool {
	return c.Environment == "production"
}

// IsTest checks if the current environment is test
func (c *Config) IsTest() bool {
	return c.Environment == "test"
}
