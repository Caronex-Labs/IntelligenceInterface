package user

import (
)

// User represents User represents a user in the database
type User struct {
	ID uint `gorm:"primaryKey"` `json:"id"` // Primary key identifier
	CreatedAt time.Time `gorm:"type:timestamp;default:now()"` `json:"created_at"` // Record creation timestamp
	UpdatedAt time.Time `gorm:"type:timestamp;default:now()"` `json:"updated_at"` // Record update timestamp

	// @gohex:begin:custom:fields
	// Add additional custom fields here
	// @gohex:end:custom:fields
}

// TableName specifies the table name for User
func (User) TableName() string {
	return "users"
}

// Custom business logic methods
// @gohex:begin:custom:business_methods
// Add your custom business logic methods here
// @gohex:end:custom:business_methods
