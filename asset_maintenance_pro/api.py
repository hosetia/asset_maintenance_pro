"""
Asset Maintenance Pro — REST API
Complete API: Smart Form, QR, Auto Assignment, SLA, Dashboard, Reports, Knowledge Base
"""
import frappe
from frappe import _
from frappe.utils import now, today, add_days, flt, getdate, date_diff
import json


# ══════════════════════════════════════════════════════════════════════════════
# PHASE 1 — Smart Form + QR + RBAC
# ══════════════════════════════════════════════════════════════════════════════

@frappe.whitelist()
def get_user_branch():
    """Return the branch of the currently logged-in user's Employee record."""
    user = frappe.session.user
    branch = frappe.db.get_value("Employee", {"user_id": user, "status": "Active"}, "branch")
    return {"branch": branch, "user": user}


@frappe.whitelist()
def get_asset_details(asset):
    """Return asset details for auto-fill on Maintenance Request form."""
    doc = frappe.get_doc("Asset", asset)
    last_maintenance = frappe.db.get_value(
        "Maintenance Request",
        {"asset": asset, "status": "Completed"},
        "modified",
        order_by="modified desc",
    )
    return {
        "asset": asset,
        "asset_name": doc.asset_name,
        "asset_category": doc.asset_category,
        "branch": getattr(doc, "branch", None) or frappe.db.get_value("Asset", asset, "branch"),
        "location": getattr(doc, "location", None),
        "last_maintenance": str(last_maintenance) if last_maintenance else None,
        "custom_last_maintenance_date": frappe.db.get_value("Asset", asset, "custom_last_maintenance_date"),
        "custom_maintenance_interval_days": frappe.db.get_value("Asset", asset, "custom_maintenance_interval_days"),
    }


@frappe.whitelist()
def get_technicians(doctype, txt, searchfield, start, page_len, filters):
    """Filtered user search: only Maintenance Technician role, optionally by branch."""
    branch = filters.get("branch") if isinstance(filters, dict) else ""
    conditions = ""
    values = {"txt": f"%{txt}%", "role": "Maintenance Technician"}

    if branch:
        # Filter technicians whose Employee.branch matches
        return frappe.db.sql("""
            SELECT u.name, u.full_name
            FROM `tabUser` u
            INNER JOIN `tabHas Role` hr ON hr.parent = u.name AND hr.role = %(role)s
            LEFT JOIN `tabEmployee` e ON e.user_id = u.name AND e.status = 'Active'
            WHERE u.enabled = 1
              AND (u.full_name LIKE %(txt)s OR u.name LIKE %(txt)s)
              AND (e.branch = %(branch)s OR %(branch)s = '')
            ORDER BY u.full_name
            LIMIT %(start)s, %(page_len)s
        """, {**values, "branch": branch, "start": start, "page_len": page_len})
    else:
        return frappe.db.sql("""
            SELECT u.name, u.full_name
            FROM `tabUser` u
            INNER JOIN `tabHas Role` hr ON hr.parent = u.name AND hr.role = %(role)s
            WHERE u.enabled = 1
              AND (u.full_name LIKE %(txt)s OR u.name LIKE %(txt)s)
            ORDER BY u.full_name
            LIMIT %(start)s, %(page_len)s
        """, {**values, "start": start, "page_len": page_len})


@frappe.whitelist()
def get_checklist_tasks(checklist):
    """Return tasks from a Maintenance Checklist template."""
    tasks = frappe.get_all(
        "Maintenance Request Checklist Item",
        filters={"parent": checklist, "parenttype": "Maintenance Checklist"},
        fields=["task", "is_mandatory"],
        order_by="idx asc",
    )
    return tasks


@frappe.whitelist()
def get_asset_qr_url(asset):
    """Return URL to the QR print format for an asset."""
    return f"/printview?doctype=Asset&name={frappe.utils.quote(asset)}&format=Asset+QR+Code&no_letterhead=1"


