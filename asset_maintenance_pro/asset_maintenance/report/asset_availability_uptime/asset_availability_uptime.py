def execute(filters=None):
    filters = filters or {}
    columns = [
        {"label":"Asset","fieldname":"asset","fieldtype":"Link","options":"Asset","width":200},
        {"label":"Branch","fieldname":"branch","fieldtype":"Link","options":"Branch","width":120},
        {"label":"Category","fieldname":"asset_category","fieldtype":"Data","width":120},
        {"label":"Criticality","fieldname":"criticality","fieldtype":"Data","width":80},
        {"label":"Total Downtime (hrs)","fieldname":"total_downtime","fieldtype":"Float","width":140},
        {"label":"Faults","fieldname":"fault_count","fieldtype":"Int","width":80},
        {"label":"Availability %","fieldname":"availability_pct","fieldtype":"Float","width":120},
        {"label":"MTTR (hrs)","fieldname":"mttr","fieldtype":"Float","width":100},
        {"label":"MTBF (days)","fieldname":"mtbf","fieldtype":"Float","width":100},
    ]

    from_date = filters.get("from_date") or "2020-01-01"
    to_date   = filters.get("to_date")   or frappe.utils.today()
    period_days = frappe.utils.date_diff(to_date, from_date) or 30
    total_hours = period_days * 24

    branch_filter = ""
    if filters.get("branch"):
        branch_filter = "AND wo.branch = %(branch)s"

    rows = frappe.db.sql("""
        SELECT wo.asset, wo.branch,
               SUM(COALESCE(wo.downtime_hours,0)) AS total_downtime,
               COUNT(*) AS fault_count
        FROM `tabMaintenance Work Order` wo
        WHERE wo.status IN ('Completed','Closed')
          AND wo.asset IS NOT NULL AND wo.asset != ''
          {f}
        GROUP BY wo.asset, wo.branch
    """.format(f=branch_filter), filters, as_dict=True)

    data = []
    for r in rows:
        downtime = float(r.total_downtime or 0)
        faults   = r.fault_count or 1
        avail    = round(max(0, (total_hours - downtime) / total_hours * 100), 1) if total_hours else 0
        mttr     = round(downtime / faults, 2) if faults else 0
        mtbf     = round(period_days / faults, 1) if faults else period_days
        asset_info = frappe.db.get_value("Asset", r.asset,
            ["asset_category","custom_criticality"], as_dict=True) or frappe._dict()
        data.append({
            "asset": r.asset, "branch": r.branch,
            "asset_category": asset_info.get("asset_category",""),
            "criticality": asset_info.get("custom_criticality",""),
            "total_downtime": downtime, "fault_count": r.fault_count,
            "availability_pct": avail, "mttr": mttr, "mtbf": mtbf,
        })
    data.sort(key=lambda x: x["availability_pct"])
    return columns, data
