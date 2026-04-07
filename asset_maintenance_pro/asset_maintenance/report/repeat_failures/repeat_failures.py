def execute(filters=None):
    filters = filters or {}
    period = int(filters.get("within_days") or 30)
    columns = [
        {"label":"Asset","fieldname":"asset","fieldtype":"Link","options":"Asset","width":180},
        {"label":"Branch","fieldname":"branch","fieldtype":"Data","width":120},
        {"label":"Category","fieldname":"asset_category","fieldtype":"Data","width":130},
        {"label":"Failures","fieldname":"failure_count","fieldtype":"Int","width":100},
        {"label":"Last Failure","fieldname":"last_failure","fieldtype":"Date","width":120},
        {"label":"Flag","fieldname":"repeat_flag","fieldtype":"Data","width":120},
    ]

    rows = frappe.db.sql("""
        SELECT mr.asset, mr.branch, a.asset_category,
               COUNT(*) AS failure_count,
               MAX(DATE(mr.creation)) AS last_failure
        FROM `tabMaintenance Request` mr
        LEFT JOIN `tabAsset` a ON a.name = mr.asset
        WHERE mr.maintenance_type='Corrective'
          AND mr.creation >= DATE_SUB(CURDATE(), INTERVAL {p} DAY)
          AND mr.asset IS NOT NULL AND mr.asset != ''
        GROUP BY mr.asset, mr.branch, a.asset_category
        HAVING failure_count > 1
        ORDER BY failure_count DESC
    """.format(p=period), as_dict=True)

    data = []
    for r in rows:
        n = r.failure_count or 0
        flag = "Critical (5+)" if n >= 5 else "High (3-4)" if n >= 3 else "Medium (2)"
        data.append({
            "asset": r.asset, "branch": r.branch,
            "asset_category": r.asset_category or "",
            "failure_count": n, "last_failure": r.last_failure, "repeat_flag": flag,
        })
    return columns, data
