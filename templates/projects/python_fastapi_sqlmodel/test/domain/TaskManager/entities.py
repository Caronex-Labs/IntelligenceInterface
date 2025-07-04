""" domain entities - Generated from Enhanced Co-located Template.
This module contains SQLModel entities for the TaskManager domain following
hexagonal architecture principles with co-location pattern implementation.
Generated from:
- domain.yaml: Base entity configuration and mixins
- entities.yaml: Entity-specific field definitions and relationships
- entities.py.j2: This enhanced Jinja2 template with best practices
Co-location Architecture:
- Templates, configurations, and generated files in same directory
- Hierarchical configuration merging for complete context
- @pyhex preservation markers for custom business logic
SQLModel Patterns Applied:
- Primary Keys: Optional[int] with default=None for auto-increment IDs
- UUID Keys: Optional[UUID] with default_factory=uuid4 for UUID primary keys
- Indexes: index=True for searchable fields (email, name, status, etc.)
- Constraints: unique=True, min_length, max_length from field validation
- Default Factories: datetime.utcnow for timestamps, uuid4 for UUIDs
- Field Descriptions: Comprehensive descriptions for API documentation
- Email Fields: Automatic unique=True and index=True for EmailStr fields
- Soft Delete: Indexed is_deleted field for efficient soft delete queries
Jinja2 Best Practices Applied:
- Macros for repeated field pattern generation
- Proper variable scoping with Jinja2 set tags
- Filters for text transformation (|title, |upper, |lower)
- Tests for conditional logic (is defined, is not none)
- Template structure improvements with clear sections
"""
# Standard library imports
from datetime import datetime
from uuid import UUID, uuid4
from typing import Optional, List, Dict, Any, Union
# Third-party imports
from sqlmodel import SQLModel, Field, Relationship
from pydantic import EmailStr, field_validator, model_validator, Field as PydanticField
from sqlalchemy import Boolean, DateTime
# @pyhex:begin:custom_imports
# Add custom imports here - preserved during regeneration
# @pyhex:end:custom_imports
# @pyhex:begin:custom_mixins
# Add custom mixin classes here - preserved during regeneration
# @pyhex:end:custom_mixins
    # Base mixins for Project entity
# A project that contains multiple tasks
class ProjectBase(SQLModel
):
    """Base model for Project with shared fields and validation.
    This base class contains common fields and validation logic that will be
    inherited by both the table model and API schemas.
    Attributes:
updated_at: Last update timestamp
created_at: Creation timestamp
id: Unique identifier
name: Project name
description: Project description
owner_email: Project owner email address
status: Project status: active, completed, archived
    """
      
    # Base fields from domain configuration
    # Unique identifier
    id: UUID = None
    # Creation timestamp
    created_at: datetime = None
    # Last update timestamp
    updated_at: datetime = None
    
    # Business fields from entities.yaml configuration following SQLModel patterns
    # Project name
    name: str = None
    # Project description
    description: str = None
    # Project owner email address
    owner_email: str = None
    # Project status: active, completed, archived
    status: str = None
    # @pyhex:begin:custom_fields_project
    # Add custom fields for Project here - preserved during regeneration
    # @pyhex:end:custom_fields_project
    
    model_config = {
        "validate_assignment": True,
        "use_enum_values": True,
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
      # @pyhex:begin:custom_config_project
      # Add custom Pydantic configuration here - preserved during regeneration
      # @pyhex:end:custom_config_project
      }
    # @pyhex:begin:custom_methods_project
    # Add custom methods for Project here - preserved during regeneration
    # @pyhex:end:custom_methods_project

class Project(ProjectBase, table=True):
    """SQLModel table definition for Project.
    This class represents the database table for Project entities.
    It inherits all fields and validation from ProjectBase and adds
    table-specific configuration and relationships.
    """
    __tablename__ = "project"
    # Foreign key fields for relationships (following SQLModel patterns)
    # Relationships from entities.yaml configuration
tasks: List["Task"] = Relationship(back_populates="project")
      # @pyhex:begin:custom_relationships_project
      # Add custom relationships for Project here - preserved during regeneration
      # @pyhex:end:custom_relationships_project
    def __repr__(self) -> str:
        """String representation of Project."""
        return f"Project(id={self.id}, updated_at={self.updated_at})"
    # @pyhex:begin:custom_table_methods_project
    # Add custom table-specific methods here - preserved during regeneration
    # @pyhex:end:custom_table_methods_project

