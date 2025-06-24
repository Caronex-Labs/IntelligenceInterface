Feature: TUI Caronex Integration
  As a user of Intelligence Interface TUI
  I want to switch between Caronex manager and implementation agents
  So that I can access coordination capabilities when needed

  Background:
    Given the Intelligence Interface TUI is running
    And the system has multiple agents available
    And I am in the main chat interface

  Scenario: Manager mode activation
    Given I am in the main TUI interface
    When I press the Caronex hotkey (Ctrl+M)
    Then I should enter manager mode
    And visual indicators should show I'm talking to Caronex
    And conversation context should switch to manager agent

  Scenario: Visual mode distinction
    Given I am switching between agent modes
    When I interact with different agent types
    Then the interface should clearly indicate current agent
    And Caronex mode should have distinct visual styling
    And agent capabilities should be clearly communicated

  Scenario: Seamless mode switching
    Given I am in any agent mode
    When I switch to a different agent mode
    Then the transition should be smooth and responsive
    And previous conversation context should be preserved
    And mode-specific UI elements should update correctly

  Scenario: Manager coordination capabilities
    Given I am in Caronex manager mode
    When I request system coordination or planning assistance
    Then Caronex should provide coordination-focused responses
    And Caronex should delegate implementation tasks appropriately
    And the interface should support coordination workflows

  Scenario: Implementation mode distinction
    Given I am in Caronex manager mode
    When I switch to implementation agent mode
    Then the agent should handle direct implementation tasks
    And the interface should reflect implementation capabilities
    And conversation context should be agent-appropriate