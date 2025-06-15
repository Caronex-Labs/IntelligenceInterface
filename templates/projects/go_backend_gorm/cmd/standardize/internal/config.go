package internal

// Configuration structures for YAML parsing

// DomainConfig represents the complete domain configuration
type DomainConfig struct {
	Version     string      `yaml:"version"`
	Domain      string      `yaml:"domain"`
	Description string      `yaml:"description"`
	Entity      EntityConfig `yaml:"entity"`
	Model       ModelConfig  `yaml:"model,omitempty"`
	Models      []ModelConfig `yaml:"models,omitempty"`
	API         APIConfig    `yaml:"api,omitempty"`
	Repository  RepositoryConfig `yaml:"repository,omitempty"`
	UseCase     UseCaseConfig `yaml:"use_case,omitempty"`
	Handlers    HandlersConfig `yaml:"handlers,omitempty"`
	Endpoints   []EndpointConfig `yaml:"endpoints,omitempty"`
	Generation  GenerationConfig `yaml:"generation,omitempty"`
	Features    FeaturesConfig `yaml:"features,omitempty"`
	Module      string      `yaml:"module,omitempty"`
}

// EntityConfig represents entity configuration
type EntityConfig struct {
	Name             string              `yaml:"name"`
	Description      string              `yaml:"description"`
	Package          string              `yaml:"package,omitempty"`
	Fields           []FieldConfig       `yaml:"fields,omitempty"`
	ComputedFields   []ComputedFieldConfig `yaml:"computed_fields,omitempty"`
	ConversionMethods []ConversionMethodConfig `yaml:"conversion_methods,omitempty"`
	CustomMethods    []CustomMethodConfig `yaml:"custom_methods,omitempty"`
	Imports          []string            `yaml:"imports,omitempty"`
	RequiresUUID     bool                `yaml:"requires_uuid,omitempty"`
}

// FieldConfig represents a field configuration
type FieldConfig struct {
	Name        string   `yaml:"name"`
	Type        string   `yaml:"type"`
	Tags        string   `yaml:"tags,omitempty"`
	Description string   `yaml:"description,omitempty"`
	Standard    bool     `yaml:"standard,omitempty"`
	Computed    bool     `yaml:"computed,omitempty"`
	Unique      bool     `yaml:"unique,omitempty"`
	Nullable    bool     `yaml:"nullable,omitempty"`
	Default     interface{} `yaml:"default,omitempty"`
	Validations []string `yaml:"validations,omitempty"`
	ModelField  string   `yaml:"model_field,omitempty"`
}

// ComputedFieldConfig represents computed field configuration
type ComputedFieldConfig struct {
	Name        string `yaml:"name"`
	NameSnake   string `yaml:"name_snake,omitempty"`
	Type        string `yaml:"type"`
	Description string `yaml:"description,omitempty"`
	Formula     string `yaml:"formula,omitempty"`
}

// ConversionMethodConfig represents conversion method configuration
type ConversionMethodConfig struct {
	Name        string `yaml:"name"`
	Description string `yaml:"description,omitempty"`
	SourceType  string `yaml:"source_type"`
	TargetType  string `yaml:"target_type"`
	Placeholder bool   `yaml:"placeholder,omitempty"`
}

// CustomMethodConfig represents custom method configuration
type CustomMethodConfig struct {
	Name                  string           `yaml:"name"`
	NameSnake            string           `yaml:"name_snake,omitempty"`
	Description          string           `yaml:"description,omitempty"`
	Parameters           []ParameterConfig `yaml:"parameters,omitempty"`
	Returns              []string         `yaml:"returns,omitempty"`
	DefaultImplementation string           `yaml:"default_implementation,omitempty"`
}

// ParameterConfig represents method parameter configuration
type ParameterConfig struct {
	Name string `yaml:"name"`
	Type string `yaml:"type"`
}

