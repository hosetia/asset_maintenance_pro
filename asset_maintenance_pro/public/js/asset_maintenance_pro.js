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

// Add Kanban shortcut to navbar when on Maintenance Request list
frappe.router.on("change", () => {
    const route = frappe.get_route();
    if (route && route[0] === "List" && route[1] === "Maintenance Request") {
        setTimeout(() => {
            if (!$(".amp-kanban-btn").length) {
                $(".list-header-subject .list-filters-area").prepend(
                    `<button class="btn btn-sm btn-default amp-kanban-btn" 
                        onclick="frappe.set_route('Kanban', 'Maintenance Request', 'Maintenance Kanban')"
                        style="margin-right:8px;">
                        <i class="fa fa-columns"></i> ${__("Kanban Board")}
                    </button>`
                );
            }
        }, 500);
    }
});
