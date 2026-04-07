import frappe
from frappe.utils import flt

def execute(filters=None):
    filters = filters or {}
    columns = [
        {"label":"Rank","fieldname":"rank","fieldtype":"Int","width":60},
        {"label":"Symptom / Issue","fieldname":"symptom","fieldtype":"Data","width":200},
        {"label":"Failure Class","fieldname":"failure_class","fieldtype":"Data","width":130},
        {"label":"Count","fieldname":"count","fieldtype":"Int","width":80},
        {"label":"% of Total","fieldname":"pct","fieldtype":"Float","width":100},
        {"label":"Cumulative %","fieldname":"cumulative_pct","fieldtype":"Float","width":120},
        {"label":"Total Downtime (hrs)","fieldname":"total_downtime","fieldtype":"Float","width":150},
    ]
    rows = frappe.db.sql("""
        SELECT COALESCE(wo.symptom_code, 'Unknown') AS symptom,
               COALESCE(wo.failure_class, 'Unknown') AS failure_class,
               COUNT(*) AS cnt,
               SUM(COALESCE(wo.downtime_hours,0)) AS total_downtime
        FROM `tabMaintenance Work Order` wo
        WHERE wo.status IN ('Completed','Closed') AND wo.work_order_type='Corrective'
        GROUP BY symptom, failure_class
        ORDER BY cnt DESC
        LIMIT 30
    """, as_dict=True)

    total = sum(r.cnt for r in rows) or 1
    cumulative = 0
    data = []
    for i, r in enumerate(rows, 1):
        pct = round(r.cnt / total * 100, 1)
        cumulative += pct
        data.append({
            "rank": i,
            "symptom": r.symptom,
            "failure_class": r.failure_class,
            "count": r.cnt,
            "pct": pct,
            "cumulative_pct": round(cumulative, 1),
            "total_downtime": round(flt(r.total_downtime), 2),
        })
    return columns, data

def get_filters():
    return [
        {"label":"Branch","fieldname":"branch","fieldtype":"Link","options":"Branch"},
        {"label":"Asset Category","fieldname":"asset_category","fieldtype":"Link","options":"Asset Category"},
        {"label":"From Date","fieldname":"from_date","fieldtype":"Date"},
        {"label":"To Date","fieldname":"to_date","fieldtype":"Date"},
    ]
