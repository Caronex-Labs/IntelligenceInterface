package di

import (
	"go_backend_gorm/internal/utils"

	"github.com/samber/do"
)

// NewInjector creates a new dependency injector with services registered
func NewInjector() *do.Injector {
	injector := do.New()

	// Register config
	do.Provide(injector, func(i *do.Injector) (*utils.Config, error) {
		return utils.NewConfig(), nil
	})

	// Register logger
	do.Provide(injector, func(i *do.Injector) (*utils.Logger, error) {
		// Get config from injector
		cfg := do.MustInvoke[*utils.Config](i)

		// Create logger config from application config
		logConfig := utils.LogConfig{
			Level:      cfg.Logger.Level,
			OutputPath: cfg.Logger.OutputPath,
			DevMode:    cfg.Logger.DevMode,
		}

		return utils.NewLogger(logConfig)
	})

	// Additional services will be registered here as the application grows

	return injector
}
