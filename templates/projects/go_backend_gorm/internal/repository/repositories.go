package repository

import (
	"reflect"

	"github.com/samber/do"

	"go_backend_gorm/internal/repository/health_repository"
)

// Repositories is a container for all application repositories
type Repositories struct {
	Health health_repository.IHealthRepository
	// Add more repositories here as your application grows
	// Fields will be dynamically added by domain repositories
	// For example:
	// User   user.IUserRepository
	// Product product.IProductRepository
	// Order  order.IOrderRepository
	
	// This struct is designed to be extended by domain repositories
	// Each domain repository will add its field to this struct
	// using the Register<Entity>Repository function
	
	// Dynamic fields
	dynamicFields map[string]interface{}
}

// NewRepositories creates a new Repositories instance with all repositories initialized
func NewRepositories(injector *do.Injector) (*Repositories, error) {
	// Get health repository
	healthRepo, err := health_repository.NewHealthRepository(injector)
	if err != nil {
		return nil, err
	}

	// Return repositories container
	return &Repositories{
		Health:        healthRepo,
		dynamicFields: make(map[string]interface{}),
		// Initialize other repositories here as needed
	}, nil
}

// RegisterRepositories registers all repositories in the dependency injection container
func RegisterRepositories(injector *do.Injector) {
	// Register Repositories container
	do.Provide(injector, NewRepositories)
	
	// Other repositories will register themselves
}

// AddField adds a field to the Repositories struct dynamically
func AddField(r *Repositories, name string, value interface{}) {
	if r.dynamicFields == nil {
		r.dynamicFields = make(map[string]interface{})
	}
	r.dynamicFields[name] = value
}

// GetField gets a field from the Repositories struct dynamically
func GetField(r *Repositories, name string) (interface{}, bool) {
	// First check if the field exists in the struct
	v := reflect.ValueOf(r).Elem()
	fieldValue := v.FieldByName(name)
	if fieldValue.IsValid() {
		return fieldValue.Interface(), true
	}
	
	// Then check if it exists in the dynamic fields
	if r.dynamicFields != nil {
		if value, ok := r.dynamicFields[name]; ok {
			return value, true
		}
	}
	
	return nil, false
}
