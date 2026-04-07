import frappe
from frappe.utils import flt

def execute(filters=None):
    filters = filters or {}
    columns = [
        {"label":"Branch","fieldname":"branch","fieldtype":"Link","options":"Branch","width":160},
        {"label":"Corrective Jobs","fieldname":"corrective_count","fieldtype":"Int","width":130},
        {"label":"Preventive Jobs","fieldname":"preventive_count","fieldtype":"Int","width":130},
        {"label":"Parts Cost","fieldname":"parts_cost","fieldtype":"Currency","width":120},
        {"label":"Vendor Cost","fieldname":"vendor_cost","fieldtype":"Currency","width":120},
        {"label":"Total Cost","fieldname":"total_cost","fieldtype":"Currency","width":120},
        {"label":"Cost/Request","fieldname":"cost_per_request","fieldtype":"Currency","width":120},
        {"label":"Downtime (hrs)","fieldname":"total_downtime","fieldtype":"Float","width":120},
    ]
    rows = frappe.db.sql("""
        SELECT mr.branch,
               SUM(IF(mr.maintenance_type='Corrective',1,0)) AS corrective_count,
               SUM(IF(mr.maintenance_type='Preventive',1,0)) AS preventive_count,
               SUM(COALESCE(mr.total_cost,0)) AS parts_cost,
               COUNT(*) AS total_requests
        FROM `tabMaintenance Request` mr
        WHERE mr.status = 'Completed'
        GROUP BY mr.branch
        ORDER BY parts_cost DESC
    """, as_dict=True)

    vendor_costs = frappe.db.sql("""
        SELECT wo.branch, SUM(COALESCE(wo.total_cost,0)) AS vendor_cost,
               SUM(COALESCE(wo.downtime_hours,0)) AS total_downtime
        FROM `tabMaintenance Work Order` wo
        WHERE wo.is_vendor_job=1 AND wo.status IN ('Completed','Closed')
        GROUP BY wo.branch
    """, as_dict=True)
    vendor_map = {r.branch: r for r in vendor_costs}

    data = []
    for r in rows:
        vc = flt(vendor_map.get(r.branch, {}).get("vendor_cost", 0))
        downtime = flt(vendor_map.get(r.branch, {}).get("total_downtime", 0))
        parts = flt(r.parts_cost)
        total = parts + vc
        count = r.total_requests or 1
        data.append({
            "branch": r.branch,
            "corrective_count": r.corrective_count,
            "preventive_count": r.preventive_count,
            "parts_cost": parts,
            "vendor_cost": vc,
            "total_cost": total,
            "cost_per_request": round(total / count, 2),
            "total_downtime": round(downtime, 2),
        })
    return columns, data

def get_filters():
    return [
        {"label":"From Date","fieldname":"from_date","fieldtype":"Date"},
        {"label":"To Date","fieldname":"to_date","fieldtype":"Date"},
        {"label":"Branch","fieldname":"branch","fieldtype":"Link","options":"Branch"},
    ]
