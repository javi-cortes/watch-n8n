# watch-n8n

Minimal FastAPI + Postgres service to store **workflow watchers** around n8n executions.
n8n sends JSON payloads, this service stores them (JSONB) and exposes a simple API to query them later.

## Requirements

- Docker
- Docker Compose

## Run

docker compose up --build -d
docker compose logs -f

Health check:

curl http://localhost:8000/health

## Configuration

Create a `.env` file:

POSTGRES_USER=app  
POSTGRES_PASSWORD=app  
POSTGRES_DB=watch_n8n  
DATABASE_URL=postgresql+psycopg2://app:app@db:5432/watch_n8n  
API_KEY=dev-secret-change-me  

If API_KEY is set, all endpoints require header:

X-API-Key: <API_KEY>

## What is a workflow watcher

A workflow watcher is external data captured around an n8n workflow execution or node.
It is not a workflow itself, just extra information that n8n’s API does not expose.

Stored fields:
- workflow_id (required)
- execution_id (optional)
- node_id (optional)
- payload (JSON, required)

## API Endpoints

GET  /health  
POST /workflow-watchers  
GET  /workflow-watchers/{id}  
GET  /workflow-watchers  

Query filters:
workflow_id  
execution_id  
node_id  
limit  
cursor  

## Response Models

Single watcher:

{
  "id": 1,
  "workflow_id": "wf_demo",
  "execution_id": "exec_001",
  "node_id": "HTTP Request",
  "payload": {
    "hello": "n8n"
  },
  "created_at": "2026-01-04T12:00:00Z"
}

List response:

{
  "items": [
    { "...": "..." }
  ],
  "next_cursor": 42
}

## Examples (cURL)

Health:

curl http://localhost:8000/health

Create a workflow watcher:

curl -X POST http://localhost:8000/workflow-watchers \
  -H "Content-Type: application/json" \
  -H "X-API-Key: dev-secret-change-me" \
  -d '{
    "workflow_id": "wf_demo",
    "execution_id": "exec_001",
    "node_id": "HTTP Request",
    "payload": {
      "status": "ok",
      "items": [1,2,3]
    }
  }'

Get watcher by id:

curl http://localhost:8000/workflow-watchers/1 \
  -H "X-API-Key: dev-secret-change-me"

List watchers by workflow:

curl "http://localhost:8000/workflow-watchers?workflow_id=wf_demo" \
  -H "X-API-Key: dev-secret-change-me"

Pagination:

curl "http://localhost:8000/workflow-watchers?workflow_id=wf_demo&limit=2" \
  -H "X-API-Key: dev-secret-change-me"

curl "http://localhost:8000/workflow-watchers?workflow_id=wf_demo&limit=2&cursor=CURSOR" \
  -H "X-API-Key: dev-secret-change-me"

## Database Schema

Table: workflow_watchers

Columns:
- id (int, primary key)
- workflow_id (varchar, indexed)
- execution_id (varchar, indexed, nullable)
- node_id (varchar, indexed, nullable)
- payload (jsonb)
- created_at (timestamptz, indexed)

Indexes:
- workflow_id
- execution_id
- node_id
- (workflow_id, execution_id)

## Quick SQL Checks

docker compose exec db psql -U app -d watch_n8n

List tables:

SELECT tablename FROM pg_tables WHERE schemaname = 'public';

Latest watchers:

SELECT id, workflow_id, execution_id, node_id, created_at
FROM workflow_watchers
ORDER BY id DESC
LIMIT 20;

View JSON payload:

SELECT id, payload
FROM workflow_watchers
ORDER BY id DESC
LIMIT 5;

Query JSONB:

SELECT id
FROM workflow_watchers
WHERE payload @> '{"status":"ok"}';

## n8n Usage

Use an HTTP Request node:
Method: POST  
URL: http://YOUR_HOST:8000/workflow-watchers  
Headers:
- Content-Type: application/json
- X-API-Key: <API_KEY>

Body:
Send workflow, execution, node info and any output you want inside payload.
