/**
 * Maintenance Request — Smart Client Script v4.0
 * - Role-based form (Requester / Technician / Manager)
 * - Asset info card with warranty status
 * - Previous maintenance history
 * - Kanban card with delay + duration
 * - Comments for all roles
 */

const STATUS_COLORS = {
    "New":"blue","Assigned":"orange","In Progress":"yellow",
    "Waiting Parts":"red","Awaiting Close":"purple","Completed":"green","Cancelled":"gray"
};
const PRIORITY_COLORS = { "Low":"#38a169","Medium":"#d69e2e","High":"#e53e3e","Critical":"#822727" };

frappe.ui.form.on("Maintenance Request", {

    setup(frm) {
        frm.set_query("asset", () => ({
            filters: { docstatus: 1, ...(frm.doc.branch ? { branch: frm.doc.branch } : {}) }
        }));
        frm.set_query("assigned_to", () => ({
            query: "asset_maintenance_pro.api.get_technicians",
            filters: { branch: frm.doc.branch || "" }
        }));
        frm.set_query("symptom_code", () => ({ filters: { taxonomy_type: "Symptom" } }));
        frm.set_query("cause_code",   () => ({ filters: { taxonomy_type: "Cause"   } }));
        frm.set_query("remedy_code",  () => ({ filters: { taxonomy_type: "Remedy"  } }));
    },

    refresh(frm) {
        const roles       = frappe.user_roles;
        const isRequester = _is_requester_only(roles);
        const isMgr       = roles.includes("System Manager") || roles.includes("Branch Manager") || roles.includes("Maintenance Coordinator");
        const isTech      = roles.includes("Maintenance Technician");

        frm.page.set_indicator(frm.doc.status, STATUS_COLORS[frm.doc.status] || "gray");

        _apply_role_visibility(frm, isRequester, isMgr, isTech);
        _render_asset_info_card(frm);
        _setup_dashboard(frm);
        _show_sla_countdown(frm);
        _show_completion_duration(frm);

        if (!isRequester) _setup_action_buttons(frm, isMgr, isTech);
        if (frm.is_new()) _autofill_branch(frm);

        // Enable comments for ALL roles
        frm.comment_box && frm.comment_box.refresh();
    },

    asset(frm) {
        if (!frm.doc.asset) {
            frm.set_value("asset_info_html", "");
            return;
        }
        frappe.call({
            method: "asset_maintenance_pro.api.get_asset_full_details",
            args: { asset: frm.doc.asset },
            callback(r) {
                if (!r.message) return;
                const d = r.message;
                if (d.branch) frm.set_value("branch", d.branch);
                frm.set_value("warranty_status", d.warranty_status);
                frm.set_value("previous_requests_count", d.previous_requests_count);
                _render_asset_card_html(frm, d);
            }
        });
    },

    branch(frm) {
        frm.set_value("asset", "");
        frm.refresh_field("asset");
    },

    assigned_to(frm) {
        if (frm.doc.assigned_to && frm.doc.status === "New")
            frm.set_value("status", "Assigned");
    },

    status(frm) {
        frm.page.set_indicator(frm.doc.status, STATUS_COLORS[frm.doc.status] || "gray");
        _toggle_completion_fields(frm);
        if (frm.doc.status === "Completed") _show_completion_duration(frm);
    },

    description(frm) {
        if (frm.doc.description && frm.doc.description.length > 10)
            _suggest_maintenance_type(frm);
    },
});

frappe.ui.form.on("Maintenance Request Checklist Item", {
    completed(frm, cdt, cdn) {
        const row = locals[cdt][cdn];
        frappe.model.set_value(cdt, cdn, "completed_by", row.completed ? frappe.session.user : null);
        frappe.model.set_value(cdt, cdn, "completed_on", row.completed ? frappe.datetime.now_datetime() : null);
        _update_checklist_progress(frm);
    }
});

// ── Role Detection ────────────────────────────────────────────────────────────
function _is_requester_only(roles) {
    return !["System Manager","Branch Manager","Maintenance Coordinator","Maintenance Technician"]
        .some(r => roles.includes(r));
}

