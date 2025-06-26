Feature: Hierarchical Configuration Merging
  As a template generation system
  I want hierarchical configuration merging across all template layers
  So that configurations inherit and override properly across the architecture

  Background:
    Given the configuration system is properly initialized
    And I have a clean working directory for configuration testing

  Scenario: Four-Layer Configuration Inheritance
    Given I have domain.yaml with base configuration:
      """
      domain:
        name: "User"
        description: "User management domain"
        version: "1.0.0"
      
      default_settings:
        validation: true
        logging: true
        cache_enabled: false
      
      field_types:
        default_string: "str"
        default_id: "int"
      """
    And I have usecase.yaml with use case-specific overrides:
      """
      usecase:
        business_logic: true
        transaction_management: true
      
      default_settings:
        cache_enabled: true  # Override domain setting
        retry_attempts: 3
      
      validation_rules:
        strict_mode: true
        email_validation: true
      """
    And I have repository.yaml with data access overrides:
      """
      repository:
        async_operations: true
        connection_pooling: true
      
      default_settings:
        logging: false  # Override domain setting
        query_timeout: 30
      
      database:
        provider: "postgresql"
        migration_support: true
      """
    And I have api.yaml with interface-specific overrides:
      """
      api:
        auto_documentation: true
        cors_enabled: true
      
      default_settings:
        validation: false  # Override domain setting
        rate_limiting: true
      
      endpoints:
        prefix: "/api/v1"
        authentication_required: true
      """
    When I merge configurations hierarchically
    Then domain configuration provides base settings for all layers
    And each layer can override and extend parent layer configuration
    And final merged configuration contains complete template context
    And configuration precedence follows Domain → UseCase → Repository → Interface
    And the merged configuration should contain:
      | Section | Key | Value | Source |
      | domain | name | User | domain |
      | default_settings | validation | false | api (highest precedence) |
      | default_settings | cache_enabled | true | usecase |
      | default_settings | logging | false | repository |
      | usecase | business_logic | true | usecase |
      | repository | async_operations | true | repository |
      | api | auto_documentation | true | api |

  Scenario: Deep Merge with Complex Nested Structures
    Given I have domain.yaml with nested configuration:
      """
      domain:
        name: "Blog"
      
      database:
        connection:
          host: "localhost"
          port: 5432
          options:
            pool_size: 10
            timeout: 30
        
      features:
        - "authentication"
        - "authorization"
      
      field_mapping:
        string_fields:
          default_length: 255
          nullable: true
        numeric_fields:
          precision: 2
      """
    And I have usecase.yaml with nested overrides:
      """
      database:
        connection:
          port: 5433  # Override port
          options:
            pool_size: 20  # Override pool_size
            max_connections: 100  # Add new option
      
      features:
        - "caching"  # Replace entire array
        - "monitoring"
      
      field_mapping:
        string_fields:
          default_length: 500  # Override default_length
          encrypted: true  # Add new field
      """
    When I perform hierarchical merging
    Then nested structures merge recursively with proper precedence
    And array values are replaced completely not merged
    And the merged database.connection.host should be "localhost" from domain
    And the merged database.connection.port should be 5433 from usecase
    And the merged database.connection.options.pool_size should be 20 from usecase
    And the merged database.connection.options.timeout should be 30 from domain
    And the merged database.connection.options.max_connections should be 100 from usecase
    And the merged features should be ["caching", "monitoring"] from usecase only
    And the merged field_mapping.string_fields.default_length should be 500 from usecase
    And the merged field_mapping.string_fields.nullable should be true from domain
    And the merged field_mapping.string_fields.encrypted should be true from usecase

  Scenario: Configuration Conflict Resolution with Warnings
    Given I have domain.yaml with conflicting keys:
      """
      domain:
        name: "Product"
      
      settings:
        environment: "development"
        debug: true
        security_level: "basic"
      """
    And I have usecase.yaml with different conflict values:
      """
      settings:
        environment: "production"  # Conflict
        debug: false  # Conflict  
        security_level: "enhanced"  # Conflict
        audit_enabled: true  # New setting
      """
    And I have repository.yaml with additional conflicts:
      """
      settings:
        debug: true  # Conflict with usecase
        database_debug: true  # New setting
      """
    When I merge with conflict resolution
    Then higher precedence layers override lower precedence
    And merge warnings are generated for significant conflicts
    And validation ensures final configuration consistency
    And the final settings.environment should be "production" from usecase
    And the final settings.debug should be true from repository (highest precedence)
    And the final settings.security_level should be "enhanced" from usecase
    And merge warnings should include conflict for "debug" between usecase and repository
    And merge warnings should include conflict for "environment" between domain and usecase

  Scenario: Null Value Handling in Hierarchical Merge
    Given I have domain.yaml with base values:
      """
      domain:
        name: "Order"
      
      settings:
        timeout: 30
        retries: 3
        cache_ttl: 300
      """
    And I have usecase.yaml with null overrides:
      """
      settings:
        timeout: null  # Should not override
        retries: 5  # Should override
        cache_ttl: null  # Should not override
        new_setting: "value"  # Should add
      """
    When I merge configurations with null handling
    Then null values don't override existing values
    And the final settings.timeout should be 30 from domain
    And the final settings.retries should be 5 from usecase
    And the final settings.cache_ttl should be 300 from domain
    And the final settings.new_setting should be "value" from usecase

  Scenario: Performance Optimization for Large Configurations
    Given I have large domain configuration with 1000+ keys
    And I have large usecase configuration with 500+ keys
    And I have large repository configuration with 300+ keys
    And I have large api configuration with 200+ keys
    When I merge configurations with performance monitoring
    Then merging should complete within acceptable time limits
    And memory usage should remain within reasonable bounds
    And the merge operation should be optimized for large datasets
    And performance metrics should be tracked and reported

  Scenario: Configuration Schema Validation After Merging
    Given I have valid domain.yaml configuration
    And I have valid usecase.yaml configuration
    And I have valid repository.yaml configuration
    And I have valid api.yaml configuration
    When I merge configurations hierarchically
    Then the merged configuration should pass schema validation
    And all required sections should be present
    And all field types should be valid
    And relationship definitions should be consistent
    And validation errors should be clearly reported if any

  Scenario: Empty Configuration Layer Handling
    Given I have domain.yaml with complete configuration
    And I have empty usecase.yaml file
    And I have repository.yaml with partial configuration
    And I have missing api.yaml file
    When I merge configurations with missing layers
    Then empty layers should not affect merging process
    And missing layers should be handled gracefully
    And the merged configuration should be valid and complete
    And warnings should be generated for missing configuration layers

  Scenario: Merge Metadata and Debugging Information
    Given I have configurations across all four layers
    When I merge configurations with metadata tracking
    Then merge result should include metadata about sources
    And merge metadata should track which layer provided each value
    And merge metadata should include timestamps and version information
    And merge metadata should be useful for debugging configuration issues
    And merge metadata should not interfere with actual configuration data