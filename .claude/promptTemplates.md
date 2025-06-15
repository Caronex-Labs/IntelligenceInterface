# Prompt Templates

## Self-Improving Prompt Patterns

The Intelligence Interface uses sophisticated prompt templates that evolve based on successful patterns, user feedback, and system learning. These templates form the communication backbone between users, agents, and the system itself.

## Template Categories

### 1. Meta-System Prompts
**Purpose**: Templates for system self-improvement and evolution

#### System Evolution Prompt
```
SYSTEM_EVOLUTION_TEMPLATE:
Context: The Intelligence Interface system is evaluating potential improvements
Current State: {{current_capabilities}}
Improvement Opportunity: {{improvement_description}}
Constraints: {{constraints}}

As the central Caronex orchestrator, analyze this improvement opportunity:

1. IMPACT ASSESSMENT:
   - What capabilities would this improvement add?
   - What are the potential risks?
   - How does this align with system evolution goals?

2. IMPLEMENTATION STRATEGY:
   - What changes are required to the architecture?
   - Which agents need to be involved?
   - What spaces need to be created or modified?

3. VALIDATION APPROACH:
   - How can we test this improvement safely?
   - What rollback mechanisms are needed?
   - What success metrics should we use?

4. EVOLUTION PATH:
   - Generate specific implementation steps
   - Create configuration changes needed
   - Design validation tests

Output a detailed evolution plan with safety guarantees.
```

#### Bootstrap Compiler Prompt
```
BOOTSTRAP_COMPILER_TEMPLATE:
Context: The system needs to generate code to improve itself
Target Component: {{component_name}}
Improvement Type: {{improvement_type}}
Current Implementation: {{current_code}}

As the bootstrap compiler, generate improved code that:

1. PRESERVES COMPATIBILITY:
   - Maintains all existing interfaces
   - Ensures backward compatibility
   - Provides migration paths

2. ENHANCES CAPABILITY:
   - Improves {{specific_metric}} by {{target_improvement}}
   - Adds new functionality: {{new_features}}
   - Optimizes performance patterns

3. ENSURES SAFETY:
   - Includes comprehensive error handling
   - Provides rollback mechanisms
   - Validates all state changes

4. MAINTAINS COHERENCE:
   - Follows existing architectural patterns
   - Integrates with current systems
   - Updates relevant documentation

Generate production-ready code with complete test coverage.
```

### 2. Agent Coordination Prompts
**Purpose**: Templates for coordinating multiple agents

#### Multi-Agent Coordination Prompt
```
AGENT_COORDINATION_TEMPLATE:
Context: Complex task requiring multiple specialized agents
Task: {{task_description}}
Available Agents: {{agent_list}}
Resource Constraints: {{constraints}}
Timeline: {{deadline}}

As Caronex coordinator, orchestrate this multi-agent workflow:

1. TASK DECOMPOSITION:
   - Break down task into agent-specific subtasks
   - Identify dependencies between subtasks
   - Determine optimal sequencing

2. AGENT ASSIGNMENT:
   - Match subtasks to most suitable agents
   - Consider agent current load and capabilities
   - Allocate appropriate resources and spaces

3. COORDINATION STRATEGY:
   - Define inter-agent communication protocols
   - Set up shared state management
   - Plan synchronization points

4. QUALITY ASSURANCE:
   - Define validation criteria for each subtask
   - Plan integration testing approach
   - Set up progress monitoring

Execute coordination plan and monitor progress continuously.
```

#### Agent Learning Prompt
```
AGENT_LEARNING_TEMPLATE:
Context: Agent {{agent_id}} is learning from experience
Learning Scenario: {{scenario_description}}
Previous Attempts: {{attempt_history}}
Success Metrics: {{success_criteria}}

As a learning agent, analyze this experience:

1. PATTERN RECOGNITION:
   - What patterns led to successful outcomes?
   - What patterns correlated with failures?
   - What environmental factors influenced results?

2. KNOWLEDGE UPDATE:
   - What new knowledge should be retained?
   - How should existing knowledge be modified?
   - What obsolete knowledge should be discarded?

3. BEHAVIOR ADAPTATION:
   - How should future behavior change?
   - What new strategies should be tried?
   - What decision-making processes need updating?

4. KNOWLEDGE SHARING:
   - What learnings are valuable to other agents?
   - How should knowledge be formatted for sharing?
   - What coordination patterns emerged?

Update internal knowledge base and share relevant insights.
```

### 3. User Interaction Prompts
**Purpose**: Templates for effective user communication

#### Adaptive User Interface Prompt
```
ADAPTIVE_UI_TEMPLATE:
Context: User {{user_id}} interaction analysis
User History: {{user_behavior_patterns}}
Current Request: {{current_request}}
System Capabilities: {{available_features}}

As an adaptive interface agent, optimize user experience:

1. PREFERENCE ANALYSIS:
   - What patterns emerge from user behavior?
   - What interface preferences are evident?
   - What workflow optimizations are possible?

2. PERSONALIZATION:
   - How should the interface adapt to this user?
   - What shortcuts or customizations would help?
   - What information should be prioritized?

3. PREDICTIVE ASSISTANCE:
   - What is the user likely to need next?
   - What common tasks can be automated?
   - What obstacles can be prevented?

4. INTERFACE EVOLUTION:
   - What interface improvements would benefit this user?
   - How should configuration evolve?
   - What new capabilities should be suggested?

Provide personalized interface configuration and assistance.
```

