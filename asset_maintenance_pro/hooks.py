app_name        = "asset_maintenance_pro"
app_title       = "Asset Maintenance Pro"
app_publisher   = "Hosetia"
app_description = "Advanced Asset Maintenance — Smart Form, Auto Assignment, SLA, Kanban, Reports, Knowledge Base"
app_email       = "dev@hosetia.com"
app_license     = "MIT"
app_version     = "2.0.0"

required_apps = ["frappe", "erpnext"]

# ── Fixtures ─────────────────────────────────────────────────────────────────
fixtures = [
    {"dt": "Role",         "filters": [["name", "in", ["Branch Manager", "Maintenance Technician"]]]},
    {"dt": "Custom Field", "filters": [["module", "=", "Asset Maintenance"]]},
]

# ── Document Events ───────────────────────────────────────────────────────────
doc_events = {
    "Maintenance Request": {
        "on_update": "asset_maintenance_pro.asset_maintenance.events.on_maintenance_request_update",
        "after_insert": "asset_maintenance_pro.asset_maintenance.events.on_maintenance_request_insert",
    },
    "Asset": {
        "after_insert": "asset_maintenance_pro.asset_maintenance.events.on_asset_insert",
    },
}

# ── Scheduler ─────────────────────────────────────────────────────────────────
scheduler_events = {
    "daily_long": [
        "asset_maintenance_pro.asset_maintenance.scheduler.generate_preventive_maintenance_requests",
        "asset_maintenance_pro.asset_maintenance.scheduler.update_technician_load_counts",
    ],
    "daily": [
        "asset_maintenance_pro.asset_maintenance.scheduler.send_overdue_notifications",
    ],
    "hourly": [
        "asset_maintenance_pro.asset_maintenance.scheduler.run_sla_escalations",
    ],
    "cron": {
        "*/30 * * * *": [
            "asset_maintenance_pro.asset_maintenance.scheduler.auto_assign_new_requests",
        ]
    },
}

# ── Permissions ───────────────────────────────────────────────────────────────
permission_query_conditions = {
    "Maintenance Request": "asset_maintenance_pro.asset_maintenance.permissions.maintenance_request_query",
}
has_permission = {
    "Maintenance Request": "asset_maintenance_pro.asset_maintenance.permissions.has_maintenance_request_permission",
}

# ── Assets ────────────────────────────────────────────────────────────────────
app_include_js  = "/assets/asset_maintenance_pro/js/asset_maintenance_pro.js"
app_include_css = "/assets/asset_maintenance_pro/css/asset_maintenance_pro.css"

doctype_js = {
    "Maintenance Request": "public/js/maintenance_request.js",
    "Asset":               "public/js/asset_custom.js",
}