# ══════════════════════════════════════════════════════════════════════════════
# PHASE 2 — Auto Assignment + SLA
# ══════════════════════════════════════════════════════════════════════════════

@frappe.whitelist()
def get_suggested_technician(branch=None, maintenance_type=None):
    """
    Suggest the best technician based on:
    1. Assignment Rules (branch + type match)
    2. Lowest current open request load
    """
    # Try assignment rules first
    filters = {"is_active": 1}
    if branch:         filters["branch"] = branch
    if maintenance_type: filters["maintenance_type"] = maintenance_type

    rules = frappe.get_all(
        "Maintenance Assignment Rule",
        filters=filters,
        fields=["assigned_technician", "max_open_requests", "current_load_count"],
        order_by="priority_order asc",
    )

    for rule in rules:
        tech = rule.assigned_technician
        load = _get_technician_load(tech)
        if load < (rule.max_open_requests or 10):
            return {"user": tech, "load": load, "source": "assignment_rule"}

    # Fallback: technician with lowest load in branch
    technicians = _get_all_technicians(branch)
    if not technicians:
        return None

    best = min(technicians, key=lambda t: _get_technician_load(t["name"]))
    return {
        "user": best["name"],
        "load": _get_technician_load(best["name"]),
        "source": "load_balance",
    }


def _get_technician_load(user):
    """Count open requests assigned to a technician."""
    return frappe.db.count("Maintenance Request", {
        "assigned_to": user,
        "status": ["in", ["New", "Assigned", "In Progress", "Waiting Parts", "Awaiting Close"]],
    })


def _get_all_technicians(branch=None):
    """Return all active Maintenance Technicians."""
    sql = """
        SELECT DISTINCT u.name, u.full_name
        FROM `tabUser` u
        INNER JOIN `tabHas Role` hr ON hr.parent = u.name AND hr.role = 'Maintenance Technician'
        WHERE u.enabled = 1
    """
    if branch:
        sql += """ AND EXISTS (
            SELECT 1 FROM `tabEmployee` e
            WHERE e.user_id = u.name AND e.branch = %s AND e.status = 'Active'
        )"""
        return frappe.db.sql(sql, branch, as_dict=True)
    return frappe.db.sql(sql, as_dict=True)


@frappe.whitelist()
def get_request_summary(name):
    """Return summary stats for a single Maintenance Request (dashboard indicators)."""
    doc = frappe.get_doc("Maintenance Request", name)

    work_log_count  = frappe.db.count("Maintenance Work Log",  {"maintenance_request": name})
    spare_part_count = frappe.db.count("Spare Part Consumption", {"maintenance_request": name})

    is_overdue = False
    sla_status = None

    if doc.due_date and doc.status not in ("Completed", "Cancelled"):
        days_left = date_diff(doc.due_date, today())
        is_overdue = days_left < 0
        sla_status = "Breached" if days_left < 0 else "At Risk" if days_left <= 1 else "On Track"

    return {
        "work_log_count":  work_log_count,
        "spare_part_count": spare_part_count,
        "is_overdue":      is_overdue,
        "sla_status":      sla_status,
    }


# ══════════════════════════════════════════════════════════════════════════════
# PHASE 3 — Dashboard + Reports
# ══════════════════════════════════════════════════════════════════════════════

