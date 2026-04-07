def execute(filters=None):
    filters = filters or {}
    columns = [
        {"label":"الجهاز",           "fieldname":"asset",         "fieldtype":"Link","options":"Asset","width":180},
        {"label":"اسم الجهاز",       "fieldname":"asset_name",    "fieldtype":"Data","width":160},
        {"label":"الفرع",            "fieldname":"branch",        "fieldtype":"Link","options":"Branch","width":120},
        {"label":"التصنيف",          "fieldname":"asset_category","fieldtype":"Data","width":130},
        {"label":"سعر الشراء",       "fieldname":"purchase_cost", "fieldtype":"Currency","width":120},
        {"label":"عمر الجهاز (سنة)", "fieldname":"age_years",     "fieldtype":"Float","width":120},
        {"label":"تكلفة الصيانة",   "fieldname":"maint_cost",    "fieldtype":"Currency","width":120},
        {"label":"تكلفة قطع الغيار","fieldname":"parts_cost",    "fieldtype":"Currency","width":130},
        {"label":"تكلفة الموردين",  "fieldname":"vendor_cost",   "fieldtype":"Currency","width":130},
        {"label":"TCO الإجمالي",     "fieldname":"tco",           "fieldtype":"Currency","width":130},
        {"label":"عدد الأعطال",      "fieldname":"fault_count",   "fieldtype":"Int","width":100},
        {"label":"التوصية",          "fieldname":"recommendation","fieldtype":"Data","width":150},
    ]

    assets = frappe.db.sql("""
        SELECT a.name AS asset, a.asset_name, a.asset_category,
               COALESCE(a.gross_purchase_amount,0) AS purchase_cost,
               TIMESTAMPDIFF(YEAR, a.purchase_date, CURDATE()) AS age_years
        FROM `tabAsset` a
        WHERE a.docstatus = 1
          AND (%(branch)s = '' OR a.branch = %(branch)s)
    """, {"branch": filters.get("branch") or ""}, as_dict=True)

    data = []
    for a in assets:
        branch = frappe.db.get_value("Asset", a.asset, "branch") or ""

        maint = frappe.db.sql("""
            SELECT SUM(COALESCE(total_cost,0)) AS maint_cost, COUNT(*) AS fault_count
            FROM `tabMaintenance Request`
            WHERE asset = %(asset)s AND status = 'Completed'
        """, {"asset": a.asset}, as_dict=True)

        parts = frappe.db.sql("""
            SELECT SUM(COALESCE(spc.amount,0)) AS parts_cost
            FROM `tabSpare Part Consumption` spc
            JOIN `tabMaintenance Request` mr ON mr.name = spc.maintenance_request
            WHERE mr.asset = %(asset)s
        """, {"asset": a.asset}, as_dict=True)

        vendor = frappe.db.sql("""
            SELECT SUM(COALESCE(total_cost,0)) AS vendor_cost
            FROM `tabMaintenance Work Order`
            WHERE asset = %(asset)s AND is_vendor_job=1 AND status IN ('Completed','Closed')
        """, {"asset": a.asset}, as_dict=True)

        purchase = float(a.purchase_cost or 0)
        maint_cost  = float(maint[0].maint_cost or 0)  if maint  else 0
        parts_cost  = float(parts[0].parts_cost or 0)  if parts  else 0
        vendor_cost = float(vendor[0].vendor_cost or 0) if vendor else 0
        tco = purchase + maint_cost + parts_cost + vendor_cost
        fault_count = maint[0].fault_count if maint else 0

        # Recommendation
        if purchase > 0 and (maint_cost + parts_cost) > purchase * 0.5:
            recommendation = "🔴 استبدال مقترح"
        elif fault_count >= 5:
            recommendation = "🟠 مراجعة شاملة"
        else:
            recommendation = "🟢 جيد"

        data.append({
            "asset": a.asset, "asset_name": a.asset_name,
            "branch": branch, "asset_category": a.asset_category,
            "purchase_cost": purchase,
            "age_years": float(a.age_years or 0),
            "maint_cost": maint_cost, "parts_cost": parts_cost,
            "vendor_cost": vendor_cost, "tco": tco,
            "fault_count": fault_count, "recommendation": recommendation,
        })

    data.sort(key=lambda x: x["tco"], reverse=True)
    return columns, data
