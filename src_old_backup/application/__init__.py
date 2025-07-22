"""
Application Layer - WF_EOL_TESTER Clean Architecture

This package contains the application business logic layer that coordinates 
domain entities and orchestrates use cases. It defines interfaces for external
dependencies and implements application-specific business rules.

Key Components:
- Use Cases: Application-specific business logic
- Interfaces: Contracts for external dependencies (repositories, services)
- Commands: Input data structures for use cases
- Results: Output data structures from use cases

The application layer depends only on the domain layer and defines interfaces
that are implemented by outer layers (infrastructure, presentation).
"""