#### User Onboarding Prompt
```
USER_ONBOARDING_TEMPLATE:
Context: New user {{user_id}} first interaction
User Background: {{user_expertise_level}}
Stated Goals: {{user_objectives}}
Available Time: {{onboarding_duration}}

As an onboarding specialist agent:

1. SKILL ASSESSMENT:
   - Evaluate user's technical background
   - Identify relevant experience areas
   - Determine appropriate complexity level

2. CUSTOMIZED INTRODUCTION:
   - Tailor introduction to user's background
   - Focus on most relevant features first
   - Provide appropriate depth of explanation

3. GUIDED EXPERIENCE:
   - Create step-by-step learning path
   - Provide hands-on examples
   - Ensure progressive skill building

4. ONGOING SUPPORT:
   - Set up continued learning resources
   - Establish help and support pathways
   - Plan follow-up check-ins

Create personalized onboarding experience with clear success milestones.
```

### 4. Code Generation Prompts
**Purpose**: Templates for intelligent code generation

#### Context-Aware Code Generation
```
CODE_GENERATION_TEMPLATE:
Context: {{project_context}}
Request: {{code_request}}
Existing Codebase: {{codebase_patterns}}
Constraints: {{coding_constraints}}
Quality Requirements: {{quality_standards}}

As an intelligent code generator:

1. CONTEXT ANALYSIS:
   - Understand existing code patterns and architecture
   - Identify relevant libraries and frameworks
   - Determine appropriate coding style and conventions

2. SOLUTION DESIGN:
   - Design solution that fits existing architecture
   - Consider performance and maintainability
   - Plan integration with existing components

3. CODE GENERATION:
   - Generate clean, well-documented code
   - Follow established patterns and conventions
   - Include appropriate error handling and validation

4. QUALITY ASSURANCE:
   - Ensure code meets quality standards
   - Provide comprehensive test coverage
   - Include necessary documentation
   - Log any technical debt created during implementation

5. TECH DEBT TRACKING:
   - Identify any compromises made during implementation
   - Log quick fixes or workarounds in TechDebt.md
   - Assess impact of any shortcuts taken
   - Plan future improvements needed

Generate production-ready code with complete documentation and tests.
```

#### Template Evolution Prompt
```
TEMPLATE_EVOLUTION_TEMPLATE:
Context: Template {{template_name}} improvement analysis
Usage Statistics: {{usage_data}}
Success Patterns: {{successful_generations}}
Failure Patterns: {{failed_generations}}
User Feedback: {{feedback_data}}

As a template evolution specialist:

1. PERFORMANCE ANALYSIS:
   - Analyze template success rates
   - Identify common failure modes
   - Evaluate user satisfaction metrics

2. PATTERN RECOGNITION:
   - Extract patterns from successful generations
   - Identify anti-patterns to avoid
   - Recognize usage context variations

3. TEMPLATE IMPROVEMENT:
   - Propose specific template enhancements
   - Design better parameter handling
   - Improve error handling and validation

4. EVOLUTION STRATEGY:
   - Plan gradual template improvement rollout
   - Design A/B testing for improvements
   - Create rollback strategy for changes

Generate improved template with validation plan.
```

#### Technical Debt Assessment Prompt
```
TECH_DEBT_ASSESSMENT_TEMPLATE:
Context: Technical debt assessment for {{component_name}}
Code Review Focus: {{review_scope}}
Quality Standards: {{quality_criteria}}
Time Constraints: {{project_timeline}}

As a technical debt assessment specialist:

1. DEBT IDENTIFICATION:
   - Scan for quick fixes and workarounds
   - Identify missing tests and documentation
   - Assess code quality and maintainability issues
   - Look for performance bottlenecks

2. IMPACT ANALYSIS:
   - Evaluate maintenance burden of identified debt
   - Assess risk of technical debt accumulation
   - Determine user experience impact
   - Calculate potential future development costs

3. PRIORITIZATION:
   - Rank technical debt by severity and impact
   - Consider effort required for resolution
   - Assess timeline for addressing each item
   - Recommend immediate vs. future action

4. DOCUMENTATION:
   - Log all identified tech debt in TechDebt.md
   - Use standard format and categorization
   - Include clear resolution recommendations
   - Set appropriate target timelines

Generate comprehensive tech debt report with actionable recommendations.
```

### 5. System Integration Prompts
**Purpose**: Templates for integrating with external systems

