package handlers

import (
	"net/http"
	"reflect"

	"github.com/samber/do"

	"go_backend_gorm/internal/interface/http/handlers/health"
	"go_backend_gorm/internal/utils"
)

// Handlers is a container for all application HTTP handlers
type Handlers struct {
	Health *health.Handler
	// Add more handlers here as your application grows
	// Fields will be dynamically added by domain handlers
	// For example:
	// User   *user.UserHandler
	// Product *product.ProductHandler
	// Order  *order.OrderHandler
	
	// This struct is designed to be extended by domain handlers
	// Each domain handler will add its field to this struct
	// using the Register<Entity>Handler function
	
	// Dynamic fields
	dynamicFields map[string]interface{}
	
	// Logger
	logger *utils.Logger
}

// NewHandlers creates a new Handlers instance with all handlers initialized
func NewHandlers(injector *do.Injector) (*Handlers, error) {
	// Get health handler
	healthHandler, err := health.NewHandler(injector)
	if err != nil {
		return nil, err
	}
	
	// Get logger
	logger := do.MustInvoke[*utils.Logger](injector)

	// Return handlers container
	return &Handlers{
		Health:        healthHandler,
		dynamicFields: make(map[string]interface{}),
		logger:        logger,
		// Initialize other handlers here as needed
	}, nil
}

// RegisterHandlers registers all handlers in the dependency injection container
func RegisterHandlers(injector *do.Injector) {
	// Register Handlers container
	do.Provide(injector, NewHandlers)
}

// RegisterAllRoutes registers all routes for all handlers
func (h *Handlers) RegisterAllRoutes(mux *http.ServeMux) {
	// Register health routes
	h.Health.RegisterRoutes(mux)
	
	// Register routes for all dynamic handlers
	for name, handler := range h.dynamicFields {
		if routeHandler, ok := handler.(interface{ RegisterRoutes(*http.ServeMux) }); ok {
			h.logger.Info("registering routes for " + name)
			routeHandler.RegisterRoutes(mux)
		}
	}
}

// AddField adds a field to the Handlers struct dynamically
func AddField(h *Handlers, name string, value interface{}) {
	if h.dynamicFields == nil {
		h.dynamicFields = make(map[string]interface{})
	}
	h.dynamicFields[name] = value
}

// GetField gets a field from the Handlers struct dynamically
func GetField(h *Handlers, name string) (interface{}, bool) {
	// First check if the field exists in the struct
	v := reflect.ValueOf(h).Elem()
	fieldValue := v.FieldByName(name)
	if fieldValue.IsValid() {
		return fieldValue.Interface(), true
	}
	
	// Then check if it exists in the dynamic fields
	if h.dynamicFields != nil {
		if value, ok := h.dynamicFields[name]; ok {
			return value, true
		}
	}
	
	return nil, false
}
