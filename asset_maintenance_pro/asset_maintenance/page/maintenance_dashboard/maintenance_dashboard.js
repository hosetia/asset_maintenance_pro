frappe.pages["maintenance-dashboard"].on_page_load = function (wrapper) {
    const page = frappe.ui.make_app_page({
        parent: wrapper,
        title: "🔧 لوحة تحكم الصيانة",
        single_column: true,
    });

    // ── Filters ───────────────────────────────────────────────────────────────
    const branch_field = page.add_field({
        fieldtype:"Link", fieldname:"branch", options:"Branch",
        label:"الفرع", change() { load_dashboard(); }
    });
    const from_field = page.add_field({
        fieldtype:"Date", fieldname:"from_date", label:"من",
        default: frappe.datetime.add_months(frappe.datetime.nowdate(), -1),
        change() { load_dashboard(); }
    });
    const to_field = page.add_field({
        fieldtype:"Date", fieldname:"to_date", label:"إلى",
        default: frappe.datetime.nowdate(),
        change() { load_dashboard(); }
    });

    // Buttons
    page.add_button("🔄 تحديث",      () => load_dashboard(),                                                            { btn_class:"btn-primary" });
    page.add_button("➕ طلب جديد",   () => frappe.new_doc("Maintenance Request"));
    page.add_button("📋 كل الطلبات", () => frappe.set_route("List","Maintenance Request"));
    page.add_button("⬛ Kanban",      () => frappe.set_route("List","Maintenance Request","kanban","Maintenance Kanban"));
    page.add_button("🗺️ Workspace",  () => frappe.set_route("Workspaces","Asset Maintenance Pro"));

    // ── CSS ───────────────────────────────────────────────────────────────────
    frappe.dom.set_style(`
        #amp-dash { padding:16px; direction:rtl; font-family:inherit; }
        .amp-card { background:#fff; border-radius:12px; padding:16px 20px;
            box-shadow:0 2px 12px rgba(0,0,0,.07); border:1px solid #edf2f7; margin-bottom:16px; }
        .amp-card-title { font-weight:700; font-size:13px; color:#2d3748;
            margin-bottom:14px; padding-bottom:8px; border-bottom:1px solid #edf2f7; }
        .amp-kpi { background:#fff; border-radius:12px; padding:18px 16px;
            box-shadow:0 2px 12px rgba(0,0,0,.07); text-align:center;
            transition:transform .2s; cursor:default; margin-bottom:12px; }
        .amp-kpi:hover { transform:translateY(-2px); box-shadow:0 6px 20px rgba(0,0,0,.12); }
        .amp-kpi-val { font-size:2rem; font-weight:800; line-height:1.1; }
        .amp-kpi-lbl { font-size:11px; color:#718096; margin-top:4px; }
        .amp-bar-row { margin-bottom:10px; }
        .amp-bar-label { font-size:12px; color:#4a5568; margin-bottom:3px;
            display:flex; justify-content:space-between; }
        .amp-bar-track { height:10px; background:#edf2f7; border-radius:5px; overflow:hidden; }
        .amp-bar-fill  { height:100%; border-radius:5px; transition:width .5s ease; }
        .amp-badge { display:inline-block; padding:2px 10px; border-radius:12px;
            font-size:11px; font-weight:700; }
        .amp-tbl table { width:100%; font-size:12px; border-collapse:collapse; }
        .amp-tbl th { background:#f7fafc; padding:8px 10px; text-align:right;
            font-weight:600; border-bottom:2px solid #e2e8f0; }
        .amp-tbl td { padding:7px 10px; border-bottom:1px solid #edf2f7; }
        .amp-tbl tr:hover td { background:#f7fafc; }
        .amp-quick-link { display:inline-block; padding:8px 16px; border-radius:8px;
            font-size:12px; font-weight:600; margin:4px; cursor:pointer;
            transition:all .2s; border:none; color:#fff; }
        .amp-quick-link:hover { opacity:.85; transform:translateY(-1px); }
    `);

    // ── Layout ────────────────────────────────────────────────────────────────
    $(wrapper).find(".page-content").html(`
    <div id="amp-dash">

      <!-- Quick Links Bar -->
      <div class="amp-card mb-3">
        <div class="amp-card-title">⚡ وصول سريع</div>
        <div id="amp-quick-links">
          ${_qlink("➕ طلب جديد",       "#28a745", "frappe.new_doc('Maintenance Request')")}
          ${_qlink("📋 كل الطلبات",     "#2490EF", "frappe.set_route('List','Maintenance Request')")}
          ${_qlink("⬛ Kanban",          "#6f42c1", "frappe.set_route('List','Maintenance Request','kanban','Maintenance Kanban')")}
          ${_qlink("🔧 أوامر العمل",    "#fd7e14", "frappe.set_route('List','Maintenance Work Order')")}
          ${_qlink("🔩 قطع الغيار",     "#17a2b8", "frappe.set_route('List','Spare Part Request')")}
          ${_qlink("🏢 الفحوصات",       "#dc3545", "frappe.set_route('List','Maintenance Inspection')")}
          ${_qlink("📜 عقود الخدمة",    "#805ad5", "frappe.set_route('List','Service Contract')")}
          ${_qlink("📚 قاعدة المعرفة",  "#6610f2", "frappe.set_route('List','Maintenance Knowledge Base')")}
        </div>
      </div>

      <!-- KPI Row -->
      <div id="amp-kpis" class="row mb-3"></div>

      <!-- Trend + Donut -->
      <div class="row mb-3">
        <div class="col-md-7">
          <div class="amp-card h-100">
            <div class="amp-card-title">📈 مؤشر طلبات الصيانة مقابل حل المشكلات</div>
            <div id="amp-trend"></div>
          </div>
        </div>
        <div class="col-md-5">
          <div class="amp-card h-100">
            <div class="amp-card-title">🔵 طلبات الصيانة حسب الحالة</div>
            <div id="amp-donut"></div>
            <div id="amp-donut-legend" class="d-flex flex-wrap justify-content-center mt-2" style="gap:6px"></div>
          </div>
        </div>
      </div>

      <!-- Top Assets + Top Branches -->
      <div class="row mb-3">
        <div class="col-md-6">
          <div class="amp-card h-100">
            <div class="amp-card-title">⚠️ الأجهزة الأكثر طلباً للصيانة مقابل الاتمام</div>
            <div id="amp-assets"></div>
          </div>
        </div>
        <div class="col-md-6">
          <div class="amp-card h-100">
            <div class="amp-card-title">🏢 الفروع الأكثر طلباً للصيانة مقابل الاتمام</div>
            <div id="amp-branches"></div>
          </div>
        </div>
      </div>

      <!-- SLA + Tech Load -->
      <div class="row mb-3">
        <div class="col-md-4">
          <div class="amp-card h-100">
            <div class="amp-card-title">⏱️ حالة SLA</div>
            <div id="amp-sla"></div>
          </div>
        </div>
        <div class="col-md-4">
          <div class="amp-card h-100">
            <div class="amp-card-title">🎯 الأولويات</div>
            <div id="amp-priority"></div>
          </div>
        </div>
        <div class="col-md-4">
          <div class="amp-card h-100">
            <div class="amp-card-title">👷 عبء الفنيين</div>
            <div id="amp-tech"></div>
          </div>
        </div>
      </div>

      <!-- Overdue Table -->
      <div class="row mb-3">
        <div class="col-md-12">
          <div class="amp-card">
            <div class="amp-card-title">🚨 الطلبات المتأخرة والمعلقة
              <a style="float:left;font-size:11px;font-weight:400" href="/app/maintenance-request">
                عرض الكل ←
              </a>
            </div>
            <div id="amp-overdue" class="amp-tbl"></div>
          </div>
        </div>
      </div>

      <!-- Cost Summary -->
      <div class="row mb-3">
        <div class="col-md-6">
          <div class="amp-card">
            <div class="amp-card-title">💰 ملخص التكاليف</div>
            <div id="amp-cost"></div>
          </div>
        </div>
        <div class="col-md-6">
          <div class="amp-card">
            <div class="amp-card-title">📊 إحصائيات سريعة</div>
            <div id="amp-stats"></div>
          </div>
        </div>
      </div>

    </div>`);

    function _qlink(label, color, onclick) {
        return `<button class="amp-quick-link" style="background:${color}"
            onclick="${onclick}">${label}</button>`;
    }

    // ── Load ──────────────────────────────────────────────────────────────────
    function load_dashboard() {
        const branch    = branch_field.get_value();
        const from_date = from_field.get_value();
        const to_date   = to_field.get_value();
        frappe.call({
            method: "asset_maintenance_pro.api.get_dashboard_data",
            args: { branch, from_date, to_date },
            freeze: true, freeze_message: "جاري التحميل...",
            callback(r) {
                if (!r.message) return;
                const d = r.message;
                _kpis(d);
                _trend(d.monthly_trend);
                _donut(d.status_counts);
                _assets(d.top_assets);
                _branches(d.branch_faults, d.branch_completed);
                _sla(d.sla);
                _priority(d.priority_counts);
                _tech(d.tech_load);
                _overdue(d.overdue_list);
                _cost(d);
                _stats(d);
            }
        });
    }

    // ── KPIs ──────────────────────────────────────────────────────────────────
    function _kpis(d) {
        const open = (d.status_counts["New"]||0)+(d.status_counts["Assigned"]||0)+
                     (d.status_counts["In Progress"]||0)+(d.status_counts["Waiting Parts"]||0)+
                     (d.status_counts["Awaiting Close"]||0);
        const completed = d.status_counts["Completed"] || 0;
        const branches_count = Object.keys(d.branch_faults||{}).length;

        const kpis = [
            { v: d.sla.overdue,     l:"طلبات لم تأخذ إجراء\nلأكثر من 3 أيام", c:"#e53e3e", bg:"#fff5f5", click:"frappe.set_route('List','Maintenance Request',{status:'In Progress'})" },
            { v: d.total_requests,  l:"إجمالي الطلبات\nالكل", c:"#2490ef", bg:"#ebf8ff", click:"frappe.set_route('List','Maintenance Request')" },
            { v: open,              l:"الطلبات المفتوحة\nجاري العمل", c:"#d69e2e", bg:"#fffff0", click:"frappe.set_route('List','Maintenance Request',{status:'In Progress'})" },
            { v: completed,         l:"إجمالي المنجز\nالفترة المحددة", c:"#38a169", bg:"#f0fff4", click:"frappe.set_route('List','Maintenance Request',{status:'Completed'})" },
            { v: branches_count,    l:"إجمالي الفروع\nالنشطة", c:"#6f42c1", bg:"#faf5ff", click:"frappe.set_route('List','Branch')" },
            { v: frappe.format(d.total_cost||0,{fieldtype:"Currency"}), l:"إجمالي التكاليف\nالفترة المحددة", c:"#17a2b8", bg:"#e6fffa", click:"" },
        ];
        $("#amp-kpis").html(kpis.map(k=>`
            <div class="col" style="padding:0 5px">
                <div class="amp-kpi" style="border-top:4px solid ${k.c};background:${k.bg}"
                    ${k.click ? `onclick="${k.click}" style="cursor:pointer;border-top:4px solid ${k.c};background:${k.bg}"` : ""}>
                    <div class="amp-kpi-val" style="color:${k.c}">${k.v}</div>
                    <div class="amp-kpi-lbl">${k.l.replace("\n","<br>")}</div>
                </div>
            </div>`).join(""));
    }

    // ── Trend ─────────────────────────────────────────────────────────────────
    function _trend(trend) {
        if (!trend?.length) { $("#amp-trend").html(_nodata()); return; }
        new frappe.Chart("#amp-trend", {
            type:"line",
            data:{ labels: trend.map(t=>t.month),
                datasets:[
                    {name:"طلبات الصيانة", values:trend.map(t=>t.count),     chartType:"line"},
                    {name:"تم الحل",        values:trend.map(t=>t.completed||0),chartType:"line"},
                ]},
            colors:["#e53e3e","#38a169"], height:220,
            lineOptions:{hideDots:0,regionFill:0},
            axisOptions:{xIsSeries:true},
        });
    }

    // ── Donut ─────────────────────────────────────────────────────────────────
    function _donut(counts) {
        const cmap = {"New":"#e53e3e","Assigned":"#f6ad55","In Progress":"#f6e05e",
            "Waiting Parts":"#fc8181","Awaiting Close":"#9f7aea","Completed":"#68d391","Cancelled":"#a0aec0"};
        const lmap = {"New":"جديدة","Assigned":"مخصصة","In Progress":"جارية",
            "Waiting Parts":"انتظار قطع","Awaiting Close":"انتظار إغلاق","Completed":"تم الحل","Cancelled":"ملغاة"};
        const entries = Object.entries(counts).filter(([,v])=>v>0);
        if (!entries.length) { $("#amp-donut").html(_nodata()); return; }
        new frappe.Chart("#amp-donut",{
            type:"donut",
            data:{labels:entries.map(([k])=>lmap[k]||k), datasets:[{values:entries.map(([,v])=>v)}]},
            colors:entries.map(([k])=>cmap[k]||"#a0aec0"), height:180,
        });
        $("#amp-donut-legend").html(entries.map(([k,v])=>`
            <span style="font-size:11px;font-weight:700;background:${cmap[k]}22;
                color:${cmap[k]};padding:2px 10px;border-radius:20px;border:1px solid ${cmap[k]}55">
                ${lmap[k]||k}: ${v}
            </span>`).join(""));
    }

    // ── Assets Bar ────────────────────────────────────────────────────────────
    function _assets(assets) {
        if (!assets?.length) { $("#amp-assets").html(_nodata()); return; }
        const top = assets.slice(0,10);
        const max = top[0].count || 1;
        $("#amp-assets").html(top.map(a=>`
            <div class="amp-bar-row">
                <div class="amp-bar-label">
                    <span style="overflow:hidden;white-space:nowrap;max-width:60%">${a.asset}</span>
                    <span><b>${a.count}</b> / <small style="color:#38a169">${a.completed||0} ✓</small></span>
                </div>
                <div style="display:flex;gap:3px">
                    <div class="amp-bar-track" style="flex:1">
                        <div class="amp-bar-fill" style="width:${a.count/max*100}%;background:#e53e3e"></div>
                    </div>
                    <div class="amp-bar-track" style="width:${Math.max((a.completed||0)/max*100,2)}%">
                        <div class="amp-bar-fill" style="width:100%;background:#38a169"></div>
                    </div>
                </div>
            </div>`).join("")+_legend());
    }

    // ── Branches Bar ──────────────────────────────────────────────────────────
    function _branches(faults, completed) {
        const entries = Object.entries(faults||{}).sort((a,b)=>b[1]-a[1]).slice(0,15);
        const comp    = completed || {};
        if (!entries.length) { $("#amp-branches").html(_nodata()); return; }
        const max = entries[0][1] || 1;
        $("#amp-branches").html(entries.map(([b,cnt])=>`
            <div class="amp-bar-row">
                <div class="amp-bar-label">
                    <span style="overflow:hidden;white-space:nowrap;max-width:60%">${b}</span>
                    <span><b>${cnt}</b> / <small style="color:#38a169">${comp[b]||0} ✓</small></span>
                </div>
                <div style="display:flex;gap:3px">
                    <div class="amp-bar-track" style="flex:1">
                        <div class="amp-bar-fill" style="width:${cnt/max*100}%;background:#e53e3e"></div>
                    </div>
                    <div class="amp-bar-track" style="width:${Math.max((comp[b]||0)/max*100,2)}%">
                        <div class="amp-bar-fill" style="width:100%;background:#68d391"></div>
                    </div>
                </div>
            </div>`).join("")+_legend());
    }

    // ── SLA ───────────────────────────────────────────────────────────────────
    function _sla(sla) {
        const total=(sla.on_track||0)+(sla.at_risk||0)+(sla.overdue||0)||1;
        [["✅ في الوقت",sla.on_track,"#38a169"],["⚠️ في خطر",sla.at_risk,"#d69e2e"],
         ["🚨 متأخر",sla.overdue,"#e53e3e"]].forEach(([lbl,cnt,color])=>{
            $("#amp-sla").append(`
                <div class="amp-bar-row">
                    <div class="amp-bar-label"><span>${lbl}</span><b style="color:${color}">${cnt||0}</b></div>
                    <div class="amp-bar-track">
                        <div class="amp-bar-fill" style="width:${Math.round((cnt||0)/total*100)}%;background:${color}"></div>
                    </div>
                </div>`);
        });
    }

    // ── Priority ──────────────────────────────────────────────────────────────
    function _priority(counts) {
        const cmap={"Critical":"#e53e3e","High":"#fd7e14","Medium":"#d69e2e","Low":"#38a169"};
        const lmap={"Critical":"حرج","High":"عالي","Medium":"متوسط","Low":"منخفض"};
        const order=["Critical","High","Medium","Low"];
        const total=Object.values(counts||{}).reduce((a,b)=>a+b,0)||1;
        order.filter(k=>counts[k]).forEach(k=>{
            $("#amp-priority").append(`
                <div class="amp-bar-row">
                    <div class="amp-bar-label"><span>${lmap[k]}</span><b style="color:${cmap[k]}">${counts[k]}</b></div>
                    <div class="amp-bar-track">
                        <div class="amp-bar-fill" style="width:${Math.round(counts[k]/total*100)}%;background:${cmap[k]}"></div>
                    </div>
                </div>`);
        });
    }

    // ── Tech Load ─────────────────────────────────────────────────────────────
    function _tech(techs) {
        if (!techs?.length) { $("#amp-tech").html(_nodata()); return; }
        const max=techs[0].count||1;
        $("#amp-tech").html(techs.map(t=>{
            const pct=Math.round(t.count/max*100);
            const color=pct>80?"#e53e3e":pct>60?"#d69e2e":"#38a169";
            return `<div class="amp-bar-row">
                <div class="amp-bar-label"><span>👷 ${t.user}</span><b style="color:${color}">${t.count}</b></div>
                <div class="amp-bar-track"><div class="amp-bar-fill" style="width:${pct}%;background:${color}"></div></div>
            </div>`;
        }).join(""));
    }

    // ── Overdue Table ─────────────────────────────────────────────────────────
    function _overdue(list) {
        if (!list?.length) { $("#amp-overdue").html(`<p class="text-muted text-center py-3">✅ لا توجد طلبات متأخرة</p>`); return; }
        const priColor={"Critical":"#e53e3e","High":"#fd7e14","Medium":"#d69e2e","Low":"#38a169"};
        $("#amp-overdue").html(`<table>
            <thead><tr>
                <th>رقم الطلب</th><th>الفرع</th><th>الجهاز</th>
                <th>الحالة</th><th>الأولوية</th><th>متأخر (يوم)</th><th>مخصص لـ</th>
            </tr></thead>
            <tbody>${list.map(r=>`<tr>
                <td><a href="/app/maintenance-request/${r.name}" target="_blank">${r.name}</a></td>
                <td>${r.branch||"-"}</td><td>${r.asset||"-"}</td>
                <td><span class="amp-badge" style="background:#fed7d7;color:#c53030">${r.status}</span></td>
                <td><b style="color:${priColor[r.priority]||"#4a5568"}">${r.priority||"-"}</b></td>
                <td style="color:#e53e3e;font-weight:700">${r.age_days} يوم</td>
                <td>${r.assigned_to||"<span style='color:#e53e3e'>غير مخصص</span>"}</td>
            </tr>`).join("")}</tbody>
        </table>`);
    }

    // ── Cost Summary ──────────────────────────────────────────────────────────
    function _cost(d) {
        const items=[
            ["💰 إجمالي التكاليف", frappe.format(d.total_cost||0,{fieldtype:"Currency"}),"#17a2b8"],
            ["✅ تكلفة المنجز",    frappe.format(d.total_cost||0,{fieldtype:"Currency"}),"#38a169"],
            ["📊 متوسط التكلفة/طلب",
             d.total_requests ? frappe.format((d.total_cost||0)/d.total_requests,{fieldtype:"Currency"}) : "0",
             "#6f42c1"],
        ];
        $("#amp-cost").html(items.map(([l,v,c])=>`
            <div style="display:flex;justify-content:space-between;padding:10px 0;
                border-bottom:1px solid #edf2f7;font-size:13px">
                <span>${l}</span>
                <b style="color:${c}">${v}</b>
            </div>`).join(""));
    }

    // ── Quick Stats ───────────────────────────────────────────────────────────
    function _stats(d) {
        const open=(d.status_counts["New"]||0)+(d.status_counts["Assigned"]||0)+
                   (d.status_counts["In Progress"]||0)+(d.status_counts["Waiting Parts"]||0);
        const comp=d.status_counts["Completed"]||0;
        const total=d.total_requests||1;
        const items=[
            ["📈 معدل الإنجاز",   `${Math.round(comp/total*100)}%`,     "#38a169"],
            ["⏳ الطلبات المفتوحة",`${open}`,                            "#fd7e14"],
            ["🔴 الحرجة",         `${d.priority_counts?.Critical||0}`,  "#e53e3e"],
            ["🏢 عدد الفروع",     `${Object.keys(d.branch_faults||{}).length}`,"#6f42c1"],
        ];
        $("#amp-stats").html(items.map(([l,v,c])=>`
            <div style="display:flex;justify-content:space-between;padding:10px 0;
                border-bottom:1px solid #edf2f7;font-size:13px">
                <span>${l}</span>
                <b style="color:${c};font-size:15px">${v}</b>
            </div>`).join(""));
    }

    function _legend() {
        return `<div style="display:flex;gap:12px;margin-top:8px;font-size:11px">
            <span>🔴 إجمالي الطلبات</span><span>🟢 تم الحل</span>
        </div>`;
    }
    function _nodata() { return `<p class="text-muted text-center py-3" style="font-size:13px">لا توجد بيانات</p>`; }

    load_dashboard();
};
