"""
Unit tests for Maintenance Request controller.
Run: bench --site your-site.local run-tests --app asset_maintenance_pro
"""

import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import add_days, today


class TestMaintenanceRequest(FrappeTestCase):

    def setUp(self):
        """Create test fixtures."""
        self._create_test_asset()

    def tearDown(self):
        frappe.db.rollback()

    def _create_test_asset(self):
        if not frappe.db.exists("Asset Category", "_Test Asset Category AMP"):
            cat = frappe.get_doc({
                "doctype": "Asset Category",
                "asset_category_name": "_Test Asset Category AMP",
                "enable_cwip_accounting": 0,
            })
            cat.insert(ignore_permissions=True)

        if not frappe.db.exists("Branch", "_Test Branch AMP"):
            branch = frappe.get_doc({"doctype": "Branch", "branch": "_Test Branch AMP"})
            branch.insert(ignore_permissions=True)

    def _make_request(self, **kwargs):
        defaults = {
            "doctype": "Maintenance Request",
            "asset": kwargs.pop("asset", None) or "_Test Asset",
            "branch": "_Test Branch AMP",
            "maintenance_type": "Corrective",
            "status": "New",
            "priority": "Medium",
            "description": "Test maintenance description",
        }
        defaults.update(kwargs)
        return frappe.get_doc(defaults)

    def test_status_syncs_kanban_column(self):
        """kanban_column must mirror status on every save."""
        mr = self._make_request()
        mr.status = "In Progress"
        mr.flags.ignore_permissions = True
        # Don't insert — just run validate
        mr._sync_kanban_column()
        self.assertEqual(mr.kanban_column, "In Progress")

    def test_completed_requires_total_cost(self):
        """Completing without total_cost should raise ValidationError."""
        mr = self._make_request()
        mr.status = "Completed"
        mr.completion_image = "/files/test.png"
        mr.total_cost = 0
        self.assertRaises(frappe.ValidationError, mr._validate_completion_fields)

    def test_completed_requires_completion_image(self):
        """Completing without completion_image should raise ValidationError."""
        mr = self._make_request()
        mr.status = "Completed"
        mr.total_cost = 500
        mr.completion_image = None
        self.assertRaises(frappe.ValidationError, mr._validate_completion_fields)

    def test_mandatory_checklist_blocks_completion(self):
        """All mandatory checklist items must be completed before status=Completed."""
        mr = self._make_request()
        mr.status = "Completed"
        mr.total_cost = 500
        mr.completion_image = "/files/done.png"
        mr.append("checklist", {
            "task": "Check oil level",
            "is_mandatory": 1,
            "completed": 0,
        })
        self.assertRaises(frappe.ValidationError, mr._validate_completion_fields)

    def test_mandatory_checklist_passes_when_done(self):
        """Completion allowed when all mandatory items are checked."""
        mr = self._make_request()
        mr.status = "Completed"
        mr.total_cost = 500
        mr.completion_image = "/files/done.png"
        mr.append("checklist", {
            "task": "Check oil level",
            "is_mandatory": 1,
            "completed": 1,
            "completed_by": "Administrator",
        })
        # Should not raise
        try:
            mr._validate_completion_fields()
            passed = True
        except frappe.ValidationError:
            passed = False
        self.assertTrue(passed)


class TestScheduler(FrappeTestCase):

    def test_generate_preventive_no_error(self):
        """Scheduler task should run without raising exceptions."""
        from asset_maintenance_pro.asset_maintenance.scheduler import (
            generate_preventive_maintenance_requests,
        )
        try:
            generate_preventive_maintenance_requests()
            passed = True
        except Exception:
            passed = False
        self.assertTrue(passed)