# API Schema Models for FastAPI integration
class ProjectCreate(ProjectBase):
    """Request schema for creating Project.
    Excludes auto-generated fields like id, timestamps.
    Used for POST requests in FastAPI endpoints.
    """
    pass

class ProjectUpdate(SQLModel):
    """Request schema for updating Project.
    All fields are optional to support partial updates.
    Used for PUT/PATCH requests in FastAPI endpoints.
    """
                          name: Optional[str] = Field(
              default=None,
              description="Project name"
              )
              description: Optional[str] = Field(
              default=None,
              description="Project description"
              )
              owner_email: Optional[str] = Field(
              default=None,
              description="Project owner email address"
              )
              status: Optional[str] = Field(
              default=None,
              description="Project status: active, completed, archived"
              )
      # @pyhex:begin:custom_update_fields_project
      # Add custom update fields here - preserved during regeneration
      # @pyhex:end:custom_update_fields_project
      class ProjectResponse(ProjectBase):
      """Response schema for Project.
      Includes all fields including auto-generated ones.
      Used for API responses in FastAPI endpoints.
      """
              # Primary key field (type depends on mixin used)

              # Timestamp fields from mixins

      
      model_config = ProjectBase.model_config.copy()
      # @pyhex:begin:custom_response_methods_project
      # Add custom response methods here - preserved during regeneration
      # @pyhex:end:custom_response_methods_project
    # Base mixins for Task entity
# A task within a project
class TaskBase(SQLModel
):
    """Base model for Task with shared fields and validation.
    This base class contains common fields and validation logic that will be
    inherited by both the table model and API schemas.
    Attributes:
updated_at: Last update timestamp
created_at: Creation timestamp
id: Unique identifier
title: Task title
description: Task description
status: Task status: pending, in_progress, completed
priority: Task priority: low, medium, high, urgent
due_date: Task due date
assigned_to: Email of assigned user
    """
      
    # Base fields from domain configuration
    # Unique identifier
    id: UUID = None
    # Creation timestamp
    created_at: datetime = None
    # Last update timestamp
    updated_at: datetime = None
    
    # Business fields from entities.yaml configuration following SQLModel patterns
    # Task title
    title: str = None
    # Task description
    description: str = None
    # Task status: pending, in_progress, completed
    status: str = None
    # Task priority: low, medium, high, urgent
    priority: str = None
    # Task due date
    due_date: datetime = None
    # Email of assigned user
    assigned_to: str = None
    # @pyhex:begin:custom_fields_task
    # Add custom fields for Task here - preserved during regeneration
    # @pyhex:end:custom_fields_task
    
    model_config = {
        "validate_assignment": True,
        "use_enum_values": True,
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
      # @pyhex:begin:custom_config_task
      # Add custom Pydantic configuration here - preserved during regeneration
      # @pyhex:end:custom_config_task
      }
    # @pyhex:begin:custom_methods_task
    # Add custom methods for Task here - preserved during regeneration
    # @pyhex:end:custom_methods_task

class Task(TaskBase, table=True):
    """SQLModel table definition for Task.
    This class represents the database table for Task entities.
    It inherits all fields and validation from TaskBase and adds
    table-specific configuration and relationships.
    """
    __tablename__ = "task"
    # Foreign key fields for relationships (following SQLModel patterns)
    # Foreign key field for Project relationship
    project_id: Optional[int] = Field(
        default=None,
foreign_key="projects.id",        description="Foreign key to Project",
        index=True  # Foreign keys should be indexed for joins
    )
    # Relationships from entities.yaml configuration
project: Optional["Project"] = Relationship(back_populates="tasks")
taskcomments: List["TaskComment"] = Relationship(back_populates="task")
      # @pyhex:begin:custom_relationships_task
      # Add custom relationships for Task here - preserved during regeneration
      # @pyhex:end:custom_relationships_task
    def __repr__(self) -> str:
        """String representation of Task."""
        return f"Task(id={self.id}, updated_at={self.updated_at})"
    # @pyhex:begin:custom_table_methods_task
    # Add custom table-specific methods here - preserved during regeneration
    # @pyhex:end:custom_table_methods_task

# API Schema Models for FastAPI integration
class TaskCreate(TaskBase):
    """Request schema for creating Task.
    Excludes auto-generated fields like id, timestamps.
    Used for POST requests in FastAPI endpoints.
    """
    pass

