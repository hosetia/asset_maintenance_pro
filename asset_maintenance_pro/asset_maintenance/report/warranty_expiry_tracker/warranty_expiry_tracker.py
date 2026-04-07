import frappe
from frappe.utils import date_diff, today, getdate

def execute(filters=None):
    filters = filters or {}
    threshold = int(filters.get("expiring_within_days") or 90)
    columns = [
        {"label":"Asset","fieldname":"asset","fieldtype":"Link","options":"Asset","width":180},
        {"label":"Asset Name","fieldname":"asset_name","fieldtype":"Data","width":160},
        {"label":"Branch","fieldname":"branch","fieldtype":"Link","options":"Branch","width":120},
        {"label":"Category","fieldname":"asset_category","fieldtype":"Data","width":130},
        {"label":"Warranty End","fieldname":"warranty_end","fieldtype":"Date","width":120},
        {"label":"Days Left","fieldname":"days_left","fieldtype":"Int","width":100},
        {"label":"Status","fieldname":"warranty_status","fieldtype":"Data","width":120},
        {"label":"Vendor","fieldname":"vendor","fieldtype":"Data","width":140},
    ]
    today_str = today()
    rows = frappe.db.sql(f"""
        SELECT name AS asset, asset_name, branch, asset_category,
               custom_warranty_end AS warranty_end,
               DATEDIFF(custom_warranty_end, CURDATE()) AS days_left,
               asset_owner
        FROM `tabAsset`
        WHERE custom_warranty_end IS NOT NULL
          AND custom_warranty_end >= CURDATE()
          AND custom_warranty_end <= DATE_ADD(CURDATE(), INTERVAL {threshold} DAY)
        ORDER BY warranty_end ASC
    """, as_dict=True)

    data = []
    for r in rows:
        d = r.days_left or 0
        status = "🔴 < 30 days" if d < 30 else "🟠 30-60 days" if d < 60 else "🟡 60-90 days"
        data.append({**r, "warranty_status": status, "vendor": r.asset_owner or ""})
    return columns, data

def get_filters():
    return [
        {"label":"Branch","fieldname":"branch","fieldtype":"Link","options":"Branch"},
        {"label":"Expiring Within (Days)","fieldname":"expiring_within_days",
         "fieldtype":"Select","options":"30\n60\n90\n180","default":"90"},
        {"label":"Asset Category","fieldname":"asset_category","fieldtype":"Link","options":"Asset Category"},
    ]
