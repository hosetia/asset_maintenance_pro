/**
 * Asset — Custom Client Script (injected via doctype_js hook)
 * Adds a "Maintenance" quick-action button and shows maintenance stats.
 */

frappe.ui.form.on("Asset", {
    refresh(frm) {
        if (frm.is_new()) return;

        frm.add_custom_button(__("New Maintenance Request"), () => {
            frappe.new_doc("Maintenance Request", {
                asset: frm.doc.name,
                branch: frm.doc.branch,
            });
        }, __("Maintenance"));

        frm.add_custom_button(__("View Maintenance History"), () => {
            frappe.set_route("List", "Maintenance Request", { asset: frm.doc.name });
        }, __("Maintenance"));

        frm.add_custom_button(__("Add Meter Reading"), () => {
            frappe.new_doc("Asset Meter Reading", {
                asset: frm.doc.name,
                branch: frm.doc.branch,
            });
        }, __("Maintenance"));

        // Show open request count
        frappe.call({
            method: "asset_maintenance_pro.api.get_asset_maintenance_summary",
            args: { asset: frm.doc.name },
            callback(r) {
                if (r.message) {
                    const s = r.message;
                    const open = (s.status_counts["New"] || 0) +
                        (s.status_counts["Assigned"] || 0) +
                        (s.status_counts["In Progress"] || 0) +
                        (s.status_counts["Waiting Parts"] || 0);

                    if (open > 0) {
                        frm.dashboard.add_comment(
                            __("{0} open maintenance request(s) for this asset.", [open]),
                            "orange",
                            true
                        );
                    }
                    if (s.overdue_count > 0) {
                        frm.dashboard.add_comment(
                            __("{0} overdue maintenance request(s)!", [s.overdue_count]),
                            "red",
                            true
                        );
                    }
                }
            },
        });
    },
});
