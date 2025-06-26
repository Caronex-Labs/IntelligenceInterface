Feature: Core Configuration Loading Foundation
  As a template generation system
  I want foundational configuration loading capabilities
  So that all Templates Domain flows can load their YAML configurations

  Background:
    Given the configuration loading system is properly initialized
    And PyYAML integration is available

  Scenario: Basic Configuration Loading
    Given I have PyYAML integration properly configured
    When I load a basic YAML configuration file
    Then the configuration should be parsed successfully
    And essential fields should be populated correctly
    And basic validation should identify missing required fields
    And the Configuration class should provide type-safe access

  Scenario: Load Valid Domain Configuration
    Given I have a valid domain configuration file:
      """
      domain:
        name: "User"
        plural: "Users"
      entities:
        - name: "User"
          fields:
            - name: "name"
              type: "str"
              required: true
              index: true
            - name: "email"
              type: "EmailStr"
              required: true
      """
    When I load the configuration using the Configuration class
    Then the domain name should be "User"
    And the domain plural should be "Users"
    And the entities list should contain one User entity
    And the User entity should have name and email fields
    And field validation should pass for required fields

  Scenario: Handle Missing Required Fields
    Given I have a configuration file missing required domain name:
      """
      domain:
        plural: "Users"
      entities: []
      """
    When I attempt to load the configuration
    Then a validation error should be raised
    And the error message should indicate "domain.name is required"
    And the Configuration object should not be created

  Scenario: Handle Invalid YAML Syntax
    Given I have a configuration file with invalid YAML syntax:
      """
      domain:
        name: "User"
        plural: "Users"
      entities:
        - name: "User"
          fields:
            - name: "name"
              type: "str"
              required: true
            - name: "email"  # Missing closing quote and invalid structure
              type: "EmailStr
              required: true
      """
    When I attempt to load the configuration
    Then a YAML parsing error should be raised
    And the error message should indicate the syntax issue
    And the line number of the error should be provided

  Scenario: Handle File Not Found
    Given a configuration file path that does not exist
    When I attempt to load the configuration from the non-existent path
    Then a file not found error should be raised
    And the error message should indicate the missing file path
    And helpful guidance should be provided

  Scenario: Type Safety Validation
    Given I have a configuration with invalid field types:
      """
      domain:
        name: 123  # Should be string
        plural: "Users"
      entities:
        - name: "User"
          fields:
            - name: "age"
              type: "invalid_type"  # Invalid type
              required: "yes"  # Should be boolean
      """
    When I attempt to load the configuration
    Then type validation errors should be raised
    And the error should specify which fields have invalid types
    And the expected types should be indicated in the error message

  Scenario: Logging Configuration Operations
    Given logging is configured for the configuration system
    When I successfully load a valid configuration file
    Then an info log should be recorded indicating successful loading
    And the log should include the configuration file path
    When I encounter a validation error
    Then an error log should be recorded with the validation details
    And the log should include the specific validation failures