// ── Role-Based Visibility ─────────────────────────────────────────────────────
function _apply_role_visibility(frm, isRequester, isMgr, isTech) {
    const REQUESTER_HIDDEN = [
        "maintenance_type","priority","kanban_column","assigned_to","due_date",
        "checklist","total_cost","completion_image","completion_notes",
        "symptom_code","cause_code","remedy_code","failure_class",
        "downtime_start","downtime_end","triage_by","verified_by",
        "request_type","reference_meter_reading","preventive_schedule",
        "closed_by","closed_on","completion_duration_hours","section_break_completion",
    ];
    const TECH_HIDDEN = [
        "total_cost","completion_image","assigned_to","triage_by","verified_by","closed_by",
    ];

    if (isRequester) {
        REQUESTER_HIDDEN.forEach(f => { try { frm.set_df_property(f,"hidden",1); } catch(e){} });
        frm.set_df_property("status","read_only",1);
        if (frm.is_new()) frm.set_intro(
            __("📝 حدد الجهاز، اشرح المشكلة، وأرفق صورة — فريق الصيانة سيتولى الباقي."), "blue");
    } else if (isTech && !isMgr) {
        TECH_HIDDEN.forEach(f => { try { frm.set_df_property(f,"hidden",1); } catch(e){} });
        _toggle_completion_fields(frm);
    } else {
        // Manager: show everything
        [...REQUESTER_HIDDEN, ...TECH_HIDDEN].forEach(f => {
            try { frm.set_df_property(f,"hidden",0); } catch(e){}
        });
        _toggle_completion_fields(frm);
    }
}

function _toggle_completion_fields(frm) {
    const roles = frappe.user_roles;
    const isMgr = roles.includes("System Manager") || roles.includes("Branch Manager") || roles.includes("Maintenance Coordinator");
    const show  = ["Awaiting Close","Completed"].includes(frm.doc.status) && isMgr;
    frm.toggle_reqd("total_cost",       show);
    frm.toggle_reqd("completion_image", show);
}

// ── Asset Info Card ───────────────────────────────────────────────────────────
function _render_asset_info_card(frm) {
    if (!frm.doc.asset || frm.is_new()) return;
    frappe.call({
        method: "asset_maintenance_pro.api.get_asset_full_details",
        args: { asset: frm.doc.asset },
        callback(r) {
            if (r.message) _render_asset_card_html(frm, r.message);
        }
    });
}

