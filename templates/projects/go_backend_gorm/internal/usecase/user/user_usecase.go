package user

import (
	"context"
	"fmt"

	"github.com/google/uuid"
	"github.com/samber/do"

	entityPkg "go_backend_gorm/internal/core/entity/user"
	repoPkg "go_backend_gorm/internal/repository/user"
	"go_backend_gorm/internal/repository"
	"go_backend_gorm/internal/utils"
)

// IUserUseCase defines the interface for user use cases
type IUserUseCase interface {
	// Create creates a new user
	Create(ctx context.Context, user *entityPkg.User) error
	// GetByID retrieves a user by ID
	GetByID(ctx context.Context, id uuid.UUID) (*entityPkg.User, error)
	// List retrieves a list of users with optional filtering
	List(ctx context.Context, filters map[string]interface{}, limit, offset int) ([]*entityPkg.User, error)
	// Update updates an existing user
	Update(ctx context.Context, user *entityPkg.User) error
	// Delete deletes a user by ID
	Delete(ctx context.Context, id uuid.UUID) error
}

// UserUseCase implements the user use case interface
type UserUseCase struct {
	userRepo repoPkg.IUserRepository
	logger *utils.Logger
}

// Ensure UserUseCase implements the IUserUseCase interface
var _ IUserUseCase = (*UserUseCase)(nil)

// NewUserUseCase creates a new user use case
func NewUserUseCase(injector *do.Injector) (*UserUseCase, error) {
	// Get dependencies from injector
	repositories := do.MustInvoke[*repository.Repositories](injector)
	log := do.MustInvoke[*utils.Logger](injector)

	// Get the user repository from the repositories container
	repoField, ok := repository.GetField(repositories, "User")
	if !ok {
		return nil, fmt.Errorf("failed to get user repository from container")
	}
	
	userRepo, ok := repoField.(repoPkg.IUserRepository)
	if !ok {
		return nil, fmt.Errorf("failed to cast user repository to correct type")
	}

	return &UserUseCase{
	userRepo: userRepo,
	logger: log,
	}, nil
}

// Create creates a new user
func (uc *UserUseCase) Create(ctx context.Context, user *entityPkg.User) error {
	uc.logger.Debug(fmt.Sprintf("creating user %+v", user))
	// Validate entity before creation
	if err := uc.validateUser(user); err != nil {
		return fmt.Errorf("validation failed: %w", err)
	}
	// Create with business logic validation
	return uc.userRepo.Create(ctx, user)
}

// GetByID retrieves a user by ID
func (uc *UserUseCase) GetByID(ctx context.Context, id uuid.UUID) (*entityPkg.User, error) {
	uc.logger.Debug(fmt.Sprintf("getting user by ID %s", id))
	
	return uc.userRepo.GetByID(ctx, id)
}

// List retrieves a list of users with optional filtering
func (uc *UserUseCase) List(ctx context.Context, filters map[string]interface{}, limit, offset int) ([]*entityPkg.User, error) {
	uc.logger.Debug(fmt.Sprintf("listing users with filters %+v, limit %d, offset %d", filters, limit, offset))
	// Apply business rules for listing
	filters = uc.applyBusinessFilters(filters)
	
	return uc.userRepo.List(ctx, filters, limit, offset)
}

// Update updates an existing user
func (uc *UserUseCase) Update(ctx context.Context, user *entityPkg.User) error {
	uc.logger.Debug(fmt.Sprintf("updating user %+v", user))
	// Validate entity before update
	if err := uc.validateUser(user); err != nil {
		return fmt.Errorf("validation failed: %w", err)
	}
	
	// Check if entity exists and user has permission to update
	existing, err := uc.userRepo.GetByID(ctx, user.ID)
	if err != nil {
		return fmt.Errorf("failed to get existing user: %w", err)
	}
	
	// Apply business rules for updates
	if err := uc.validateUpdate(existing, user); err != nil {
		return fmt.Errorf("update validation failed: %w", err)
	}
	
	return uc.userRepo.Update(ctx, user)
}

// Delete deletes a user by ID
func (uc *UserUseCase) Delete(ctx context.Context, id uuid.UUID) error {
	uc.logger.Debug(fmt.Sprintf("deleting user with ID %s", id))
	// Check if entity exists and can be deleted
	existing, err := uc.userRepo.GetByID(ctx, id)
	if err != nil {
		return fmt.Errorf("failed to get user for deletion: %w", err)
	}
	
	// Apply business rules for deletion
	if err := uc.validateDelete(existing); err != nil {
		return fmt.Errorf("delete validation failed: %w", err)
	}
	
	return uc.userRepo.Delete(ctx, id)
}

// validateUser validates a user entity
func (uc *UserUseCase) validateUser(user *entityPkg.User) error {
	// @gohex:begin:custom:validate_user
	// Add validation logic here
	// Example validations:
	// - required validation
	// - format validation
	// - business_rules validation
	return nil
	// @gohex:end:custom:validate_user
}

// applyBusinessFilters applies business rules to filters
func (uc *UserUseCase) applyBusinessFilters(filters map[string]interface{}) map[string]interface{} {
	// @gohex:begin:custom:apply_business_filters
	// Add business filter logic here
	// Example: Add tenant filtering, access control, etc.
	return filters
	// @gohex:end:custom:apply_business_filters
}

// validateUpdate validates business rules for updates
func (uc *UserUseCase) validateUpdate(existing, updated *entityPkg.User) error {
	// @gohex:begin:custom:validate_update
	// Add update validation logic here
	// Example: Check permissions, validate changes, etc.
	return nil
	// @gohex:end:custom:validate_update
}

// validateDelete validates business rules for deletion
func (uc *UserUseCase) validateDelete(user *entityPkg.User) error {
	// @gohex:begin:custom:validate_delete
	// Add delete validation logic here
	// Example: Check dependencies, permissions, etc.
	return nil
	// @gohex:end:custom:validate_delete
}

// Custom business logic methods
// @gohex:begin:custom:business_methods
// Add your custom business logic methods here
// @gohex:end:custom:business_methods
