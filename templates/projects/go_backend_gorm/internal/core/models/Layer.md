# Models Layer Documentation

## Purpose
The Models layer contains database-specific data structures that map directly to database tables and handle all persistence concerns.

## Responsibilities

### What Models Are
- **Database Representations**: Models directly represent database table structures
- **ORM Integration**: Models contain all GORM tags and database constraints
- **Data Persistence**: Models handle database-specific concerns like primary keys, foreign keys, indexes
- **Migration Blueprints**: Models define the database schema through struct tags

### What Models Are NOT
- **Not Business Logic**: Models don't contain business validation or domain rules
- **Not API Responses**: Models don't contain HTTP-specific serialization
- **Not Transfer Objects**: Models are specific to the repository layer

## Data Flow

```
UseCase → Repository → Model → Database
UseCase ← Repository ← Model ← Database
```

## Key Patterns

### 1. Database Constraints
Models define all database-level constraints:
- Primary keys (`gorm:"primaryKey"`)
- Foreign keys (`gorm:"foreignKey:UserID"`)
- Unique constraints (`gorm:"uniqueIndex"`)
- Not null constraints (`gorm:"not null"`)
- Default values (`gorm:"default:true"`)
- Column types (`gorm:"type:text"`)

### 2. Relationships
Models define database relationships:
- **BelongsTo**: `gorm:"foreignKey:UserID"`
- **HasOne**: `gorm:"foreignKey:UserID"`
- **HasMany**: `gorm:"foreignKey:UserID"`
- **ManyToMany**: `gorm:"many2many:user_roles"`

### 3. Table Configuration
Models control table-level settings:
- Table naming (`TableName()` method)
- Soft deletes (with `gorm.DeletedAt`)
- Timestamps (CreatedAt, UpdatedAt)

### 4. Hooks and Callbacks
Models can implement GORM hooks:
- `BeforeCreate()` - Set UUIDs, defaults
- `BeforeUpdate()` - Update timestamps
- `AfterFind()` - Post-processing

## Architecture Benefits

1. **Database Abstraction**: Repository layer can change database schemas without affecting business logic
2. **Migration Safety**: Database constraints are clearly defined and versioned
3. **Performance**: Database-specific optimizations (indexes, constraints) are explicit
4. **Data Integrity**: Database-level constraints ensure data consistency

## Template Variables Available

- `{{.Entity}}` - PascalCase entity name (e.g., "User")
- `{{.EntitySnake}}` - snake_case entity name (e.g., "user")
- `{{.EntitiesSnake}}` - snake_case plural name (e.g., "users")
- `{{.Fields}}` - Array of configured fields with database tags
- `{{.Relationships}}` - Array of relationship configurations

## Generated Structure

```go
type {{.Entity}} struct {
    ID        uuid.UUID `gorm:"type:uuid;primaryKey" json:"id"`
    // Configured fields with database tags
    // Relationship fields based on configuration
    CreatedAt time.Time `gorm:"type:timestamp;default:now()" json:"created_at"`
    UpdatedAt time.Time `gorm:"type:timestamp;default:now()" json:"updated_at"`
}

func ({{.Entity}}) TableName() string {
    return "{{.EntitiesSnake}}"
}

func (m *{{.Entity}}) BeforeCreate() error {
    // UUID generation and default value setting
}

// Relationship methods (if configured)
func (m *{{.Entity}}) GetRelatedEntities() error
func (m *{{.Entity}}) AddRelatedEntity() error
```

## Configuration-Driven Features

The template uses configuration to generate:
- **Field Tags**: Database-specific GORM tags from field configuration
- **Relationships**: Association definitions from relationship configuration
- **Constraints**: Database constraints from field validation rules
- **Indexes**: Database indexes from field configuration
- **Default Values**: Default value handling from field configuration

## Database Constraints vs Business Validation

| Concern | Layer | Example |
|---------|-------|---------|
| Data Type | Model | `gorm:"type:varchar(255)"` |
| Required Field | Model | `gorm:"not null"` |
| Unique Value | Model | `gorm:"uniqueIndex"` |
| Foreign Key | Model | `gorm:"foreignKey:UserID"` |
| Business Rule | Entity | `ValidateEmail()` method |
| Cross-field Logic | Entity | `ValidatePasswordStrength()` |
| External API | UseCase | Check external service |

This separation ensures that database constraints handle data integrity while business validation handles domain rules.