@frappe.whitelist()
def get_dashboard_data(branch=None, from_date=None, to_date=None):
    """
    Main dashboard payload:
    - Status counts (Kanban summary)
    - Heatmap data (faults per branch)
    - SLA summary
    - Top assets by fault count
    - Technician performance
    - Monthly trend
    """
    filters = {}
    if branch: filters["branch"] = branch
    if from_date: filters["creation"] = [">=", from_date]
    if to_date:   filters["creation"] = ["<=", to_date]

    all_requests = frappe.get_all(
        "Maintenance Request",
        filters=filters,
        fields=["name", "status", "branch", "asset", "priority", "maintenance_type",
                "assigned_to", "due_date", "total_cost", "creation", "kanban_column"],
    )

    # ── Status counts ─────────────────────────────────────────────────────────
    status_counts = {}
    for r in all_requests:
        status_counts[r.status] = status_counts.get(r.status, 0) + 1

    # ── Priority counts ───────────────────────────────────────────────────────
    priority_counts = {}
    for r in all_requests:
        priority_counts[r.priority] = priority_counts.get(r.priority, 0) + 1

    # ── Heatmap: faults per branch ────────────────────────────────────────────
    branch_faults = {}
    for r in all_requests:
        b = r.branch or "Unknown"
        branch_faults[b] = branch_faults.get(b, 0) + 1

    # ── SLA summary ───────────────────────────────────────────────────────────
    open_statuses = {"New", "Assigned", "In Progress", "Waiting Parts", "Awaiting Close"}
    today_date = getdate(today())
    overdue_count = sum(
        1 for r in all_requests
        if r.status in open_statuses
        and r.due_date
        and getdate(r.due_date) < today_date
    )
    at_risk_count = sum(
        1 for r in all_requests
        if r.status in open_statuses
        and r.due_date
        and 0 <= date_diff(r.due_date, today()) <= 1
    )

    # ── Top assets by fault count ─────────────────────────────────────────────
    asset_faults = {}
    for r in all_requests:
        if r.asset:
            asset_faults[r.asset] = asset_faults.get(r.asset, 0) + 1
    top_assets = sorted(asset_faults.items(), key=lambda x: x[1], reverse=True)[:10]

    # ── Technician load ───────────────────────────────────────────────────────
    tech_load = {}
    for r in all_requests:
        if r.assigned_to and r.status in open_statuses:
            tech_load[r.assigned_to] = tech_load.get(r.assigned_to, 0) + 1

    # ── Total cost ────────────────────────────────────────────────────────────
    total_cost = sum(flt(r.total_cost) for r in all_requests if r.status == "Completed")

    # ── Monthly trend (last 6 months) ─────────────────────────────────────────
    monthly_trend = frappe.db.sql("""
        SELECT DATE_FORMAT(creation, '%%Y-%%m') AS month, COUNT(*) AS count
        FROM `tabMaintenance Request`
        WHERE creation >= DATE_SUB(NOW(), INTERVAL 6 MONTH)
        {branch_filter}
        GROUP BY month
        ORDER BY month ASC
    """.format(branch_filter=f"AND branch = {frappe.db.escape(branch)}" if branch else ""),
        as_dict=True
    )

    # Branch completed counts
    branch_completed = {}
    for r in all_requests:
        if r.status == "Completed" and r.branch:
            branch_completed[r.branch] = branch_completed.get(r.branch, 0) + 1

    # Asset completed counts
    asset_completed = {}
    for r in all_requests:
        if r.status == "Completed" and r.asset:
            asset_completed[r.asset] = asset_completed.get(r.asset, 0) + 1

    # Top assets with completed
    top_assets_full = [
        {"asset": a, "count": c, "completed": asset_completed.get(a, 0)}
        for a, c in top_assets
    ]

    # Monthly trend with completed
    monthly_completed = frappe.db.sql("""
        SELECT DATE_FORMAT(modified, '%%Y-%%m') AS month, COUNT(*) AS count
        FROM `tabMaintenance Request`
        WHERE status = 'Completed'
          AND modified >= DATE_SUB(NOW(), INTERVAL 6 MONTH)
        {branch_filter}
        GROUP BY month ORDER BY month ASC
    """.format(branch_filter=f"AND branch = {frappe.db.escape(branch)}" if branch else ""),
        as_dict=True)
    completed_map = {r.month: r.count for r in monthly_completed}
    for row in monthly_trend:
        row["completed"] = completed_map.get(row.month, 0)

    # Overdue list with age
    overdue_list = frappe.db.sql("""
        SELECT name, branch, asset, status, priority, assigned_to,
               DATEDIFF(CURDATE(), DATE(creation)) AS age_days,
               due_date
        FROM `tabMaintenance Request`
        WHERE status IN ('New','Assigned','In Progress','Waiting Parts')
          AND (due_date < CURDATE() OR DATEDIFF(CURDATE(), DATE(creation)) > 3)
        {branch_filter}
        ORDER BY age_days DESC
        LIMIT 20
    """.format(branch_filter=f"AND branch = {frappe.db.escape(branch)}" if branch else ""),
        as_dict=True)

    return {
        "status_counts":   status_counts,
        "priority_counts": priority_counts,
        "branch_faults":   branch_faults,
        "branch_completed": branch_completed,
        "sla": {
            "overdue": overdue_count,
            "at_risk": at_risk_count,
            "on_track": len([r for r in all_requests
                             if r.status in open_statuses
                             and r.due_date
                             and date_diff(r.due_date, today()) > 1]),
        },
        "top_assets":    top_assets_full,
        "tech_load":     [{"user": u, "count": c} for u, c in sorted(tech_load.items(), key=lambda x: x[1], reverse=True)],
        "total_cost":    total_cost,
        "total_requests": len(all_requests),
        "monthly_trend": monthly_trend,
        "overdue_list":  [dict(r) for r in overdue_list],
    }


