def execute(filters=None):
    filters = filters or {}
    status_filter = filters.get("status_filter") or "All"
    branch_filter = filters.get("branch") or ""
    from_date = filters.get("from_date") or frappe.utils.add_months(frappe.utils.today(), -1)
    to_date   = filters.get("to_date")   or frappe.utils.today()

    columns = [
        {"label":"رقم الطلب",        "fieldname":"name",                     "fieldtype":"Link",     "options":"Maintenance Request","width":160},
        {"label":"تاريخ الإنشاء",    "fieldname":"creation_date",            "fieldtype":"Date",     "width":110},
        {"label":"الفرع",            "fieldname":"branch",                   "fieldtype":"Link",     "options":"Branch","width":130},
        {"label":"الجهاز",           "fieldname":"asset",                    "fieldtype":"Link",     "options":"Asset","width":150},
        {"label":"نوع الصيانة",      "fieldname":"maintenance_type",         "fieldtype":"Data",     "width":110},
        {"label":"الأولوية",         "fieldname":"priority",                 "fieldtype":"Data",     "width":80},
        {"label":"الحالة",           "fieldname":"status",                   "fieldtype":"Data",     "width":120},
        {"label":"المعين إليه",      "fieldname":"assigned_to",              "fieldtype":"Link",     "options":"User","width":130},
        {"label":"تاريخ الاستحقاق", "fieldname":"due_date",                 "fieldtype":"Date",     "width":110},
        {"label":"تاريخ الإغلاق",   "fieldname":"closed_on",                "fieldtype":"Datetime", "width":140},
        {"label":"مدة الإنجاز (ساعة)","fieldname":"completion_duration_hours","fieldtype":"Float",   "width":140},
        {"label":"التكلفة",          "fieldname":"total_cost",               "fieldtype":"Currency", "width":110},
        {"label":"نوع الطلب",        "fieldname":"request_type",             "fieldtype":"Data",     "width":120},
        {"label":"وصف المشكلة",      "fieldname":"description_short",        "fieldtype":"Data",     "width":200},
    ]

    cond = "WHERE DATE(mr.creation) BETWEEN %(from_date)s AND %(to_date)s"
    params = {"from_date": from_date, "to_date": to_date}

    if branch_filter:
        cond += " AND mr.branch = %(branch)s"
        params["branch"] = branch_filter

    if status_filter == "Completed":
        cond += " AND mr.status = 'Completed'"
    elif status_filter == "Open":
        cond += " AND mr.status NOT IN ('Completed','Cancelled')"
    elif status_filter == "Overdue":
        cond += " AND mr.status NOT IN ('Completed','Cancelled') AND mr.due_date < CURDATE()"
    elif status_filter == "Cancelled":
        cond += " AND mr.status = 'Cancelled'"

    rows = frappe.db.sql(f"""
        SELECT mr.name, DATE(mr.creation) AS creation_date,
               mr.branch, mr.asset, mr.maintenance_type, mr.priority,
               mr.status, mr.assigned_to, mr.due_date, mr.closed_on,
               mr.completion_duration_hours, mr.total_cost,
               mr.request_type, LEFT(mr.description,80) AS description_short
        FROM `tabMaintenance Request` mr
        {cond}
        ORDER BY mr.creation DESC
    """, params, as_dict=True)

    data = [dict(r) for r in rows]

    # Totals
    total_cost  = sum(float(r.get("total_cost") or 0) for r in rows)
    total_hours = sum(float(r.get("completion_duration_hours") or 0) for r in rows)
    data.append({})
    data.append({
        "name": f"📊 الإجمالي: {len(rows)} طلب",
        "total_cost": total_cost,
        "completion_duration_hours": round(total_hours, 1),
    })
    return columns, data
