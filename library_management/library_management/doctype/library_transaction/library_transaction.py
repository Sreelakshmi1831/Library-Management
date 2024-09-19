import frappe
from frappe.utils import getdate
from frappe.model.document import Document

class LibraryTransaction(Document):
    def before_submit(self):
        # Check if article_name is not empty
        if not self.article_name:
            frappe.throw("Please select at least one article in the 'Article Name' field before submitting the transaction.")

        notifications = []  # List to store all messages

        if self.type == "Issue":
            self.validate_issue()
            self.validate_maximum_limit()

            # Iterate over each article in the 'article_name' child table
            for article_row in self.article_name:
                article_doc = frappe.get_doc("Article", article_row.article_name)

                if article_doc.status != "Available":
                    frappe.throw(f"Article {article_row.article_name} is already issued or not available for issuing")

                article_doc.status = "Issued"
                article_doc.save()

                # Collect notification messages
                notifications.append(f"Article {article_row.article_name} issued successfully.")

        elif self.type == "Return":
            self.validate_return()

            # Iterate over each article in the 'article_name' child table
            for article_row in self.article_name:
                article_doc = frappe.get_doc("Article", article_row.article_name)

                if article_doc.status != "Issued":
                    frappe.throw(f"Article {article_row.article_name} is not issued or already returned")

                article_doc.status = "Available"
                article_doc.save()

                # Collect notification messages
                notifications.append(f"Article {article_row.article_name} returned successfully.")

        # Display all notifications in one message
        if notifications:
            frappe.msgprint("\n".join(notifications))

    def on_submit(self):
        if self.type == "Issue":
           
            # Handling article issue
            member_doc = frappe.get_doc('Library Member', self.library_member)
            for article_row in self.article_name:
                member_doc.append("issues_article", {
                    "issued_article": article_row.article_name,
                    "issued_date": self.date
                })
            member_doc.save()
            frappe.msgprint(f"Issued articles to member {self.library_member}.")

        elif self.type == "Return":
            
            member_doc = frappe.get_doc('Library Member', self.library_member)
            for article_row in self.article_name:
                fine = 0

                for issue_row in member_doc.issues_article:
                    if issue_row.issued_article == article_row.article_name:
                        issue_date = getdate(issue_row.issued_date)
                        return_date = getdate(self.date)
                        days_diff = (return_date - issue_date).days
                        frappe.msgprint(f"Days between issue and return: {days_diff}")

                        # If return date exceeds 7 days, impose a fine
                        if days_diff > 7:
                            late_days = days_diff - 7
                            fine = late_days * 10  # Fine calculation
                            issue_row.fine_amount = fine
                            frappe.msgprint(f"A fine of {fine} rupees has been imposed for late return.")

                        # Add fine details to the Fine Pay child table only if fine exists
                        if fine > 0:
                            member_doc.append("fine_amount", {
                                "library_member": self.library_member,
                                "article": article_row.article_name,
                                "return_date": self.date,
                                "fine_amount": fine
                            })
                            frappe.msgprint(f"Added fine details for article {article_row.article_name}.")

                        # Remove the article from the issues_article child table
                        member_doc.remove(issue_row)
                        break

            member_doc.save()
            frappe.msgprint(f"Returned articles by member {self.library_member}.")

    def validate_issue(self):
        self.validate_membership()
        for article_row in self.article_name:
            article_doc = frappe.get_doc("Article", article_row.article_name)
            if article_doc.status == "Issued":
                frappe.throw(f"Article {article_row.article_name} is already issued by another member")

    def validate_return(self):
        for article_row in self.article_name:
            article_doc = frappe.get_doc("Article", article_row.article_name)
            if article_doc.status == "Available":
                frappe.throw(f"Article {article_row.article_name} cannot be returned without being issued first")

    def validate_membership(self):
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
        member = frappe.get_doc("Library Member", self.library_member)
        total_fine = 0
        for fine_amount_entry in member.fine_amount:
            if fine_amount_entry.fine_amount > 0:
                total_fine += fine_amount_entry.fine_amount

        if total_fine > 0:
            frappe.throw(f"This member has an outstanding fine of {total_fine}. Please clear the fine before performing any transactions.")
