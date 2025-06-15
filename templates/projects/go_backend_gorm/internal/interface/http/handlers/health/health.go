package health

import (
	"encoding/json"
	"net/http"
	"time"

	"github.com/samber/do"

	"go_backend_gorm/internal/usecase"
	"go_backend_gorm/internal/utils"

	"go_backend_gorm/internal/interface/http/common"
)

// Handler handles health check requests
type Handler struct {
	healthUseCase usecase.IHealthUseCase
	logger        *utils.Logger
}

// Ensure Handler implements the IHandler interface
var _ common.IHandler = (*Handler)(nil)

// NewHandler creates a new health check handler
func NewHandler(injector *do.Injector) (*Handler, error) {
	// Get dependencies from injector
	useCases, err := do.Invoke[*usecase.UseCases](injector)
	if err != nil {
		return nil, err
	}

	log := do.MustInvoke[*utils.Logger](injector)

	return &Handler{
		healthUseCase: useCases.Health,
		logger:        log,
	}, nil
}

// RegisterRoutes registers all routes for the health handler
func (h *Handler) RegisterRoutes(mux *http.ServeMux) {
	h.logger.Info("registering health routes")
	mux.HandleFunc("/api/v1/health", h.HandleHealth)
}

// HealthResponse represents the health check response
type HealthResponse struct {
	Status    string    `json:"status"`
	Uptime    string    `json:"uptime"`
	Timestamp time.Time `json:"timestamp"`
}

// HandleHealth handles the health check endpoint
func (h *Handler) HandleHealth(w http.ResponseWriter, r *http.Request) {
	// Only allow GET requests
	if r.Method != http.MethodGet {
		w.WriteHeader(http.StatusMethodNotAllowed)
		return
	}

	start := time.Now()
	ctx := r.Context()

	// Perform health check
	status, err := h.healthUseCase.Check(ctx)
	if err != nil {
		h.logger.LogError(ctx, err, "health check failed")
		w.WriteHeader(http.StatusInternalServerError)
		err := json.NewEncoder(w).Encode(map[string]string{"error": "internal server error"})
		if err != nil {
			return
		}
		return
	}

	// Log the request
	duration := time.Since(start)
	h.logger.LogRequest(ctx, r.Method, r.URL.Path, http.StatusOK, duration)

	// Return the health status
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	err = json.NewEncoder(w).Encode(status)
	if err != nil {
		return
	}
}
