app_name = "asset_maintenance_pro"
app_title = "Asset Maintenance Pro"
app_publisher = "Your Company"
app_description = "Advanced Asset Maintenance Management with Kanban, preventive scheduling, and branch-level access control"
app_email = "dev@example.com"
app_license = "MIT"
app_version = "1.0.0"

required_apps = ["frappe", "erpnext"]

# ─── Fixtures ────────────────────────────────────────────────────────────────
fixtures = [
    {"dt": "Role", "filters": [["name", "in", ["Branch Manager", "Maintenance Technician"]]]},
    {"dt": "Custom Field", "filters": [["module", "=", "Asset Maintenance"]]},
]

# ─── Document Events ──────────────────────────────────────────────────────────
doc_events = {
    "Maintenance Request": {
        "on_update": "asset_maintenance_pro.asset_maintenance.events.on_maintenance_request_update",
    },
    "Asset": {
        "after_insert": "asset_maintenance_pro.asset_maintenance.events.on_asset_insert",
    },
}

# ─── Scheduler Events ────────────────────────────────────────────────────────
scheduler_events = {
    "daily_long": [
        "asset_maintenance_pro.asset_maintenance.scheduler.generate_preventive_maintenance_requests",
    ],
    "daily": [
        "asset_maintenance_pro.asset_maintenance.scheduler.send_overdue_notifications",
    ],
}

# ─── Permission Hooks ────────────────────────────────────────────────────────
permission_query_conditions = {
    "Maintenance Request": "asset_maintenance_pro.asset_maintenance.permissions.maintenance_request_query",
}

has_permission = {
    "Maintenance Request": "asset_maintenance_pro.asset_maintenance.permissions.has_maintenance_request_permission",
}

# ─── JS / CSS ────────────────────────────────────────────────────────────────
app_include_js = "/assets/asset_maintenance_pro/js/asset_maintenance_pro.js"
app_include_css = "/assets/asset_maintenance_pro/css/asset_maintenance_pro.css"

doctype_js = {
    "Maintenance Request": "public/js/maintenance_request.js",
    "Asset": "public/js/asset_custom.js",
}

# ─── Override Asset DocType to add custom fields via Custom Field fixtures ───
# Custom fields on Asset are defined in fixtures; no override_doctype_class needed