// ModelConfig represents model configuration
type ModelConfig struct {
	Name                string                    `yaml:"name"`
	TableName           string                    `yaml:"table_name,omitempty"`
	Description         string                    `yaml:"description,omitempty"`
	Fields              []ModelFieldConfig        `yaml:"fields,omitempty"`
	Indexes             []ModelIndexConfig        `yaml:"indexes,omitempty"`
	Constraints         []ModelConstraintConfig   `yaml:"constraints,omitempty"`
	Hooks               ModelHooksConfig          `yaml:"hooks,omitempty"`
	ComputedMethods     []ModelMethodConfig       `yaml:"computed_methods,omitempty"`
	ValidationMethods   []ModelMethodConfig       `yaml:"validation_methods,omitempty"`
	CustomMethods       []ModelMethodConfig       `yaml:"custom_methods,omitempty"`
	Relationships       []ModelRelationshipConfig `yaml:"relationships,omitempty"`
	Imports             []string                  `yaml:"imports,omitempty"`
	RequiresUUID        bool                      `yaml:"requires_uuid,omitempty"`
	RequiresTime        bool                      `yaml:"requires_time,omitempty"`
	SoftDelete          bool                      `yaml:"soft_delete,omitempty"`
}

// ModelFieldConfig represents a model field configuration
type ModelFieldConfig struct {
	Name             string      `yaml:"name"`
	Type             string      `yaml:"type"`
	GormTags         string      `yaml:"gorm_tags,omitempty"`
	JSONTags         string      `yaml:"json_tags,omitempty"`
	Description      string      `yaml:"description,omitempty"`
	Standard         bool        `yaml:"standard,omitempty"`
	Unique           bool        `yaml:"unique,omitempty"`
	Nullable         bool        `yaml:"nullable,omitempty"`
	DefaultValue     interface{} `yaml:"default,omitempty"`
	MaxLength        int         `yaml:"max_length,omitempty"`
	MinLength        int         `yaml:"min_length,omitempty"`
	Constraints      []string    `yaml:"constraints,omitempty"`
	Validations      []string    `yaml:"validations,omitempty"`
	ExcludeFromJSON  bool        `yaml:"exclude_from_json,omitempty"`
	Sensitive        bool        `yaml:"sensitive,omitempty"`
}

// ModelIndexConfig represents a database index configuration
type ModelIndexConfig struct {
	Name   string   `yaml:"name"`
	Fields []string `yaml:"fields"`
	Unique bool     `yaml:"unique,omitempty"`
	Type   string   `yaml:"type,omitempty"`
}

// ModelConstraintConfig represents a database constraint configuration
type ModelConstraintConfig struct {
	Name      string `yaml:"name"`
	Type      string `yaml:"type"`
	Condition string `yaml:"condition,omitempty"`
	Fields    []string `yaml:"fields,omitempty"`
}

// ModelHooksConfig represents GORM hooks configuration
type ModelHooksConfig struct {
	BeforeCreate bool `yaml:"before_create,omitempty"`
	BeforeUpdate bool `yaml:"before_update,omitempty"`
	AfterCreate  bool `yaml:"after_create,omitempty"`
	AfterUpdate  bool `yaml:"after_update,omitempty"`
	BeforeDelete bool `yaml:"before_delete,omitempty"`
	AfterDelete  bool `yaml:"after_delete,omitempty"`
	AfterFind    bool `yaml:"after_find,omitempty"`
}

// ModelMethodConfig represents a model method configuration
type ModelMethodConfig struct {
	Name           string `yaml:"name"`
	NameSnake      string `yaml:"name_snake,omitempty"`
	Description    string `yaml:"description,omitempty"`
	Returns        string `yaml:"returns,omitempty"`
	Parameters     string `yaml:"parameters,omitempty"`
	Implementation string `yaml:"implementation,omitempty"`
	Placeholder    bool   `yaml:"placeholder,omitempty"`
}

// ModelRelationshipConfig represents a model relationship configuration
type ModelRelationshipConfig struct {
	Type         string `yaml:"type"`         // belongsTo, hasOne, hasMany, manyToMany
	Entity       string `yaml:"entity"`       // Related entity name
	ForeignKey   string `yaml:"foreign_key,omitempty"`
	JoinTable    string `yaml:"join_table,omitempty"`
	Description  string `yaml:"description,omitempty"`
}

// APIConfig represents API configuration
type APIConfig struct {
	BasePath  string           `yaml:"base_path,omitempty"`
	Requests  []RequestConfig  `yaml:"requests,omitempty"`
	Responses []ResponseConfig `yaml:"responses,omitempty"`
}

