package main

import (
	"context"
	"net/http"
	"os"
	"os/signal"
	"syscall"
	"time"

	"github.com/samber/do"

	"go_backend_gorm/external/postgres"
	httpServer "go_backend_gorm/internal/interface/http"
	"go_backend_gorm/internal/repository"
	"go_backend_gorm/internal/usecase"
	"go_backend_gorm/internal/utils"
)

func main() {
	// Create dependency injector
	injector := do.New()

	// Register config
	config := utils.NewConfig()
	do.Provide(injector, func(i *do.Injector) (*utils.Config, error) {
		return config, nil
	})

	// Register logger
	do.Provide(injector, func(i *do.Injector) (*utils.Logger, error) {
		// Create a logger config from the application config
		cfg := do.MustInvoke[*utils.Config](i)
		logConfig := utils.LogConfig{
			Level:      cfg.Logger.Level,
			OutputPath: cfg.Logger.OutputPath,
			DevMode:    cfg.Logger.DevMode,
		}
		return utils.NewLogger(logConfig)
	})

	// Register database connection
	do.Provide(injector, postgres.NewDB)

	// Register repositories container
	repository.RegisterRepositories(injector)

	// Register individual use cases
	do.Provide(injector, usecase.NewHealthUseCase)

	// Register use cases container
	usecase.RegisterUseCases(injector)

	// Create and start server
	server, err := httpServer.NewServer(injector)
	if err != nil {
		logger := do.MustInvoke[*utils.Logger](injector)
		logger.Fatal("failed to create server")
	}

	// Start server in a goroutine
	go func() {
		if err := server.Start(); err != nil && err != http.ErrServerClosed {
			logger := do.MustInvoke[*utils.Logger](injector)
			logger.Fatal("server failed to start")
		}
	}()

	logger := do.MustInvoke[*utils.Logger](injector)
	logger.Info("server started")

	// Wait for interrupt signal
	quit := make(chan os.Signal, 1)
	signal.Notify(quit, os.Interrupt, syscall.SIGTERM)
	<-quit

	// Create shutdown context with timeout
	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	// Shutdown server gracefully
	if err := server.Shutdown(ctx); err != nil {
		logger.Fatal("server shutdown failed")
	}

	logger.Info("server stopped")
}
