package common

import "net/http"

// IHandler defines the common interface for all HTTP handlers
type IHandler interface {
	// RegisterRoutes registers all routes for this handler
	RegisterRoutes(mux *http.ServeMux)
}