function _render_asset_card_html(frm, d) {
    const warrantyColor = d.warranty_status === "ضمان ساري" ? "#38a169" :
                          d.warranty_status === "ضمان منتهي" ? "#e53e3e" : "#a0aec0";

    const prevCount = d.previous_requests_count || 0;

    const html = `
    <div style="background:linear-gradient(135deg,#f0f4ff,#e8f0fe);border-radius:10px;
                padding:14px 18px;margin:10px 0;font-size:13px;line-height:2;direction:rtl">

        <div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:8px">

            <!-- Asset Identity -->
            <div>
                <div style="font-weight:700;font-size:15px;color:#2d3748">
                    📦 ${d.asset_name || d.asset}
                    <span style="font-size:11px;color:#718096;font-weight:400;margin-right:8px">
                        (${d.asset})
                    </span>
                </div>
                <div style="color:#4a5568">
                    ${d.asset_category ? `📁 ${d.asset_category} &nbsp;|&nbsp;` : ""}
                    ${d.location ? `📍 ${d.location} &nbsp;|&nbsp;` : ""}
                    ${d.manufacturer ? `🏭 ${d.manufacturer} &nbsp;|&nbsp;` : ""}
                    ${d.model ? `🔖 ${d.model}` : ""}
                </div>
            </div>

            <!-- Warranty Badge -->
            <div style="text-align:center">
                <div style="background:${warrantyColor}22;color:${warrantyColor};
                            font-weight:700;padding:6px 16px;border-radius:20px;
                            border:1px solid ${warrantyColor};font-size:12px">
                    🛡️ ${d.warranty_status || "لا يوجد ضمان"}
                </div>
                ${d.warranty_end ? `<div style="font-size:11px;color:#718096;margin-top:2px">ينتهي: ${d.warranty_end}</div>` : ""}
            </div>
        </div>

        <hr style="margin:8px 0;border-color:#e2e8f0">

        <div style="display:flex;gap:24px;flex-wrap:wrap">
            <div>
                🔧 <b>آخر صيانة:</b>
                ${d.last_maintenance
                    ? frappe.datetime.str_to_user(d.last_maintenance)
                    : "<span style='color:#e53e3e'>لا يوجد تاريخ</span>"}
            </div>
            <div>
                📊 <b>الصيانات السابقة:</b>
                <span style="background:#fed7d7;color:#c53030;padding:1px 8px;
                             border-radius:10px;font-weight:700">${prevCount}</span>
            </div>
            <div>
                ⚡ <b>الأهمية:</b>
                <span style="font-weight:700;color:${
                    d.criticality === "A - Critical" ? "#e53e3e" :
                    d.criticality === "B - Important" ? "#d69e2e" : "#38a169"
                }">${d.criticality || "غير محدد"}</span>
            </div>
            ${d.serial_no ? `<div>🔢 <b>Serial:</b> ${d.serial_no}</div>` : ""}
        </div>

        ${prevCount > 2 ? `
        <div style="background:#fff3cd;border-radius:6px;padding:6px 12px;margin-top:8px;font-size:12px;color:#856404">
            ⚠️ هذا الجهاز لديه <b>${prevCount}</b> طلب صيانة سابق — قد يحتاج مراجعة شاملة
        </div>` : ""}
    </div>`;

    frm.set_df_property("asset_info_html","options", html);
    frm.refresh_field("asset_info_html");
}

// ── Dashboard Indicators ──────────────────────────────────────────────────────
function _setup_dashboard(frm) {
    if (frm.is_new()) return;
    frappe.call({
        method: "asset_maintenance_pro.api.get_request_summary",
        args: { name: frm.doc.name },
        callback(r) {
            if (!r.message) return;
            const s = r.message;
            frm.dashboard.reset();
            if (s.work_log_count)   frm.dashboard.add_indicator(`📝 ${s.work_log_count} سجل عمل`, "blue");
            if (s.spare_part_count) frm.dashboard.add_indicator(`🔩 ${s.spare_part_count} قطعة غيار`, "orange");
            if (s.is_overdue)       frm.dashboard.add_indicator("⚠️ متأخر", "red");
            if (s.sla_status)       frm.dashboard.add_indicator(
                `SLA: ${s.sla_status}`,
                s.sla_status === "Breached" ? "red" : s.sla_status === "At Risk" ? "orange" : "green"
            );
            if (s.previous_count)   frm.dashboard.add_indicator(`🔄 ${s.previous_count} طلب سابق لهذا الجهاز`, "yellow");
        }
    });
}

function _show_sla_countdown(frm) {
    if (!frm.doc.due_date || ["Completed","Cancelled"].includes(frm.doc.status)) return;
    const diff = Math.ceil((new Date(frm.doc.due_date) - new Date()) / 86400000);
    if (diff < 0)
        frm.dashboard.add_indicator(`⏰ متأخر ${Math.abs(diff)} يوم`, "red");
    else if (diff <= 2)
        frm.dashboard.add_indicator(`⏰ موعد التسليم خلال ${diff} يوم`, "orange");
}

function _show_completion_duration(frm) {
    if (frm.doc.status !== "Completed" || !frm.doc.requested_on || !frm.doc.closed_on) return;
    const start = new Date(frm.doc.requested_on);
    const end   = new Date(frm.doc.closed_on);
    const hours = Math.round((end - start) / 3600000 * 10) / 10;
    frm.dashboard.add_indicator(`✅ أُنجز في ${hours} ساعة`, "green");
    frm.set_value("completion_duration_hours", hours);
}

