package utils

import (
	"os"
	"strconv"
)

// Config holds all configuration for the application
type Config struct {
	Port        int
	Environment string
	Logger      LoggerConfig
	Database    DatabaseConfig
}

// LoggerConfig holds logger-specific configuration
type LoggerConfig struct {
	Level      string
	OutputPath string
	DevMode    bool
}

// DatabaseConfig holds database-specific configuration
type DatabaseConfig struct {
	Host     string
	Port     int
	User     string
	Password string
	Name     string
	SSLMode  string
}

// NewConfig creates a new configuration with values from environment variables
func NewConfig() *Config {
	port, err := strconv.Atoi(getEnv("PORT", "8080"))
	if err != nil {
		port = 8080
	}

	dbPort, err := strconv.Atoi(getEnv("DB_PORT", "5432"))
	if err != nil {
		dbPort = 5432
	}

	loggerDevMode, _ := strconv.ParseBool(getEnv("LOGGER_DEV_MODE", "true"))

	return &Config{
		Port:        port,
		Environment: getEnv("ENVIRONMENT", "development"),
		Logger: LoggerConfig{
			Level:      getEnv("LOG_LEVEL", "info"),
			OutputPath: getEnv("LOG_OUTPUT", "stdout"),
			DevMode:    loggerDevMode,
		},
		Database: DatabaseConfig{
			Host:     getEnv("DB_HOST", "localhost"),
			Port:     dbPort,
			User:     getEnv("DB_USER", "postgres"),
			Password: getEnv("DB_PASSWORD", "postgres"),
			Name:     getEnv("DB_NAME", "postgres"),
			SSLMode:  getEnv("DB_SSL_MODE", "disable"),
		},
	}
}

// GetDSN returns the database connection string
func (c *DatabaseConfig) GetDSN() string {
	return "postgres://" + c.User + ":" + c.Password + "@" + c.Host + ":" + strconv.Itoa(c.Port) + "/" + c.Name + "?sslmode=" + c.SSLMode
}

// getEnv retrieves an environment variable or returns a default value if not set
func getEnv(key, defaultValue string) string {
	value, exists := os.LookupEnv(key)
	if !exists {
		return defaultValue
	}
	return value
}
