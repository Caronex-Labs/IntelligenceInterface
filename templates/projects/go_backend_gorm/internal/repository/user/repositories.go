package user

import (
	"github.com/samber/do"

	"go_backend_gorm/internal/repository"
)

// RegisterUserRepository registers the user repository in the dependency injection container
func RegisterUserRepository(injector *do.Injector) {
	// Register the repository implementation
	do.Provide(injector, NewUserRepository)
	
	// Register a callback to add the repository to the Repositories struct
	do.ProvideNamedValue(injector, "register_user_repository", func(r *repository.Repositories) {
		// This will be called after Repositories is created
		// Add the User repository to the Repositories struct
		repo, err := do.Invoke[IUserRepository](injector)
		if err != nil {
			panic(err)
		}
		
		// Add the field dynamically using reflection
		repository.AddField(r, "User", repo)
	})
}
