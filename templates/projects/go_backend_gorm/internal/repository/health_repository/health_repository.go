package health_repository

import (
	"context"

	"github.com/samber/do"

	"go_backend_gorm/external/postgres"
	"go_backend_gorm/internal/utils"
)

// IHealthRepository defines the interface for health check operations
type IHealthRepository interface {
	// CheckDatabase verifies the database connection is active
	CheckDatabase(ctx context.Context) error
}

// HealthRepository implements the health repository interface
type HealthRepository struct {
	db     *postgres.DB
	logger *utils.Logger
}

// Ensure HealthRepository implements the IHealthRepository interface
var _ IHealthRepository = (*HealthRepository)(nil)

// NewHealthRepository creates a new health repository
func NewHealthRepository(injector *do.Injector) (IHealthRepository, error) {
	// Get dependencies from injector
	db := do.MustInvoke[*postgres.DB](injector)
	log := do.MustInvoke[*utils.Logger](injector)

	return &HealthRepository{
		db:     db,
		logger: log,
	}, nil
}

// CheckDatabase verifies that the database connection is active
func (r *HealthRepository) CheckDatabase(ctx context.Context) error {
	r.logger.Debug("checking database connection")
	sqlDB, err := r.db.DB.DB()
	if err != nil {
		return err
	}
	return sqlDB.PingContext(ctx)
}
