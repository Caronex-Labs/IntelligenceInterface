package user

import (
	"context"
	"errors"
	"fmt"

	"github.com/google/uuid"
	"github.com/samber/do"
	"gorm.io/gorm"

	"go_backend_gorm/external/postgres"
	entityPkg "go_backend_gorm/internal/core/entity/user"
	modelsPkg "go_backend_gorm/internal/core/models/user"
	"go_backend_gorm/internal/utils"
)

// IUserRepository defines the interface for user repository operations
type IUserRepository interface {
	// Create creates a new user
	Create(ctx context.Context, user *entityPkg.User) error
	// GetByID retrieves a user by ID
	GetByID(ctx context.Context, id uuid.UUID) (*entityPkg.User, error)
	// List retrieves a list of users with optional filtering and pagination
	List(ctx context.Context, filters map[string]interface{}, limit, offset int) ([]*entityPkg.User, error)
	// Update updates an existing user
	Update(ctx context.Context, user *entityPkg.User) error
	// Delete deletes a user by ID
	Delete(ctx context.Context, id uuid.UUID) error
}

// UserRepository implements the user repository interface
type UserRepository struct {
	db     *postgres.DB
	logger *utils.Logger
}

// Ensure UserRepository implements the IUserRepository interface
var _ IUserRepository = (*UserRepository)(nil)

// NewUserRepository creates a new user repository
func NewUserRepository(injector *do.Injector) (IUserRepository, error) {
	// Get dependencies from injector
	db := do.MustInvoke[*postgres.DB](injector)
	log := do.MustInvoke[*utils.Logger](injector)

	return &UserRepository{
		db:     db,
		logger: log,
	}, nil
}

// Create creates a new user
func (r *UserRepository) Create(ctx context.Context, user *entityPkg.User) error {
	r.logger.Debug(fmt.Sprintf("creating user %+v", user))
	
	// Convert entity to model
	model := user.ToUserModel()
	return r.db.WithContext(ctx).Transaction(func(tx *gorm.DB) error {
		return tx.Create(model).Error
	})
}

// GetByID retrieves a user by ID
func (r *UserRepository) GetByID(ctx context.Context, id uuid.UUID) (*entityPkg.User, error) {
	r.logger.Debug(fmt.Sprintf("getting user by ID %s", id))
	
	var model modelsPkg.User
	err := r.db.WithContext(ctx).First(&model, "id = ?", id).Error
	if err != nil {
		if errors.Is(err, gorm.ErrRecordNotFound) {
			return nil, fmt.Errorf("user not found: %w", err)
		}
		return nil, err
	}
	
	// Convert model to entity
	entity := entityPkg.FromUserModel(&model)
	return entity, nil
}

// List retrieves a list of users with optional filtering and pagination
func (r *UserRepository) List(ctx context.Context, filters map[string]interface{}, limit, offset int) ([]*entityPkg.User, error) {
	r.logger.Debug(fmt.Sprintf("listing users with filters %+v, limit %d, offset %d", filters, limit, offset))
	
	var models []modelsPkg.User
	
	query := r.db.WithContext(ctx)
	// Apply filters if provided
	if filters != nil {
		for key, value := range filters {
			query = query.Where(key, value)
		}
	}
	// Apply pagination
	if limit > 0 {
		if limit > 100 {
			limit = 100
		}
		query = query.Limit(limit)
	} else {
		query = query.Limit(20)
	}
	if offset > 0 {
		query = query.Offset(offset)
	}
	
	err := query.Find(&models).Error
	if err != nil {
		return nil, err
	}
	
	// Convert models to entities
	entities := make([]*entityPkg.User, len(models))
	for i, model := range models {
		modelCopy := model // Create a copy to avoid reference issues
		entities[i] = entityPkg.FromUserModel(&modelCopy)
	}
	
	return entities, nil
}

// Update updates an existing user
func (r *UserRepository) Update(ctx context.Context, user *entityPkg.User) error {
	r.logger.Debug(fmt.Sprintf("updating user %+v", user))
	
	// Convert entity to model
	model := user.ToUserModel()
	return r.db.WithContext(ctx).Transaction(func(tx *gorm.DB) error {
		return tx.Save(model).Error
	})
}

// Delete deletes a user by ID
func (r *UserRepository) Delete(ctx context.Context, id uuid.UUID) error {
	r.logger.Debug(fmt.Sprintf("deleting user with ID %s", id))
	return r.db.WithContext(ctx).Transaction(func(tx *gorm.DB) error {
		return tx.Delete(&modelsPkg.User{}, "id = ?", id).Error
	})
}

// Custom repository methods
// @gohex:begin:custom:repository_methods
// Add your custom repository methods here
// @gohex:end:custom:repository_methods