@frappe.whitelist()
def get_kanban_data(branch=None):
    """Return requests grouped by kanban_column for board rendering."""
    filters = {"status": ["not in", ["Cancelled"]]}
    if branch: filters["branch"] = branch

    requests = frappe.get_list(
        "Maintenance Request",
        filters=filters,
        fields=["name","asset","branch","priority","status","kanban_column",
                "assigned_to","due_date","maintenance_type","description"],
        order_by="priority desc, due_date asc",
        limit_page_length=500,
    )

    columns = ["New","Assigned","In Progress","Waiting Parts","Awaiting Close","Completed"]
    board = {col: [] for col in columns}
    for req in requests:
        col = req.kanban_column or "New"
        if col in board:
            board[col].append(req)

    return {"columns": columns, "board": board}


@frappe.whitelist()
def get_maintenance_requests(branch=None, asset=None, status=None,
                              assigned_to=None, limit_page_length=20, limit_start=0):
    """Paginated list with permission scoping."""
    filters = {}
    if branch:      filters["branch"]      = branch
    if asset:       filters["asset"]       = asset
    if status:      filters["status"]      = status
    if assigned_to: filters["assigned_to"] = assigned_to

    requests = frappe.get_list(
        "Maintenance Request",
        filters=filters,
        fields=["name","asset","branch","maintenance_type","priority","status",
                "kanban_column","assigned_to","due_date","total_cost",
                "requested_by","requested_on","closed_on"],
        limit_page_length=int(limit_page_length),
        limit_start=int(limit_start),
        order_by="modified desc",
    )
    return {"data": requests, "total": len(requests)}


@frappe.whitelist()
def get_maintenance_request(name):
    doc = frappe.get_doc("Maintenance Request", name)
    frappe.has_permission("Maintenance Request", doc=doc, throw=True)
    return doc.as_dict()


@frappe.whitelist(methods=["POST"])
def transition_status(name, new_status):
    doc = frappe.get_doc("Maintenance Request", name)
    frappe.has_permission("Maintenance Request", "write", doc=doc, throw=True)
    return doc.transition_status(new_status)