function _update_checklist_progress(frm) {
    const items = frm.doc.checklist || [];
    if (!items.length) return;
    const done = items.filter(r => r.completed).length;
    const pct  = Math.round(done / items.length * 100);
    frm.dashboard.add_indicator(
        `✓ Checklist ${done}/${items.length} (${pct}%)`,
        pct === 100 ? "green" : pct > 50 ? "orange" : "red"
    );
}

function _suggest_maintenance_type(frm) {
    const desc = (frm.doc.description || "").toLowerCase();
    const kw = {
        "Corrective":  ["مش شغال","عطل","خربان","توقف","broken","fail","crash","لا يعمل"],
        "Preventive":  ["صيانة دورية","تنظيف","فحص","cleaning","inspection"],
        "Inspection":  ["كشف","مراجعة","تقرير","report","audit"],
    };
    for (const [type, words] of Object.entries(kw)) {
        if (words.some(w => desc.includes(w)) && frm.doc.maintenance_type !== type) {
            frm.set_value("maintenance_type", type);
            frappe.show_alert({ message: `💡 نوع الصيانة: ${type}`, indicator:"blue" }, 3);
            break;
        }
    }
}

// ── Action Buttons ────────────────────────────────────────────────────────────
function _setup_action_buttons(frm, isMgr, isTech) {
    if (frm.is_new()) return;
    const status = frm.doc.status;

    if (isMgr && status === "New")
        frm.add_custom_button("⚡ تعيين", () => _quick_assign(frm), "الإجراءات");
    if ((isMgr || isTech) && status === "Assigned")
        frm.add_custom_button("▶️ بدء العمل", () => _transition(frm,"In Progress"), "الإجراءات");
    if ((isMgr || isTech) && status === "In Progress") {
        frm.add_custom_button("🔩 انتظار قطع", () => _transition(frm,"Waiting Parts"), "الإجراءات");
        frm.add_custom_button("✅ تم الإنجاز", () => _transition(frm,"Awaiting Close"), "الإجراءات");
    }
    if ((isMgr || isTech) && status === "Waiting Parts")
        frm.add_custom_button("▶️ استئناف", () => _transition(frm,"In Progress"), "الإجراءات");
    if (isMgr && status === "Awaiting Close")
        frm.add_custom_button("🏁 إغلاق وتأكيد", () => _complete_request(frm), "الإجراءات");
    if (isMgr && !["Completed","Cancelled"].includes(status))
        frm.add_custom_button("❌ إلغاء", () => _transition(frm,"Cancelled"), "الإجراءات");

    if (!["Completed","Cancelled"].includes(status)) {
        frm.add_custom_button("📝 سجل عمل", () => _quick_work_log(frm));
        if (isMgr || isTech)
            frm.add_custom_button("🔩 قطعة غيار", () => _quick_spare_part(frm));
    }

    frm.add_custom_button("سجلات العمل", () =>
        frappe.set_route("List","Maintenance Work Log",{maintenance_request:frm.doc.name}), "عرض");
    frm.add_custom_button("قطع الغيار", () =>
        frappe.set_route("List","Spare Part Consumption",{maintenance_request:frm.doc.name}), "عرض");
    frm.add_custom_button("📊 Kanban", () =>
        frappe.set_route("List","Maintenance Request","kanban","Maintenance Kanban"), "عرض");
}

// ── Helpers ───────────────────────────────────────────────────────────────────
function _autofill_branch(frm) {
    frappe.call({
        method: "asset_maintenance_pro.api.get_user_branch",
        callback(r) {
            if (r.message?.branch) frm.set_value("branch", r.message.branch);
        }
    });
}

function _transition(frm, new_status) {
    frappe.confirm(`هل تريد تحويل الطلب إلى <b>${new_status}</b>؟`,
        () => frm.call("transition_status",{new_status}).then(()=>frm.reload_doc()));
}

function _complete_request(frm) {
    if (!frm.doc.total_cost || frm.doc.total_cost <= 0)
        return frappe.msgprint({message:"الرجاء إدخال <b>التكلفة الإجمالية</b>",indicator:"red"});
    if (!frm.doc.completion_image)
        return frappe.msgprint({message:"الرجاء إرفاق <b>صورة الإنجاز</b>",indicator:"red"});
    const inc = (frm.doc.checklist||[]).filter(r=>r.is_mandatory&&!r.completed).map(r=>r.task);
    if (inc.length)
        return frappe.msgprint({message:`أكمل المهام الإلزامية:<br>${inc.join("<br>")}`,indicator:"red"});
    _transition(frm, "Completed");
}

