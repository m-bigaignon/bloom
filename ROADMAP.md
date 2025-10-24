# Bloom Framework Roadmap

This document tracks planned features and enhancements for the Bloom DDD framework, organized by priority.

## Current Implementation Status

### ✅ Implemented Core Features

- **Entity** - Identity-based equality with generic type parameters
- **Value Object** - Immutable dataclass-like objects with structural equality
- **Aggregate** - Version tracking and domain event collection
- **Domain Events** - Pydantic-based events with UUID generation
- **Repository Pattern** - Protocol-based interfaces for sync and async operations
  - In-memory implementation
  - SQLAlchemy implementation
  - Runtime type validation
- **Unit of Work Pattern** - Transaction management with sync and async variants
  - Memory-backed UoW
  - SQLAlchemy-backed UoW with scoped sessions
  - Event publishing integration (sync and async)
- **Event Bus** - Event handler registration and dispatching
  - Synchronous event handling via `HandlersRegistry`
  - Asynchronous event handling via `AsyncHandlersRegistry`
  - Concurrent dispatch with error isolation

---

## 🔴 CRITICAL Priority

### 1. Specification Pattern

**Status:** Not started
**Complexity:** Medium

For encapsulating business rules and queries with composable, reusable domain logic.

**Requirements:**

- Base `Specification[T]` class with `is_satisfied_by(entity: T) -> bool`
- Logical composition operators (AND, OR, NOT)
- Repository integration for query building
- SQLAlchemy query translation

**Benefits:**

- Prevents anemic domain models
- Enables complex, composable queries
- Centralizes business rules

---

### 2. Domain Service Pattern

**Status:** Not started
**Complexity:** Low

For operations that don't naturally fit in entities/aggregates.

**Requirements:**

- Base `DomainService` class with guidelines
- Clear distinction from application services
- Documentation and examples

**Benefits:**

- Provides structure for cross-aggregate operations
- Maintains domain logic in domain layer
- Prevents bloated aggregates

---

### 3. Aggregate Root Enforcement

**Status:** Partially implemented
**Complexity:** Medium

Ensure invariants across aggregate boundaries.

**Requirements:**

- Only aggregate roots retrievable via repositories
- Child entities accessible only through aggregate root
- Transaction boundaries aligned with aggregates
- Validation/enforcement mechanisms

**Current State:**

- Aggregate class exists with versioning
- No enforcement of aggregate boundaries

---

### 4. Event Publishing/Handling Infrastructure

**Status:** ✅ Implemented (Sync + Async)
**Complexity:** High

**Requirements:**

- ✅ Event bus/dispatcher implementation
- ✅ Event handler registration and routing
- ✅ Integration with UoW for transactional publishing
- ✅ Async event handling support
- ✅ Error handling (concurrent dispatch with error logging)
- ⏳ Retry strategies (future enhancement)

**Current State:**

- Events can be raised and collected via `Aggregate.raise_event()`
- Events can be flushed via `Aggregate.flush_events()`
- `HandlersRegistry` for synchronous event handlers
- `AsyncHandlersRegistry` for asynchronous event handlers
- Concurrent event dispatch with isolated error handling
- Integration with both sync and async UoW patterns
- Comprehensive test coverage (tests/events/test_async_event_bus.py)

**Implementation Details:**

- Synchronous handlers registered and dispatched via `HandlersRegistry`
- Asynchronous handlers run concurrently via `asyncio.gather()`
- Handler exceptions logged without stopping other handlers
- Type-safe handler registration using generics

---

## 🟡 HIGH Priority

*Features that significantly improve DDD implementation*

### 5. Optimistic Concurrency Control

**Status:** Partially implemented
**Complexity:** Medium

Aggregate versioning exists but no conflict detection.

**Requirements:**

- `ConcurrencyException` for version conflicts
- Integration with SQLAlchemy `version_id_col`
- Automatic version increment on commit
- Retry strategies and helpers

**Current State:**

- Aggregates have `_version` attribute
- Version incremented via `_increment_version()`
- No automatic conflict detection

---

### 6. Domain Event Sourcing Support

**Status:** Not started
**Complexity:** High

Optional pattern for event-sourced aggregates.

**Requirements:**

- Event store abstraction
- Aggregate reconstruction from events
- Snapshot support for performance
- Event versioning and migration
- Separate repository implementations

---

### 7. Factory Pattern

**Status:** Not started
**Complexity:** Low

For complex object creation.

**Requirements:**

- Base `AggregateFactory[T]` class
- Aggregate reconstitution from persistence
- Validation during creation
- Integration with repositories

---

### 8. Saga/Process Manager Pattern

**Status:** Not started
**Complexity:** High

For long-running business processes.

**Requirements:**

- Saga/Process Manager base classes
- State management
- Coordination of multiple aggregates
- Compensation logic support
- Timeout handling

---

### 9. Rich Repository Query Support

**Status:** Partially implemented
**Complexity:** Medium

Beyond basic CRUD operations.

**Requirements:**