class TaskUpdate(SQLModel):
    """Request schema for updating Task.
    All fields are optional to support partial updates.
    Used for PUT/PATCH requests in FastAPI endpoints.
    """
                          title: Optional[str] = Field(
              default=None,
              description="Task title"
              )
              description: Optional[str] = Field(
              default=None,
              description="Task description"
              )
              status: Optional[str] = Field(
              default=None,
              description="Task status: pending, in_progress, completed"
              )
              priority: Optional[str] = Field(
              default=None,
              description="Task priority: low, medium, high, urgent"
              )
              due_date: Optional[datetime] = Field(
              default=None,
              description="Task due date"
              )
              assigned_to: Optional[str] = Field(
              default=None,
              description="Email of assigned user"
              )
      # @pyhex:begin:custom_update_fields_task
      # Add custom update fields here - preserved during regeneration
      # @pyhex:end:custom_update_fields_task
      class TaskResponse(TaskBase):
      """Response schema for Task.
      Includes all fields including auto-generated ones.
      Used for API responses in FastAPI endpoints.
      """
              # Primary key field (type depends on mixin used)

              # Timestamp fields from mixins

      
      model_config = TaskBase.model_config.copy()
      # @pyhex:begin:custom_response_methods_task
      # Add custom response methods here - preserved during regeneration
      # @pyhex:end:custom_response_methods_task
    # Base mixins for TaskComment entity
# A comment on a task
class TaskCommentBase(SQLModel
):
    """Base model for TaskComment with shared fields and validation.
    This base class contains common fields and validation logic that will be
    inherited by both the table model and API schemas.
    Attributes:
updated_at: Last update timestamp
created_at: Creation timestamp
id: Unique identifier
content: Comment content
author_email: Email of comment author
    """
      
    # Base fields from domain configuration
    # Unique identifier
    id: UUID = None
    # Creation timestamp
    created_at: datetime = None
    # Last update timestamp
    updated_at: datetime = None
    
    # Business fields from entities.yaml configuration following SQLModel patterns
    # Comment content
    content: str = None
    # Email of comment author
    author_email: str = None
    # @pyhex:begin:custom_fields_taskcomment
    # Add custom fields for TaskComment here - preserved during regeneration
    # @pyhex:end:custom_fields_taskcomment
    
    model_config = {
        "validate_assignment": True,
        "use_enum_values": True,
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
      # @pyhex:begin:custom_config_taskcomment
      # Add custom Pydantic configuration here - preserved during regeneration
      # @pyhex:end:custom_config_taskcomment
      }
    # @pyhex:begin:custom_methods_taskcomment
    # Add custom methods for TaskComment here - preserved during regeneration
    # @pyhex:end:custom_methods_taskcomment

class TaskComment(TaskCommentBase, table=True):
    """SQLModel table definition for TaskComment.
    This class represents the database table for TaskComment entities.
    It inherits all fields and validation from TaskCommentBase and adds
    table-specific configuration and relationships.
    """
    __tablename__ = "task_comment"
    # Foreign key fields for relationships (following SQLModel patterns)
    # Foreign key field for Task relationship
    task_id: Optional[int] = Field(
        default=None,
foreign_key="tasks.id",        description="Foreign key to Task",
        index=True  # Foreign keys should be indexed for joins
    )
    # Relationships from entities.yaml configuration
task: Optional["Task"] = Relationship(back_populates="taskcomments")
      # @pyhex:begin:custom_relationships_taskcomment
      # Add custom relationships for TaskComment here - preserved during regeneration
      # @pyhex:end:custom_relationships_taskcomment
    def __repr__(self) -> str:
        """String representation of TaskComment."""
        return f"TaskComment(id={self.id}, updated_at={self.updated_at})"
    # @pyhex:begin:custom_table_methods_taskcomment
    # Add custom table-specific methods here - preserved during regeneration
    # @pyhex:end:custom_table_methods_taskcomment

# API Schema Models for FastAPI integration
class TaskCommentCreate(TaskCommentBase):
    """Request schema for creating TaskComment.
    Excludes auto-generated fields like id, timestamps.
    Used for POST requests in FastAPI endpoints.
    """
    pass