function _quick_assign(frm) {
    frappe.call({
        method: "asset_maintenance_pro.api.get_suggested_technician",
        args: { branch: frm.doc.branch, maintenance_type: frm.doc.maintenance_type },
        callback(r) {
            const suggested = r.message?.user || "";
            new frappe.ui.Dialog({
                title: "⚡ تعيين طلب الصيانة",
                fields: [
                    { fieldname:"assigned_to", fieldtype:"Link", label:"تعيين إلى",
                      options:"User", reqd:1, default:suggested,
                      description: suggested ? `💡 مقترح: ${suggested}` : "",
                      get_query:()=>({query:"asset_maintenance_pro.api.get_technicians",
                                      filters:{branch:frm.doc.branch||""}}) },
                    { fieldname:"due_date", fieldtype:"Date", label:"تاريخ الاستحقاق",
                      default:frappe.datetime.add_days(frappe.datetime.nowdate(),3) },
                    { fieldname:"priority", fieldtype:"Select", label:"الأولوية",
                      options:"Low\nMedium\nHigh\nCritical", default:frm.doc.priority||"Medium" },
                    { fieldname:"maintenance_type", fieldtype:"Select", label:"نوع الصيانة",
                      options:"Corrective\nPreventive\nInspection", default:frm.doc.maintenance_type||"Corrective" },
                ],
                primary_action_label: "تعيين",
                primary_action(vals) {
                    frm.set_value("assigned_to", vals.assigned_to);
                    frm.set_value("due_date",    vals.due_date);
                    frm.set_value("priority",    vals.priority);
                    frm.set_value("maintenance_type", vals.maintenance_type);
                    frm.set_value("status", "Assigned");
                    frm.save().then(()=>frappe.show_alert({message:"تم التعيين ✅",indicator:"green"}));
                    this.hide();
                }
            }).show();
        }
    });
}

function _quick_work_log(frm) {
    new frappe.ui.Dialog({
        title: "📝 إضافة سجل عمل",
        fields: [
            { fieldname:"log_type", fieldtype:"Select", label:"النوع",
              options:"Work Note\nParts Order\nInspection\nOther", default:"Work Note", reqd:1 },
            { fieldname:"time_spent_hours", fieldtype:"Float", label:"الوقت المستغرق (ساعات)" },
            { fieldname:"description", fieldtype:"Text Editor", label:"التفاصيل", reqd:1 },
        ],
        primary_action_label: "حفظ",
        primary_action(vals) {
            frappe.call({
                method:"asset_maintenance_pro.api.add_work_log",
                args:{maintenance_request:frm.doc.name,...vals},
                freeze:true,
                callback(r){ if(r.message){ frappe.show_alert({message:"تم الحفظ ✅",indicator:"green"}); frm.reload_doc(); } }
            });
            this.hide();
        }
    }).show();
}

function _quick_spare_part(frm) {
    new frappe.ui.Dialog({
        title: "🔩 إضافة قطعة غيار",
        fields: [
            { fieldname:"item_code", fieldtype:"Link", label:"القطعة", options:"Item", reqd:1 },
            { fieldname:"qty", fieldtype:"Float", label:"الكمية", default:1, reqd:1 },
            { fieldname:"rate", fieldtype:"Currency", label:"السعر" },
            { fieldname:"warehouse", fieldtype:"Link", label:"المستودع", options:"Warehouse", reqd:1 },
        ],
        primary_action_label: "إضافة",
        primary_action(vals) {
            frappe.db.insert({ doctype:"Spare Part Consumption", maintenance_request:frm.doc.name, ...vals })
                .then(()=>{ frappe.show_alert({message:"تمت الإضافة ✅",indicator:"green"}); frm.reload_doc(); });
            this.hide();
        }
    }).show();
}
