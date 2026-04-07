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
    ]

    rows = frappe.db.sql("""
        SELECT name AS asset, asset_name, branch, asset_category,
               custom_warranty_end AS warranty_end,
               DATEDIFF(custom_warranty_end, CURDATE()) AS days_left
        FROM `tabAsset`
        WHERE custom_warranty_end IS NOT NULL
          AND custom_warranty_end >= CURDATE()
          AND custom_warranty_end <= DATE_ADD(CURDATE(), INTERVAL {t} DAY)
        ORDER BY warranty_end ASC
    """.format(t=threshold), as_dict=True)

    data = []
    for r in rows:
        d = r.days_left or 0
        status = "< 30 days" if d < 30 else "30-60 days" if d < 60 else "60-90 days"
        data.append({
            "asset": r.asset, "asset_name": r.asset_name, "branch": r.branch,
            "asset_category": r.asset_category, "warranty_end": r.warranty_end,
            "days_left": d, "warranty_status": status,
        })
    return columns, data
