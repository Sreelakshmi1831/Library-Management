frappe.ui.form.on('Library Transaction', {
    onload: function(frm) {
        frm.set_query('article', () => {
            return {
                filters: {
                    status: 'Available'
                }
            };
        });
		
    }
});
frappe.ui.form.on('Library Transaction', {
    after_submit: function (frm) {
        if (frm.doc.total_fine && frm.doc.total_fine > 0) {
            let message = `<b>Total Fine Amount:</b> ${frm.doc.total_fine} rupees`;

            frappe.msgprint({
                title: __('Total Fine'),
                message: message,
                indicator: 'orange'
            });
        }
    }
});
frappe.ui.form.on('Library Transaction', {
    refresh: function(frm) {
        frm.set_query("article_name", function() {
            if (frm.doc.journal) {
                return {
                    filters: {
                        "journal": frm.doc.journal
                    }
                };
            } else {
                return {};
            }
        });
    },

    article_name: function(frm) {
        if (frm.doc.article_name) {
            // Fetch the journal and column number from the selected article
            frappe.db.get_value('Article', frm.doc.article_name, ['journal', 'column_number'], (r) => {
                if (r && r.journal) {
                    // Convert column number to alphabetic order (e.g., 1 -> A, 2 -> B)
                    let column_letter = String.fromCharCode(64 + r.column_number); // Assuming column_number starts from 1
                    
                    // Display message with journal and column information
                    frappe.msgprint(`This article belongs to the journal section <b>${r.journal}</b> and is located in column <b>${column_letter}</b>.`);
                }
            });
        }
    },

    journal: function(frm) {
        frm.set_query("article_name", function() {
            if (frm.doc.journal) {
                return {
                    filters: {
                        "journal": frm.doc.journal
                    }
                };
            } else {
                return {};
            }
        });

        // Clear the article_name field when the journal is changed
        frm.set_value("article_name", []);
    }
});

    

