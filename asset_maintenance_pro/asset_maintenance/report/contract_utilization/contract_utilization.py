def execute(filters=None):
    filters = filters or {}
    columns = [
        {"label":"Contract","fieldname":"contract","fieldtype":"Link","options":"Service Contract","width":180},
        {"label":"Vendor","fieldname":"vendor","fieldtype":"Link","options":"Supplier","width":160},
        {"label":"Type","fieldname":"contract_type","fieldtype":"Data","width":110},
        {"label":"Status","fieldname":"status","fieldtype":"Data","width":110},
        {"label":"Days Remaining","fieldname":"days_remaining","fieldtype":"Int","width":130},
        {"label":"Visits Included","fieldname":"visits_included","fieldtype":"Int","width":130},
        {"label":"Visits Used","fieldname":"visits_used","fieldtype":"Int","width":110},
        {"label":"Visits Remaining","fieldname":"visits_remaining","fieldtype":"Int","width":130},
        {"label":"Utilization %","fieldname":"utilization_pct","fieldtype":"Float","width":120},
        {"label":"Annual Value","fieldname":"annual_value","fieldtype":"Currency","width":120},
    ]

    contracts = frappe.get_all("Service Contract",
        fields=["name","vendor","contract_type","status","end_date",
                "included_visits_per_year","visits_used","annual_value"]
    )
    data = []
    for c in contracts:
        days_rem = frappe.utils.date_diff(c.end_date, frappe.utils.today()) if c.end_date else 0
        included = c.included_visits_per_year or 0
        used     = c.visits_used or 0
        util_pct = round(used / included * 100, 1) if included else 0
        data.append({
            "contract": c.name, "vendor": c.vendor,
            "contract_type": c.contract_type, "status": c.status,
            "days_remaining": max(0, days_rem),
            "visits_included": included, "visits_used": used,
            "visits_remaining": max(0, included - used),
            "utilization_pct": util_pct,
            "annual_value": float(c.annual_value or 0),
        })
    data.sort(key=lambda x: x["days_remaining"])
    return columns, data
