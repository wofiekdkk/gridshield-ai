# GridShield AI - User Manual

## Login
Open http://localhost:5173
- Admin: `admin / admin123` (full control)
- Operator: `operator / operator123` (approve recovery)
- Viewer: `viewer / viewer123` (read-only)

## Pages

### Dashboard
Overview of grid status, active faults, live event feed.

### Digital Twin
Interactive SVG topology. Click any component to inspect.
Red = faulted (pulsing), Cyan = critical load, Green = normal.

### Live Sensors
Real-time charts of voltage, current, temperature, load.
Table of latest 30 readings from all sensors.

### Fault Center
List all faults (active + historical). Click to inspect.
Press "Auto-Recover" to run full recovery pipeline.

### AI Diagnostics
Latest classification with probability bar chart.
History of all AI predictions.

### Recovery Center
Candidate plans grouped by fault.
Each plan shows: restored load, cascade risk, feasibility.
Click "Execute Plan" on feasible plans.

### Fault Simulator
Inject faults manually:
1. Choose component
2. Choose fault type (14 types)
3. Set severity (slider)
4. Click INJECT FAULT
5. Watch AI pipeline execute in Dashboard event feed

### Analytics
Fault distribution pie chart, vulnerable components ranking,
recovery success rate metrics.

### History
Full chronological system event log.

## Demo Flow (5 minutes)

1. Login as admin
2. Go to Dashboard - verify NORMAL state
3. Open Fault Simulator
4. Select LINE_7, TRANSMISSION_LINE_FAILURE, severity 0.85
5. Click INJECT FAULT
6. Return to Dashboard - fault appears, event feed updates
7. Go to Recovery Center - 3 plans visible
8. Note Plan A is REJECTED, Plan B is FEASIBLE with highest score
9. Click Execute Plan on Plan B
10. Return to Dashboard - fault marked RECOVERED
11. Go to History - full timeline visible
