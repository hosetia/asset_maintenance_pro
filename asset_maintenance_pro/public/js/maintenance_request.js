/**
 * Maintenance Request — Smart Client Script
 * Role-based form: Requester sees minimal fields, Manager/Tech sees full form
 */

const STATUS_COLORS = {
    "New":"blue","Assigned":"orange","In Progress":"yellow",
    "Waiting Parts":"red","Awaiting Close":"purple","Completed":"green","Cancelled":"gray"
};

frappe.ui.form.on("Maintenance Request", {

    setup(frm) {
        // Filter assets by user's branch only
        frm.set_query("asset", () => {
            const filters = { docstatus: 1 };
            if (frm.doc.branch) filters.branch = frm.doc.branch;
            return { filters };
        });

        // Technicians only in assigned_to
        frm.set_query("assigned_to", () => ({
            query: "asset_maintenance_pro.api.get_technicians",
            filters: { branch: frm.doc.branch || "" }
        }));

        // Symptom code filter
        frm.set_query("symptom_code", () => ({
            filters: { taxonomy_type: "Symptom" }
        }));
        frm.set_query("cause_code", () => ({
            filters: { taxonomy_type: "Cause" }
        }));
        frm.set_query("remedy_code", () => ({
            filters: { taxonomy_type: "Remedy" }
        }));
    },

    refresh(frm) {
        const roles = frappe.user_roles;
        const isRequester = _is_requester_only(roles);
        const isMgr  = roles.includes("System Manager") || roles.includes("Branch Manager") || roles.includes("Maintenance Coordinator");
        const isTech = roles.includes("Maintenance Technician");

        // Apply role-based visibility
        _apply_role_visibility(frm, isRequester, isMgr, isTech);

        frm.page.set_indicator(frm.doc.status, STATUS_COLORS[frm.doc.status] || "gray");
        _setup_dashboard(frm);
        _show_sla_countdown(frm);

        if (!isRequester) {
            _setup_action_buttons(frm, isMgr, isTech);
        }

        if (frm.is_new()) {
            _autofill_branch(frm);
        }
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
        frm.page.set_indicator(frm.doc.status, STATUS_COLORS[frm.doc.status] || "gray");
        _toggle_completion_fields(frm);
    },

    description(frm) {
        if (frm.doc.description && frm.doc.description.length > 10)
            _suggest_maintenance_type(frm);
    },
});

// ── Role Detection ────────────────────────────────────────────────────────────

function _is_requester_only(roles) {
    const mgr_roles = ["System Manager","Branch Manager","Maintenance Coordinator","Maintenance Technician"];
    return !roles.some(r => mgr_roles.includes(r));
}

// ── Role-Based Field Visibility ───────────────────────────────────────────────

function _apply_role_visibility(frm, isRequester, isMgr, isTech) {

    // ── REQUESTER: Only see basic request fields ──────────────────────────────
    if (isRequester) {
        // Show only: asset, branch, description, images, issue_type, impact
        const requester_fields = ["asset","branch","description","images","issue_type","impact","is_food_safety_impact","is_closure_risk"];
        const hidden_for_requester = [
            "maintenance_type","priority","status","kanban_column","assigned_to","due_date",
            "checklist","total_cost","completion_image","completion_notes",
            "symptom_code","cause_code","remedy_code","failure_class",
            "downtime_start","downtime_end","triage_by","verified_by",
            "request_type","reference_meter_reading","preventive_schedule",
            "requested_by","requested_on","closed_by","closed_on",
            "section_break_completion","section_break_checklist",
        ];

        hidden_for_requester.forEach(f => {
            try { frm.set_df_property(f, "hidden", 1); } catch(e) {}
        });

        // Make key fields required for requester
        frm.toggle_reqd("asset", true);
        frm.toggle_reqd("description", true);

        // Hide save button label — show friendly message
        if (frm.is_new()) {
            frm.set_intro(
                __("📝 Describe the issue with the equipment. Our maintenance team will take it from there."),
                "blue"
            );
        }

        // Read-only: cannot change status
        frm.set_df_property("status", "read_only", 1);
        return;
    }

    // ── TECHNICIAN: Can update status, add logs, but NOT completion cost/image ─
    if (isTech && !isMgr) {
        const hidden_for_tech = [
            "total_cost","completion_image","assigned_to",
            "triage_by","verified_by","closed_by","closed_on",
        ];
        hidden_for_tech.forEach(f => {
            try { frm.set_df_property(f, "hidden", 1); } catch(e) {}
        });

        // Technicians can update: status (limited), checklist, work logs, symptom/cause/remedy
        frm.set_df_property("status", "read_only",
            !["In Progress","Waiting Parts","Awaiting Close"].includes(frm.doc.status) ? 0 : 0
        );
        _toggle_completion_fields(frm);
        return;
    }

    // ── MANAGER / COORDINATOR: Full access ────────────────────────────────────
    // Unhide all fields
    const all_fields = [
        "maintenance_type","priority","status","assigned_to","due_date",
        "checklist","total_cost","completion_image","completion_notes",
        "symptom_code","cause_code","remedy_code","failure_class",
        "downtime_start","downtime_end","triage_by","verified_by",
        "requested_by","requested_on","closed_by","closed_on",
    ];
    all_fields.forEach(f => {
        try { frm.set_df_property(f, "hidden", 0); } catch(e) {}
    });
    _toggle_completion_fields(frm);
}

