# Step 05: Core API Endpoints - Part 2

## Overview
Implement secondary operations and business logic endpoints

## What Gets Built

### Core Components
- Component 1
- Component 2
- Component 3

### Database Schema
If applicable, the migration file for this step.

### API Endpoints
- POST /api/resource
- GET /api/resource
- GET /api/resource/:id
- PUT /api/resource/:id
- DELETE /api/resource/:id

## Implementation Details

### TypeScript/Rust Code Snippets

#### Models and Types
```typescript
// Type definitions for this step
interface Resource {
  id: string;
  name: string;
  createdAt: Date;
  updatedAt: Date;
}
```

#### Backend Handler (Rust/Axum)
```rust
// Handler implementation
async fn create_resource(
    State(db): State<Pool<Postgres>>,
    Json(payload): Json<CreateResourceRequest>,
) -> Result<Json<Resource>, ApiError> {
    // Implementation
    Ok(Json(resource))
}
```

#### Frontend Component (React/TypeScript)
```typescript
// Component implementation
export function ResourceForm() {
  return (
    <div>
      {/* Form implementation */}
    </div>
  );
}
```

### PostgreSQL Migration
```sql
-- Migration for this step
CREATE TABLE resources (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name VARCHAR(255) NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_resources_created_at ON resources(created_at);
```

## Testing

### Unit Tests
```rust
#[cfg(test)]
mod tests {
    use super::*;

    #[tokio::test]
    async fn test_create_resource() {
        // Test implementation
    }
}
```

### Integration Tests
```typescript
describe('Resource API', () => {
  it('should create a resource', async () => {
    // Test implementation
  });
});
```

### Acceptance Criteria
- [ ] Component functions as expected
- [ ] All unit tests pass
- [ ] Integration tests cover happy path and error cases
- [ ] Database migration can rollback cleanly
- [ ] API returns correct status codes
- [ ] Error handling works properly

## File Paths

### Backend (Rust)
- `/src/models/resource.rs` - Resource struct definitions
- `/src/handlers/resource.rs` - Resource handlers
- `/src/db/migrations/[timestamp]_create_resources.sql` - Database migration

### Frontend (TypeScript/React)
- `/app/components/ResourceForm.tsx` - Resource form component
- `/app/hooks/useResource.ts` - Resource API hook
- `/lib/api/resource.ts` - Resource API client

## Verification Criteria

- [ ] Code compiles without warnings
- [ ] All acceptance criteria met
- [ ] Tests run and pass
- [ ] Code follows project style guide
- [ ] Documentation updated
