import frappe
from frappe.utils import flt

def execute(filters=None):
    filters = filters or {}
    columns = [
        {"label":"Branch","fieldname":"branch","fieldtype":"Link","options":"Branch","width":140},
        {"label":"Asset Category","fieldname":"asset_category","fieldtype":"Data","width":140},
        {"label":"Planned","fieldname":"planned","fieldtype":"Int","width":90},
        {"label":"Completed","fieldname":"completed","fieldtype":"Int","width":100},
        {"label":"Overdue","fieldname":"overdue","fieldtype":"Int","width":90},
        {"label":"Compliance %","fieldname":"compliance_pct","fieldtype":"Float","width":120},
        {"label":"Avg Days Late","fieldname":"avg_days_late","fieldtype":"Float","width":120},
    ]
    rows = frappe.db.sql("""
        SELECT mr.branch, a.asset_category,
               COUNT(*) AS planned,
               SUM(IF(mr.status='Completed',1,0)) AS completed,
               SUM(IF(mr.status NOT IN ('Completed','Cancelled') AND mr.due_date < CURDATE(),1,0)) AS overdue,
               AVG(IF(mr.status='Completed' AND mr.due_date IS NOT NULL,
                   DATEDIFF(mr.modified, mr.due_date), NULL)) AS avg_days_late
        FROM `tabMaintenance Request` mr
        LEFT JOIN `tabAsset` a ON a.name = mr.asset
        WHERE mr.request_type = 'Preventive (Auto-generated)'
          {f}
        GROUP BY mr.branch, a.asset_category
    """.format(f=f"AND mr.branch='{filters['branch']}'" if filters.get("branch") else ""), as_dict=True)

    data = []
    for r in rows:
        planned = r.planned or 1
        comp = r.completed or 0
        data.append({
            "branch": r.branch,
            "asset_category": r.asset_category or "Unknown",
            "planned": planned,
            "completed": comp,
            "overdue": r.overdue or 0,
            "compliance_pct": round(comp / planned * 100, 1),
            "avg_days_late": round(flt(r.avg_days_late), 1),
        })
    data.sort(key=lambda x: x["compliance_pct"])
    return columns, data

def get_filters():
    return [
        {"label":"Branch","fieldname":"branch","fieldtype":"Link","options":"Branch"},
        {"label":"From Date","fieldname":"from_date","fieldtype":"Date"},
        {"label":"To Date","fieldname":"to_date","fieldtype":"Date"},
    ]
