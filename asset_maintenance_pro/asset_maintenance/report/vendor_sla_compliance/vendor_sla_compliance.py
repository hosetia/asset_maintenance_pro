import frappe
from frappe.utils import flt

def execute(filters=None):
    columns = [
        {"label":"Vendor","fieldname":"vendor","fieldtype":"Link","options":"Supplier","width":180},
        {"label":"Contract","fieldname":"contract","fieldtype":"Link","options":"Service Contract","width":160},
        {"label":"Type","fieldname":"contract_type","fieldtype":"Data","width":110},
        {"label":"SLA Response (hrs)","fieldname":"sla_response","fieldtype":"Float","width":150},
        {"label":"Avg Actual (hrs)","fieldname":"avg_actual","fieldtype":"Float","width":140},
        {"label":"Compliance %","fieldname":"compliance_pct","fieldtype":"Float","width":120},
        {"label":"Jobs This Period","fieldname":"job_count","fieldtype":"Int","width":130},
        {"label":"Visits Used","fieldname":"visits_used","fieldtype":"Int","width":110},
        {"label":"Visits Included","fieldname":"visits_included","fieldtype":"Int","width":130},
    ]
    contracts = frappe.get_all("Service Contract",
        filters={"status": ["in", ["Active","Expiring Soon"]]},
        fields=["name","vendor","contract_type","response_time_hours","included_visits_per_year","visits_used"]
    )
    data = []
    for c in contracts:
        jobs = frappe.get_all("Maintenance Work Order",
            filters={"vendor": c.vendor, "is_vendor_job": 1, "status": ["in", ["Completed","Closed"]]},
            fields=["vendor_response_time"]
        )
        avg_actual = (sum(flt(j.vendor_response_time) for j in jobs) / len(jobs)) if jobs else 0
        sla = c.response_time_hours or 1
        comp = min(100, round(sla / avg_actual * 100, 1)) if avg_actual else 100
        data.append({
            "vendor": c.vendor,
            "contract": c.name,
            "contract_type": c.contract_type,
            "sla_response": sla,
            "avg_actual": round(avg_actual, 2),
            "compliance_pct": comp,
            "job_count": len(jobs),
            "visits_used": c.visits_used or 0,
            "visits_included": c.included_visits_per_year or 0,
        })
    data.sort(key=lambda x: x["compliance_pct"])
    return columns, data

def get_filters():
    return [
        {"label":"Vendor","fieldname":"vendor","fieldtype":"Link","options":"Supplier"},
        {"label":"Contract Type","fieldname":"contract_type","fieldtype":"Select",
         "options":"\nHVAC\nRefrigeration\nFire Safety\nGas\nPest Control\nIT"},
    ]
