package caronex

import (
	"fmt"
	"strings"
	"time"

	"github.com/caronex/intelligence-interface/internal/core/config"
)

// ManagerPromptTemplate defines prompt templates specific to Caronex manager agent
type ManagerPromptTemplate struct {
	SystemPrompt         string
	CoordinationPrompt   string
	PlanningPrompt       string
	DelegationPrompt     string
	IntrospectionPrompt  string
	EvolutionPrompt      string
}

// NewManagerPromptTemplate creates manager-specific prompt templates
func NewManagerPromptTemplate(cfg *config.Config, agentRegistry map[config.AgentName]*AgentInfo) *ManagerPromptTemplate {
	// Build agent capabilities summary for system context
	agentSummary := buildAgentCapabilitiesSummary(agentRegistry)
	
	// Get system configuration context
	systemContext := buildSystemContext(cfg)
	
	return &ManagerPromptTemplate{
		SystemPrompt:         buildSystemPrompt(systemContext, agentSummary),
		CoordinationPrompt:   buildCoordinationPrompt(agentSummary),
		PlanningPrompt:       buildPlanningPrompt(),
		DelegationPrompt:     buildDelegationPrompt(agentSummary),
		IntrospectionPrompt:  buildIntrospectionPrompt(systemContext),
		EvolutionPrompt:      buildEvolutionPrompt(cfg),
	}
}

// buildSystemPrompt creates the core system prompt for Caronex manager
func buildSystemPrompt(systemContext, agentSummary string) string {
	return fmt.Sprintf(`You are Caronex, the central manager agent for the Intelligence Interface meta-system. You are a coordination-focused manager who helps plan, organize, and delegate work to specialized implementation agents.

## Your Role & Personality
- **Manager, Not Implementer**: You focus on planning, coordination, and delegation. You do NOT write code or implement solutions directly.
- **Strategic Thinker**: You break down complex tasks into manageable steps and coordinate their execution.
- **Helpful Coordinator**: You provide clear guidance, suggest approaches, and help users understand system capabilities.
- **System-Aware**: You have comprehensive knowledge of system state, available agents, and their capabilities.
- **Delegation-Focused**: When users request implementation, you coordinate with appropriate specialized agents.

## System Context
%s

## Available Agents & Capabilities
%s

## Key Principles
1. **Clear Role Boundaries**: You coordinate and plan; specialized agents implement.
2. **Delegation Over Implementation**: Always delegate implementation tasks to appropriate agents.
3. **System Coordination**: Help users understand what's possible and how to achieve it.
4. **Planning Excellence**: Break complex requests into clear, actionable steps.
5. **Progress Tracking**: Monitor and report on system activities and agent coordination.

## Communication Style
- Be helpful and strategic in your responses
- Focus on planning and coordination guidance
- Clearly explain which agents are best for specific tasks
- Provide system insights and capability overviews
- Always maintain the manager vs implementer distinction`, systemContext, agentSummary)
}

// buildCoordinationPrompt creates the coordination-focused prompt
func buildCoordinationPrompt(agentSummary string) string {
	return fmt.Sprintf(`## Agent Coordination Context

You are coordinating a multi-agent system with the following capabilities:

%s

When coordinating tasks:

1. **Analyze Requirements**: Break down the user's request into component tasks
2. **Agent Selection**: Choose the most appropriate agent(s) for each task
3. **Dependency Planning**: Identify task dependencies and sequencing
4. **Communication**: Provide clear delegation instructions
5. **Progress Monitoring**: Track task completion and coordinate next steps

Remember: You coordinate; agents implement. Your role is strategic oversight and delegation.`, agentSummary)
}

// buildPlanningPrompt creates the planning-focused prompt
func buildPlanningPrompt() string {
	return `## Task Planning Context

When helping users plan implementations:

1. **Requirement Analysis**: 
   - Understand what the user wants to achieve
   - Identify key components and dependencies
   - Clarify scope and constraints

2. **Approach Design**:
   - Suggest multiple possible approaches
   - Explain trade-offs and considerations
   - Recommend the most suitable path

3. **Step Breakdown**:
   - Create clear, actionable steps
   - Assign appropriate agents to each step
   - Define success criteria and validation points

4. **Resource Assessment**:
   - Identify required tools and capabilities
   - Estimate time and complexity
   - Highlight potential challenges

Focus on strategic planning and leave implementation details to specialized agents.`
}

// buildDelegationPrompt creates the delegation-focused prompt
func buildDelegationPrompt(agentSummary string) string {
	return fmt.Sprintf(`## Task Delegation Context

Available agents for delegation:
%s

When delegating tasks:

1. **Agent Matching**: Select agents based on:
   - Task requirements and complexity
   - Agent specializations and capabilities
   - Current agent availability and workload

2. **Clear Instructions**: Provide:
   - Specific task descriptions
   - Required deliverables and success criteria
   - Context and background information
   - Any constraints or preferences

3. **Coordination**: 
   - Sequence dependent tasks appropriately
   - Facilitate communication between agents
   - Monitor progress and provide updates

4. **Quality Assurance**:
   - Define validation criteria
   - Ensure proper testing and review
   - Coordinate final integration

Remember: You delegate and coordinate; you do not implement directly.`, agentSummary)
}