- Specification-based queries (depends on #1)
- Pagination abstractions (`Page[T]`, `PageRequest`)
- Sorting/filtering helpers
- `count()` and `exists()` operations
- Batch operations

**Current State:**

- Basic CRUD: `add()`, `get()`, `remove()`, `list()`

---

### 10. Domain Exception Hierarchy

**Status:** Not started
**Complexity:** Low

Structured error handling for domain layer.

**Requirements:**

- `DomainException` base class
- `ValidationException`
- `BusinessRuleViolation`
- `AggregateNotFoundException`
- `ConcurrencyException` (see #5)

---

## 🟢 MEDIUM Priority

*Developer experience and productivity features*

### 11. Aggregate Snapshot Support

**Status:** Not started
**Complexity:** Medium

Performance optimization for event sourcing.

**Requirements:**

- Snapshot storage abstraction
- Configurable snapshot strategies (every N events, time-based)
- Snapshot + delta event loading
- Depends on: #6 (Event Sourcing)

---

### 12. Repository Decorators/Middleware

**Status:** Not started
**Complexity:** Medium

Cross-cutting concerns for repositories.

**Requirements:**

- `CachingRepository` decorator
- `LoggingRepository` decorator
- `MetricsRepository` decorator
- `ValidatingRepository` decorator
- Composable decorator pattern

---

### 13. UoW Repository Auto-Registration

**Status:** Not started
**Complexity:** Medium

Reduce boilerplate in UoW implementations.

**Requirements:**

- Convention-based repository discovery
- Type-safe repository access
- Automatic initialization
- Example: `uow.products` instead of manual setup

---

### 14. Validation Framework Integration

**Status:** Partially implemented
**Complexity:** Low

**Requirements:**

- Enhanced Pydantic integration for value objects
- Validation helpers for aggregates
- Business rule validation utilities
- Custom validator decorators

**Current State:**

- Events use Pydantic
- Value Objects use dataclass (not Pydantic)

---

### 15. Query Objects/CQRS Support

**Status:** Not started
**Complexity:** High

Read model separation from write models.

**Requirements:**

- Query object pattern
- Query handler registration/dispatch
- Read model abstractions
- Eventual consistency helpers
- Separate read/write databases support

---

### 16. Outbox Pattern

**Status:** Not started
**Complexity:** High

Reliable event publishing.

**Requirements:**

- Transactional outbox table
- Polling publisher service
- Message broker integration (RabbitMQ, Kafka, etc.)
- Idempotency handling
- Dead letter queue support

---

### 17. Testing Utilities

**Status:** Not started
**Complexity:** Medium

Make testing DDD code easier.

**Requirements:**

- Aggregate test fixtures/builders
- Event assertion helpers (`assert_events_raised()`)
- Repository test doubles with assertions
- UoW test utilities
- Time manipulation helpers

---

## 🔵 LOW Priority

*Advanced and nice-to-have features*

### 18. Multi-tenancy Support

**Status:** Not started
**Complexity:** High

### 19. Soft Delete Support

**Status:** Not started
**Complexity:** Low

### 20. Audit Trail/Temporal Patterns

**Status:** Not started
**Complexity:** Medium

### 21. Additional Repository Backends

**Status:** Not started
**Complexity:** Varies

Options: MongoDB, Redis, Cosmos DB, DynamoDB

### 22. GraphQL/API Layer Helpers

**Status:** Not started
**Complexity:** Medium

### 23. Domain Model Visualization

**Status:** Not started
**Complexity:** High

### 24. Performance Monitoring

**Status:** Not started
**Complexity:** Medium

### 25. Migration Support

**Status:** Not started
**Complexity:** High

---

## 🏗️ INFRASTRUCTURE

*Cross-cutting framework improvements*

### 26. Comprehensive Documentation

**Status:** Minimal
**Complexity:** Ongoing

**Current State:**

- Basic docstrings in code
- Example application in tests/example/
- CLAUDE.md for AI assistance

**Needed:**

- Patterns guide
- Best practices documentation
- Tutorial series
- Migration guides from other frameworks
- API reference documentation

---

### 27. CLI Tools

**Status:** Not started
**Complexity:** Medium

**Requirements:**

- `bloom init` - Initialize new project
- `bloom generate aggregate <name>` - Scaffold aggregate
- `bloom generate entity <name>` - Scaffold entity
- `bloom generate value-object <name>` - Scaffold value object
- `bloom generate repository <name>` - Scaffold repository

---

### 28. IDE/Editor Support

**Status:** Basic
**Complexity:** Low

**Current State:**

- Type hints for IDE autocomplete
- Strict mypy configuration

**Enhancements:**

- Enhanced type stubs
- VS Code snippets
- PyCharm live templates
- Template generators

---

### 29. Framework Adapters

**Status:** Basic FastAPI example
**Complexity:** Medium

**Requirements:**

- FastAPI integration utilities
- Django integration package
- Flask integration package
- Dedicated async framework support documentation

**Current State:**

- Example FastAPI application in tests/example/
- Async repository and UoW variants exist

---

## Feature Dependencies

```
Event Sourcing (#6)
  └─> Aggregate Snapshot Support (#11)

Specification Pattern (#1)
  └─> Rich Repository Query Support (#9)

Event Publishing (#4)
  ├─> Saga/Process Manager (#8)
  ├─> Outbox Pattern (#16)
  └─> CQRS Support (#15)

Optimistic Concurrency Control (#5)
  └─> Domain Exception Hierarchy (#10)
```

---

## Next Steps

**Recommended Implementation Order:**

1. ~~**Event Publishing Infrastructure** (#4)~~ - ✅ **COMPLETED** (2025-10-24)
2. **Domain Exception Hierarchy** (#10) - Foundation for error handling
3. **Optimistic Concurrency Control** (#5) - Complete aggregate versioning
4. **Specification Pattern** (#1) - Enable rich domain logic
5. **Rich Repository Query Support** (#9) - Practical query capabilities
6. **Outbox Pattern** (#16) - Reliable event publishing for distributed systems
7. **Saga/Process Manager** (#8) - Now unblocked by event publishing

---

## Contributing

When implementing features from this roadmap:

1. Update the status in this document
2. Add tests to appropriate test modules
4. Add examples to tests/example/ if applicable
5. Document in docstrings and update main documentation

---
