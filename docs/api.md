# API Documentation

## Base URL

- Development: `http://localhost:8000`
- Production: TBD

## Health Check

### GET /api/health/

Returns API health status.

**Response:**
```json
{
  "status": "ok",
  "version": "0.1.0"
}
```

## Projects

### GET /api/projects
List all projects.

### POST /api/projects
Create a new project.

**Request Body:**
```json
{
  "name": "My Workshop",
  "templateId": "eHMI-design"
}
```

### GET /api/projects/{id}
Get project details.

### PUT /api/projects/{id}
Update project.

### DELETE /api/projects/{id}
Delete project.

## Assets

### POST /api/projects/{id}/assets
Upload workshop materials.

### GET /api/projects/{id}/assets
List project assets.

### GET /api/assets/{id}
Get asset details.

## Analysis

### POST /api/projects/{id}/analysis/start
Start analysis workflow.

### GET /api/projects/{id}/analysis/status
Get analysis status.

### GET /api/projects/{id}/analysis/results
Get analysis results.

## Agent Runs

### GET /api/projects/{id}/runs
List agent runs for a project.

### GET /api/runs/{id}
Get agent run details.

### POST /api/runs/{id}/rerun
Rerun an agent.

## Review

### GET /api/projects/{id}/review
Get review items.

### POST /api/review/{id}/approve
Approve a review item.

### POST /api/review/{id}/reject
Reject a review item.

### POST /api/review/{id}/revise
Submit revision.

## Export

### POST /api/projects/{id}/export
Generate export.

**Request Body:**
```json
{
  "format": "docx",
  "sections": ["summary", "findings", "recommendations"]
}
```

### GET /api/projects/{id}/exports
List export history.

## Realtime

### WS /api/ws/projects/{id}
WebSocket for real-time updates.

**Events:**
- `agent_run_started`
- `agent_run_completed`
- `agent_run_failed`
- `review_requested`
- `export_completed`