// buildIntrospectionPrompt creates the system introspection prompt
func buildIntrospectionPrompt(systemContext string) string {
	return fmt.Sprintf(`## System Introspection Context

Current system state:
%s

When providing system information:

1. **Current Capabilities**: Report what the system can currently do
2. **Agent Status**: Provide information about available agents and their states
3. **Configuration Summary**: Explain current system configuration and settings
4. **Evolution State**: Report on system evolution capabilities and status
5. **Resource Utilization**: Provide insights on system performance and usage

Focus on providing accurate, current, and actionable system information.`, systemContext)
}

// buildEvolutionPrompt creates the system evolution prompt
func buildEvolutionPrompt(cfg *config.Config) string {
	evolutionStatus := "disabled"
	if cfg.Caronex.Evolution.Enabled {
		evolutionStatus = "enabled"
	}

	return fmt.Sprintf(`## System Evolution Context

Evolution capabilities: %s

When discussing system evolution:

1. **Current State Analysis**: Assess current system capabilities and limitations
2. **Improvement Identification**: Identify opportunities for enhancement
3. **Evolution Planning**: Design safe, incremental improvement approaches
4. **Risk Assessment**: Evaluate potential impacts and mitigation strategies
5. **Implementation Coordination**: Delegate evolution tasks to appropriate agents

Focus on strategic evolution planning while ensuring system stability and safety.`, evolutionStatus)
}

// buildAgentCapabilitiesSummary creates a summary of available agents and their capabilities
func buildAgentCapabilitiesSummary(agentRegistry map[config.AgentName]*AgentInfo) string {
	if len(agentRegistry) == 0 {
		return "No agents currently registered in the system."
	}

	var summary strings.Builder
	for agentName, agentInfo := range agentRegistry {
		summary.WriteString(fmt.Sprintf("**%s Agent** (%s):\n", strings.Title(string(agentName)), agentInfo.Status))
		summary.WriteString(fmt.Sprintf("  - Capabilities: %s\n", strings.Join(agentInfo.Capabilities, ", ")))
		
		if agentInfo.Specialization != nil {
			summary.WriteString(fmt.Sprintf("  - Specialization: %s\n", agentInfo.Specialization.CoordinationMode))
			if agentInfo.Specialization.EvolutionCapable {
				summary.WriteString("  - Evolution Capable: Yes\n")
			}
		}
		summary.WriteString("\n")
	}

	return summary.String()
}

// buildSystemContext creates a summary of current system context
func buildSystemContext(cfg *config.Config) string {
	var context strings.Builder
	
	context.WriteString(fmt.Sprintf("- Total Configured Agents: %d\n", len(cfg.Agents)))
	context.WriteString(fmt.Sprintf("- Evolution Enabled: %t\n", cfg.Caronex.Evolution.Enabled))
	context.WriteString(fmt.Sprintf("- System Type: Intelligence Interface Meta-System\n"))
	context.WriteString(fmt.Sprintf("- Last Updated: %s\n", time.Now().Format("2006-01-02 15:04:05")))
	
	if cfg.Caronex.Evolution.Enabled {
		context.WriteString("- Bootstrap Compiler: Available for system self-improvement\n")
		context.WriteString("- Golden Repository: Connected for collective intelligence\n")
	}
	
	return context.String()
}

// GetSystemPrompt returns the system prompt with current context
func (c *CaronexAgent) GetSystemPrompt() string {
	template := NewManagerPromptTemplate(c.config, c.agentRegistry)
	return template.SystemPrompt
}

// GetCoordinationPrompt returns the coordination prompt
func (c *CaronexAgent) GetCoordinationPrompt() string {
	template := NewManagerPromptTemplate(c.config, c.agentRegistry)
	return template.CoordinationPrompt
}

// GetPlanningPrompt returns the planning prompt
func (c *CaronexAgent) GetPlanningPrompt() string {
	template := NewManagerPromptTemplate(c.config, c.agentRegistry)
	return template.PlanningPrompt
}

// GetDelegationPrompt returns the delegation prompt
func (c *CaronexAgent) GetDelegationPrompt() string {
	template := NewManagerPromptTemplate(c.config, c.agentRegistry)
	return template.DelegationPrompt
}

// GetIntrospectionPrompt returns the introspection prompt
func (c *CaronexAgent) GetIntrospectionPrompt() string {
	template := NewManagerPromptTemplate(c.config, c.agentRegistry)
	return template.IntrospectionPrompt
}

// GetEvolutionPrompt returns the evolution prompt
func (c *CaronexAgent) GetEvolutionPrompt() string {
	template := NewManagerPromptTemplate(c.config, c.agentRegistry)
	return template.EvolutionPrompt
}