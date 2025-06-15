package http

import (
	"context"
	"fmt"
	"net/http"
	"time"

	"github.com/samber/do"

	"go_backend_gorm/internal/utils"
)

// Server handles HTTP server operations
type Server struct {
	server *http.Server
	logger *utils.Logger
}

// NewServer creates a new HTTP server
func NewServer(injector *do.Injector) (*Server, error) {
	// Get dependencies from injector
	router, err := NewRouter(injector)
	if err != nil {
		return nil, err
	}

	cfg := do.MustInvoke[*utils.Config](injector)
	logger := do.MustInvoke[*utils.Logger](injector)

	// Create server with configured router
	addr := fmt.Sprintf(":%d", cfg.Port)
	server := &http.Server{
		Addr:         addr,
		Handler:      router.Setup(),
		ReadTimeout:  10 * time.Second,
		WriteTimeout: 10 * time.Second,
		IdleTimeout:  120 * time.Second,
	}

	return &Server{
		server: server,
		logger: logger,
	}, nil
}

// Start begins listening for HTTP requests
func (s *Server) Start() error {
	s.logger.Info(fmt.Sprintf("starting server on %s", s.server.Addr))
	return s.server.ListenAndServe()
}

// Shutdown gracefully stops the HTTP server
func (s *Server) Shutdown(ctx context.Context) error {
	s.logger.Info("shutting down server")
	return s.server.Shutdown(ctx)
}