function _toggle_completion_fields(frm) {
    const roles = frappe.user_roles;
    const isMgr = roles.includes("System Manager") || roles.includes("Branch Manager") || roles.includes("Maintenance Coordinator");
    const show = ["Awaiting Close","Completed"].includes(frm.doc.status) && isMgr;
    frm.toggle_reqd("total_cost", show);
    frm.toggle_reqd("completion_image", show);
}

// ── Helpers ───────────────────────────────────────────────────────────────────

function _autofill_branch(frm) {
    frappe.call({
        method: "asset_maintenance_pro.api.get_user_branch",
        callback(r) {
            if (r.message && r.message.branch)
                frm.set_value("branch", r.message.branch);
        }
    });
}

function _show_asset_info_card(frm, d) {
    const html = `<div style="background:#f0f4ff;border-left:4px solid #2490ef;
        padding:10px 16px;border-radius:6px;margin:8px 0;font-size:13px;line-height:1.8">
        <b>📦 ${d.asset_name || d.asset}</b><br>
        <span style="color:#555">
            ${d.asset_category ? "📁 " + d.asset_category + " &nbsp;|&nbsp;" : ""}
            ${d.location ? "📍 " + d.location + " &nbsp;|&nbsp;" : ""}
            ${d.last_maintenance
                ? "🔧 Last Maintenance: " + frappe.datetime.str_to_user(d.last_maintenance)
                : "🔧 No maintenance history"}
            ${d.custom_criticality
                ? "&nbsp;|&nbsp; ⚡ Criticality: " + d.custom_criticality
                : ""}
        </span></div>`;
    frm.set_intro(html, false);
}

function _suggest_maintenance_type(frm) {
    const desc = (frm.doc.description || "").toLowerCase();
    const keywords = {
        "Corrective":  ["مش شغال","بطيء","خربان","توقف","error","broken","not working","slow","crash","fail","عطل"],
        "Preventive":  ["صيانة دورية","تنظيف","فحص","periodic","cleaning","inspection","check","lube"],
        "Inspection":  ["كشف","مراجعة","تقرير","report","review","audit"],
    };
    for (const [type, words] of Object.entries(keywords)) {
        if (words.some(w => desc.includes(w))) {
            if (!frm.doc.maintenance_type || frm.doc.maintenance_type !== type) {
                frm.set_value("maintenance_type", type);
                frappe.show_alert({ message: __("💡 Type set to: {0}",[type]), indicator:"blue" }, 3);
            }
            break;
        }
    }
}

function _setup_dashboard(frm) {
    if (frm.is_new()) return;
    frappe.call({
        method: "asset_maintenance_pro.api.get_request_summary",
        args: { name: frm.doc.name },
        callback(r) {
            if (!r.message) return;
            const s = r.message;
            if (s.work_log_count)   frm.dashboard.add_indicator(__("{0} Work Log(s)",[s.work_log_count]), "blue");
            if (s.spare_part_count) frm.dashboard.add_indicator(__("{0} Spare Part(s)",[s.spare_part_count]), "orange");
            if (s.is_overdue)       frm.dashboard.add_indicator(__("⚠️ OVERDUE"), "red");
            if (s.sla_status)       frm.dashboard.add_indicator(
                __("SLA: {0}",[s.sla_status]),
                s.sla_status === "Breached" ? "red" : s.sla_status === "At Risk" ? "orange" : "green"
            );
        }
    });
}

