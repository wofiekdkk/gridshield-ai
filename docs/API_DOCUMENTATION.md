# GridShield AI - API Documentation

Base URL: `http://localhost:8000/api/v1`

Interactive docs: `http://localhost:8000/docs`

## Authentication
POST `/auth/login` → `{ access_token, user }`

## Grid
- GET `/grid/state`
- GET `/grid/components`
- POST `/grid/simulate`
- GET `/grid/history`

## Sensors
- GET `/sensors`
- GET `/sensors/{id}/readings`
- POST `/sensors/ingest`

## Faults
- GET `/faults?active_only=false`
- GET `/faults/{fault_id}`
- POST `/faults/inject` body: `{component_id, fault_type, severity, duration}`
- POST `/faults/reset`

## Recovery
- GET `/recovery/plans?fault_id=...`
- GET `/recovery/plans/{plan_id}`
- POST `/recovery/execute` body: `{plan_id}`
- POST `/recovery/auto-recover/{fault_id}`

## AI
- GET `/ai/predictions`
- GET `/ai/localizations`
- POST `/ai/predict/anomaly` body: feature dict
- POST `/ai/predict/classify` body: feature dict

## Analytics
- GET `/analytics/summary`
- GET `/analytics/fault-distribution`
- GET `/analytics/vulnerable-components`
- GET `/analytics/recent-events`

## WebSocket
Connect: `ws://localhost:8000/api/v1/ws/grid`

Events broadcast: `sensor_update`, `fault_detected`, `fault_classified`,
`fault_localized`, `cascade_predicted`, `recovery_plans_generated`,
`recovery_executed`, `grid_state_changed`, `grid_reset`.
