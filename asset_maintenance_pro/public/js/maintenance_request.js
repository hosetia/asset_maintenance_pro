/**
 * Maintenance Request — Smart Client Script
 * Phase 1: RBAC auto-fill, Asset filtering by Branch, QR support
 * Phase 2: Auto Assignment hints, SLA countdown
 */

const STATUS_COLORS = {
    "New":"blue","Assigned":"orange","In Progress":"yellow",
    "Waiting Parts":"red","Awaiting Close":"purple","Completed":"green","Cancelled":"gray"
};
const PRIORITY_ICONS = {"Low":"🟢","Medium":"🟡","High":"🟠","Critical":"🔴"};

frappe.ui.form.on("Maintenance Request", {

    setup(frm) {
        frm.set_query("asset", () => {
            const filters = { docstatus: 1 };
            if (frm.doc.branch) filters.branch = frm.doc.branch;
            return { filters };
        });
        frm.set_query("assigned_to", () => ({
            query: "asset_maintenance_pro.api.get_technicians",
            filters: { branch: frm.doc.branch || "" }
        }));
    },

    refresh(frm) {
        _setup_indicator(frm);
        _setup_dashboard(frm);
        _setup_action_buttons(frm);
        _toggle_completion_fields(frm);
        _show_sla_countdown(frm);
        if (frm.is_new()) _autofill_branch(frm);
    },

    asset(frm) {
        if (!frm.doc.asset) return;
        frappe.call({
            method: "asset_maintenance_pro.api.get_asset_details",
            args: { asset: frm.doc.asset },
            callback(r) {
                if (!r.message) return;
                const d = r.message;
                if (d.branch) frm.set_value("branch", d.branch);
                _show_asset_info_card(frm, d);
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
        _setup_indicator(frm);
        _toggle_completion_fields(frm);
    },

    priority(frm) {
        if (!frm.doc.priority) return;
        const icon = PRIORITY_ICONS[frm.doc.priority] || "";
        frm.set_intro(`${icon} <b>${frm.doc.priority} Priority</b>`,
            frm.doc.priority === "Critical" ? "red" :
            frm.doc.priority === "High" ? "orange" : "blue");
    },

    description(frm) {
        if (frm.doc.description && frm.doc.description.length > 10)
            _suggest_maintenance_type(frm);
    },

    preventive_schedule(frm) {
        if (!frm.doc.preventive_schedule) return;
        frappe.call({
            method: "asset_maintenance_pro.api.get_checklist_tasks",
            args: { checklist: frm.doc.preventive_schedule },
            callback(r) {
                if (!r.message || !r.message.length) return;
                frm.clear_table("checklist");
                r.message.forEach(t => frm.add_child("checklist",
                    { task: t.task, is_mandatory: t.is_mandatory }));
                frm.refresh_field("checklist");
                frappe.show_alert({ message: __("{0} tasks loaded",[r.message.length]), indicator:"green"});
            }
        });
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

// ── Helpers ──────────────────────────────────────────────────────────────────

function _autofill_branch(frm) {
    frappe.call({
        method: "asset_maintenance_pro.api.get_user_branch",
        callback(r) {
            if (r.message && r.message.branch)
                frm.set_value("branch", r.message.branch);
        }
    });
}

function _setup_indicator(frm) {
    frm.page.set_indicator(frm.doc.status, STATUS_COLORS[frm.doc.status] || "gray");
}

function _setup_dashboard(frm) {
    if (frm.is_new()) return;
    frappe.call({
        method: "asset_maintenance_pro.api.get_request_summary",
        args: { name: frm.doc.name },
        callback(r) {
            if (!r.message) return;
            const s = r.message;
            if (s.work_log_count)  frm.dashboard.add_indicator(__("{0} Work Log(s)",[s.work_log_count]), "blue");
            if (s.spare_part_count) frm.dashboard.add_indicator(__("{0} Spare Part(s)",[s.spare_part_count]), "orange");
            if (s.is_overdue)      frm.dashboard.add_indicator(__("⚠️ OVERDUE"), "red");
            if (s.sla_status)      frm.dashboard.add_indicator(
                __("SLA: {0}",[s.sla_status]),
                s.sla_status === "Breached" ? "red" : s.sla_status === "At Risk" ? "orange" : "green"
            );
        }
    });
}

function _show_asset_info_card(frm, d) {
    const html = `<div style="background:#f0f4ff;border-left:4px solid #2490ef;
        padding:10px 14px;border-radius:6px;margin:8px 0;font-size:13px;line-height:1.8">
        <b>📦 ${d.asset_name || d.asset}</b><br>
        <span style="color:#555">
            ${d.asset_category ? "📁 " + d.asset_category + " &nbsp;|&nbsp;" : ""}
            ${d.location ? "📍 " + d.location + " &nbsp;|&nbsp;" : ""}
            ${d.last_maintenance
                ? "🔧 Last Maintenance: " + frappe.datetime.str_to_user(d.last_maintenance)
                : "🔧 No maintenance history"}
        </span></div>`;
    frm.set_intro(html, false);
}

function _suggest_maintenance_type(frm) {
    const desc = (frm.doc.description || "").toLowerCase();
    const keywords = {
        "Corrective":  ["مش شغال","بطيء","خربان","توقف","error","broken","not working","slow","crash","fail"],
        "Preventive":  ["صيانة دورية","تنظيف","فحص","periodic","cleaning","inspection","check","lube"],
        "Inspection":  ["كشف","مراجعة","تقرير","report","review","audit"],
    };
    for (const [type, words] of Object.entries(keywords)) {
        if (words.some(w => desc.includes(w))) {
            if (frm.doc.maintenance_type !== type) {
                frm.set_value("maintenance_type", type);
                frappe.show_alert({ message: __("💡 Suggested type: {0}",[type]), indicator:"blue" }, 3);
            }
            break;
        }
    }
}

function _update_checklist_progress(frm) {
    const items = frm.doc.checklist || [];
    if (!items.length) return;
    const done = items.filter(r => r.completed).length;
    const pct  = Math.round((done / items.length) * 100);
    frm.dashboard.add_indicator(
        __("Checklist: {0}/{1} ({2}%)",[done, items.length, pct]),
        pct === 100 ? "green" : pct > 50 ? "orange" : "red"
    );
}

function _toggle_completion_fields(frm) {
    const show = ["Awaiting Close","Completed"].includes(frm.doc.status);
    frm.toggle_reqd("total_cost", show);
    frm.toggle_reqd("completion_image", show);
}

function _show_sla_countdown(frm) {
    if (!frm.doc.due_date || ["Completed","Cancelled"].includes(frm.doc.status)) return;
    const diff = Math.ceil((new Date(frm.doc.due_date) - new Date()) / 86400000);
    if (diff < 0)
        frm.dashboard.add_indicator(__("⚠️ Overdue by {0} day(s)",[Math.abs(diff)]), "red");
    else if (diff <= 2)
        frm.dashboard.add_indicator(__("⏰ Due in {0} day(s)",[diff]), "orange");
}

function _setup_action_buttons(frm) {
    if (frm.is_new()) return;
    const status = frm.doc.status;
    const roles  = frappe.user_roles;
    const isMgr  = roles.includes("System Manager") || roles.includes("Branch Manager");
    const isTech = roles.includes("Maintenance Technician");

    if (status === "New" && isMgr)
        frm.add_custom_button(__("⚡ Quick Assign"), () => _quick_assign(frm), __("Actions"));
    if (status === "Assigned" && (isMgr || isTech))
        frm.add_custom_button(__("▶️ Start Work"), () => _transition(frm,"In Progress"), __("Actions"));
    if (status === "In Progress" && (isMgr || isTech)) {
        frm.add_custom_button(__("🔩 Request Parts"), () => _transition(frm,"Waiting Parts"), __("Actions"));
        frm.add_custom_button(__("✅ Mark Done"), () => _transition(frm,"Awaiting Close"), __("Actions"));
    }
    if (status === "Waiting Parts" && (isMgr || isTech))
        frm.add_custom_button(__("▶️ Resume Work"), () => _transition(frm,"In Progress"), __("Actions"));
    if (status === "Awaiting Close" && isMgr)
        frm.add_custom_button(__("🏁 Complete"), () => _complete_request(frm), __("Actions"));
    if (!["Completed","Cancelled"].includes(status) && isMgr)
        frm.add_custom_button(__("❌ Cancel"), () => _transition(frm,"Cancelled"), __("Actions"));

    if (!["Completed","Cancelled"].includes(status)) {
        frm.add_custom_button(__("📝 Work Log"), () => _quick_work_log(frm));
        frm.add_custom_button(__("🔩 Spare Part"), () => _quick_spare_part(frm));
    }

    frm.add_custom_button(__("Work Logs"), () =>
        frappe.set_route("List","Maintenance Work Log",{maintenance_request:frm.doc.name}), __("View"));
    frm.add_custom_button(__("Spare Parts"), () =>
        frappe.set_route("List","Spare Part Consumption",{maintenance_request:frm.doc.name}), __("View"));
    frm.add_custom_button(__("📊 Kanban"), () =>
        frappe.set_route("List","Maintenance Request","kanban","Maintenance Kanban"), __("View"));
}

function _quick_assign(frm) {
    frappe.call({
        method: "asset_maintenance_pro.api.get_suggested_technician",
        args: { branch: frm.doc.branch, maintenance_type: frm.doc.maintenance_type },
        callback(r) {
            const suggested = r.message ? r.message.user : "";
            new frappe.ui.Dialog({
                title: __("⚡ Quick Assign"),
                fields: [
                    { fieldname:"assigned_to", fieldtype:"Link", label:__("Assign To"),
                      options:"User", reqd:1, default:suggested,
                      description: suggested ? __("💡 Suggested: {0}",[suggested]) : "",
                      get_query:() => ({query:"asset_maintenance_pro.api.get_technicians",
                                        filters:{branch:frm.doc.branch||""}}) },
                    { fieldname:"due_date", fieldtype:"Date", label:__("Due Date"),
                      default:frappe.datetime.add_days(frappe.datetime.nowdate(),3) },
                    { fieldname:"priority", fieldtype:"Select", label:__("Priority"),
                      options:"Low\nMedium\nHigh\nCritical", default:frm.doc.priority||"Medium" },
                ],
                primary_action_label: __("Assign"),
                primary_action(vals) {
                    frm.set_value("assigned_to", vals.assigned_to);
                    frm.set_value("due_date", vals.due_date);
                    frm.set_value("priority", vals.priority);
                    frm.set_value("status", "Assigned");
                    frm.save();
                    this.hide();
                }
            }).show();
        }
    });
}

function _transition(frm, new_status) {
    frappe.confirm(__("Move to <b>{0}</b>?",[new_status]),
        () => frm.call("transition_status",{new_status}).then(()=>frm.reload_doc()));
}

function _complete_request(frm) {
    if (!frm.doc.total_cost || frm.doc.total_cost <= 0)
        return frappe.msgprint({message:__("Please fill <b>Total Cost</b> first."),indicator:"red"});
    if (!frm.doc.completion_image)
        return frappe.msgprint({message:__("Please attach a <b>Completion Image</b> first."),indicator:"red"});
    const inc = (frm.doc.checklist||[]).filter(r=>r.is_mandatory&&!r.completed).map(r=>r.task);
    if (inc.length)
        return frappe.msgprint({message:__("Complete mandatory items:<br>{0}",[inc.join("<br>")]),indicator:"red"});
    _transition(frm, "Completed");
}

function _quick_work_log(frm) {
    new frappe.ui.Dialog({
        title: __("📝 Add Work Log"),
        fields: [
            { fieldname:"log_type", fieldtype:"Select", label:__("Type"),
              options:"Work Note\nParts Order\nInspection\nOther", default:"Work Note", reqd:1 },
            { fieldname:"time_spent_hours", fieldtype:"Float", label:__("Time Spent (Hours)") },
            { fieldname:"description", fieldtype:"Text Editor", label:__("Description"), reqd:1 },
        ],
        primary_action_label: __("Save"),
        primary_action(vals) {
            frappe.call({
                method:"asset_maintenance_pro.api.add_work_log",
                args:{maintenance_request:frm.doc.name,...vals},
                freeze:true,
                callback(r){if(r.message){frappe.show_alert({message:__("Saved"),indicator:"green"});frm.reload_doc();}}
            });
            this.hide();
        }
    }).show();
}

function _quick_spare_part(frm) {
    new frappe.ui.Dialog({
        title: __("🔩 Add Spare Part"),
        fields: [
            { fieldname:"item_code", fieldtype:"Link", label:__("Item"), options:"Item", reqd:1 },
            { fieldname:"qty", fieldtype:"Float", label:__("Quantity"), default:1, reqd:1 },
            { fieldname:"rate", fieldtype:"Currency", label:__("Rate") },
            { fieldname:"warehouse", fieldtype:"Link", label:__("Warehouse"), options:"Warehouse", reqd:1 },
        ],
        primary_action_label: __("Add"),
        primary_action(vals) {
            frappe.db.insert({
                doctype:"Spare Part Consumption",
                maintenance_request:frm.doc.name, ...vals
            }).then(()=>{
                frappe.show_alert({message:__("Added"),indicator:"green"});
                frm.reload_doc();
            });
            this.hide();
        }
    }).show();
}
