package user

import (
	"time"
	
	modelsPkg "go_backend_gorm/internal/core/models/user"
)

// User 
type User struct {
	ID uint `json:"id"` // Unique identifier
	CreatedAt time.Time `json:"created_at"` // Creation timestamp
	UpdatedAt time.Time `json:"updated_at"` // Last update timestamp
	// @gohex:begin:custom:fields
	// Add your custom fields here
	// @gohex:end:custom:fields
}

// FromUserModel converts a model to an entity
func FromUserModel(model *modelsPkg.User) *User {
	if model == nil {
		return nil
	}
	
	entity := &User{
		ID: model.ID,
		CreatedAt: model.CreatedAt,
		UpdatedAt: model.UpdatedAt,
	}
	
	// @gohex:begin:custom:from_model_mapping
	// Map custom fields from model to entity
	// @gohex:end:custom:from_model_mapping
	
	return entity
}

// ToUserModel converts an entity to a model
func (e *User) ToUserModel() *modelsPkg.User {
	if e == nil {
		return nil
	}
	
	model := &modelsPkg.User{
		ID: e.ID,
		CreatedAt: e.CreatedAt,
		UpdatedAt: e.UpdatedAt,
	}
	
	// @gohex:begin:custom:to_model_mapping
	// Map custom fields from entity to model
	// @gohex:end:custom:to_model_mapping
	
	return model
}

// FromUserRequest converts a request to an entity
func FromUserRequest(request interface{}) *User {
	// @gohex:begin:custom:from_request_implementation
	// Implementation will be added by the developer
	// Example:
	// if req, ok := request.(*CreateUserRequest); ok {
	//     return &User{
	//         IsActive: true,
	//     }
	// }
	return &User{}
	// @gohex:end:custom:from_request_implementation
}

// ToUserResponse converts an entity to a response
func (e *User) ToUserResponse() interface{} {
	// @gohex:begin:custom:to_response_implementation
	// Implementation will be added by the developer
	// Example:
	// return &UserResponse{
	//     ID: e.ID,
	//     CreatedAt: e.CreatedAt,
	// }
	return nil
	// @gohex:end:custom:to_response_implementation
}

// @gohex:begin:custom:methods
// Add your custom entity methods here
// @gohex:end:custom:methods
