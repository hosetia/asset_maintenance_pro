/**
 * Asset Maintenance Pro — Global Desk JS
 * Handles real-time socket events for in-app notifications.
 */

frappe.realtime.on("asset_maintenance_notification", (data) => {
    if (!data) return;
    frappe.show_alert(
        {
            message: data.subject || __("Maintenance update"),
            indicator: "blue",
        },
        8
    );
});
