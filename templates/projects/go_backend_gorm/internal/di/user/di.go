package user

import (
	"github.com/samber/do"

	handlersPkg "go_backend_gorm/internal/interface/http/handlers/user"
	repositoryPkg "go_backend_gorm/internal/repository/user"
	usecasePkg "go_backend_gorm/internal/usecase/user"
)

// RegisterUser registers all user components in the dependency injection container
func RegisterUser(injector *do.Injector) {
	// Register entity
	// Entity creation is typically handled by the repository or use case
	// No need to register entity constructors
	
	// Register repository
	repositoryPkg.RegisterUserRepository(injector)
	
	// Register use case
	usecasePkg.RegisterUserUseCase(injector)
	
	// Register handler
	handlersPkg.RegisterUserHandler(injector)
}
