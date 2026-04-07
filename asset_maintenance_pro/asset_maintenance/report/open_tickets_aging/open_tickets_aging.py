def execute(filters=None):
    filters = filters or {}
    columns = [
        {"label":"Request","fieldname":"name","fieldtype":"Link","options":"Maintenance Request","width":160},
        {"label":"Branch","fieldname":"branch","fieldtype":"Link","options":"Branch","width":120},
        {"label":"Asset","fieldname":"asset","fieldtype":"Link","options":"Asset","width":150},
        {"label":"Priority","fieldname":"priority","fieldtype":"Data","width":80},
        {"label":"Status","fieldname":"status","fieldtype":"Data","width":120},
        {"label":"Age (Days)","fieldname":"age_days","fieldtype":"Int","width":100},
        {"label":"Bucket","fieldname":"bucket","fieldtype":"Data","width":110},
        {"label":"Assigned To","fieldname":"assigned_to","fieldtype":"Link","options":"User","width":140},
        {"label":"SLA Status","fieldname":"sla_status","fieldtype":"Data","width":110},
    ]

    rows = frappe.db.sql("""
        SELECT name, branch, asset, priority, status,
               DATEDIFF(CURDATE(), DATE(creation)) AS age_days,
               assigned_to, due_date
        FROM `tabMaintenance Request`
        WHERE status IN ('New','Assigned','In Progress','Waiting Parts','Awaiting Close')
        ORDER BY creation ASC
    """, as_dict=True)

    today = frappe.utils.today()
    data = []
    for r in rows:
        age = r.age_days or 0
        bucket = "0-1d" if age <= 1 else "1-3d" if age <= 3 else "3-7d" if age <= 7 else ">7d"
        sla = "Breached" if r.due_date and r.due_date < frappe.utils.getdate(today) else "On Track"
        data.append({
            "name": r.name, "branch": r.branch, "asset": r.asset,
            "priority": r.priority, "status": r.status,
            "age_days": age, "bucket": bucket,
            "assigned_to": r.assigned_to, "sla_status": sla,
        })
    return columns, data
