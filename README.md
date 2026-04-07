# Asset Maintenance Pro

Advanced Asset Maintenance Management for ERPNext — with Kanban workflow,
preventive scheduling, branch-scoped access control, multi-channel notifications,
and automatic stock entry creation.

---

## Features

| Feature | Details |
|---------|---------|
| **Kanban Board** | 6-column flow: New → Assigned → In Progress → Waiting Parts → Awaiting Close → Completed |
| **Branch Isolation** | Branch Managers create/view requests only for their branch; Technicians see only their assignments |
| **Completion Gate** | Cannot mark Completed without `total_cost` + `completion_image` + all mandatory checklist items |
| **Preventive Scheduler** | Daily job generates requests from Maintenance Checklists (calendar-day or meter-threshold triggers) |
| **Stock Integration** | On completion, auto-creates a Stock Entry for Spare Part Consumption records |
| **Asset Update** | Updates `Asset.custom_last_maintenance_date` on every completion |
| **Notifications** | In-App (Frappe Notification Log + realtime), Email, optional SMS via configurable REST API |
| **REST API** | Full CRUD-style endpoints under `/api/method/asset_maintenance_pro.api.*` |
| **Work Logs** | Auto-logged on every status change; manual entries by Technicians |

---

## DocTypes

### Maintenance Request (main)
Primary transaction document. One per maintenance event.

| Field | Type | Notes |
|-------|------|-------|
| `asset` | Link → Asset | Required; auto-fills branch |
| `branch` | Link → Branch | Required; permission-scoped |
| `maintenance_type` | Select | Corrective / Preventive / Predictive / Inspection |
| `priority` | Select | Low / Medium / High / Critical |
| `status` | Select | Kanban column driver |
| `assigned_to` | Link → User | Filtered to Maintenance Technician role |
| `description` | Text Editor | Problem description |
| `images` | Table | Child: Maintenance Request Image |
| `checklist` | Table | Child: Maintenance Request Checklist Item |
| `total_cost` | Currency | **Required on Completed** |
| `completion_image` | Attach Image | **Required on Completed** |

Naming series: `MNT-.YYYY.-.#####`

### Maintenance Checklist (preventive schedule template)
Defines the schedule and task list for preventive maintenance.

| Field | Type | Notes |
|-------|------|-------|
| `asset_category` | Link → Asset Category | Applies to all assets in this category |
| `trigger_type` | Select | Calendar / Meter Reading / Both |
| `maintenance_interval_days` | Int | Days between auto-generated requests |
| `meter_threshold` | Float | Meter units between requests |
| `tasks` | Table | Default checklist rows cloned into each request |

### Maintenance Work Log
Timestamped journal entries attached to a request.
Auto-created on every status change. Technicians add manual entries.

### Spare Part Consumption
Records items consumed during repair. On `Maintenance Request` completion,
all linked records become a `Stock Entry (Material Issue)`.

### Asset Meter Reading
Odometer / hour-meter readings per asset. Feeds the meter-based preventive scheduler.

### Asset Maintenance Settings (Single)
Global configuration: notification toggles, SMS API credentials, default warehouse,
stock entry type, scheduler lookahead days.

---

## Roles

| Role | Can Create Requests | Branch Scope | Update Status | Add Work Logs |
|------|:-------------------:|:------------:|:-------------:|:-------------:|
| **System Manager** | ✅ All branches | All | ✅ | ✅ |
| **Branch Manager** | ✅ Own branch only | Own branch | ✅ | ✅ |
| **Maintenance Technician** | ❌ | Assigned only | ✅ (limited) | ✅ (assigned only) |

---

## Installation

```bash
# 1. Get the app
bench get-app https://github.com/your-org/asset_maintenance_pro.git

# 2. Install on your site
bench --site your-site.local install-app asset_maintenance_pro

# 3. Run migrations (creates DocTypes, fixtures, default settings)
bench --site your-site.local migrate

# 4. Build frontend assets
bench build --app asset_maintenance_pro

# 5. Restart
bench restart
```

---

## Configuration

1. Go to **Asset Maintenance Settings** (search in Awesome Bar)
2. Enable/disable Email, In-App, SMS notifications
3. For SMS: fill in API URL, API Key, API Secret, and From Number
4. Set Default Warehouse for stock entries
5. Enable Preventive Scheduler and set look-ahead days

### SMS API Integration
The SMS dispatcher sends a POST request to your configured `sms_api_url` with this payload:

```json
{
  "to": "+1234567890",
  "from": "MAINTENANCE",
  "message": "Maintenance Request MNT-2024-00001 is now In Progress",
  "api_key": "your_api_key"
}
```

Authorization header: `Bearer <sms_api_secret>` (if secret is set).

Adapt `asset_maintenance_pro/asset_maintenance/notifications.py → _send_sms()` to match your provider's schema.

---

## REST API Reference

