def execute(filters=None):
    filters = filters or {}
    columns = [
        {"label":"Technician","fieldname":"technician","fieldtype":"Link","options":"User","width":160},
        {"label":"Jobs Completed","fieldname":"jobs_completed","fieldtype":"Int","width":130},
        {"label":"Total Hours","fieldname":"total_hours","fieldtype":"Float","width":110},
        {"label":"Avg Hours/Job","fieldname":"avg_hours","fieldtype":"Float","width":120},
        {"label":"Open Jobs","fieldname":"open_jobs","fieldtype":"Int","width":100},
        {"label":"Overdue Jobs","fieldname":"overdue_jobs","fieldtype":"Int","width":110},
    ]

    rows = frappe.db.sql("""
        SELECT tl.technician,
               COUNT(DISTINCT wo.name) AS jobs_completed,
               SUM(COALESCE(tl.hours,0)) AS total_hours,
               AVG(COALESCE(tl.hours,0)) AS avg_hours
        FROM `tabWork Order Time Log` tl
        JOIN `tabMaintenance Work Order` wo ON wo.name = tl.parent
        WHERE wo.status IN ('Completed','Closed')
        GROUP BY tl.technician
        ORDER BY jobs_completed DESC
    """, as_dict=True)

    data = []
    for r in rows:
        open_j = frappe.db.count("Maintenance Work Order", {
            "lead_technician": r.technician,
            "status": ["in", ["Ready","Scheduled Today","On Route","On Site","Repairing","Testing"]]
        })
        overdue_j = frappe.db.count("Maintenance Request", {
            "assigned_to": r.technician,
            "status": ["in", ["New","Assigned","In Progress","Waiting Parts"]],
            "due_date": ["<", frappe.utils.today()]
        })
        data.append({
            "technician": r.technician,
            "jobs_completed": r.jobs_completed,
            "total_hours": round(float(r.total_hours or 0), 2),
            "avg_hours": round(float(r.avg_hours or 0), 2),
            "open_jobs": open_j,
            "overdue_jobs": overdue_j,
        })
    return columns, data
