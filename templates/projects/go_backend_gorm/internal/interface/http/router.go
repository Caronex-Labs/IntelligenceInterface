package http

import (
	"net/http"

	"github.com/samber/do"

	"go_backend_gorm/internal/interface/http/handlers"
	"go_backend_gorm/internal/utils"
)

// Router handles the registration of all API endpoints
type Router struct {
	mux      *http.ServeMux
	handlers *handlers.Handlers
	logger   *utils.Logger
}

// NewRouter creates a new router instance
func NewRouter(injector *do.Injector) (*Router, error) {
	// Get dependencies from injector
	h, err := handlers.NewHandlers(injector)
	if err != nil {
		return nil, err
	}

	log := do.MustInvoke[*utils.Logger](injector)

	return &Router{
		mux:      http.NewServeMux(),
		handlers: h,
		logger:   log,
	}, nil
}

// Setup registers all routes and returns the configured router
func (r *Router) Setup() *http.ServeMux {
	// Log route registration
	r.logger.Info("setting up routes")

	// Delegate route registration to handlers
	r.handlers.RegisterAllRoutes(r.mux)

	return r.mux
}