class TaskCommentUpdate(SQLModel):
    """Request schema for updating TaskComment.
    All fields are optional to support partial updates.
    Used for PUT/PATCH requests in FastAPI endpoints.
    """
                          content: Optional[str] = Field(
              default=None,
              description="Comment content"
              )
              author_email: Optional[str] = Field(
              default=None,
              description="Email of comment author"
              )
      # @pyhex:begin:custom_update_fields_taskcomment
      # Add custom update fields here - preserved during regeneration
      # @pyhex:end:custom_update_fields_taskcomment
      class TaskCommentResponse(TaskCommentBase):
      """Response schema for TaskComment.
      Includes all fields including auto-generated ones.
      Used for API responses in FastAPI endpoints.
      """
              # Primary key field (type depends on mixin used)

              # Timestamp fields from mixins

      
      model_config = TaskCommentBase.model_config.copy()
      # @pyhex:begin:custom_response_methods_taskcomment
      # Add custom response methods here - preserved during regeneration
      # @pyhex:end:custom_response_methods_taskcomment
    # @pyhex:begin:custom_entities
    # Add custom entity classes here - preserved during regeneration
    # @pyhex:end:custom_entities
    # Domain service functions
      def create_project_from_dict(data: Dict[str, Any]) -> Project:
      """Create Project instance from dictionary.
      Args:
      data: Dictionary containing Project field values
      Returns:
      New Project instance
      Raises:
      ValueError: If required fields are missing or invalid
      """
      # @pyhex:begin:custom_creation_logic_project
      # Add custom creation logic here - preserved during regeneration
      # @pyhex:end:custom_creation_logic_project
      return Project(**data)
      def validate_project_business_rules(entity: Project) -> List[str]:
      """Validate business rules for Project.
      Args:
      entity: Project instance to validate
      Returns:
      List of validation error messages (empty if valid)
      """
      errors = []
      # @pyhex:begin:custom_business_validation_project
      # Add custom business rule validation here - preserved during regeneration
      # @pyhex:end:custom_business_validation_project
      return errors
      def create_task_from_dict(data: Dict[str, Any]) -> Task:
      """Create Task instance from dictionary.
      Args:
      data: Dictionary containing Task field values
      Returns:
      New Task instance
      Raises:
      ValueError: If required fields are missing or invalid
      """
      # @pyhex:begin:custom_creation_logic_task
      # Add custom creation logic here - preserved during regeneration
      # @pyhex:end:custom_creation_logic_task
      return Task(**data)
      def validate_task_business_rules(entity: Task) -> List[str]:
      """Validate business rules for Task.
      Args:
      entity: Task instance to validate
      Returns:
      List of validation error messages (empty if valid)
      """
      errors = []
      # @pyhex:begin:custom_business_validation_task
      # Add custom business rule validation here - preserved during regeneration
      # @pyhex:end:custom_business_validation_task
      return errors
      def create_taskcomment_from_dict(data: Dict[str, Any]) -> TaskComment:
      """Create TaskComment instance from dictionary.
      Args:
      data: Dictionary containing TaskComment field values
      Returns:
      New TaskComment instance
      Raises:
      ValueError: If required fields are missing or invalid
      """
      # @pyhex:begin:custom_creation_logic_taskcomment
      # Add custom creation logic here - preserved during regeneration
      # @pyhex:end:custom_creation_logic_taskcomment
      return TaskComment(**data)
      def validate_taskcomment_business_rules(entity: TaskComment) -> List[str]:
      """Validate business rules for TaskComment.
      Args:
      entity: TaskComment instance to validate
      Returns:
      List of validation error messages (empty if valid)
      """
      errors = []
      # @pyhex:begin:custom_business_validation_taskcomment
      # Add custom business rule validation here - preserved during regeneration
      # @pyhex:end:custom_business_validation_taskcomment
      return errors
    # @pyhex:begin:custom_domain_functions
    # Add custom domain service functions here - preserved during regeneration
    # @pyhex:end:custom_domain_functions
    # Export all entity classes for easy importing
    __all__ = [
      "Project",
      "ProjectBase",
      "ProjectCreate",
      "ProjectUpdate",
      "ProjectResponse",
      "Task",
      "TaskBase",
      "TaskCreate",
      "TaskUpdate",
      "TaskResponse",
      "TaskComment",
      "TaskCommentBase",
      "TaskCommentCreate",
      "TaskCommentUpdate",
      "TaskCommentResponse",
    # Custom exports
    # @pyhex:begin:custom_exports
    # Add custom exports here - preserved during regeneration
    # @pyhex:end:custom_exports
    ]