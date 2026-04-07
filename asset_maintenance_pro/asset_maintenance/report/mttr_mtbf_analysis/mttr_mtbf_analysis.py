def execute(filters=None):
    filters = filters or {}
    columns = [
        {"label":"Asset","fieldname":"asset","fieldtype":"Link","options":"Asset","width":180},
        {"label":"Category","fieldname":"asset_category","fieldtype":"Data","width":120},
        {"label":"Branch","fieldname":"branch","fieldtype":"Link","options":"Branch","width":120},
        {"label":"Faults","fieldname":"fault_count","fieldtype":"Int","width":80},
        {"label":"Total Downtime (hrs)","fieldname":"total_downtime","fieldtype":"Float","width":140},
        {"label":"MTTR (hrs)","fieldname":"mttr","fieldtype":"Float","width":110},
        {"label":"MTBF (days)","fieldname":"mtbf","fieldtype":"Float","width":110},
    ]

    from_date = filters.get("from_date") or "2020-01-01"
    to_date   = filters.get("to_date")   or frappe.utils.today()
    period_days = frappe.utils.date_diff(to_date, from_date) or 365

    branch_filter = ""
    if filters.get("branch"):
        branch_filter = "AND wo.branch = %(branch)s"

    rows = frappe.db.sql("""
        SELECT wo.asset, wo.branch,
               COUNT(*) AS fault_count,
               SUM(COALESCE(wo.downtime_hours,0)) AS total_downtime
        FROM `tabMaintenance Work Order` wo
        WHERE wo.status IN ('Completed','Closed')
          AND wo.asset IS NOT NULL AND wo.work_order_type='Corrective'
          {f}
        GROUP BY wo.asset, wo.branch
        ORDER BY fault_count DESC
    """.format(f=branch_filter), filters, as_dict=True)

    data = []
    for r in rows:
        n = r.fault_count or 1
        d = float(r.total_downtime or 0)
        asset_info = frappe.db.get_value("Asset", r.asset, ["asset_category"], as_dict=True) or frappe._dict()
        data.append({
            "asset": r.asset, "branch": r.branch,
            "asset_category": asset_info.get("asset_category",""),
            "fault_count": r.fault_count,
            "total_downtime": round(d, 2),
            "mttr": round(d / n, 2),
            "mtbf": round(period_days / n, 1),
        })
    return columns, data