function _show_sla_countdown(frm) {
    if (!frm.doc.due_date || ["Completed","Cancelled"].includes(frm.doc.status)) return;
    const diff = Math.ceil((new Date(frm.doc.due_date) - new Date()) / 86400000);
    if (diff < 0)
        frm.dashboard.add_indicator(__("⚠️ Overdue by {0} day(s)",[Math.abs(diff)]), "red");
    else if (diff <= 2)
        frm.dashboard.add_indicator(__("⏰ Due in {0} day(s)",[diff]), "orange");
}

function _setup_action_buttons(frm, isMgr, isTech) {
    if (frm.is_new()) return;
    const status = frm.doc.status;

    // Manager actions
    if (isMgr) {
        if (status === "New")
            frm.add_custom_button(__("⚡ Assign"), () => _quick_assign(frm), __("Actions"));
        if (status === "Awaiting Close")
            frm.add_custom_button(__("🏁 Complete"), () => _complete_request(frm), __("Actions"));
        if (!["Completed","Cancelled"].includes(status))
            frm.add_custom_button(__("❌ Cancel"), () => _transition(frm,"Cancelled"), __("Actions"));
    }

    // Technician actions
    if (isTech || isMgr) {
        if (status === "Assigned")
            frm.add_custom_button(__("▶️ Start Work"), () => _transition(frm,"In Progress"), __("Actions"));
        if (status === "In Progress") {
            frm.add_custom_button(__("🔩 Request Parts"), () => _transition(frm,"Waiting Parts"), __("Actions"));
            frm.add_custom_button(__("✅ Mark Done"), () => _transition(frm,"Awaiting Close"), __("Actions"));
        }
        if (status === "Waiting Parts")
            frm.add_custom_button(__("▶️ Resume"), () => _transition(frm,"In Progress"), __("Actions"));
    }

    // Work log + spare part — for tech and manager (not requester)
    if (!["Completed","Cancelled"].includes(status)) {
        frm.add_custom_button(__("📝 Work Log"), () => _quick_work_log(frm));
        if (isMgr || isTech)
            frm.add_custom_button(__("🔩 Spare Part"), () => _quick_spare_part(frm));
    }

    // View links
    frm.add_custom_button(__("Work Logs"), () =>
        frappe.set_route("List","Maintenance Work Log",{maintenance_request:frm.doc.name}), __("View"));
    frm.add_custom_button(__("Spare Parts"), () =>
        frappe.set_route("List","Spare Part Consumption",{maintenance_request:frm.doc.name}), __("View"));
    frm.add_custom_button(__("📊 Kanban"), () =>
        frappe.set_route("List","Maintenance Request","kanban","Maintenance Kanban"), __("View"));
}

// ── Action Dialogs ────────────────────────────────────────────────────────────

function _quick_assign(frm) {
    frappe.call({
        method: "asset_maintenance_pro.api.get_suggested_technician",
        args: { branch: frm.doc.branch, maintenance_type: frm.doc.maintenance_type },
        callback(r) {
            const suggested = r.message ? r.message.user : "";
            new frappe.ui.Dialog({
                title: __("⚡ Assign Request"),
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
                    { fieldname:"maintenance_type", fieldtype:"Select", label:__("Type"),
                      options:"Corrective\nPreventive\nInspection", default:frm.doc.maintenance_type||"Corrective" },
                ],
                primary_action_label: __("Assign"),
                primary_action(vals) {
                    frm.set_value("assigned_to", vals.assigned_to);
                    frm.set_value("due_date", vals.due_date);
                    frm.set_value("priority", vals.priority);
                    frm.set_value("maintenance_type", vals.maintenance_type);
                    frm.set_value("status", "Assigned");
                    frm.save().then(() =>
                        frappe.show_alert({message:__("Assigned ✅"),indicator:"green"})
                    );
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
                callback(r){
                    if(r.message){
                        frappe.show_alert({message:__("Saved ✅"),indicator:"green"});
                        frm.reload_doc();
                    }
                }
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
                frappe.show_alert({message:__("Added ✅"),indicator:"green"});
                frm.reload_doc();
            });
            this.hide();
        }
    }).show();
}
