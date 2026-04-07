frappe.ui.form.on("Maintenance Technical Manual", {
    refresh(frm) {
        if (frm.doc.external_url) {
            frm.add_custom_button("🔗 فتح الرابط الخارجي", () => {
                window.open(frm.doc.external_url, "_blank");
            });
        }
        if (frm.doc.file_attachment) {
            frm.add_custom_button("📄 عرض الملف", () => {
                window.open(frm.doc.file_attachment, "_blank");
            });
        }
    }
});
