frappe.ui.form.on('Library Membership', {
    refresh: function(frm) {
        frm.add_custom_button('Make a payment', () => {
            // Fetch the membership fee from the current Library Membership document
            let total_payment = frm.doc.membership_fee || 0;

            let d = new frappe.ui.Dialog({
                title: 'Enter Payment Details',
                fields: [
                    {
                        label: 'Library Member',
                        fieldname: 'library_member',
                        fieldtype: 'Data',
                        default: frm.doc.library_member || '',
                        read_only: 1
                    },
                    {
                        label: 'Payment Amount',
                        fieldname: 'payment_amount',
                        fieldtype: 'Currency',
                        default: total_payment,
                        reqd: 1
                    },
                    {
                        label: 'Payment Method',
                        fieldname: 'payment_method',
                        fieldtype: 'Select',
                        options: 'Cash\nCard\nBank',
                        reqd: 1
                    }
                ],
                size: 'small',
                primary_action_label: 'Submit',
                primary_action(values) {
                    // Create the document object for Library Payment
                    let payment_doc = {
                        doctype: "Library Payment",
                        library_member: frm.doc.library_member,
                        payment_amount: values.payment_amount,
                        payment_method: values.payment_method
                    };

                    // Create the payment document
                    frappe.call({
                        method: "frappe.client.insert",
                        args: {
                            doc: payment_doc
                        },
                        callback: function(response) {
                            if (!response.exc) {
                                // Successfully created the payment document
                                frappe.msgprint('Payment has been successfully created.');
                                
                                // Automatically check the "Paid" checkbox on the Library Membership
                                frm.set_value('paid', 1);
                                
                                // Save the form to update the Paid status
                                frm.save_or_update({
                                    callback: function() {
                                        frappe.msgprint('Library Membership has been updated as Paid.');
                                    }
                                });

                                // Close the dialog
                                d.hide();
                            } else {
                                frappe.msgprint('There was an error creating the payment.');
                            }
                        }
                    });
                }
            });
            d.show();
        });
    }
});
