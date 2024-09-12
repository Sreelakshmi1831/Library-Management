import frappe
from frappe.utils import getdate
from frappe.model.document import Document

class LibraryTransaction(Document):
    def before_submit(self):
        if self.type == "Issue":
            self.validate_issue()
            self.validate_maximum_limit()

            # Iterate over each article in the 'article_name' child table
            for article_row in self.article_name:
                article_doc = frappe.get_doc("Article", article_row.article_name)
                frappe.msgprint(f"Article status before issuing: {article_doc.status}")

                if article_doc.status != "Available":
                    frappe.throw(f"Article {article_row.article_name} is already issued or not available for issuing")

                article_doc.status = "Issued"
                article_doc.save()
                frappe.msgprint(f"Article {article_row.article_name} issued successfully.")

        elif self.type == "Return":
            self.validate_return()

            # Iterate over each article in the 'article_name' child table
            for article_row in self.article_name:
                article_doc = frappe.get_doc("Article", article_row.article_name)

                if article_doc.status != "Issued":
                    frappe.throw(f"Article {article_row.article_name} is not issued or already returned")

                article_doc.status = "Available"
                article_doc.save()
                frappe.msgprint(f"Article {article_row.article_name} returned successfully.")

    def on_submit(self):
        if self.type == "Issue":
            frappe.msgprint("Processing issue on submit")
            # Handling article issue
            member_doc = frappe.get_doc('Library Member', self.library_member)
            for article_row in self.article_name:
                member_doc.append("issues_article", {  # Correct field name
                    "issued_article": article_row.article_name,
                    "issued_date": self.date  # Store the issue date
                })
            member_doc.save()
            frappe.msgprint(f"Issued articles to member {self.library_member}.")

        elif self.type == "Return":
            frappe.msgprint("Processing return on submit")
            # Handling article return
            member_doc = frappe.get_doc('Library Member', self.library_member)
            for article_row in self.article_name:
                fine = 0  # Initialize the fine to 0

                for issue_row in member_doc.issues_article:  # Correct field name
                    if issue_row.issued_article == article_row.article_name:
                        issue_date = getdate(issue_row.issued_date)  # Convert to date object
                        return_date = getdate(self.date)  # Convert to date object

                        # Calculate days between issue date and return date
                        days_diff = (return_date - issue_date).days
                        frappe.msgprint(f"Days between issue and return: {days_diff}")

                        # If return date exceeds 7 days, impose a fine for late return
                        if days_diff > 7:
                            late_days = days_diff - 7
                            fine = late_days * 10  # Apply fine of 10 currency units per day
                            issue_row.fine_amount = fine
                            frappe.msgprint(f"A fine of {fine} rupees has been imposed for late return.")

                        # Add fine details to the Fine Pay child table, including Member field
                        member_doc.append("fine_amount", {
                            "library_member": self.library_member,  # Add this field
                            "article": article_row.article_name,
                            "return_date": self.date,
                            "fine_amount": fine  # Ensure the correct field name is used
                        })

                        frappe.msgprint(f"Added fine details for article {article_row.article_name} to Fine Pay table.")

                        # Remove the article from the issues_article child table
                        member_doc.remove(issue_row)
                        break

            member_doc.save()
            frappe.msgprint(f"Returned articles by member {self.library_member}.")

    def validate_issue(self):
        self.validate_membership()
        for article_row in self.article_name:
            article_doc = frappe.get_doc("Article", article_row.article_name)
            # Article cannot be issued if it is already issued
            if article_doc.status == "Issued":
                frappe.throw(f"Article {article_row.article_name} is already issued by another member")

    def validate_return(self):
        for article_row in self.article_name:
            article_doc = frappe.get_doc("Article", article_row.article_name)
            # Article cannot be returned if it is not issued first
            if article_doc.status == "Available":
                frappe.throw(f"Article {article_row.article_name} cannot be returned without being issued first")

    def validate_membership(self):
        # Check if a valid membership exists for this library member
        valid_membership = frappe.db.exists(
            "Library Membership",
            {
                "library_member": self.library_member,
                "docstatus": 1,
                "from_date": ("<=", self.date),
                "to_date": (">=", self.date),
            },
        )
        if not valid_membership:
            frappe.throw("The member does not have a valid membership")

    def validate_maximum_limit(self):
        max_articles = frappe.db.get_single_value("Library Settings", "max_articles")
        count = frappe.db.count(
            "Library Transaction",
            {"library_member": self.library_member, "type": "Issue", "docstatus": 1},
        )
        if count >= max_articles:
            frappe.throw("Maximum limit reached for issuing articles")

    def before_save(self):
        self.validate_fine_status()

    def validate_fine_status(self):
        # Fetch the library member document
        member = frappe.get_doc("Library Member", self.library_member)

        # Check if the member has any outstanding fines
        total_fine = 0
        for fine_amount_entry in member.fine_amount:  # Correct reference to the 'fine_amount' child table
            if fine_amount_entry.fine_amount > 0:  # Check if there's an unpaid fine
                total_fine += fine_amount_entry.fine_amount

        # If the member has outstanding fines, raise an error
        if total_fine > 0:
            frappe.throw(f"This member has an outstanding fine of {total_fine}. Please clear the fine before performing any transactions.")

    @staticmethod
    def custom_query(doctype, txt, filters, limit_start, limit_page_length=20):
        # Example of a custom query method
        query = """
            SELECT `tabLibrary Transaction`.name, `tabLibrary Transaction`.date
            FROM `tabLibrary Transaction`
            WHERE `tabLibrary Transaction`.docstatus = 1
            AND `tabLibrary Transaction`.library_member LIKE %s
            LIMIT %s, %s
        """
        return frappe.db.sql(query, (f"%{txt}%", limit_start, limit_page_length), as_dict=True)