// RequestConfig represents request type configuration
type RequestConfig struct {
	Name        string        `yaml:"name"`
	Description string        `yaml:"description,omitempty"`
	Fields      []FieldConfig `yaml:"fields,omitempty"`
}

// ResponseConfig represents response type configuration
type ResponseConfig struct {
	Name        string        `yaml:"name"`
	Description string        `yaml:"description,omitempty"`
	Fields      []FieldConfig `yaml:"fields,omitempty"`
}

// RepositoryConfig represents repository configuration
type RepositoryConfig struct {
	Description   string               `yaml:"description,omitempty"`
	Interface     RepositoryInterfaceConfig `yaml:"interface,omitempty"`
	Implementation RepositoryImplConfig `yaml:"implementation,omitempty"`
	CustomMethods []CustomMethodConfig `yaml:"custom_methods,omitempty"`
	Queries       []QueryConfig        `yaml:"queries,omitempty"`
	Pagination    PaginationConfig     `yaml:"pagination,omitempty"`
	Filtering     FilteringConfig      `yaml:"filtering,omitempty"`
	Caching       CachingConfig        `yaml:"caching,omitempty"`
	Logging       LoggingConfig        `yaml:"logging,omitempty"`
	Transactions  TransactionConfig    `yaml:"transactions,omitempty"`
}

// RepositoryInterfaceConfig represents repository interface configuration
type RepositoryInterfaceConfig struct {
	Name           string                 `yaml:"name,omitempty"`
	StandardMethods RepositoryMethodsConfig `yaml:"standard_methods,omitempty"`
	CustomMethods  []RepositoryMethodConfig `yaml:"custom_methods,omitempty"`
}

// RepositoryMethodsConfig represents standard CRUD method configuration
type RepositoryMethodsConfig struct {
	Create    bool `yaml:"create,omitempty"`
	GetByID   bool `yaml:"get_by_id,omitempty"`
	List      bool `yaml:"list,omitempty"`
	Update    bool `yaml:"update,omitempty"`
	Delete    bool `yaml:"delete,omitempty"`
	Count     bool `yaml:"count,omitempty"`
	Exists    bool `yaml:"exists,omitempty"`
	GetByField bool `yaml:"get_by_field,omitempty"`
}

// RepositoryMethodConfig represents individual repository method configuration
type RepositoryMethodConfig struct {
	Name           string                    `yaml:"name"`
	Description    string                    `yaml:"description,omitempty"`
	Parameters     []RepositoryParameterConfig `yaml:"parameters,omitempty"`
	Returns        string                    `yaml:"returns,omitempty"`
	Query          string                    `yaml:"query,omitempty"`
	Filterable     bool                      `yaml:"filterable,omitempty"`
	Paginatable    bool                      `yaml:"paginatable,omitempty"`
	Cacheable      bool                      `yaml:"cacheable,omitempty"`
	Transaction    bool                      `yaml:"transaction,omitempty"`
	Implementation string                    `yaml:"implementation,omitempty"`
	Placeholder    bool                      `yaml:"placeholder,omitempty"`
}

// RepositoryParameterConfig represents method parameter configuration
type RepositoryParameterConfig struct {
	Name string `yaml:"name"`
	Type string `yaml:"type"`
	Description string `yaml:"description,omitempty"`
	Required bool `yaml:"required,omitempty"`
}

// RepositoryImplConfig represents repository implementation configuration
type RepositoryImplConfig struct {
	Name         string   `yaml:"name,omitempty"`
	Dependencies []string `yaml:"dependencies,omitempty"`
	ErrorHandling string  `yaml:"error_handling,omitempty"`
}

// QueryConfig represents custom query configuration
type QueryConfig struct {
	Name        string `yaml:"name"`
	Description string `yaml:"description,omitempty"`
	SQL         string `yaml:"sql,omitempty"`
	GORM        string `yaml:"gorm,omitempty"`
	Parameters  []RepositoryParameterConfig `yaml:"parameters,omitempty"`
	Returns     string `yaml:"returns,omitempty"`
}

// PaginationConfig represents pagination configuration
type PaginationConfig struct {
	Enabled     bool   `yaml:"enabled,omitempty"`
	DefaultLimit int   `yaml:"default_limit,omitempty"`
	MaxLimit    int    `yaml:"max_limit,omitempty"`
	Type        string `yaml:"type,omitempty"` // offset, cursor
}

