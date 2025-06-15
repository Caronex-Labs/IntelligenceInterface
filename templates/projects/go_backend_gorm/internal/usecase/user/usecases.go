package user

import (
	"github.com/samber/do"

	"go_backend_gorm/internal/usecase"
)

// RegisterUserUseCase registers the user use case in the dependency injection container
func RegisterUserUseCase(injector *do.Injector) {
	// Register the use case implementation
	do.Provide(injector, NewUserUseCase)
	
	// Register a callback to add the use case to the UseCases struct
	do.ProvideNamedValue(injector, "register_user_usecase", func(uc *usecase.UseCases) {
		// This will be called after UseCases is created
		// Add the User use case to the UseCases struct
		useCase, err := do.Invoke[*UserUseCase](injector)
		if err != nil {
			panic(err)
		}
		
		// Add the field dynamically using reflection
		usecase.AddField(uc, "User", useCase)
	})
}
