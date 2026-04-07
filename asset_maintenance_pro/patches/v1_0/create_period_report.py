"""Patch: Skip — report permissions handled by fixtures."""
import frappe

def execute():
    # Permissions are managed via report JSON fixtures — nothing to do here
    frappe.db.commit()
    print("✅ Skipped (handled by fixtures)")
