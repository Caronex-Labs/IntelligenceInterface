package user

import (
	"encoding/json"
	"fmt"
	"net/http"
	"time"

	"github.com/google/uuid"
	"github.com/samber/do"

	entityPkg "go_backend_gorm/internal/core/entity/user"
	"go_backend_gorm/internal/usecase"
	usecasePkg "go_backend_gorm/internal/usecase/user"
	"go_backend_gorm/internal/utils"
	"go_backend_gorm/internal/interface/http/common"
)

// Handler handles user requests
type Handler struct {
	userUseCase usecasePkg.IUserUseCase
	logger        *utils.Logger
}

// Ensure Handler implements the IHandler interface
var _ common.IHandler = (*Handler)(nil)

// NewHandler creates a new user handler
func NewHandler(injector *do.Injector) (*Handler, error) {
	// Get dependencies from injector
	useCases, err := do.Invoke[*usecase.UseCases](injector)
	if err != nil {
		return nil, err
	}

	// Get the user use case from the use cases container
	useCaseField, ok := usecase.GetField(useCases, "User")
	if !ok {
		return nil, fmt.Errorf("failed to get user use case from container")
	}
	
	userUseCase, ok := useCaseField.(usecasePkg.IUserUseCase)
	if !ok {
		return nil, fmt.Errorf("failed to cast user use case to correct type")
	}

	log := do.MustInvoke[*utils.Logger](injector)

	return &Handler{
		userUseCase: userUseCase,
		logger:        log,
	}, nil
}

// RegisterRoutes registers all routes for the user handler
func (h *Handler) RegisterRoutes(mux *http.ServeMux) {
	h.logger.Info("registering user routes")
	
	// Register routes
	mux.HandleFunc("/api/v1/users", h.handleUsers)
	mux.HandleFunc("/api/v1/users/", h.handleUserByID)
}

// handleUsers handles GET and POST requests for users
func (h *Handler) handleUsers(w http.ResponseWriter, r *http.Request) {
	start := time.Now()
	ctx := r.Context()

	switch r.Method {
	case http.MethodGet:
		// Handle GET request (list users)
		// Parse query parameters for filtering and pagination
		query := r.URL.Query()
		limit := 10 // Default limit
		offset := 0 // Default offset

		// TODO: Parse query parameters for filtering
		// Example:
		// if limitStr := query.Get("limit"); limitStr != "" {
		//     if limitVal, err := strconv.Atoi(limitStr); err == nil && limitVal > 0 {
		//         limit = limitVal
		//     }
		// }
		// if offsetStr := query.Get("offset"); offsetStr != "" {
		//     if offsetVal, err := strconv.Atoi(offsetStr); err == nil && offsetVal >= 0 {
		//         offset = offsetVal
		//     }
		// }
		_ = query // Silence unused variable warning until query parsing is implemented

		// Get users from use case
		users, err := h.userUseCase.List(ctx, nil, limit, offset)
		if err != nil {
			h.logger.LogError(ctx, err, "failed to list users")
			http.Error(w, "Internal server error", http.StatusInternalServerError)
			return
		}

		// Return users as JSON
		w.Header().Set("Content-Type", "application/json")
		err = json.NewEncoder(w).Encode(users)
		if err != nil {
			h.logger.LogError(ctx, err, "failed to encode users to JSON")
			return
		}

	case http.MethodPost:
		// Handle POST request (create user)
		var user entityPkg.User
		err := json.NewDecoder(r.Body).Decode(&user)
		if err != nil {
			h.logger.LogError(ctx, err, "failed to decode request body")
			http.Error(w, "Invalid request body", http.StatusBadRequest)
			return
		}

		// Create user using use case
		err = h.userUseCase.Create(ctx, &user)
		if err != nil {
			h.logger.LogError(ctx, err, "failed to create user")
			http.Error(w, "Internal server error", http.StatusInternalServerError)
			return
		}

		// Return created user as JSON
		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusCreated)
		err = json.NewEncoder(w).Encode(user)
		if err != nil {
			h.logger.LogError(ctx, err, "failed to encode user to JSON")
			return
		}

	default:
		w.WriteHeader(http.StatusMethodNotAllowed)
	}

	// Log the request
	duration := time.Since(start)
	h.logger.LogRequest(ctx, r.Method, r.URL.Path, http.StatusOK, duration)
}

// handleUserByID handles GET, PUT, and DELETE requests for a specific user
func (h *Handler) handleUserByID(w http.ResponseWriter, r *http.Request) {
	start := time.Now()
	ctx := r.Context()

	// Extract ID from URL
	idStr := r.URL.Path[len("/api/v1/users/"):]
	id, err := uuid.Parse(idStr)
	if err != nil {
		h.logger.LogError(ctx, err, "invalid user ID")
		http.Error(w, "Invalid user ID", http.StatusBadRequest)
		return
	}

	switch r.Method {
	case http.MethodGet:
		// Handle GET request (get user by ID)
		user, err := h.userUseCase.GetByID(ctx, id)
		if err != nil {
			h.logger.LogError(ctx, err, "failed to get user")
			http.Error(w, "User not found", http.StatusNotFound)
			return
		}

		// Return user as JSON
		w.Header().Set("Content-Type", "application/json")
		err = json.NewEncoder(w).Encode(user)
		if err != nil {
			h.logger.LogError(ctx, err, "failed to encode user to JSON")
			return
		}

	case http.MethodPut:
		// Handle PUT request (update user)
		var user entityPkg.User
		err := json.NewDecoder(r.Body).Decode(&user)
		if err != nil {
			h.logger.LogError(ctx, err, "failed to decode request body")
			http.Error(w, "Invalid request body", http.StatusBadRequest)
			return
		}

		// Ensure ID in URL matches ID in body
		user.ID = id

		// Update user using use case
		err = h.userUseCase.Update(ctx, &user)
		if err != nil {
			h.logger.LogError(ctx, err, "failed to update user")
			http.Error(w, "Internal server error", http.StatusInternalServerError)
			return
		}

		// Return updated user as JSON
		w.Header().Set("Content-Type", "application/json")
		err = json.NewEncoder(w).Encode(user)
		if err != nil {
			h.logger.LogError(ctx, err, "failed to encode user to JSON")
			return
		}

	case http.MethodDelete:
		// Handle DELETE request (delete user)
		err := h.userUseCase.Delete(ctx, id)
		if err != nil {
			h.logger.LogError(ctx, err, "failed to delete user")
			http.Error(w, "Internal server error", http.StatusInternalServerError)
			return
		}

		// Return success response
		w.WriteHeader(http.StatusNoContent)

	default:
		w.WriteHeader(http.StatusMethodNotAllowed)
	}

	// Log the request
	duration := time.Since(start)
	h.logger.LogRequest(ctx, r.Method, r.URL.Path, http.StatusOK, duration)
}