// FilteringConfig represents filtering configuration
type FilteringConfig struct {
	Enabled      bool     `yaml:"enabled,omitempty"`
	Fields       []string `yaml:"fields,omitempty"`
	Operators    []string `yaml:"operators,omitempty"`
	SearchFields []string `yaml:"search_fields,omitempty"`
}

// CachingConfig represents caching configuration
type CachingConfig struct {
	Enabled bool   `yaml:"enabled,omitempty"`
	TTL     string `yaml:"ttl,omitempty"`
	Keys    []string `yaml:"keys,omitempty"`
}

// LoggingConfig represents logging configuration
type LoggingConfig struct {
	Enabled bool   `yaml:"enabled,omitempty"`
	Level   string `yaml:"level,omitempty"`
	Methods []string `yaml:"methods,omitempty"`
}

// TransactionConfig represents transaction configuration
type TransactionConfig struct {
	Enabled bool     `yaml:"enabled,omitempty"`
	Methods []string `yaml:"methods,omitempty"`
}

// UseCaseConfig represents use case configuration
type UseCaseConfig struct {
	Description     string                   `yaml:"description,omitempty"`
	Interface       UseCaseInterfaceConfig   `yaml:"interface,omitempty"`
	Implementation  UseCaseImplConfig        `yaml:"implementation,omitempty"`
	BusinessMethods []BusinessMethodConfig   `yaml:"business_methods,omitempty"`
	Validation      ValidationConfig         `yaml:"validation,omitempty"`
	Transactions    TransactionConfig        `yaml:"transactions,omitempty"`
	Logging         LoggingConfig            `yaml:"logging,omitempty"`
	Events          EventConfig              `yaml:"events,omitempty"`
	Dependencies    []DependencyConfig       `yaml:"dependencies,omitempty"`
}

// UseCaseInterfaceConfig represents use case interface configuration
type UseCaseInterfaceConfig struct {
	Name            string                    `yaml:"name,omitempty"`
	StandardMethods UseCaseStandardMethods    `yaml:"standard_methods,omitempty"`
	BusinessMethods []UseCaseMethodConfig     `yaml:"business_methods,omitempty"`
}

// UseCaseStandardMethods represents standard CRUD method configuration for use cases
type UseCaseStandardMethods struct {
	Create    bool `yaml:"create,omitempty"`
	GetByID   bool `yaml:"get_by_id,omitempty"`
	List      bool `yaml:"list,omitempty"`
	Update    bool `yaml:"update,omitempty"`
	Delete    bool `yaml:"delete,omitempty"`
	Validate  bool `yaml:"validate,omitempty"`
	Count     bool `yaml:"count,omitempty"`
}

// UseCaseMethodConfig represents individual use case method configuration
type UseCaseMethodConfig struct {
	Name            string                      `yaml:"name"`
	Description     string                      `yaml:"description,omitempty"`
	Parameters      []UseCaseParameterConfig    `yaml:"parameters,omitempty"`
	Returns         string                      `yaml:"returns,omitempty"`
	Validation      []string                    `yaml:"validation,omitempty"`
	Repositories    []string                    `yaml:"repositories,omitempty"`
	Transactional   bool                        `yaml:"transactional,omitempty"`
	Authorization   []string                    `yaml:"authorization,omitempty"`
	Events          []string                    `yaml:"events,omitempty"`
	Implementation  string                      `yaml:"implementation,omitempty"`
	Placeholder     bool                        `yaml:"placeholder,omitempty"`
	Conversions     ConversionConfig            `yaml:"conversions,omitempty"`
}

// UseCaseParameterConfig represents method parameter configuration
type UseCaseParameterConfig struct {
	Name        string `yaml:"name"`
	Type        string `yaml:"type"`
	Description string `yaml:"description,omitempty"`
	Required    bool   `yaml:"required,omitempty"`
	Validation  []string `yaml:"validation,omitempty"`
}

// UseCaseImplConfig represents use case implementation configuration
type UseCaseImplConfig struct {
	Name            string   `yaml:"name,omitempty"`
	Dependencies    []string `yaml:"dependencies,omitempty"`
	ErrorHandling   string   `yaml:"error_handling,omitempty"`
}

