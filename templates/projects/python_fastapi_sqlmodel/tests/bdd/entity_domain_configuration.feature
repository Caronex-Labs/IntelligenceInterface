Feature: Entity Domain Configuration Support
  As an Entity Template Flow developer
  I want specific configuration support for domain and entity YAML files
  So that I can immediately test entity template generation

  Background:
    Given I have a configuration loader with entity domain support

  Scenario: Load domain configuration from separate files
    Given I have domain.yaml with base entity configuration:
      """
      name: "User"
      plural: "Users"
      description: "User management domain"
      package: "user"
      base_fields:
        - name: "id"
          type: "int"
          required: false
          index: true
        - name: "created_at"
          type: "datetime"
          default: "datetime.utcnow"
        - name: "updated_at"
          type: "datetime"
          default: "datetime.utcnow"
      """
    And I have entities.yaml with entity-specific field definitions:
      """
      entities:
        - name: "User"
          description: "System user entity"
          fields:
            - name: "username"
              type: "str"
              required: true
              unique: true
              index: true
            - name: "email"
              type: "EmailStr"
              required: true
              unique: true
            - name: "full_name"
              type: "str"
              required: true
            - name: "is_active"
              type: "bool"
              default: "true"
      """
    When I load entity domain configuration from both files
    Then the configuration should be successfully merged
    And the User entity should have base fields from domain.yaml
    And the User entity should have specific fields from entities.yaml
    And the domain information should be properly set

  Scenario: Configuration merging with field inheritance
    Given I have domain.yaml with base field mixins:
      """
      name: "Product"
      plural: "Products"
      base_fields:
        - name: "id"
          type: "int"
          required: false
          index: true
        - name: "created_at"
          type: "datetime"
          default: "datetime.utcnow"
        - name: "updated_at"
          type: "datetime"
          default: "datetime.utcnow"
      mixins:
        - name: "Timestamped"
          fields:
            - name: "created_at"
              type: "datetime"
              default: "datetime.utcnow"
            - name: "updated_at"
              type: "datetime"
              default: "datetime.utcnow"
        - name: "SoftDelete"
          fields:
            - name: "deleted_at"
              type: "Optional[datetime]"
              required: false
      """
    And I have entities.yaml with mixin usage:
      """
      entities:
        - name: "Product"
          mixins: ["Timestamped", "SoftDelete"]
          fields:
            - name: "name"
              type: "str"
              required: true
              index: true
            - name: "price"
              type: "float"
              required: true
            - name: "description"
              type: "Optional[str]"
              required: false
      """
    When I load entity domain configuration from both files
    Then the Product entity should include all mixin fields
    And the Product entity should have its specific fields
    And field precedence should be handled correctly

  Scenario: Entity relationships across separate files
    Given I have domain.yaml with relationship configuration:
      """
      name: "Blog"
      plural: "Blogs"
      relationships:
        - name: "user_posts"
          from_entity: "User"
          to_entity: "Post"
          type: "one_to_many"
          back_populates: "author"
        - name: "post_comments"
          from_entity: "Post"
          to_entity: "Comment"
          type: "one_to_many"
          back_populates: "post"
      """
    And I have entities.yaml with entity definitions:
      """
      entities:
        - name: "User"
          fields:
            - name: "username"
              type: "str"
              required: true
              unique: true
        - name: "Post"
          fields:
            - name: "title"
              type: "str"
              required: true
            - name: "content"
              type: "str"
              required: true
            - name: "author_id"
              type: "int"
              required: true
        - name: "Comment"
          fields:
            - name: "content"
              type: "str"
              required: true
            - name: "post_id"
              type: "int"
              required: true
      """
    When I load entity domain configuration from both files
    Then entities should have proper relationship configurations
    And foreign key fields should be validated
    And relationship back_populates should be consistent

  Scenario: SQLModel-specific validation
    Given I have domain.yaml with SQLModel configuration:
      """
      name: "Order"
      plural: "Orders"
      sqlmodel_config:
        table_naming: "snake_case"
        field_naming: "snake_case"
        generate_id_fields: true
        timestamp_fields: ["created_at", "updated_at"]
      """
    And I have entities.yaml with SQLModel-compatible fields:
      """
      entities:
        - name: "Order"
          table_name: "orders"
          fields:
            - name: "order_number"
              type: "str"
              required: true
              unique: true
              sqlmodel_field: "Field(index=True)"
            - name: "total_amount"
              type: "float"
              required: true
              sqlmodel_field: "Field(ge=0)"
            - name: "status"
              type: "str"
              required: true
              sqlmodel_field: "Field(default='pending')"
      """
    When I load entity domain configuration from both files
    Then SQLModel field configurations should be validated
    And table naming conventions should be applied
    And SQLModel-specific field attributes should be processed

  Scenario: Configuration validation errors
    Given I have domain.yaml with invalid configuration:
      """
      name: "InvalidDomain"
      base_fields:
        - name: "123invalid"  # Invalid field name
          type: "str"
      """
    And I have entities.yaml with conflicting field definitions:
      """
      entities:
        - name: "InvalidEntity"
          fields:
            - name: "field1"
              type: "str"
            - name: "field1"  # Duplicate field name
              type: "int"
      """
    When I attempt to load entity domain configuration from both files
    Then I should receive a configuration validation error
    And the error should specify the invalid field name
    And the error should mention the duplicate field conflict
    And the error should provide helpful suggestions

  Scenario: Missing configuration files
    Given I have domain.yaml with valid configuration
    But entities.yaml file does not exist
    When I attempt to load entity domain configuration
    Then I should receive a configuration file error
    And the error should specify which file is missing
    And the error should provide guidance on creating the missing file

  Scenario: Template generation readiness validation
    Given I have complete domain and entity configurations
    When I validate the configuration for template generation
    Then all required fields for SQLModel templates should be present
    And relationship definitions should be complete
    And field types should be compatible with SQLModel
    And the configuration should support immediate entity template generation