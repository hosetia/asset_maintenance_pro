"""Patch: Seed default Asset Taxonomy codes (Symptom/Cause/Remedy/Failure)."""
import frappe

TAXONOMY = [
    # Symptoms
    ("SYM-001","Symptom","No Cooling","Refrigeration"),
    ("SYM-002","Symptom","Gas Smell",""),
    ("SYM-003","Symptom","Breaker Trip",""),
    ("SYM-004","Symptom","No Power",""),
    ("SYM-005","Symptom","Overheating",""),
    ("SYM-006","Symptom","Unusual Noise",""),
    ("SYM-007","Symptom","Water Leak","Plumbing"),
    ("SYM-008","Symptom","Fire Alarm Triggered","Fire Safety"),
    ("SYM-009","Symptom","Unit Not Starting",""),
    ("SYM-010","Symptom","Low Pressure","HVAC"),
    # Causes
    ("CAU-001","Cause","Compressor Failed","Refrigeration"),
    ("CAU-002","Cause","Thermostat Fault",""),
    ("CAU-003","Cause","Gas Leak",""),
    ("CAU-004","Cause","Power Fluctuation",""),
    ("CAU-005","Cause","Capacitor Failed",""),
    ("CAU-006","Cause","Dirty Coils","HVAC"),
    ("CAU-007","Cause","Fan Motor Failed",""),
    ("CAU-008","Cause","Wiring Issue",""),
    ("CAU-009","Cause","Misuse / Operator Error",""),
    ("CAU-010","Cause","Age / Normal Wear",""),
    # Remedies
    ("REM-001","Remedy","Replace Compressor",""),
    ("REM-002","Remedy","Replace Thermostat",""),
    ("REM-003","Remedy","Gas Recharge",""),
    ("REM-004","Remedy","Replace Capacitor",""),
    ("REM-005","Remedy","Clean Coils",""),
    ("REM-006","Remedy","Replace Fan Motor",""),
    ("REM-007","Remedy","Tighten Connections",""),
    ("REM-008","Remedy","Replace Breaker",""),
    ("REM-009","Remedy","Operator Retraining",""),
    ("REM-010","Remedy","Preventive Service",""),
    # Failure Classes
    ("FC-001","Failure Class","Electrical",""),
    ("FC-002","Failure Class","Mechanical",""),
    ("FC-003","Failure Class","Operational",""),
    ("FC-004","Failure Class","Cleaning",""),
    ("FC-005","Failure Class","External",""),
    ("FC-006","Failure Class","Age/Wear",""),
    ("FC-007","Failure Class","Misuse",""),
]

def execute():
    for code, ttype, desc, category in TAXONOMY:
        if not frappe.db.exists("Asset Taxonomy", code):
            doc = frappe.get_doc({
                "doctype": "Asset Taxonomy",
                "code": code,
                "taxonomy_type": ttype,
                "description": desc,
                "asset_category": category or None,
                "is_active": 1,
            })
            doc.flags.ignore_permissions = True
            doc.insert()
    frappe.db.commit()
    print(f"✅ {len(TAXONOMY)} taxonomy codes created")
