frappe.ui.form.on('Article', {
    before_save: function(frm) {
        if (frm.doc.journal) {
            // Fetch all articles in the same journal to determine the current row and column numbers
            frappe.db.get_list('Article', {
                filters: {
                    journal: frm.doc.journal
                },
                fields: ['name'],
                order_by: 'creation asc'  // Sort by creation date to maintain article order
            }).then((result) => {
                // Determine the index of the current article
                let current_index = result.findIndex(article => article.name === frm.doc.name);

                // Calculate the row number (should be consistent for all articles in the journal)
                let row_number = (current_index % 5) + 1; // This will give 1 for the first row, 2 for the second, etc.

                // Calculate the column number (changes after every 5 articles)
                let column_number = Math.floor(current_index / 5) + 1; // Changes after every 5 articles

                // Get the first letter of the journal name and make it uppercase for the prefix
                let journal_prefix = frm.doc.journal.charAt(0).toUpperCase();

                // Set the row number field (consistent across the journal)
                frm.set_value('row_number', row_number);

                // Set the journal_prefix_row_number field (e.g., F1, F2, F3, ...)
                frm.set_value('journal_prefix_row_number', `${journal_prefix}${column_number}`);
            });
        }
    }
});
