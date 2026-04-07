frappe.pages["maintenance-dashboard"].on_page_load = function (wrapper) {
    const page = frappe.ui.make_app_page({
        parent: wrapper,
        title: "🔧 Maintenance Dashboard",
        single_column: true,
    });

    // ── Filters ──────────────────────────────────────────────────────────────
    const branch_field = page.add_field({
        fieldtype: "Link",
        fieldname: "branch",
        options: "Branch",
        label: "Branch",
        change() { load_dashboard(); }
    });

    const from_field = page.add_field({
        fieldtype: "Date",
        fieldname: "from_date",
        label: "From",
        default: frappe.datetime.add_months(frappe.datetime.nowdate(), -1),
        change() { load_dashboard(); }
    });

    const to_field = page.add_field({
        fieldtype: "Date",
        fieldname: "to_date",
        label: "To",
        default: frappe.datetime.nowdate(),
        change() { load_dashboard(); }
    });

    page.add_button(__("🔄 Refresh"), () => load_dashboard(), { btn_class: "btn-primary" });
    page.add_button(__("⬛ Kanban Board"), () =>
        frappe.set_route("List", "Maintenance Request", "kanban", "Maintenance Kanban"));
    page.add_button(__("📋 All Requests"), () =>
        frappe.set_route("List", "Maintenance Request"));

    // ── Layout ───────────────────────────────────────────────────────────────
    $(wrapper).find(".page-content").html(`
        <div id="amp-dashboard" style="padding:20px">

            <!-- KPI Cards Row -->
            <div id="amp-kpis" class="row mb-4"></div>

            <!-- SLA Summary -->
            <div class="row mb-4">
                <div class="col-md-4">
                    <div class="card h-100">
                        <div class="card-header"><b>⏱️ SLA Status</b></div>
                        <div class="card-body" id="amp-sla"></div>
                    </div>
                </div>
                <div class="col-md-8">
                    <div class="card h-100">
                        <div class="card-header"><b>📈 Monthly Trend</b></div>
                        <div class="card-body" id="amp-trend"></div>
                    </div>
                </div>
            </div>

            <!-- Status + Priority -->
            <div class="row mb-4">
                <div class="col-md-6">
                    <div class="card h-100">
                        <div class="card-header"><b>📊 Requests by Status</b></div>
                        <div class="card-body" id="amp-status-chart"></div>
                    </div>
                </div>
                <div class="col-md-6">
                    <div class="card h-100">
                        <div class="card-header"><b>🎯 Requests by Priority</b></div>
                        <div class="card-body" id="amp-priority-chart"></div>
                    </div>
                </div>
            </div>

            <!-- Heatmap + Top Assets -->
            <div class="row mb-4">
                <div class="col-md-6">
                    <div class="card h-100">
                        <div class="card-header"><b>🗺️ Faults Heatmap by Branch</b></div>
                        <div class="card-body" id="amp-heatmap"></div>
                    </div>
                </div>
                <div class="col-md-6">
                    <div class="card h-100">
                        <div class="card-header"><b>⚠️ Top Assets by Faults</b></div>
                        <div class="card-body" id="amp-top-assets"></div>
                    </div>
                </div>
            </div>

            <!-- Technician Load -->
            <div class="row mb-4">
                <div class="col-md-12">
                    <div class="card">
                        <div class="card-header"><b>👷 Technician Workload</b></div>
                        <div class="card-body" id="amp-tech-load"></div>
                    </div>
                </div>
            </div>

            <!-- Quick Links -->
            <div class="row mb-4">
                <div class="col-md-12">
                    <div class="card">
                        <div class="card-header"><b>⚡ Quick Actions</b></div>
                        <div class="card-body">
                            <div class="row text-center">
                                ${_quick_link("New Request", "Maintenance Request", "new", "#28a745")}
                                ${_quick_link("Open Requests", "Maintenance Request", "list?status=New", "#2490ef")}
                                ${_quick_link("Overdue", "Maintenance Request", "list?status=In Progress", "#e53e3e")}
                                ${_quick_link("Kanban", "kanban", "", "#805ad5", true)}
                                ${_quick_link("Knowledge Base", "Maintenance Knowledge Base", "list", "#6610f2")}
                                ${_quick_link("SLA Policies", "Maintenance SLA Policy", "list", "#e83e8c")}
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `);

    function _quick_link(label, doctype, action, color, is_kanban = false) {
        return `<div class="col-md-2 mb-2">
            <div class="amp-stat-card" style="cursor:pointer;border-top:3px solid ${color}"
                onclick="${is_kanban
                    ? "frappe.set_route('List','Maintenance Request','kanban','Maintenance Kanban')"
                    : `frappe.set_route('List','${doctype}')`
                }">
                <div style="font-size:1.5rem">${
                    {"New Request":"➕","Open Requests":"📋","Overdue":"⚠️",
                     "Kanban":"⬛","Knowledge Base":"📚","SLA Policies":"⏱️"}[label] || "📌"
                }</div>
                <div class="amp-stat-label mt-2">${label}</div>
            </div>
        </div>`;
    }

    // ── Load Dashboard ────────────────────────────────────────────────────────
    function load_dashboard() {
        const branch    = branch_field.get_value();
        const from_date = from_field.get_value();
        const to_date   = to_field.get_value();

        frappe.call({
            method: "asset_maintenance_pro.api.get_dashboard_data",
            args: { branch, from_date, to_date },
            freeze: true,
            freeze_message: __("Loading Dashboard..."),
            callback(r) {
                if (!r.message) return;
                const d = r.message;
                _render_kpis(d);
                _render_sla(d.sla);
                _render_status_chart(d.status_counts);
                _render_priority_chart(d.priority_counts);
                _render_heatmap(d.branch_faults);
                _render_top_assets(d.top_assets);
                _render_tech_load(d.tech_load);
                _render_trend(d.monthly_trend);
            }
        });
    }

    // ── KPI Cards ─────────────────────────────────────────────────────────────
    function _render_kpis(d) {
        const open = (d.status_counts["New"] || 0) +
                     (d.status_counts["Assigned"] || 0) +
                     (d.status_counts["In Progress"] || 0) +
                     (d.status_counts["Waiting Parts"] || 0) +
                     (d.status_counts["Awaiting Close"] || 0);

        const kpis = [
            { label: "Total Requests",  value: d.total_requests,                 color: "#2490ef", icon: "📋" },
            { label: "Open",            value: open,                              color: "#ff8c00", icon: "🔓" },
            { label: "Completed",       value: d.status_counts["Completed"] || 0, color: "#38a169", icon: "✅" },
            { label: "Overdue",         value: d.sla.overdue,                     color: "#e53e3e", icon: "⚠️" },
            { label: "At Risk (SLA)",   value: d.sla.at_risk,                     color: "#805ad5", icon: "⏰" },
            { label: "Total Cost",      value: `${frappe.format(d.total_cost, {fieldtype:"Currency"})}`, color: "#17a2b8", icon: "💰" },
        ];

        $("#amp-kpis").html(kpis.map(k => `
            <div class="col-md-2 mb-3">
                <div class="amp-stat-card" style="border-top:4px solid ${k.color}">
                    <div style="font-size:1.8rem">${k.icon}</div>
                    <div class="amp-stat-number" style="color:${k.color}">${k.value}</div>
                    <div class="amp-stat-label">${k.label}</div>
                </div>
            </div>
        `).join(""));
    }

    // ── SLA ───────────────────────────────────────────────────────────────────
    function _render_sla(sla) {
        const total = (sla.overdue || 0) + (sla.at_risk || 0) + (sla.on_track || 0);
        if (!total) { $("#amp-sla").html("<p class='text-muted'>No open requests</p>"); return; }

        const items = [
            { label: "✅ On Track",  count: sla.on_track, color: "#38a169", pct: Math.round(sla.on_track/total*100) },
            { label: "⏰ At Risk",   count: sla.at_risk,  color: "#ff8c00", pct: Math.round(sla.at_risk/total*100) },
            { label: "🚨 Breached",  count: sla.overdue,  color: "#e53e3e", pct: Math.round(sla.overdue/total*100) },
        ];

        $("#amp-sla").html(items.map(item => `
            <div class="mb-3">
                <div class="d-flex justify-content-between mb-1">
                    <span>${item.label}</span>
                    <b style="color:${item.color}">${item.count}</b>
                </div>
                <div class="amp-progress">
                    <div class="amp-progress-bar" style="width:${item.pct}%;background:${item.color}"></div>
                </div>
            </div>
        `).join(""));
    }

    // ── Status Chart ──────────────────────────────────────────────────────────
    function _render_status_chart(counts) {
        if (!Object.keys(counts).length) { $("#amp-status-chart").html("<p class='text-muted'>No data</p>"); return; }
        const colors = { "New":"#2490ef","Assigned":"#ff8c00","In Progress":"#f0b429",
                         "Waiting Parts":"#e53e3e","Awaiting Close":"#805ad5","Completed":"#38a169","Cancelled":"#a0aec0" };
        const labels = Object.keys(counts);
        const values = Object.values(counts);

        new frappe.Chart("#amp-status-chart", {
            type: "bar",
            data: {
                labels,
                datasets: [{ values, chartType: "bar" }]
            },
            colors: labels.map(l => colors[l] || "#a0aec0"),
            height: 200,
            axisOptions: { xIsSeries: false },
            tooltipOptions: { formatTooltipX: d => d, formatTooltipY: d => `${d} requests` },
        });
    }

    // ── Priority Chart ────────────────────────────────────────────────────────
    function _render_priority_chart(counts) {
        if (!Object.keys(counts).length) { $("#amp-priority-chart").html("<p class='text-muted'>No data</p>"); return; }
        const colors = { "Low":"#38a169","Medium":"#f0b429","High":"#ff8c00","Critical":"#e53e3e" };
        const order  = ["Critical","High","Medium","Low"];
        const labels = order.filter(k => counts[k]);
        const values = labels.map(k => counts[k]);

        new frappe.Chart("#amp-priority-chart", {
            type: "pie",
            data: { labels, datasets: [{ values }] },
            colors: labels.map(l => colors[l] || "#a0aec0"),
            height: 200,
        });
    }

    // ── Heatmap ───────────────────────────────────────────────────────────────
    function _render_heatmap(branch_faults) {
        const entries = Object.entries(branch_faults).sort((a, b) => b[1] - a[1]);
        if (!entries.length) { $("#amp-heatmap").html("<p class='text-muted'>No data</p>"); return; }
        const max = Math.max(...entries.map(e => e[1]));

        $("#amp-heatmap").html(`
            <div class="table-responsive">
                <table class="table table-sm">
                    <thead><tr><th>Branch</th><th>Faults</th><th>Heat</th></tr></thead>
                    <tbody>
                        ${entries.map(([branch, count]) => {
                            const pct  = Math.round(count / max * 100);
                            const heat = pct > 75 ? "#e53e3e" : pct > 50 ? "#ff8c00" : pct > 25 ? "#f0b429" : "#38a169";
                            return `<tr>
                                <td>${branch}</td>
                                <td><b>${count}</b></td>
                                <td>
                                    <div class="amp-progress" style="width:120px">
                                        <div class="amp-progress-bar" style="width:${pct}%;background:${heat}"></div>
                                    </div>
                                </td>
                            </tr>`;
                        }).join("")}
                    </tbody>
                </table>
            </div>
        `);
    }

    // ── Top Assets ────────────────────────────────────────────────────────────
    function _render_top_assets(assets) {
        if (!assets || !assets.length) { $("#amp-top-assets").html("<p class='text-muted'>No data</p>"); return; }
        const max = assets[0].count;

        $("#amp-top-assets").html(`
            ${assets.map((a, i) => {
                const pct  = Math.round(a.count / max * 100);
                const medal = i === 0 ? "🥇" : i === 1 ? "🥈" : i === 2 ? "🥉" : "  ";
                return `<div class="mb-2">
                    <div class="d-flex justify-content-between">
                        <span>${medal} <a href="#" onclick="frappe.set_route('List','Maintenance Request',{asset:'${a.asset}'})">${a.asset}</a></span>
                        <b>${a.count}</b>
                    </div>
                    <div class="amp-progress">
                        <div class="amp-progress-bar" style="width:${pct}%"></div>
                    </div>
                </div>`;
            }).join("")}
        `);
    }

    // ── Technician Load ───────────────────────────────────────────────────────
    function _render_tech_load(techs) {
        if (!techs || !techs.length) { $("#amp-tech-load").html("<p class='text-muted'>No open assignments</p>"); return; }
        const max = techs[0].count;

        $("#amp-tech-load").html(`
            <div class="row">
                ${techs.map(t => {
                    const pct   = Math.round(t.count / Math.max(max, 10) * 100);
                    const color = pct > 80 ? "#e53e3e" : pct > 60 ? "#ff8c00" : "#38a169";
                    return `<div class="col-md-4 mb-3">
                        <div class="d-flex justify-content-between mb-1">
                            <span>👷 ${t.user}</span>
                            <b style="color:${color}">${t.count} open</b>
                        </div>
                        <div class="amp-progress">
                            <div class="amp-progress-bar" style="width:${pct}%;background:${color}"></div>
                        </div>
                    </div>`;
                }).join("")}
            </div>
        `);
    }

    // ── Monthly Trend ─────────────────────────────────────────────────────────
    function _render_trend(trend) {
        if (!trend || !trend.length) { $("#amp-trend").html("<p class='text-muted'>No data</p>"); return; }

        new frappe.Chart("#amp-trend", {
            type: "line",
            data: {
                labels: trend.map(t => t.month),
                datasets: [{ name: "Requests", values: trend.map(t => t.count), chartType: "line" }]
            },
            colors: ["#2490ef"],
            height: 200,
            lineOptions: { hideDots: 0, regionFill: 1 },
            axisOptions: { xIsSeries: true },
        });
    }

    // ── Initial Load ──────────────────────────────────────────────────────────
    load_dashboard();
};