// BusinessMethodConfig represents business logic method configuration
type BusinessMethodConfig struct {
	Name           string                   `yaml:"name"`
	Description    string                   `yaml:"description,omitempty"`
	Parameters     []UseCaseParameterConfig `yaml:"parameters,omitempty"`
	Returns        string                   `yaml:"returns,omitempty"`
	Steps          []BusinessStepConfig     `yaml:"steps,omitempty"`
	Validation     []string                 `yaml:"validation,omitempty"`
	Authorization  []string                 `yaml:"authorization,omitempty"`
	Transactional  bool                     `yaml:"transactional,omitempty"`
	Events         []string                 `yaml:"events,omitempty"`
	Implementation string                   `yaml:"implementation,omitempty"`
	Placeholder    bool                     `yaml:"placeholder,omitempty"`
	Conversions    ConversionConfig         `yaml:"conversions,omitempty"`
}

// BusinessStepConfig represents individual steps in business methods
type BusinessStepConfig struct {
	Name         string            `yaml:"name"`
	Type         string            `yaml:"type"` // validate, repository_call, business_logic, event
	Repository   string            `yaml:"repository,omitempty"`
	Method       string            `yaml:"method,omitempty"`
	Validation   string            `yaml:"validation,omitempty"`
	Event        string            `yaml:"event,omitempty"`
	Conversions  ConversionConfig  `yaml:"conversions,omitempty"`
	ErrorHandling string           `yaml:"error_handling,omitempty"`
}

// ConversionConfig represents entity/DTO conversion configuration
type ConversionConfig struct {
	InputConversion  []ConversionStepConfig `yaml:"input_conversion,omitempty"`
	OutputConversion []ConversionStepConfig `yaml:"output_conversion,omitempty"`
	AutoDetect       bool                   `yaml:"auto_detect,omitempty"`
}

// ConversionStepConfig represents individual conversion steps
type ConversionStepConfig struct {
	From   string `yaml:"from"`
	To     string `yaml:"to"`
	Method string `yaml:"method,omitempty"`
}

// ValidationConfig represents validation configuration
type ValidationConfig struct {
	Enabled bool     `yaml:"enabled,omitempty"`
	Rules   []string `yaml:"rules,omitempty"`
	Custom  []string `yaml:"custom,omitempty"`
}

// EventConfig represents event configuration
type EventConfig struct {
	Enabled bool     `yaml:"enabled,omitempty"`
	Types   []string `yaml:"types,omitempty"`
	Publisher string `yaml:"publisher,omitempty"`
}

// DependencyConfig represents dependency configuration
type DependencyConfig struct {
	Name string `yaml:"name"`
	Type string `yaml:"type"`
	Alias string `yaml:"alias,omitempty"`
}

// HandlersConfig represents comprehensive handlers configuration
type HandlersConfig struct {
	Description        string                    `yaml:"description,omitempty"`
	Handler           HandlerConfig             `yaml:"handler,omitempty"`
	StandardEndpoints StandardEndpointsConfig   `yaml:"standard_endpoints,omitempty"`
	CustomEndpoints   []CustomEndpointConfig    `yaml:"custom_endpoints,omitempty"`
	RequestTypes      []DTOConfig               `yaml:"request_types,omitempty"`
	ResponseTypes     []DTOConfig               `yaml:"response_types,omitempty"`
	ErrorHandling     ErrorHandlingConfig       `yaml:"error_handling,omitempty"`
	Middleware        MiddlewareConfig          `yaml:"middleware,omitempty"`
	OpenAPI          OpenAPIConfig             `yaml:"openapi,omitempty"`
	Endpoints        []EndpointConfig          `yaml:"endpoints,omitempty"` // Legacy support
}

// HandlerConfig represents handler-level configuration
type HandlerConfig struct {
	Name         string   `yaml:"name,omitempty"`
	Description  string   `yaml:"description,omitempty"`
	BasePath     string   `yaml:"base_path,omitempty"`
	Dependencies []string `yaml:"dependencies,omitempty"`
	Middleware   []string `yaml:"middleware,omitempty"`
}

// StandardEndpointsConfig represents standard CRUD endpoint configuration
type StandardEndpointsConfig struct {
	Create   EndpointDetailsConfig `yaml:"create,omitempty"`
	List     EndpointDetailsConfig `yaml:"list,omitempty"`
	GetByID  EndpointDetailsConfig `yaml:"get_by_id,omitempty"`
	Update   EndpointDetailsConfig `yaml:"update,omitempty"`
	Delete   EndpointDetailsConfig `yaml:"delete,omitempty"`
}

