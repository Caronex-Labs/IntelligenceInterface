package usecase

import (
	"context"
	"time"

	"github.com/samber/do"

	"go_backend_gorm/internal/repository/health_repository"
	"go_backend_gorm/internal/repository"
	"go_backend_gorm/internal/utils"
)

// HealthStatus represents the health status of the application
type HealthStatus struct {
	Status    string    `json:"status"`
	Database  bool      `json:"database"`
	Uptime    string    `json:"uptime"`
	Timestamp time.Time `json:"timestamp"`
}

// IHealthUseCase defines the interface for health check use cases
type IHealthUseCase interface {
	Check(ctx context.Context) (*HealthStatus, error)
}

// HealthUseCase handles health check business logic
type HealthUseCase struct {
	healthRepo health_repository.IHealthRepository
	logger     *utils.Logger
	startTime  time.Time
}

// Ensure HealthUseCase implements the IHealthUseCase interface
var _ IHealthUseCase = (*HealthUseCase)(nil)

// NewHealthUseCase creates a new health use case
func NewHealthUseCase(injector *do.Injector) (*HealthUseCase, error) {
	// Get dependencies from injector
	repositories, err := do.Invoke[*repository.Repositories](injector)
	if err != nil {
		return nil, err
	}

	log := do.MustInvoke[*utils.Logger](injector)

	return &HealthUseCase{
		healthRepo: repositories.Health,
		logger:     log,
		startTime:  time.Now(),
	}, nil
}

// Check performs a health check of the application components
func (uc *HealthUseCase) Check(ctx context.Context) (*HealthStatus, error) {
	uc.logger.Debug("performing health check")

	// Check database connection
	dbErr := uc.healthRepo.CheckDatabase(ctx)
	dbStatus := dbErr == nil

	// Set overall status
	status := "ok"
	if !dbStatus {
		status = "degraded"
		uc.logger.LogError(ctx, dbErr, "database health check failed")
	}

	// Return health status
	return &HealthStatus{
		Status:    status,
		Database:  dbStatus,
		Uptime:    time.Since(uc.startTime).String(),
		Timestamp: time.Now(),
	}, nil
}
