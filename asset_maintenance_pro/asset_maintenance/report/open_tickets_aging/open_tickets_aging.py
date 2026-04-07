import frappe
from frappe.utils import date_diff, today

def execute(filters=None):
    filters = filters or {}
    columns = [
        {"label":"Request","fieldname":"name","fieldtype":"Link","options":"Maintenance Request","width":160},
        {"label":"Branch","fieldname":"branch","fieldtype":"Link","options":"Branch","width":120},
        {"label":"Asset","fieldname":"asset","fieldtype":"Link","options":"Asset","width":150},
        {"label":"Priority","fieldname":"priority","fieldtype":"Data","width":80},
        {"label":"Status","fieldname":"status","fieldtype":"Data","width":120},
        {"label":"Age (Days)","fieldname":"age_days","fieldtype":"Int","width":100},
        {"label":"Bucket","fieldname":"bucket","fieldtype":"Data","width":110},
        {"label":"Assigned To","fieldname":"assigned_to","fieldtype":"Link","options":"User","width":140},
        {"label":"SLA Status","fieldname":"sla_status","fieldtype":"Data","width":110},
    ]
    open_statuses = ("New","Assigned","In Progress","Waiting Parts","Awaiting Close","Triage","Approved")
    rows = frappe.get_all("Maintenance Request",
        filters={"status": ["in", open_statuses]},
        fields=["name","branch","asset","priority","status","creation","due_date","assigned_to"],
        order_by="creation asc"
    )
    today_date = today()
    data = []
    for r in rows:
        age = date_diff(today_date, r.creation.date() if hasattr(r.creation, "date") else r.creation)
        bucket = ("0-4h" if age == 0 else "4-24h" if age <= 1 else "1-3d" if age <= 3 else ">3d")
        sla = "Breached" if r.due_date and r.due_date < frappe.utils.getdate(today_date) else "On Track"
        data.append({
            "name": r.name, "branch": r.branch, "asset": r.asset,
            "priority": r.priority, "status": r.status,
            "age_days": age, "bucket": bucket,
            "assigned_to": r.assigned_to, "sla_status": sla,
        })
    return columns, data

def get_filters():
    return [
        {"label":"Branch","fieldname":"branch","fieldtype":"Link","options":"Branch"},
        {"label":"Priority","fieldname":"priority","fieldtype":"Select","options":"\nLow\nMedium\nHigh\nCritical"},
    ]
