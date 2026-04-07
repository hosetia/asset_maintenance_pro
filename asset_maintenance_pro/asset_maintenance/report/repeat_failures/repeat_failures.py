import frappe
from frappe.utils import date_diff

def execute(filters=None):
    filters = filters or {}
    period = int(filters.get("within_days") or 30)
    columns = [
        {"label":"Asset","fieldname":"asset","fieldtype":"Link","options":"Asset","width":180},
        {"label":"Branch","fieldname":"branch","fieldtype":"Data","width":120},
        {"label":"Category","fieldname":"asset_category","fieldtype":"Data","width":130},
        {"label":f"Failures (Last {period}d)","fieldname":"failure_count","fieldtype":"Int","width":150},
        {"label":"Last Failure","fieldname":"last_failure","fieldtype":"Date","width":120},
        {"label":"Repeat Flag","fieldname":"repeat_flag","fieldtype":"Data","width":120},
    ]
    rows = frappe.db.sql(f"""
        SELECT mr.asset, mr.branch, a.asset_category,
               COUNT(*) AS failure_count,
               MAX(DATE(mr.creation)) AS last_failure
        FROM `tabMaintenance Request` mr
        LEFT JOIN `tabAsset` a ON a.name = mr.asset
        WHERE mr.maintenance_type = 'Corrective'
          AND mr.creation >= DATE_SUB(CURDATE(), INTERVAL {period} DAY)
          AND mr.asset IS NOT NULL
        GROUP BY mr.asset, mr.branch, a.asset_category
        HAVING failure_count > 1
        ORDER BY failure_count DESC
    """, as_dict=True)

    data = []
    for r in rows:
        flag = "🔴 Critical" if r.failure_count >= 5 else "🟠 High" if r.failure_count >= 3 else "🟡 Medium"
        data.append({
            "asset": r.asset, "branch": r.branch,
            "asset_category": r.asset_category or "",
            "failure_count": r.failure_count,
            "last_failure": r.last_failure,
            "repeat_flag": flag,
        })
    return columns, data

def get_filters():
    return [
        {"label":"Branch","fieldname":"branch","fieldtype":"Link","options":"Branch"},
        {"label":"Within (Days)","fieldname":"within_days","fieldtype":"Select",
         "options":"7\n30\n90","default":"30"},
        {"label":"Asset Category","fieldname":"asset_category","fieldtype":"Link","options":"Asset Category"},
    ]