All endpoints require Frappe authentication (token or session cookie).

### List Requests
```
GET /api/method/asset_maintenance_pro.api.get_maintenance_requests
    ?branch=Branch-001&status=New&limit_page_length=20&limit_start=0
```

### Get Single Request
```
GET /api/method/asset_maintenance_pro.api.get_maintenance_request
    ?name=MNT-2024-00001
```

### Transition Status
```
POST /api/method/asset_maintenance_pro.api.transition_status
Body: { "name": "MNT-2024-00001", "new_status": "In Progress" }
```

### Add Work Log
```
POST /api/method/asset_maintenance_pro.api.add_work_log
Body: {
  "maintenance_request": "MNT-2024-00001",
  "log_type": "Work Note",
  "description": "Replaced filter element",
  "time_spent_hours": 1.5
}
```

### Get Work Logs
```
GET /api/method/asset_maintenance_pro.api.get_work_logs
    ?maintenance_request=MNT-2024-00001
```

### Get Spare Parts
```
GET /api/method/asset_maintenance_pro.api.get_spare_parts
    ?maintenance_request=MNT-2024-00001
```

### Add Meter Reading
```
POST /api/method/asset_maintenance_pro.api.add_meter_reading
Body: { "asset": "ACC-AST-00001", "meter_value": 12500, "uom": "Hours" }
```

### Kanban Board Data
```
GET /api/method/asset_maintenance_pro.api.get_kanban_data
    ?branch=Branch-001
```

### Asset Summary
```
GET /api/method/asset_maintenance_pro.api.get_asset_maintenance_summary
    ?asset=ACC-AST-00001
```

---

## Preventive Maintenance Setup

1. Create a **Maintenance Checklist** document
   - Set `Asset Category` to target all matching assets automatically
   - Choose Trigger Type: **Calendar (Days)** or **Meter Reading** or **Both**
   - Add task rows to the `Tasks` table — these are cloned into each generated request
   - Mark mandatory tasks with `Is Mandatory = 1`

2. The daily scheduler (`generate_preventive_maintenance_requests`) runs at midnight
   - It checks each active checklist against every asset in the matching category
   - If the calendar interval or meter threshold is exceeded, a new `Maintenance Request`
     is created with `Request Type = Preventive (Auto-generated)`
   - Duplicate open requests for the same asset + checklist are skipped

3. To test manually:
   ```bash
   bench --site your-site.local execute \
     asset_maintenance_pro.asset_maintenance.scheduler.generate_preventive_maintenance_requests
   ```

---

## Kanban Board Setup

In Frappe's List view for **Maintenance Request**:
1. Click the **Kanban** view toggle (board icon)
2. Set **Column Based On** = `Kanban Column`
3. Save the Kanban Board view

The `kanban_column` field is automatically synced from `status` on every save.

---

## Stock Entry Flow

When a Maintenance Request is marked **Completed**:
1. All `Spare Part Consumption` records for that request are fetched
2. A `Stock Entry (Material Issue)` is auto-submitted with those items
3. The Stock Entry name is stored in each `Spare Part Consumption.stock_entry` field
4. If stock entry creation fails (e.g. insufficient stock), an Error Log is created
   and the completion still proceeds

---

## Custom Fields Added to Asset

| Field | Type | Description |
|-------|------|-------------|
| `custom_last_maintenance_date` | Date | Auto-updated on request completion |
| `custom_maintenance_interval_days` | Int | Per-asset override of checklist interval |
| `custom_meter_threshold` | Float | Per-asset override of checklist meter threshold |
| `custom_current_meter_value` | Float | Latest meter reading (read-only) |
| `custom_meter_uom` | Link → UOM | UOM for meter readings |

---

## Hooks Reference

| Hook | Module | Purpose |
|------|--------|---------|
| `doc_events["Maintenance Request"]["on_update"]` | `events.py` | Fires REST webhooks |
| `doc_events["Asset"]["after_insert"]` | `events.py` | Hints about applicable schedules |
| `scheduler_events["daily_long"]` | `scheduler.py` | Generate preventive requests |
| `scheduler_events["daily"]` | `scheduler.py` | Overdue notifications |
| `permission_query_conditions` | `permissions.py` | Branch/assignment list filter |
| `has_permission` | `permissions.py` | Document-level write control |

---

## Development

```bash
# After schema changes
bench --site your-site.local migrate

# After Python changes
bench --site your-site.local clear-cache

# After JS/CSS changes
bench build --app asset_maintenance_pro

# Run tests
bench --site your-site.local run-tests --app asset_maintenance_pro

# Test scheduler manually
bench --site your-site.local execute \
  asset_maintenance_pro.asset_maintenance.scheduler.generate_preventive_maintenance_requests

bench --site your-site.local execute \
  asset_maintenance_pro.asset_maintenance.scheduler.send_overdue_notifications
```

---

## License

MIT