// EndpointDetailsConfig represents detailed endpoint configuration
type EndpointDetailsConfig struct {
	Enabled       bool                    `yaml:"enabled,omitempty"`
	Method        string                  `yaml:"method,omitempty"`
	Path          string                  `yaml:"path,omitempty"`
	RequestType   string                  `yaml:"request_type,omitempty"`
	ResponseType  string                  `yaml:"response_type,omitempty"`
	UseCaseMethod string                  `yaml:"use_case_method,omitempty"`
	StatusCode    int                     `yaml:"status_code,omitempty"`
	Validation    []string                `yaml:"validation,omitempty"`
	Authorization []string                `yaml:"authorization,omitempty"`
	QueryParams   []QueryParamConfig      `yaml:"query_params,omitempty"`
	PathParams    []PathParamConfig       `yaml:"path_params,omitempty"`
	Pagination    PaginationConfig        `yaml:"pagination,omitempty"`
	Filtering     FilteringConfig         `yaml:"filtering,omitempty"`
	RateLimiting  RateLimitingConfig      `yaml:"rate_limiting,omitempty"`
}

// CustomEndpointConfig represents custom endpoint configuration
type CustomEndpointConfig struct {
	Name          string              `yaml:"name"`
	Description   string              `yaml:"description,omitempty"`
	Method        string              `yaml:"method"`
	Path          string              `yaml:"path"`
	RequestType   string              `yaml:"request_type,omitempty"`
	ResponseType  string              `yaml:"response_type,omitempty"`
	UseCaseMethod string              `yaml:"use_case_method"`
	StatusCode    int                 `yaml:"status_code,omitempty"`
	Validation    []string            `yaml:"validation,omitempty"`
	Authorization []string            `yaml:"authorization,omitempty"`
	PathParams    []PathParamConfig   `yaml:"path_params,omitempty"`
	RateLimiting  RateLimitingConfig  `yaml:"rate_limiting,omitempty"`
}

// PathParamConfig represents path parameter configuration
type PathParamConfig struct {
	Name        string `yaml:"name"`
	Type        string `yaml:"type"`
	Description string `yaml:"description,omitempty"`
	Required    bool   `yaml:"required,omitempty"`
}

// DTOConfig represents Data Transfer Object configuration
type DTOConfig struct {
	Name        string           `yaml:"name"`
	Description string           `yaml:"description,omitempty"`
	Fields      []DTOFieldConfig `yaml:"fields,omitempty"`
}

// DTOFieldConfig represents DTO field configuration
type DTOFieldConfig struct {
	Name        string   `yaml:"name"`
	Type        string   `yaml:"type"`
	JSONTag     string   `yaml:"json_tag"`
	Validation  []string `yaml:"validation,omitempty"`
	Description string   `yaml:"description,omitempty"`
	Optional    bool     `yaml:"optional,omitempty"`
}

// ErrorHandlingConfig represents error handling configuration
type ErrorHandlingConfig struct {
	Enabled      bool                `yaml:"enabled,omitempty"`
	CustomErrors []CustomErrorConfig `yaml:"custom_errors,omitempty"`
}

// CustomErrorConfig represents custom error configuration
type CustomErrorConfig struct {
	Code    string `yaml:"code"`
	Status  int    `yaml:"status"`
	Message string `yaml:"message"`
}

// MiddlewareConfig represents middleware configuration
type MiddlewareConfig struct {
	CORS           CORSConfig           `yaml:"cors,omitempty"`
	RateLimiting   RateLimitingConfig   `yaml:"rate_limiting,omitempty"`
	Authentication AuthenticationConfig `yaml:"authentication,omitempty"`
	RequestLogging RequestLoggingConfig `yaml:"request_logging,omitempty"`
	RequestID      RequestIDConfig      `yaml:"request_id,omitempty"`
}

// CORSConfig represents CORS configuration
type CORSConfig struct {
	Enabled        bool     `yaml:"enabled,omitempty"`
	AllowedOrigins []string `yaml:"allowed_origins,omitempty"`
	AllowedMethods []string `yaml:"allowed_methods,omitempty"`
	AllowedHeaders []string `yaml:"allowed_headers,omitempty"`
}

