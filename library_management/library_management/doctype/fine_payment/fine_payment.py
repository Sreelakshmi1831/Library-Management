import frappe
from frappe.model.document import Document

class FinePayment(Document):
    def before_save(self):
        self.set_fine_amount()

    def set_fine_amount(self):
        # Fetch the library member document
        member = frappe.get_doc("Library Member", self.library_member)

        # Calculate total fine amount
        total_fine = sum(entry.fine_amount for entry in member.fine_amount if entry.fine_amount > 0)

        # Set the total fine amount to the field
        self.fine_amount = total_fine
        
        
@frappe.whitelist()
def get_total_fine_amount(library_member):
    # Fetch the library member document
    member = frappe.get_doc("Library Member", library_member)

    # Calculate total fine amount
    total_fine = sum(entry.fine_amount for entry in member.fine_amount if entry.fine_amount > 0)

    return {"fine_amount": total_fine}
