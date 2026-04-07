/**
 * Maintenance Request — Client Script
 * Handles status transitions, quick actions, and form validation hints.
 */

frappe.ui.form.on("Maintenance Request", {

    // ── Setup ─────────────────────────────────────────────────────────────────

    setup(frm) {
        frm.set_query("asset", () => {
            const filters = {};
            if (frm.doc.branch) {
                filters.branch = frm.doc.branch;
            }
            return { filters };
        });

        frm.set_query("assigned_to", () => {
            return {
                query: "frappe.core.doctype.user.user.user_query",
                filters: { role: "Maintenance Technician" },
            };
        });
    },

    // ── Refresh ───────────────────────────────────────────────────────────────

    refresh(frm) {
        _add_status_indicator(frm);
        _add_action_buttons(frm);
        _toggle_completion_section(frm);
    },

    // ── Field events ──────────────────────────────────────────────────────────

    asset(frm) {
        if (frm.doc.asset) {
            frappe.db.get_value("Asset", frm.doc.asset, ["branch", "asset_name"], (r) => {
                if (r && r.branch) {
                    frm.set_value("branch", r.branch);
                }
            });
        }
    },

    status(frm) {
        _toggle_completion_section(frm);
        _add_status_indicator(frm);
    },

    assigned_to(frm) {
        if (frm.doc.assigned_to && frm.doc.status === "New") {
            frm.set_value("status", "Assigned");
        }
    },
});

// ── Child table events ────────────────────────────────────────────────────────

frappe.ui.form.on("Maintenance Request Checklist Item", {
    completed(frm, cdt, cdn) {
        const row = locals[cdt][cdn];
        if (row.completed) {
            frappe.model.set_value(cdt, cdn, "completed_by", frappe.session.user);
            frappe.model.set_value(cdt, cdn, "completed_on", frappe.datetime.now_datetime());
        } else {
            frappe.model.set_value(cdt, cdn, "completed_by", null);
            frappe.model.set_value(cdt, cdn, "completed_on", null);
        }
    },
});

// ── Helpers ───────────────────────────────────────────────────────────────────

function _add_status_indicator(frm) {
    const colors = {
        "New": "blue",
        "Assigned": "orange",
        "In Progress": "yellow",
        "Waiting Parts": "red",
        "Awaiting Close": "purple",
        "Completed": "green",
        "Cancelled": "gray",
    };
    frm.page.set_indicator(frm.doc.status, colors[frm.doc.status] || "gray");
}

function _add_action_buttons(frm) {
    if (frm.is_new()) return;

    const status = frm.doc.status;
    const roles = frappe.user_roles;
    const isManager = roles.includes("System Manager") || roles.includes("Branch Manager");
    const isTechnician = roles.includes("Maintenance Technician");

    // Kanban-style transition buttons in a group
    frm.remove_custom_button(__("Assign"), __("Actions"));
    frm.remove_custom_button(__("Start Work"), __("Actions"));
    frm.remove_custom_button(__("Request Parts"), __("Actions"));
    frm.remove_custom_button(__("Mark Awaiting Close"), __("Actions"));
    frm.remove_custom_button(__("Complete"), __("Actions"));
    frm.remove_custom_button(__("Cancel Request"), __("Actions"));

    if (status === "New" && isManager) {
        frm.add_custom_button(__("Assign"), () => _transition(frm, "Assigned"), __("Actions"));
    }

    if (status === "Assigned" && (isManager || isTechnician)) {
        frm.add_custom_button(__("Start Work"), () => _transition(frm, "In Progress"), __("Actions"));
    }

    if (status === "In Progress" && (isManager || isTechnician)) {
        frm.add_custom_button(__("Request Parts"), () => _transition(frm, "Waiting Parts"), __("Actions"));
        frm.add_custom_button(__("Mark Awaiting Close"), () => _transition(frm, "Awaiting Close"), __("Actions"));
    }

    if (status === "Waiting Parts" && (isManager || isTechnician)) {
        frm.add_custom_button(__("Resume Work"), () => _transition(frm, "In Progress"), __("Actions"));
    }

    if (status === "Awaiting Close" && isManager) {
        frm.add_custom_button(__("Complete"), () => _complete_request(frm), __("Actions"));
    }

    if (!["Completed", "Cancelled"].includes(status) && isManager) {
        frm.add_custom_button(__("Cancel Request"), () => _transition(frm, "Cancelled"), __("Actions"));
    }

    // Quick Add Work Log button (always visible for non-completed)
    if (!["Completed", "Cancelled"].includes(status)) {
        frm.add_custom_button(__("Add Work Log"), () => _quick_work_log(frm));
    }

    // View Work Logs
    frm.add_custom_button(__("Work Logs"), () => {
        frappe.set_route("List", "Maintenance Work Log", {
            maintenance_request: frm.doc.name,
        });
    }, __("View"));

    // View Spare Parts
    frm.add_custom_button(__("Spare Parts"), () => {
        frappe.set_route("List", "Spare Part Consumption", {
            maintenance_request: frm.doc.name,
        });
    }, __("View"));
}

function _toggle_completion_section(frm) {
    const show = frm.doc.status === "Awaiting Close" || frm.doc.status === "Completed";
    frm.toggle_reqd("total_cost", show);
    frm.toggle_reqd("completion_image", show);
}

function _transition(frm, new_status) {
    frappe.confirm(
        __("Move to <b>{0}</b>?", [new_status]),
        () => {
            frm.call("transition_status", { new_status }).then((r) => {
                if (r.message) {
                    frm.reload_doc();
                    frappe.show_alert({
                        message: __("Status updated to {0}", [new_status]),
                        indicator: "green",
                    });
                }
            });
        }
    );
}

function _complete_request(frm) {
    if (!frm.doc.total_cost || frm.doc.total_cost <= 0) {
        frappe.msgprint({
            message: __("Please fill in <b>Total Cost</b> before completing."),
            indicator: "red",
        });
        return;
    }
    if (!frm.doc.completion_image) {
        frappe.msgprint({
            message: __("Please attach a <b>Completion Image</b> before completing."),
            indicator: "red",
        });
        return;
    }
    _transition(frm, "Completed");
}

function _quick_work_log(frm) {
    const d = new frappe.ui.Dialog({
        title: __("Add Work Log"),
        fields: [
            {
                fieldname: "log_type",
                fieldtype: "Select",
                label: __("Log Type"),
                options: "Work Note\nParts Order\nInspection\nOther",
                default: "Work Note",
                reqd: 1,
            },
            {
                fieldname: "time_spent_hours",
                fieldtype: "Float",
                label: __("Time Spent (Hours)"),
            },
            {
                fieldname: "description",
                fieldtype: "Text Editor",
                label: __("Description"),
                reqd: 1,
            },
        ],
        primary_action_label: __("Save"),
        primary_action(values) {
            frappe.call({
                method: "asset_maintenance_pro.api.add_work_log",
                args: {
                    maintenance_request: frm.doc.name,
                    log_type: values.log_type,
                    description: values.description,
                    time_spent_hours: values.time_spent_hours,
                },
                freeze: true,
                callback(r) {
                    if (r.message) {
                        frappe.show_alert({ message: __("Work log added"), indicator: "green" });
                        d.hide();
                    }
                },
            });
        },
    });
    d.show();
}
