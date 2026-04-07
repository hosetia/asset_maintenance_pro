/**
 * Asset Maintenance Pro — Global App JS
 * - Realtime notifications
 * - Kanban Board custom card renderer
 * - Dashboard page
 */

// ── Realtime Notifications ──────────────────────────────────────────────────
frappe.realtime.on("asset_maintenance_notification", (data) => {
    if (!data) return;
    frappe.show_alert({ message: data.subject || __("Maintenance update"), indicator: "blue" }, 8);
});

// ── Kanban Card Customization ───────────────────────────────────────────────
// Runs when user opens Kanban view on Maintenance Request
frappe.views.KanbanView = class AmpKanbanView extends frappe.views.KanbanView {
    get_column_header_html(column) {
        const icons = {
            "New": "🔵", "Assigned": "🟠", "In Progress": "🟡",
            "Waiting Parts": "🔴", "Awaiting Close": "🟣", "Completed": "🟢"
        };
        const icon = icons[column.column_name] || "⚪";
        return `<div class="kanban-column-title">
            ${icon} <b>${column.column_name}</b>
            <span class="badge badge-pill badge-light ml-2">${column.cards ? column.cards.length : 0}</span>
        </div>`;
    }
};

// ── Router: show Kanban button on Maintenance Request list ──────────────────
$(document).on("page-change", function () {
    setTimeout(() => {
        const route = frappe.get_route();
        if (route && route[0] === "List" && route[1] === "Maintenance Request") {
            if (!$(".amp-kanban-shortcut").length) {
                $(".page-actions .standard-actions").prepend(`
                    <button class="btn btn-sm btn-primary amp-kanban-shortcut mr-2"
                        onclick="frappe.set_route('List','Maintenance Request','kanban','Maintenance Kanban')">
                        ⬛ Kanban Board
                    </button>
                    <button class="btn btn-sm btn-default amp-dashboard-shortcut mr-2"
                        onclick="frappe.set_route('Page','maintenance-dashboard')">
                        📊 Dashboard
                    </button>
                `);
            }
        }
    }, 600);
});
