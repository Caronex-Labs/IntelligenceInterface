package usecase

import (
	"reflect"

	"github.com/samber/do"
)

// UseCases is a container for all application use cases
type UseCases struct {
	Health IHealthUseCase
	// Add more use cases here as your application grows
	// Fields will be dynamically added by domain use cases
	// For example:
	// User   user.IUserUseCase
	// Product product.IProductUseCase
	// Order  order.IOrderUseCase
	
	// This struct is designed to be extended by domain use cases
	// Each domain use case will add its field to this struct
	// using the Register<Entity>UseCase function
	
	// Dynamic fields
	dynamicFields map[string]interface{}
}

// NewUseCases creates a new UseCases instance with all use cases initialized
func NewUseCases(injector *do.Injector) (*UseCases, error) {
	// Get health use case
	healthUC, err := do.Invoke[*HealthUseCase](injector)
	if err != nil {
		return nil, err
	}

	// Return use cases container
	return &UseCases{
		Health:        healthUC,
		dynamicFields: make(map[string]interface{}),
		// Initialize other use cases here as needed
	}, nil
}

// RegisterUseCases registers all use cases in the dependency injection container
func RegisterUseCases(injector *do.Injector) {
	// Register UseCases container
	do.Provide(injector, NewUseCases)
}

// AddField adds a field to the UseCases struct dynamically
func AddField(uc *UseCases, name string, value interface{}) {
	if uc.dynamicFields == nil {
		uc.dynamicFields = make(map[string]interface{})
	}
	uc.dynamicFields[name] = value
}

// GetField gets a field from the UseCases struct dynamically
func GetField(uc *UseCases, name string) (interface{}, bool) {
	// First check if the field exists in the struct
	v := reflect.ValueOf(uc).Elem()
	fieldValue := v.FieldByName(name)
	if fieldValue.IsValid() {
		return fieldValue.Interface(), true
	}
	
	// Then check if it exists in the dynamic fields
	if uc.dynamicFields != nil {
		if value, ok := uc.dynamicFields[name]; ok {
			return value, true
		}
	}
	
	return nil, false
}