#### Golden Repository Integration
```
GOLDEN_REPOSITORY_TEMPLATE:
Context: Pattern contribution to golden repository
Local Pattern: {{pattern_description}}
Success Metrics: {{pattern_performance}}
Generalization Potential: {{reusability_analysis}}

As a golden repository contributor:

1. PATTERN ANALYSIS:
   - Evaluate pattern quality and effectiveness
   - Assess generalization potential
   - Identify abstraction opportunities

2. CONTRIBUTION PREPARATION:
   - Package pattern for sharing
   - Create comprehensive documentation
   - Develop usage examples and tests

3. COMMUNITY INTEGRATION:
   - Format contribution for community standards
   - Provide clear benefits and use cases
   - Include performance benchmarks

4. MAINTENANCE PLANNING:
   - Plan ongoing pattern maintenance
   - Set up feedback collection mechanisms
   - Design evolution tracking

Prepare pattern for golden repository contribution.
```

#### External Tool Integration
```
TOOL_INTEGRATION_TEMPLATE:
Context: Integrating external tool {{tool_name}}
Tool Capabilities: {{tool_features}}
Integration Requirements: {{integration_needs}}
System Architecture: {{current_architecture}}

As a tool integration specialist:

1. CAPABILITY MAPPING:
   - Map tool capabilities to system needs
   - Identify integration points
   - Plan capability exposure to agents

2. INTEGRATION DESIGN:
   - Design tool wrapper interfaces
   - Plan error handling and fallbacks
   - Consider security and permissions

3. IMPLEMENTATION STRATEGY:
   - Create integration implementation plan
   - Design testing and validation approach
   - Plan rollout and monitoring

4. SYSTEM EVOLUTION:
   - Consider how integration affects system evolution
   - Plan tool capability evolution handling
   - Design upgrade and maintenance strategies

Generate complete tool integration plan with implementation details.
```

## Prompt Evolution Mechanisms

### 1. Automatic Prompt Improvement
```yaml
prompt_evolution:
  triggers:
    - success_rate_threshold: 0.85
    - usage_frequency: "daily"
    - user_feedback_score: 4.0
  
  improvement_methods:
    - pattern_extraction: "successful_interactions"
    - failure_analysis: "failed_interactions"
    - user_preference_learning: "behavior_patterns"
    - context_optimization: "environmental_factors"
  
  validation_process:
    - a_b_testing: "new_vs_old_prompts"
    - performance_monitoring: "success_metrics"
    - user_satisfaction: "feedback_collection"
    - rollback_capability: "safety_guarantee"
```

### 2. Context-Aware Prompt Selection
```yaml
prompt_selection:
  factors:
    - user_expertise_level: "beginner|intermediate|expert"
    - task_complexity: "simple|moderate|complex"
    - system_load: "low|medium|high"
    - time_constraints: "none|moderate|urgent"
  
  selection_algorithm:
    - context_matching: "find_best_fit"
    - performance_prediction: "estimate_success_rate"
    - resource_optimization: "minimize_token_usage"
    - learning_opportunity: "maximize_improvement"
```

### 3. Dynamic Prompt Generation
```yaml
dynamic_prompts:
  generation_triggers:
    - novel_use_case: "no_existing_template"
    - context_variation: "significant_difference"
    - performance_requirement: "specific_optimization"
  
  generation_process:
    - template_composition: "combine_existing_patterns"
    - context_adaptation: "customize_for_situation"
    - performance_optimization: "tune_for_efficiency"
    - validation_testing: "ensure_effectiveness"
```

## Prompt Quality Metrics

### 1. Effectiveness Metrics
- **Success Rate**: Percentage of successful prompt executions
- **Quality Score**: Average quality of generated outputs
- **User Satisfaction**: User feedback and ratings
- **Task Completion**: Percentage of completed objectives

### 2. Efficiency Metrics
- **Token Usage**: Average tokens consumed per prompt
- **Response Time**: Average time to generate response
- **Resource Utilization**: System resources consumed
- **Cost Effectiveness**: Cost per successful outcome

### 3. Evolution Metrics
- **Improvement Rate**: Rate of prompt quality improvement
- **Adaptation Speed**: Time to adapt to new patterns
- **Learning Efficiency**: Knowledge gained per interaction
- **Pattern Recognition**: Ability to identify successful patterns

## Future Prompt Directions

### 1. Multi-Modal Prompts
- **Visual Prompts**: Integration with images and diagrams
- **Audio Prompts**: Voice-based interactions
- **Interactive Prompts**: Dynamic user interaction
- **Contextual Prompts**: Environment-aware prompting

### 2. Quantum Prompts
- **Superposition Prompts**: Multiple prompt states simultaneously
- **Entangled Prompts**: Correlated prompt behaviors
- **Quantum Coherence**: Maintaining prompt consistency across states
- **Quantum Learning**: Learning across multiple realities

### 3. Emergent Prompts
- **Self-Generating Prompts**: Prompts that create other prompts
- **Collective Prompts**: Community-generated prompt patterns
- **Evolutionary Prompts**: Prompts that evolve through natural selection
- **Swarm Prompts**: Collaborative prompt generation