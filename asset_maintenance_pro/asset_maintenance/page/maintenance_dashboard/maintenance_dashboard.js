frappe.pages["maintenance-dashboard"].on_page_load = function (wrapper) {
    const page = frappe.ui.make_app_page({
        parent: wrapper,
        title: "🔧 لوحة تحكم الصيانة",
        single_column: true,
    });

    // ── Filters ───────────────────────────────────────────────────────────────
    const branch_field = page.add_field({
        fieldtype: "Link", fieldname: "branch", options: "Branch",
        label: "الفرع", change() { load_dashboard(); }
    });
    const from_field = page.add_field({
        fieldtype: "Date", fieldname: "from_date", label: "من",
        default: frappe.datetime.add_months(frappe.datetime.nowdate(), -1),
        change() { load_dashboard(); }
    });
    const to_field = page.add_field({
        fieldtype: "Date", fieldname: "to_date", label: "إلى",
        default: frappe.datetime.nowdate(),
        change() { load_dashboard(); }
    });

    page.add_button(__("🔄 تحديث"), () => load_dashboard(), { btn_class: "btn-primary" });
    page.add_button(__("⬛ Kanban"), () => frappe.set_route("List","Maintenance Request","kanban","Maintenance Kanban"));
    page.add_button(__("📋 كل الطلبات"), () => frappe.set_route("List","Maintenance Request"));
    page.add_button(__("➕ طلب جديد"), () => frappe.new_doc("Maintenance Request"));

    // ── HTML Layout ───────────────────────────────────────────────────────────
    $(wrapper).find(".page-content").html(`
    <div id="amp-dash" style="padding:16px;direction:rtl">

      <!-- KPI Cards -->
      <div id="amp-kpis" class="row mb-3"></div>

      <!-- Row 2: Trend + Donut -->
      <div class="row mb-3">
        <div class="col-md-7">
          <div class="amp-card h-100">
            <div class="amp-card-title">مؤشر طلبات الصيانة خلال الفترة</div>
            <div id="amp-trend-chart" style="min-height:220px"></div>
          </div>
        </div>
        <div class="col-md-5">
          <div class="amp-card h-100">
            <div class="amp-card-title">طلبات الصيانة</div>
            <div id="amp-donut-chart" style="min-height:220px"></div>
            <div id="amp-donut-legend" class="d-flex flex-wrap justify-content-center mt-2" style="gap:8px"></div>
          </div>
        </div>
      </div>

      <!-- Row 3: Top Assets + Top Branches -->
      <div class="row mb-3">
        <div class="col-md-6">
          <div class="amp-card h-100">
            <div class="amp-card-title">الأجهزة الأكثر طلباً للصيانة مقابل اتمام الصيانة</div>
            <div id="amp-assets-chart" style="min-height:280px"></div>
          </div>
        </div>
        <div class="col-md-6">
          <div class="amp-card h-100">
            <div class="amp-card-title">الفروع الأكثر طلباً للصيانة مقابل اتمام الصيانة</div>
            <div id="amp-branches-chart" style="min-height:280px"></div>
          </div>
        </div>
      </div>

      <!-- Row 4: SLA + Technician Load -->
      <div class="row mb-3">
        <div class="col-md-4">
          <div class="amp-card h-100">
            <div class="amp-card-title">⏱️ حالة SLA</div>
            <div id="amp-sla-bars"></div>
          </div>
        </div>
        <div class="col-md-8">
          <div class="amp-card h-100">
            <div class="amp-card-title">👷 عبء الفنيين</div>
            <div id="amp-tech-chart" style="min-height:200px"></div>
          </div>
        </div>
      </div>

      <!-- Row 5: Overdue table -->
      <div class="row mb-3">
        <div class="col-md-12">
          <div class="amp-card">
            <div class="amp-card-title">🚨 الطلبات المتأخرة</div>
            <div id="amp-overdue-table"></div>
          </div>
        </div>
      </div>

    </div>
    `);

    // ── CSS ───────────────────────────────────────────────────────────────────
    frappe.dom.set_style(`
        .amp-card {
            background: #fff;
            border-radius: 12px;
            padding: 16px 20px;
            box-shadow: 0 2px 12px rgba(0,0,0,0.07);
            border: 1px solid #edf2f7;
            margin-bottom: 16px;
        }
        .amp-card-title {
            font-weight: 700;
            font-size: 13px;
            color: #2d3748;
            margin-bottom: 14px;
            padding-bottom: 8px;
            border-bottom: 1px solid #edf2f7;
        }
        .amp-kpi {
            background: #fff;
            border-radius: 12px;
            padding: 18px 20px;
            box-shadow: 0 2px 12px rgba(0,0,0,0.07);
            border: 1px solid #edf2f7;
            margin-bottom: 12px;
            text-align: center;
            transition: transform 0.2s;
            cursor: default;
        }
        .amp-kpi:hover { transform: translateY(-2px); box-shadow: 0 6px 20px rgba(0,0,0,0.12); }
        .amp-kpi-val { font-size: 2.2rem; font-weight: 800; line-height: 1.1; }
        .amp-kpi-lbl { font-size: 11px; color: #718096; margin-top: 4px; }
        .amp-bar-row { margin-bottom: 10px; }
        .amp-bar-label { font-size: 12px; color: #4a5568; margin-bottom: 3px; display:flex; justify-content:space-between; }
        .amp-bar-track { height: 10px; background: #edf2f7; border-radius: 5px; overflow: hidden; }
        .amp-bar-fill  { height: 100%; border-radius: 5px; transition: width 0.5s ease; }
        .amp-legend-dot { width:10px;height:10px;border-radius:50%;display:inline-block;margin-left:4px; }
        .amp-overdue-table table { width:100%; font-size:13px; border-collapse:collapse; }
        .amp-overdue-table th { background:#f7fafc;padding:8px 12px;text-align:right;font-weight:600;border-bottom:2px solid #e2e8f0; }
        .amp-overdue-table td { padding:8px 12px;border-bottom:1px solid #edf2f7; }
        .amp-overdue-table tr:hover td { background:#f7fafc; }
        .amp-badge { display:inline-block;padding:2px 8px;border-radius:10px;font-size:11px;font-weight:600; }
        .amp-stars { color:#f6ad55; font-size:14px; }
    `);

    // ── Load Dashboard ────────────────────────────────────────────────────────
    function load_dashboard() {
        const branch   = branch_field.get_value();
        const from_date = from_field.get_value();
        const to_date   = to_field.get_value();

        $("#amp-kpis").html(_skeleton(5, "col-md-2-4"));
        frappe.call({
            method: "asset_maintenance_pro.api.get_dashboard_data",
            args: { branch, from_date, to_date },
            callback(r) {
                if (!r.message) return;
                const d = r.message;
                _render_kpis(d);
                _render_trend(d.monthly_trend);
                _render_donut(d.status_counts);
                _render_assets_chart(d.top_assets);
                _render_branches_chart(d.branch_faults, d.branch_completed);
                _render_sla(d.sla);
                _render_tech(d.tech_load);
                _render_overdue(d.overdue_list);
            }
        });
    }

    // ── KPI Cards ─────────────────────────────────────────────────────────────
    function _render_kpis(d) {
        const open = (d.status_counts["New"]||0)+(d.status_counts["Assigned"]||0)+
                     (d.status_counts["In Progress"]||0)+(d.status_counts["Waiting Parts"]||0)+
                     (d.status_counts["Awaiting Close"]||0);

        const kpis = [
            { val: d.sla.overdue,                   lbl:"طلبات لم تأخذ إجراء\nلأكثر من 3 أيام", color:"#e53e3e", bg:"#fff5f5" },
            { val: d.total_requests,                 lbl:"الأجهزة - الكل",          color:"#2490ef", bg:"#ebf8ff" },
            { val: open,                             lbl:"الأجهزة - تم تعيينه لي",  color:"#d69e2e", bg:"#fffff0" },
            { val: d.total_requests,                 lbl:"اجمالي طلبات الصيانه",    color:"#38a169", bg:"#f0fff4" },
            { val: Object.keys(d.branch_faults||{}).length, lbl:"اجمالي الفروع",   color:"#6f42c1", bg:"#faf5ff" },
        ];

        $("#amp-kpis").html(kpis.map(k => `
            <div class="col" style="padding:0 6px">
                <div class="amp-kpi" style="border-top:4px solid ${k.color};background:${k.bg}">
                    <div class="amp-kpi-val" style="color:${k.color}">${k.val}</div>
                    <div class="amp-kpi-lbl">${k.lbl.replace("\n","<br>")}</div>
                </div>
            </div>
        `).join(""));
    }

    // ── Trend Chart ───────────────────────────────────────────────────────────
    function _render_trend(trend) {
        if (!trend || !trend.length) { $("#amp-trend-chart").html(_no_data()); return; }
        new frappe.Chart("#amp-trend-chart", {
            type: "line",
            data: {
                labels: trend.map(t => t.month),
                datasets: [
                    { name:"طلبات الصيانة", values: trend.map(t => t.count), chartType:"line" },
                    { name:"تم الحل",        values: trend.map(t => t.completed || 0), chartType:"line" },
                ]
            },
            colors: ["#e53e3e","#38a169"],
            height: 220,
            lineOptions: { hideDots: 0, regionFill: 0 },
            axisOptions: { xIsSeries: true },
        });
    }

    // ── Donut Chart ───────────────────────────────────────────────────────────
    function _render_donut(counts) {
        const color_map = {
            "New":"#e53e3e","Assigned":"#f6ad55","In Progress":"#f6e05e",
            "Waiting Parts":"#fc8181","Awaiting Close":"#9f7aea",
            "Completed":"#68d391","Cancelled":"#a0aec0"
        };
        const label_map = {
            "New":"جديدة","Assigned":"مخصصة","In Progress":"جارية",
            "Waiting Parts":"انتظار قطع","Awaiting Close":"انتظار إغلاق",
            "Completed":"تم الحل","Cancelled":"ملغاة"
        };

        const entries = Object.entries(counts).filter(([k,v]) => v > 0);
        if (!entries.length) { $("#amp-donut-chart").html(_no_data()); return; }

        const labels = entries.map(([k]) => label_map[k] || k);
        const values = entries.map(([k,v]) => v);
        const colors = entries.map(([k]) => color_map[k] || "#a0aec0");

        new frappe.Chart("#amp-donut-chart", {
            type: "donut",
            data: { labels, datasets: [{ values }] },
            colors,
            height: 200,
        });

        // Legend
        $("#amp-donut-legend").html(entries.map(([k,v]) => `
            <span style="font-size:12px;font-weight:600;background:${color_map[k]}22;
                         color:${color_map[k]};padding:3px 10px;border-radius:20px">
                ${label_map[k]||k}: ${v}
            </span>
        `).join(""));
    }

    // ── Assets Chart (horizontal bar: total vs completed) ─────────────────────
    function _render_assets_chart(assets) {
        if (!assets || !assets.length) { $("#amp-assets-chart").html(_no_data()); return; }
        const top10 = assets.slice(0, 10);
        const max   = top10[0].count;

        $("#amp-assets-chart").html(top10.map(a => `
            <div class="amp-bar-row">
                <div class="amp-bar-label">
                    <span>${a.asset}</span><span>${a.count}</span>
                </div>
                <div style="display:flex;align-items:center;gap:4px">
                    <div class="amp-bar-track" style="flex:1">
                        <div class="amp-bar-fill" style="width:${a.count/max*100}%;background:#e53e3e"></div>
                    </div>
                    <div class="amp-bar-track" style="width:${(a.completed||0)/max*100+10}%">
                        <div class="amp-bar-fill" style="width:100%;background:#38a169"></div>
                    </div>
                </div>
            </div>
        `).join("") + `
            <div style="display:flex;gap:16px;margin-top:10px;font-size:11px">
                <span><span class="amp-legend-dot" style="background:#e53e3e"></span> اجمالي طلبات الصيانة</span>
                <span><span class="amp-legend-dot" style="background:#38a169"></span> تم الحل</span>
            </div>
        `);
    }

    // ── Branches Chart ────────────────────────────────────────────────────────
    function _render_branches_chart(branch_faults, branch_completed) {
        const faults    = Object.entries(branch_faults || {}).sort((a,b) => b[1]-a[1]).slice(0,15);
        const completed = branch_completed || {};
        if (!faults.length) { $("#amp-branches-chart").html(_no_data()); return; }
        const max = faults[0][1];

        $("#amp-branches-chart").html(faults.map(([b,cnt]) => {
            const comp = completed[b] || 0;
            return `
                <div class="amp-bar-row">
                    <div class="amp-bar-label"><span>${b}</span><span>${cnt}</span></div>
                    <div style="display:flex;align-items:center;gap:4px">
                        <div class="amp-bar-track" style="flex:1">
                            <div class="amp-bar-fill" style="width:${cnt/max*100}%;background:#e53e3e"></div>
                        </div>
                        <div class="amp-bar-track" style="width:${comp/max*100+5}%">
                            <div class="amp-bar-fill" style="width:100%;background:#68d391"></div>
                        </div>
                    </div>
                </div>`;
        }).join("") + `
            <div style="display:flex;gap:16px;margin-top:10px;font-size:11px">
                <span><span class="amp-legend-dot" style="background:#e53e3e"></span> اجمالي طلبات الصيانة</span>
                <span><span class="amp-legend-dot" style="background:#68d391"></span> تم الحل</span>
            </div>
        `);
    }

    // ── SLA Bars ──────────────────────────────────────────────────────────────
    function _render_sla(sla) {
        const total = (sla.on_track||0) + (sla.at_risk||0) + (sla.overdue||0) || 1;
        const items = [
            { label:"✅ في الوقت",   count: sla.on_track, color:"#38a169" },
            { label:"⚠️ في خطر",    count: sla.at_risk,  color:"#d69e2e" },
            { label:"🚨 متأخر",      count: sla.overdue,  color:"#e53e3e" },
        ];
        $("#amp-sla-bars").html(items.map(item => `
            <div class="amp-bar-row">
                <div class="amp-bar-label">
                    <span>${item.label}</span>
                    <b style="color:${item.color}">${item.count}</b>
                </div>
                <div class="amp-bar-track">
                    <div class="amp-bar-fill" style="width:${Math.round((item.count||0)/total*100)}%;background:${item.color}"></div>
                </div>
            </div>
        `).join(""));
    }

    // ── Technician Load ───────────────────────────────────────────────────────
    function _render_tech(techs) {
        if (!techs || !techs.length) { $("#amp-tech-chart").html(_no_data()); return; }
        const max = techs[0].count || 1;
        $("#amp-tech-chart").html(`<div class="row">${
            techs.map(t => {
                const pct   = Math.round(t.count / max * 100);
                const color = pct > 80 ? "#e53e3e" : pct > 60 ? "#d69e2e" : "#38a169";
                return `<div class="col-md-4 mb-3">
                    <div class="amp-bar-label"><span>👷 ${t.user}</span><b>${t.count} مفتوح</b></div>
                    <div class="amp-bar-track">
                        <div class="amp-bar-fill" style="width:${pct}%;background:${color}"></div>
                    </div>
                </div>`;
            }).join("")
        }</div>`);
    }

    // ── Overdue Table ─────────────────────────────────────────────────────────
    function _render_overdue(list) {
        if (!list || !list.length) {
            $("#amp-overdue-table").html(`<p class="text-muted text-center py-3">✅ لا توجد طلبات متأخرة</p>`);
            return;
        }
        $("#amp-overdue-table").html(`
            <div class="amp-overdue-table">
                <table>
                    <thead>
                        <tr>
                            <th>رقم الطلب</th><th>الفرع</th><th>الجهاز</th>
                            <th>الحالة</th><th>الأولوية</th><th>متأخر منذ</th>
                            <th>مخصص لـ</th><th>تقييم العمل</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${list.map(r => {
                            const age     = r.age_days || 0;
                            const pri_col = r.priority === "Critical" ? "#e53e3e" : r.priority === "High" ? "#d69e2e" : "#4a5568";
                            const stars   = "★".repeat(r.rating||0) + "☆".repeat(5-(r.rating||0));
                            return `<tr>
                                <td><a href="/app/maintenance-request/${r.name}" target="_blank">${r.name}</a></td>
                                <td>${r.branch||"-"}</td>
                                <td>${r.asset||"-"}</td>
                                <td><span class="amp-badge" style="background:#fed7d7;color:#c53030">${r.status}</span></td>
                                <td><b style="color:${pri_col}">${r.priority||"-"}</b></td>
                                <td style="color:#e53e3e;font-weight:700">متأخر منذ: ${age} يوم</td>
                                <td>${r.assigned_to||"غير مخصص"}</td>
                                <td><span class="amp-stars">${stars}</span></td>
                            </tr>`;
                        }).join("")}
                    </tbody>
                </table>
            </div>
        `);
    }

    function _no_data() { return `<p class="text-muted text-center py-4" style="font-size:13px">لا توجد بيانات</p>`; }
    function _skeleton(n, cls) {
        return Array(n).fill(`<div class="${cls||'col-md-2'}" style="padding:0 6px">
            <div style="height:90px;background:#f0f0f0;border-radius:12px;animation:pulse 1.5s infinite"></div>
        </div>`).join("");
    }

    load_dashboard();
};
