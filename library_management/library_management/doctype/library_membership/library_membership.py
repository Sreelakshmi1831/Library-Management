import frappe
from frappe.model.document import Document
from datetime import datetime
from frappe.utils.data import date_diff

class LibraryMembership(Document):
    def before_save(self):
        self.calculate_and_set_membership_fee()

    def calculate_and_set_membership_fee(self):
        if self.from_date and self.to_date:
            total_payment, _ = self.calculate_membership_fee()
            self.membership_fee = total_payment

    def calculate_membership_fee(self):
        # Convert string dates to datetime objects
        from_date = datetime.strptime(self.from_date, '%Y-%m-%d').date()
        to_date = datetime.strptime(self.to_date, '%Y-%m-%d').date()

        # Calculate number of days
        days = date_diff(to_date, from_date) + 1  # Include both start and end date
        total_payment = days * 5  # ₹5 per day

        return total_payment, days

    def before_submit(self):
        self.validate_dates()
        self.check_payment_status()
        self.create_or_update_payment_entry()
        self.check_active_membership()

    def validate_dates(self):
        if self.from_date > self.to_date:
            frappe.throw("The 'from_date' cannot be later than the 'to_date'.")

    def create_or_update_payment_entry(self):
        total_payment = self.membership_fee

        # Create or update Library Payment entry
        existing_payment = frappe.get_all("Library Payment", filters={
            "library_member": self.library_member,
            "docstatus": 0
        }, limit=1)

        if existing_payment:
            payment_entry = frappe.get_doc("Library Payment", existing_payment[0].name)
        else:
            payment_entry = frappe.new_doc("Library Payment")

        payment_entry.library_member = self.library_member
        payment_entry.payment_amount = total_payment
        payment_entry.payment_method = "Cash"  # Set this dynamically if needed
        payment_entry.save()

        frappe.msgprint(f"Membership fee of ₹{total_payment} has been calculated.")

    def check_payment_status(self):
        if not self.paid:
            frappe.throw("Please make payment for Membership.")

    def on_submit(self):
        frappe.msgprint(f"Membership for {self.library_member} has been submitted successfully.")
   
    def check_active_membership(self):
        exists = frappe.db.exists(
           "Library Membership",
           { "library_member" : self.library_member,
             "docstatus": 1,
             "to_date" : (">" , self.from_date),
            } 
        )
        if exists:
            frappe.throw(" There is an active membership for this member")            