// RateLimitingConfig represents rate limiting configuration
type RateLimitingConfig struct {
	Enabled             bool `yaml:"enabled,omitempty"`
	GlobalLimit        int  `yaml:"global_limit,omitempty"`
	PerIPLimit         int  `yaml:"per_ip_limit,omitempty"`
	RequestsPerMinute  int  `yaml:"requests_per_minute,omitempty"`
}

// AuthenticationConfig represents authentication configuration
type AuthenticationConfig struct {
	Enabled       bool     `yaml:"enabled,omitempty"`
	ExcludePaths  []string `yaml:"exclude_paths,omitempty"`
	JWTSecretEnv  string   `yaml:"jwt_secret_env,omitempty"`
}

// RequestLoggingConfig represents request logging configuration
type RequestLoggingConfig struct {
	Enabled        bool `yaml:"enabled,omitempty"`
	IncludeBody    bool `yaml:"include_body,omitempty"`
	IncludeHeaders bool `yaml:"include_headers,omitempty"`
}

// RequestIDConfig represents request ID configuration
type RequestIDConfig struct {
	Enabled bool   `yaml:"enabled,omitempty"`
	Header  string `yaml:"header,omitempty"`
}

// OpenAPIConfig represents OpenAPI documentation configuration
type OpenAPIConfig struct {
	Enabled     bool               `yaml:"enabled,omitempty"`
	Title       string             `yaml:"title,omitempty"`
	Description string             `yaml:"description,omitempty"`
	Version     string             `yaml:"version,omitempty"`
	Contact     OpenAPIContactConfig `yaml:"contact,omitempty"`
	Tags        []OpenAPITagConfig `yaml:"tags,omitempty"`
}

// OpenAPIContactConfig represents OpenAPI contact configuration
type OpenAPIContactConfig struct {
	Name  string `yaml:"name,omitempty"`
	Email string `yaml:"email,omitempty"`
}

// OpenAPITagConfig represents OpenAPI tag configuration
type OpenAPITagConfig struct {
	Name        string `yaml:"name"`
	Description string `yaml:"description,omitempty"`
}

// EndpointConfig represents endpoint configuration
type EndpointConfig struct {
	Method         string           `yaml:"method"`
	Path           string           `yaml:"path"`
	Handler        string           `yaml:"handler"`
	Description    string           `yaml:"description,omitempty"`
	Request        string           `yaml:"request,omitempty"`
	Response       string           `yaml:"response,omitempty"`
	StatusCode     int              `yaml:"status_code,omitempty"`
	UseCaseMethod  string           `yaml:"use_case_method,omitempty"`
	QueryParams    []QueryParamConfig `yaml:"query_params,omitempty"`
}

// QueryParamConfig represents query parameter configuration
type QueryParamConfig struct {
	Name        string      `yaml:"name"`
	Type        string      `yaml:"type"`
	Required    bool        `yaml:"required,omitempty"`
	Optional    bool        `yaml:"optional,omitempty"`
	Default     interface{} `yaml:"default,omitempty"`
	Description string      `yaml:"description,omitempty"`
}

// GenerationConfig represents generation options
type GenerationConfig struct {
	PreserveCustomCode bool `yaml:"preserve_custom_code,omitempty"`
	GenerateTests      bool `yaml:"generate_tests,omitempty"`
	GenerateMigrations bool `yaml:"generate_migrations,omitempty"`
	SoftDelete         bool `yaml:"soft_delete,omitempty"`
	UUIDPrimaryKey     bool `yaml:"uuid_primary_key,omitempty"`
	OverwriteGenerated bool `yaml:"overwrite_generated,omitempty"`
	BackupOnOverwrite  bool `yaml:"backup_on_overwrite,omitempty"`
}

// FeaturesConfig represents feature flags
type FeaturesConfig struct {
	Authentication bool `yaml:"authentication,omitempty"`
	Authorization  bool `yaml:"authorization,omitempty"`
	Auditing       bool `yaml:"auditing,omitempty"`
	Caching        bool `yaml:"caching,omitempty"`
	RateLimiting   bool `yaml:"rate_limiting,omitempty"`
}
