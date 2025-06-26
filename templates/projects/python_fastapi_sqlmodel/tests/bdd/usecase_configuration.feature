Feature: Use Case Configuration Support
  As a Use Case Template Flow developer
  I want specific configuration support for use case YAML files
  So that I can test use case template generation with business logic patterns

  Background:
    Given the use case configuration loading system is properly initialized
    And PyYAML integration is available for use case configurations
    And the hierarchical configuration merging system is available

  Scenario: Basic Use Case Configuration Loading
    Given I have usecase.yaml with business logic configuration:
      """
      name: "UserManagement"
      description: "User management use case orchestration"
      methods:
        - name: "create_user"
          input_schema: "CreateUserRequest"
          output_schema: "UserResponse"
          transaction_boundary: true
          dependencies: ["user_repository", "email_service"]
          business_rules: ["email_uniqueness", "password_strength"]
        - name: "get_user_by_id"
          input_schema: "GetUserRequest"
          output_schema: "UserResponse"
          transaction_boundary: false
          dependencies: ["user_repository"]
          business_rules: ["user_exists"]
      dependencies:
        - "user_repository"
        - "email_service"
        - "notification_service"
      error_handling:
        validation_error: "UserValidationError"
        not_found_error: "UserNotFoundError"
        duplicate_error: "UserAlreadyExistsError"
      """
    And I have business-rules.yaml with domain-specific rules:
      """
      rules:
        - name: "email_uniqueness"
          type: "validation"
          condition: "email not in existing_emails"
          error_message: "Email address already exists"
          severity: "error"
        - name: "password_strength"
          type: "validation"
          condition: "password_meets_complexity_requirements"
          error_message: "Password must meet complexity requirements"
          severity: "error"
        - name: "user_exists"
          type: "constraint"
          condition: "user.id exists in database"
          error_message: "User not found"
          severity: "error"
      validation_groups:
        - name: "user_creation"
          rules: ["email_uniqueness", "password_strength"]
        - name: "user_access"
          rules: ["user_exists"]
      """
    When I load use case configuration using the configuration loader
    Then the usecase.yaml should provide use case interface and implementation specs
    And the business-rules.yaml should provide validation and business constraint rules
    And configuration should support dependency injection patterns
    And the merged configuration should enable use case template generation

  Scenario: Business Logic Orchestration Configuration
    Given I have usecase.yaml with service dependencies and transaction boundaries:
      """
      name: "OrderProcessing"
      description: "Order processing with complex business logic"
      methods:
        - name: "create_order"
          input_schema: "CreateOrderRequest"
          output_schema: "OrderResponse"
          transaction_boundary: true
          dependencies: 
            - "order_repository"
            - "inventory_service"
            - "payment_service"
            - "notification_service"
          business_rules: 
            - "inventory_availability"
            - "payment_validation"
            - "customer_credit_check"
          orchestration_steps:
            - "validate_order_items"
            - "check_inventory_availability"
            - "reserve_inventory"
            - "process_payment"
            - "create_order_record"
            - "send_confirmation"
        - name: "cancel_order"
          input_schema: "CancelOrderRequest"
          output_schema: "OrderResponse"
          transaction_boundary: true
          dependencies: ["order_repository", "inventory_service", "refund_service"]
          business_rules: ["order_cancellable", "refund_policy"]
      service_composition:
        transaction_manager: "database_transaction_manager"
        event_publisher: "domain_event_publisher"
        cache_manager: "redis_cache_manager"
      """
    When I load the use case configuration
    Then dependency injection patterns should be properly configured
    And transaction boundary specifications should be available
    And business method signatures should be defined with input/output schemas
    And service composition configuration should be accessible
    And orchestration steps should be properly ordered

  Scenario: Business Rules Validation Configuration
    Given I have business-rules.yaml with domain validation rules:
      """
      rules:
        - name: "inventory_availability"
          type: "business_logic"
          condition: "requested_quantity <= available_quantity"
          error_message: "Insufficient inventory available"
          severity: "error"
          context: "order_processing"
        - name: "payment_validation"
          type: "validation"
          condition: "payment_method.is_valid() and payment_amount > 0"
          error_message: "Invalid payment information"
          severity: "error"
          context: "order_processing"
        - name: "customer_credit_check"
          type: "business_logic"
          condition: "customer.credit_score >= minimum_credit_score"
          error_message: "Customer credit check failed"
          severity: "warning"
          context: "order_processing"
      validation_groups:
        - name: "order_creation_validation"
          rules: ["inventory_availability", "payment_validation"]
          execution_order: ["inventory_availability", "payment_validation", "customer_credit_check"]
        - name: "payment_processing"
          rules: ["payment_validation", "customer_credit_check"]
      error_handling:
        aggregation_strategy: "collect_all_errors"
        early_termination: false
        custom_exceptions:
          - rule: "inventory_availability"
            exception: "InsufficientInventoryError"
          - rule: "payment_validation"
            exception: "PaymentValidationError"
      """
    When I load the business rules configuration
    Then validation rules should be properly structured
    And constraint definitions should be available for template generation
    And error handling patterns should be configured
    And validation groups should define proper execution order
    And custom exception mappings should be available

  Scenario: Use Case Configuration Integration with Hierarchical Merging
    Given I have use case configuration with dependencies on entity and repository configs
    And I have domain configuration with base settings
    And I have repository configuration with data access patterns
    When I load the complete hierarchical configuration
    Then use case config should merge properly with entity and repository layers
    And dependency references should be validated against available services
    And configuration hierarchy should maintain proper precedence
    And use case layer should override lower layer configurations appropriately
    And merged configuration should be ready for template generation

  Scenario: Use Case Configuration Validation and Error Handling
    Given I have usecase.yaml with invalid method configuration:
      """
      name: "InvalidUserCase"
      methods:
        - name: ""  # Invalid empty method name
          input_schema: "InvalidRequest"
          dependencies: ["nonexistent_service"]  # Invalid dependency
          business_rules: ["undefined_rule"]  # Invalid business rule reference
      dependencies: []  # Missing required dependencies
      """
    And I have business-rules.yaml with invalid rule definitions:
      """
      rules:
        - name: ""  # Invalid empty rule name
          type: "invalid_type"  # Invalid rule type
          condition: ""  # Empty condition
          severity: "unknown"  # Invalid severity
      """
    When I attempt to load the use case configuration
    Then specific validation errors should be identified for use case configuration
    And detailed error messages should be provided for business rules
    And suggestions for fixing the configuration should be included
    And the system should fail gracefully without corruption

  Scenario: Use Case Configuration with Complex Dependency Injection
    Given I have usecase.yaml with complex dependency injection patterns:
      """
      name: "ECommerceCheckout"
      description: "Complex e-commerce checkout process"
      methods:
        - name: "process_checkout"
          input_schema: "CheckoutRequest"
          output_schema: "CheckoutResponse"
          transaction_boundary: true
          dependencies:
            repositories:
              - "cart_repository"
              - "order_repository"
              - "customer_repository"
            services:
              - "payment_service"
              - "inventory_service"
              - "shipping_service"
              - "tax_service"
              - "discount_service"
            external_apis:
              - "fraud_detection_api"
              - "address_validation_api"
            event_handlers:
              - "order_created_handler"
              - "inventory_updated_handler"
          business_rules:
            - "cart_not_empty"
            - "customer_authenticated"
            - "payment_method_valid"
            - "shipping_address_valid"
            - "inventory_available"
            - "fraud_check_passed"
      dependency_injection:
        interface_mappings:
          "PaymentService": "stripe_payment_service"
          "ShippingService": "fedex_shipping_service"
          "InventoryService": "warehouse_inventory_service"
        scoped_dependencies:
          - "database_session"
          - "user_context"
        singleton_dependencies:
          - "cache_manager"
          - "event_publisher"
      """
    When I load the complex use case configuration
    Then dependency categories should be properly organized
    And interface mappings should be available for dependency injection
    And scoped and singleton dependencies should be clearly identified
    And all dependency types should be supported for template generation

  Scenario: Use Case Configuration Performance and Caching
    Given I have loaded a use case configuration previously
    When I request the same use case configuration again
    Then the cached configuration should be returned if not modified
    And file modification time should be checked for cache invalidation
    And performance should be optimized for repeated loads
    And memory usage should be efficient for large configurations

  Scenario: Use Case Configuration Schema Validation
    Given I have a use case configuration file with invalid schema structure:
      """
      invalid_root_key: "this should not be here"
      name: 123  # Should be string
      methods: "not_a_list"  # Should be list
      dependencies: 
        invalid_structure: true  # Should be list of strings
      """
    When I load the configuration with schema validation enabled
    Then schema validation errors should be detected
    And specific schema violations should be reported
    And valid schema examples should be provided in error messages
    And configuration should be rejected safely

  Scenario: Use Case Configuration with Template Generation Integration
    Given I have a complete use case configuration with all required elements
    And the configuration includes dependency injection patterns
    And business rules are properly defined
    When I prepare the configuration for template generation
    Then all template variables should be properly populated
    And dependency injection configuration should be template-ready
    And business rule configurations should be available for code generation
    And the configuration should integrate seamlessly with existing template flows