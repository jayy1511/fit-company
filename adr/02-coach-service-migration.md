# ADR 02: Coach Service Migration

## Context

The WOD feature was slow and needed to be separated from the main app.

## Decision

We built a new `coach` service to handle WOD generation using FastAPI.

## Implementation Steps

### Phase 1: Setup

- Created a new FastAPI app in `coach/`.
- Moved WOD logic from `fitness_coach_service.py` into this new service.
- Defined schemas using Pydantic.
- Added JWT-based auth and route protection.
- Implemented a clean `/fitness/wod` GET endpoint.

### Phase 2: Integration

- Monolith’s `/fitness/wod` now calls the coach service via HTTP.
- Auth is preserved using the `Authorization` header.
- Monolith shows `/internal/history?email=...` for the coach to fetch exercise history.

### Phase 3: Deployment

- Added both services to `docker-compose.yml`.
- Verified communication using service names like `http://coach:8000`.
- Set required environment variables.
- Ran both services locally to validate.

### Phase 4: Testing and Load Simulation

- Load tested with K6 to validate performance.
- Ensured correct behavior (for example: exercises not repeated).
- Monitored response times and error rates.

### Phase 5: Documentation

- Wrote OpenAPI specs for both services.
- Documented endpoints and example requests.
- Added this ADR to explain migration rationale.

## Technical Details

- Coach pulls all exercises and yesterday’s history from monolith.
- It filters out duplicates and returns a randomized WOD.
- Both sides verify JWT tokens.

## Advantages

- Faster response times.
- Improved Scalability
- Simpler code separation for future feature additions.

## Pros

- Easier to test and deploy coach independently.
- Improved and more efficient WOD handling.

## Cons

- Adds inter-service communication complexity.
- Requires extra monitoring and coordination.