@frappe.whitelist(methods=["POST"])
def add_work_log(maintenance_request, log_type, description, time_spent_hours=None):
    frappe.has_permission("Maintenance Work Log", "create", throw=True)
    wl = frappe.get_doc({
        "doctype": "Maintenance Work Log",
        "maintenance_request": maintenance_request,
        "log_type": log_type,
        "description": description,
        "time_spent_hours": time_spent_hours,
        "logged_by": frappe.session.user,
        "log_datetime": now(),
    })
    wl.insert()
    return {"name": wl.name, "status": "created"}


@frappe.whitelist()
def get_work_logs(maintenance_request):
    frappe.has_permission("Maintenance Request", "read",
        doc=frappe.get_doc("Maintenance Request", maintenance_request), throw=True)
    return {"data": frappe.get_all(
        "Maintenance Work Log",
        filters={"maintenance_request": maintenance_request},
        fields=["name","log_type","description","logged_by","log_datetime","time_spent_hours"],
        order_by="log_datetime desc",
    )}


@frappe.whitelist()
def get_spare_parts(maintenance_request):
    frappe.has_permission("Maintenance Request", "read",
        doc=frappe.get_doc("Maintenance Request", maintenance_request), throw=True)
    return {"data": frappe.get_all(
        "Spare Part Consumption",
        filters={"maintenance_request": maintenance_request},
        fields=["name","item_code","item_name","qty","uom","rate","amount","warehouse","stock_entry"],
        order_by="consumed_on desc",
    )}


@frappe.whitelist(methods=["POST"])
def add_meter_reading(asset, meter_value, uom, notes=None):
    frappe.has_permission("Asset Meter Reading", "create", throw=True)
    branch = frappe.db.get_value("Asset", asset, "branch")
    mr = frappe.get_doc({
        "doctype": "Asset Meter Reading",
        "asset": asset,
        "branch": branch,
        "meter_value": meter_value,
        "uom": uom,
        "reading_date": today(),
        "notes": notes,
    })
    mr.insert()
    return {"name": mr.name, "delta": mr.delta, "previous_reading": mr.previous_reading}


@frappe.whitelist()
def get_asset_maintenance_summary(asset=None, branch=None):
    filters = {}
    if asset:  filters["asset"]  = asset
    if branch: filters["branch"] = branch

    all_requests = frappe.get_list(
        "Maintenance Request", filters=filters,
        fields=["status","total_cost","due_date"],
    )
    status_counts = {}
    total_cost    = 0.0
    overdue_count = 0
    today_date    = getdate(today())

    for r in all_requests:
        status_counts[r.status] = status_counts.get(r.status, 0) + 1
        total_cost += flt(r.total_cost)
        if r.due_date and getdate(r.due_date) < today_date \
                and r.status not in ("Completed","Cancelled"):
            overdue_count += 1

    return {
        "status_counts":   status_counts,
        "total_cost":      total_cost,
        "overdue_count":   overdue_count,
        "total_requests":  len(all_requests),
    }


# ══════════════════════════════════════════════════════════════════════════════
# KNOWLEDGE BASE
# ══════════════════════════════════════════════════════════════════════════════

@frappe.whitelist()
def search_knowledge_base(query, asset_category=None):
    """Search the knowledge base by keyword."""
    filters = {"is_published": 1}
    if asset_category:
        filters["asset_category"] = asset_category

    results = frappe.get_all(
        "Maintenance Knowledge Base",
        filters=filters,
        fields=["name","title","asset_category","maintenance_type","views","helpful_votes"],
        or_filters={"title": ["like", f"%{query}%"], "tags": ["like", f"%{query}%"]},
        order_by="helpful_votes desc, views desc",
        limit_page_length=10,
    )
    return results


@frappe.whitelist(methods=["POST"])
def mark_kb_helpful(name):
    """Increment helpful vote on a Knowledge Base article."""
    current = frappe.db.get_value("Maintenance Knowledge Base", name, "helpful_votes") or 0
    frappe.db.set_value("Maintenance Knowledge Base", name, "helpful_votes", current + 1)
    frappe.db.commit()
    return {"helpful_votes": current + 1}
