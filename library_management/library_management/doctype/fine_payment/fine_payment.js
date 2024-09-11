frappe.ui.form.on("Fine Payment", {
  library_member: function (frm) {
    if (frm.doc.library_member) {
      // Fetch total amount when form is refreshed
      frm.call({
        method: "library_management.library_management.doctype.fine_payment.fine_payment.get_total_fine_amount",
        args: {
          library_member: frm.doc.library_member,
        },
        callback: function (fine_amount) {
          if (fine_amount.message) {
            //frm.set_value("fine_amount", fine_amount.message.total_unpaid_fines);
          }
        },
      });
    }
  },
});
