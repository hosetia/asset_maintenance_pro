/**
 * Maintenance Work Order — Smart Client Script
 * Timer controls, task progress, quick actions
 */

const WO_STATUS_COLORS = {
    "Draft":"gray","Ready":"blue","Scheduled Today":"blue","On Route":"orange",
    "On Site":"yellow","Repairing":"yellow","Testing":"purple",
    "Completed":"green","Manager Verification":"purple","Closed":"green","Cancelled":"red"
};

frappe.ui.form.on("Maintenance Work Order", {

    refresh(frm) {
        frm.page.set_indicator(frm.doc.status, WO_STATUS_COLORS[frm.doc.status] || "gray");
        _setup_wo_dashboard(frm);
        _setup_wo_buttons(frm);
        _update_task_progress(frm);
    },

    status(frm) {
        frm.page.set_indicator(frm.doc.status, WO_STATUS_COLORS[frm.doc.status] || "gray");
    },

    actual_start(frm) {
        if (frm.doc.actual_start && !frm.doc.status.includes("On")) {
            frm.set_value("status", "On Site");
        }
    },
});

frappe.ui.form.on("Work Order Task", {
    completed(frm, cdt, cdn) {
        const row = locals[cdt][cdn];
        frappe.model.set_value(cdt, cdn, "completed_by", row.completed ? frappe.session.user : null);
        frappe.model.set_value(cdt, cdn, "completed_on", row.completed ? frappe.datetime.now_datetime() : null);
        _update_task_progress(frm);
    }
});

frappe.ui.form.on("Work Order Time Log", {
    from_time(frm, cdt, cdn) { _calc_hours(frm, cdt, cdn); },
    to_time(frm, cdt, cdn)   { _calc_hours(frm, cdt, cdn); },
});

function _calc_hours(frm, cdt, cdn) {
    const row = locals[cdt][cdn];
    if (row.from_time && row.to_time) {
        const diff = frappe.datetime.get_diff(row.to_time, row.from_time, "hours");
        frappe.model.set_value(cdt, cdn, "hours", Math.round(diff * 100) / 100);
    }
}

function _update_task_progress(frm) {
    const tasks = frm.doc.tasks || [];
    if (!tasks.length) return;
    const done  = tasks.filter(t => t.completed).length;
    const total = tasks.length;
    const pct   = Math.round(done / total * 100);
    frm.dashboard.add_indicator(
        __("Tasks: {0}/{1} ({2}%)", [done, total, pct]),
        pct === 100 ? "green" : pct > 50 ? "orange" : "red"
    );
}

function _setup_wo_dashboard(frm) {
    if (frm.is_new()) return;
    if (frm.doc.total_hours)
        frm.dashboard.add_indicator(__("⏱️ {0} hrs logged", [frm.doc.total_hours]), "blue");
    if (frm.doc.downtime_hours)
        frm.dashboard.add_indicator(__("⬇️ {0} hrs downtime", [frm.doc.downtime_hours]), "red");
    if (frm.doc.total_cost)
        frm.dashboard.add_indicator(__("💰 {0}", [format_currency(frm.doc.total_cost)]), "green");
}

function _setup_wo_buttons(frm) {
    if (frm.is_new()) return;
    const status = frm.doc.status;
    const roles  = frappe.user_roles;
    const isMgr  = roles.includes("System Manager") || roles.includes("Branch Manager");
    const isTech = roles.includes("Maintenance Technician") || roles.includes("Maintenance Coordinator");

    // Timer controls
    if (["Ready","Scheduled Today","On Route","On Site","Repairing"].includes(status) && (isTech || isMgr)) {
        frm.add_custom_button(__("▶️ Start Timer"), () => {
            frm.call("start_timer").then(() => frm.reload_doc());
        }, __("Actions"));
        frm.add_custom_button(__("⏹️ Stop Timer"), () => {
            frm.call("stop_timer").then(() => frm.reload_doc());
        }, __("Actions"));
    }

    // Status transitions
    if (status === "Ready" && (isTech || isMgr))
        frm.add_custom_button(__("🚗 On Route"), () => _wo_transition(frm, "On Route"), __("Actions"));
    if (status === "On Route" && (isTech || isMgr))
        frm.add_custom_button(__("📍 Arrived On Site"), () => _wo_transition(frm, "On Site"), __("Actions"));
    if (status === "On Site" && (isTech || isMgr))
        frm.add_custom_button(__("🔧 Start Repairing"), () => _wo_transition(frm, "Repairing"), __("Actions"));
    if (status === "Repairing" && (isTech || isMgr))
        frm.add_custom_button(__("🧪 Testing"), () => _wo_transition(frm, "Testing"), __("Actions"));
    if (status === "Testing" && (isTech || isMgr))
        frm.add_custom_button(__("✅ Completed"), () => _complete_wo(frm), __("Actions"));
    if (status === "Completed" && isMgr)
        frm.add_custom_button(__("🏁 Close & Verify"), () => _verify_wo(frm), __("Actions"));
}

function _wo_transition(frm, new_status) {
    frm.set_value("status", new_status);
    frm.save();
}

function _complete_wo(frm) {
    if (!frm.doc.completion_photos)
        return frappe.msgprint({message:__("Please attach a completion photo."),indicator:"red"});
    const incomplete = (frm.doc.tasks||[]).filter(t=>t.is_mandatory&&!t.completed).map(t=>t.task);
    if (incomplete.length)
        return frappe.msgprint({message:__("Complete mandatory tasks first:<br>{0}",[incomplete.join("<br>")]),indicator:"red"});
    frm.set_value("status","Completed");
    if (!frm.doc.actual_end) frm.set_value("actual_end", frappe.datetime.now_datetime());
    frm.save();
}

function _verify_wo(frm) {
    new frappe.ui.Dialog({
        title: __("🏁 Manager Verification"),
        fields: [
            {fieldname:"verification_notes",fieldtype:"Text Editor",label:__("Verification Notes"),reqd:1},
        ],
        primary_action_label: __("Verify & Close"),
        primary_action(vals) {
            frm.set_value("status","Closed");
            frm.set_value("verification_notes", vals.verification_notes);
            frm.save();
            this.hide();
        }
    }).show();
}

function format_currency(val) {
    return frappe.format(val, {fieldtype:"Currency"});
}
