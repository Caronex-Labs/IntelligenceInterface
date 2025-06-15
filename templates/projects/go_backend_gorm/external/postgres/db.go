package postgres

import (
	"context"
	"fmt"

	"github.com/samber/do"
	"gorm.io/driver/postgres"
	"gorm.io/gorm"

	"go_backend_gorm/internal/utils"
)

// DB represents a database connection
type DB struct {
	*gorm.DB
	logger *utils.Logger
}

// NewDB creates a new database connection
func NewDB(injector *do.Injector) (*DB, error) {
	// Get dependencies from injector
	cfg := do.MustInvoke[*utils.Config](injector)
	log := do.MustInvoke[*utils.Logger](injector)

	// Get connection string
	dsn := cfg.Database.GetDSN()
	log.Info("connecting to database", utils.String("dsn", maskPassword(dsn)))

	// Create connection
	db, err := gorm.Open(postgres.Open(dsn), &gorm.Config{})
	if err != nil {
		return nil, fmt.Errorf("unable to connect to database: %w", err)
	}

	// Test the connection
	sqlDB, err := db.DB()
	if err != nil {
		return nil, fmt.Errorf("failed to get database connection: %w", err)
	}

	if err := sqlDB.Ping(); err != nil {
		return nil, fmt.Errorf("failed to ping database: %w", err)
	}

	log.Info("database connection established")

	return &DB{
		DB:     db,
		logger: log,
	}, nil
}

// WithContext returns a new DB instance with the given context
func (db *DB) WithContext(ctx context.Context) *gorm.DB {
	return db.DB.WithContext(ctx)
}

// Close closes the database connection
func (db *DB) Close() {
	sqlDB, err := db.DB.DB()
	if err != nil {
		db.logger.Error("failed to get database connection", utils.Error(err))
		return
	}
	
	if err := sqlDB.Close(); err != nil {
		db.logger.Error("failed to close database connection", utils.Error(err))
		return
	}
	
	db.logger.Info("database connection closed")
}

// maskPassword replaces the password in a DSN with asterisks for logging
func maskPassword(dsn string) string {
	var result string
	inPassword := false

	for i := 0; i < len(dsn); i++ {
		if !inPassword && i > 0 && dsn[i-1] == ':' && dsn[i] != '/' {
			inPassword = true
		} else if inPassword && dsn[i] == '@' {
			// Replace password with asterisks
			result += "********"
			inPassword = false
			i = i
		}

		if !inPassword {
			result += string(dsn[i])
		}
	}

	return result
}
