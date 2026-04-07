import frappe
from frappe.utils import flt

def execute(filters=None):
    filters = filters or {}
    columns = [
        {"label":"Item","fieldname":"item_code","fieldtype":"Link","options":"Item","width":160},
        {"label":"Item Name","fieldname":"item_name","fieldtype":"Data","width":180},
        {"label":"Branch","fieldname":"branch","fieldtype":"Link","options":"Branch","width":120},
        {"label":"Asset Category","fieldname":"asset_category","fieldtype":"Data","width":140},
        {"label":"Qty Used","fieldname":"total_qty","fieldtype":"Float","width":90},
        {"label":"Total Amount","fieldname":"total_amount","fieldtype":"Currency","width":120},
        {"label":"Times Used","fieldname":"usage_count","fieldtype":"Int","width":100},
        {"label":"In Stock","fieldname":"in_stock","fieldtype":"Float","width":90},
    ]
    rows = frappe.db.sql("""
        SELECT spc.item_code, spc.item_name,
               mr.branch,
               a.asset_category,
               SUM(spc.qty) AS total_qty,
               SUM(spc.amount) AS total_amount,
               COUNT(*) AS usage_count
        FROM `tabSpare Part Consumption` spc
        LEFT JOIN `tabMaintenance Request` mr ON mr.name = spc.maintenance_request
        LEFT JOIN `tabAsset` a ON a.name = mr.asset
        WHERE 1=1
          {f}
        GROUP BY spc.item_code, mr.branch, a.asset_category
        ORDER BY total_amount DESC
    """.format(f=f"AND mr.branch='{filters['branch']}'" if filters.get("branch") else ""), as_dict=True)

    data = []
    for r in rows:
        stock = frappe.db.sql("""
            SELECT SUM(actual_qty) FROM `tabBin` WHERE item_code=%s
        """, r.item_code)
        in_stock = flt(stock[0][0]) if stock and stock[0][0] else 0
        data.append({**r, "in_stock": in_stock})
    return columns, data

def get_filters():
    return [
        {"label":"Branch","fieldname":"branch","fieldtype":"Link","options":"Branch"},
        {"label":"Item","fieldname":"item_code","fieldtype":"Link","options":"Item"},
        {"label":"From Date","fieldname":"from_date","fieldtype":"Date"},
        {"label":"To Date","fieldname":"to_date","fieldtype":"Date"},
    ]
