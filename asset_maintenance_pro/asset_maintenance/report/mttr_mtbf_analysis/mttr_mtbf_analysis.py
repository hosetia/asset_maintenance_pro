import frappe
from frappe.utils import flt, date_diff

def execute(filters=None):
    filters = filters or {}
    columns = [
        {"label":"Asset","fieldname":"asset","fieldtype":"Link","options":"Asset","width":180},
        {"label":"Category","fieldname":"asset_category","fieldtype":"Data","width":120},
        {"label":"Branch","fieldname":"branch","fieldtype":"Link","options":"Branch","width":120},
        {"label":"Faults","fieldname":"fault_count","fieldtype":"Int","width":80},
        {"label":"Total Downtime (hrs)","fieldname":"total_downtime","fieldtype":"Float","width":140},
        {"label":"MTTR (hrs)","fieldname":"mttr","fieldtype":"Float","width":110,"description":"Mean Time to Repair"},
        {"label":"MTBF (days)","fieldname":"mtbf","fieldtype":"Float","width":110,"description":"Mean Time Between Failures"},
        {"label":"First Time Fix %","fieldname":"first_fix_pct","fieldtype":"Float","width":130},
    ]
    rows = frappe.db.sql("""
        SELECT wo.asset, wo.branch,
               COUNT(*) AS fault_count,
               SUM(COALESCE(wo.downtime_hours,0)) AS total_downtime
        FROM `tabMaintenance Work Order` wo
        WHERE wo.status IN ('Completed','Closed')
          AND wo.asset IS NOT NULL AND wo.work_order_type = 'Corrective'
          {f}
        GROUP BY wo.asset, wo.branch
        ORDER BY fault_count DESC
    """.format(f=f"AND wo.branch='{filters['branch']}'" if filters.get("branch") else ""), as_dict=True)

    period_days = date_diff(
        filters.get("to_date") or frappe.utils.today(),
        filters.get("from_date") or "2020-01-01"
    ) or 365

    data = []
    for r in rows:
        n = r.fault_count or 1
        d = flt(r.total_downtime)
        asset_info = frappe.db.get_value("Asset", r.asset, ["asset_category","custom_criticality"], as_dict=True) or {}
        data.append({
            "asset": r.asset,
            "asset_category": asset_info.get("asset_category",""),
            "branch": r.branch,
            "fault_count": r.fault_count,
            "total_downtime": round(d, 2),
            "mttr": round(d / n, 2),
            "mtbf": round(period_days / n, 1),
            "first_fix_pct": 100,  # placeholder — needs repeat failure join
        })
    return columns, data

def get_filters():
    return [
        {"label":"Branch","fieldname":"branch","fieldtype":"Link","options":"Branch"},
        {"label":"From Date","fieldname":"from_date","fieldtype":"Date"},
        {"label":"To Date","fieldname":"to_date","fieldtype":"Date"},
        {"label":"Asset Category","fieldname":"asset_category","fieldtype":"Link","options":"Asset Category"},
    ]
