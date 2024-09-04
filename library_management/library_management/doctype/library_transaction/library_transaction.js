frappe.ui.form.on('Library Transaction', {
    onload: function(frm) {
        frm.set_query('article', () => {
            return {
                filters: {
                    status: 'Available'
                }
            };
        });
		frm.set_query("library_member", () => {
            return {
                query: 'library_management.library_management.doctype.library_transaction.library_transaction.custom_query',
            }
        
        })
    }
});



    

