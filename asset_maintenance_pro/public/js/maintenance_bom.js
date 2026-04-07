frappe.ui.form.on("Maintenance BOM", {
    refresh(frm) {
        if (!frm.is_new()) {
            frm.add_custom_button("إنشاء طلب قطع غيار", () => {
                frappe.new_doc("Spare Part Request", {
                    notes: `من BOM: ${frm.doc.bom_name}`,
                });
            });
        }
    }
});
