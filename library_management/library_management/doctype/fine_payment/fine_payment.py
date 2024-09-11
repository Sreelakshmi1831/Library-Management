import frappe
from frappe.model.document import Document

class FinePayment(Document):
    def before_save(self):
        # Calculate the total fine amount before saving the document
        self.set_fine_amount()

    def set_fine_amount(self):
        # Fetch the library member document using the linked 'library_member' field
        member = frappe.get_doc("Library Member", self.library_member)

        # Calculate the total fine amount from the 'fine_amount' field in the 'fine_amount' child table
        total_fine = sum(entry.fine_amount for entry in member.fine_amount if entry.fine_amount > 0)

        # Set the total fine amount to the 'fine_amount' field in the 'Fine Payment' doctype
        self.fine_amount = total_fine

    def on_submit(self):
        # After the fine is paid, clear the fines from the Fine Amount table
        self.clear_fines_from_fine_amount()

    def clear_fines_from_fine_amount(self):
        # Fetch the library member document
        member = frappe.get_doc("Library Member", self.library_member)

        # Get the list of fines that need to be cleared
        to_remove = [entry for entry in member.fine_amount if entry.fine_amount > 0]

        # Remove the entries from the 'fine_amount' child table
        for entry in to_remove:
            member.fine_amount.remove(entry)

        # Save the updated library member document
        member.save()

        # Display a message to the user
        frappe.msgprint(f"All fines for member {self.library_member} have been cleared.")
        
@frappe.whitelist()
def get_total_fine_amount(library_member):
    # Fetch the library member document
    member = frappe.get_doc("Library Member", library_member)

    # Calculate total fine amount from the 'fine_amount' child table
    total_fine = sum(entry.fine_amount for entry in member.fine_amount if entry.fine_amount > 0)

    # Return the total fine amount
    return {"fine_amount": total_fine}
