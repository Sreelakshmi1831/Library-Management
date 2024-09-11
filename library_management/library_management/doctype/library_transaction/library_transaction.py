import frappe
from frappe.utils import getdate
from frappe.model.document import Document

class LibraryTransaction(Document):
    def before_submit(self):
        if self.type == "Issue":
            self.validate_issue()
            self.validate_maximum_limit()

            # Set the article status to "Issued" only if it's available
            article = frappe.get_doc("Article", self.article)
            frappe.msgprint(f"Article status before issuing: {article.status}")

            if article.status != "Available":
                frappe.throw("Article is already issued or not available for issuing")

            article.status = "Issued"
            article.save()
            frappe.msgprint(f"Article {self.article} issued successfully.")

        elif self.type == "Return":
            self.validate_return()

            # Set the article status to "Available"
            article = frappe.get_doc("Article", self.article)

            if article.status != "Issued":
                frappe.throw("Article is not issued or already returned")

            article.status = "Available"
            article.save()
            frappe.msgprint(f"Article {self.article} returned successfully.")

    def on_submit(self):
        if self.type == "Issue":
            frappe.msgprint("Processing issue on submit")
            # Handling article issue
            doc = frappe.get_doc('Library Member', self.library_member)
            doc.append("issues_articles", {
                "issued_article": self.article,
                "issued_date": self.date  # Store the issue date
            })
            doc.save()
            frappe.msgprint(f"Issued article {self.article} to member {self.library_member}.")

        elif self.type == "Return":
            frappe.msgprint("Processing return on submit")
            # Handling article return
            doc = frappe.get_doc('Library Member', self.library_member)
            fine = 0  # Initialize the fine to 0

            for i in doc.issues_articles:
                if i.issued_article == self.article:
                    issue_date = getdate(i.issued_date)  # Convert to date object
                    return_date = getdate(self.date)  # Convert to date object

                    # Calculate days between issue date and return date
                    days_diff = (return_date - issue_date).days
                    frappe.msgprint(f"Days between issue and return: {days_diff}")

                    # If return date exceeds 7 days, impose a fine for late return
                    if days_diff > 7:
                        late_days = days_diff - 7
                        fine = late_days * 10  # Apply fine of 10 currency units per day
                        i.fine_amount = fine
                        frappe.msgprint(f"A fine of {fine} rupees has been imposed for late return.")

                    # Add fine details to the Fine Pay child table, including Member field
                    doc.append("fine_amount", {
                        "member": self.library_member, 
                        "article": self.article,
                        "return_date": self.date,
                        "fine_amount": fine  # Ensure the correct field name is used
                    })

                    frappe.msgprint(f"Added fine details for article {self.article} to Fine Pay table.")

                    # Remove the article from the issues_articles child table
                    doc.remove(i)
                    break

            doc.save()
            frappe.msgprint(f"Returned article {self.article} by member {self.library_member}.")

    def validate_issue(self):
        self.validate_membership()
        article = frappe.get_doc("Article", self.article)
        # Article cannot be issued if it is already issued
        if article.status == "Issued":
            frappe.throw("Article is already issued by another member")

    def validate_return(self):
        article = frappe.get_doc("Article", self.article)
        # Article cannot be returned if it is not issued first
        if article.status == "Available":
            frappe.throw("Article cannot be returned without being issued first")

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
import frappe
from frappe.utils import getdate
from frappe.model.document import Document

class LibraryTransaction(Document):
    def before_submit(self):
        if self.type == "Issue":
            self.validate_issue()
            self.validate_maximum_limit()

            # Set the article status to "Issued" only if it's available
            article = frappe.get_doc("Article", self.article)
            frappe.msgprint(f"Article status before issuing: {article.status}")

            if article.status != "Available":
                frappe.throw("Article is already issued or not available for issuing")

            article.status = "Issued"
            article.save()
            frappe.msgprint(f"Article {self.article} issued successfully.")

        elif self.type == "Return":
            self.validate_return()

            # Set the article status to "Available"
            article = frappe.get_doc("Article", self.article)

            if article.status != "Issued":
                frappe.throw("Article is not issued or already returned")

            article.status = "Available"
            article.save()
            frappe.msgprint(f"Article {self.article} returned successfully.")

    def on_submit(self):
        if self.type == "Issue":
            frappe.msgprint("Processing issue on submit")
            # Handling article issue
            doc = frappe.get_doc('Library Member', self.library_member)
            doc.append("issues_articles", {
                "issued_article": self.article,
                "issued_date": self.date  # Store the issue date
            })
            doc.save()
            frappe.msgprint(f"Issued article {self.article} to member {self.library_member}.")

        elif self.type == "Return":
            frappe.msgprint("Processing return on submit")
            # Handling article return
            doc = frappe.get_doc('Library Member', self.library_member)
            fine = 0  # Initialize the fine to 0

            for i in doc.issues_articles:
                if i.issued_article == self.article:
                    issue_date = getdate(i.issued_date)  # Convert to date object
                    return_date = getdate(self.date)  # Convert to date object

                    # Calculate days between issue date and return date
                    days_diff = (return_date - issue_date).days
                    frappe.msgprint(f"Days between issue and return: {days_diff}")

                    # If return date exceeds 7 days, impose a fine for late return
                    if days_diff > 7:
                        late_days = days_diff - 7
                        fine = late_days * 10  # Apply fine of 10 currency units per day
                        i.fine_amount = fine
                        frappe.msgprint(f"A fine of {fine} rupees has been imposed for late return.")

                    # Add fine details to the Fine Pay child table, including Member field
                    doc.append("fine_amount", {
                        "member": self.library_member, 
                        "article": self.article,
                        "return_date": self.date,
                        "fine_amount": fine  # Ensure the correct field name is used
                    })

                    frappe.msgprint(f"Added fine details for article {self.article} to Fine Pay table.")

                    # Remove the article from the issues_articles child table
                    doc.remove(i)
                    break

            doc.save()
            frappe.msgprint(f"Returned article {self.article} by member {self.library_member}.")

    def validate_issue(self):
        self.validate_membership()
        article = frappe.get_doc("Article", self.article)
        # Article cannot be issued if it is already issued
        if article.status == "Issued":
            frappe.throw("Article is already issued by another member")

    def validate_return(self):
        article = frappe.get_doc("Article", self.article)
        # Article cannot be returned if it is not issued first
        if article.status == "Available":
            frappe.throw("Article cannot be returned without being issued first")

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
import frappe
from frappe.utils import getdate
from frappe.model.document import Document

class LibraryTransaction(Document):
    def before_submit(self):
        if self.type == "Issue":
            self.validate_issue()
            self.validate_maximum_limit()

            # Set the article status to "Issued" only if it's available
            article = frappe.get_doc("Article", self.article)
            frappe.msgprint(f"Article status before issuing: {article.status}")

            if article.status != "Available":
                frappe.throw("Article is already issued or not available for issuing")

            article.status = "Issued"
            article.save()
            frappe.msgprint(f"Article {self.article} issued successfully.")

        elif self.type == "Return":
            self.validate_return()

            # Set the article status to "Available"
            article = frappe.get_doc("Article", self.article)

            if article.status != "Issued":
                frappe.throw("Article is not issued or already returned")

            article.status = "Available"
            article.save()
            frappe.msgprint(f"Article {self.article} returned successfully.")

    def on_submit(self):
        if self.type == "Issue":
            frappe.msgprint("Processing issue on submit")
            # Handling article issue
            doc = frappe.get_doc('Library Member', self.library_member)
            doc.append("issues_articles", {
                "issued_article": self.article,
                "issued_date": self.date  # Store the issue date
            })
            doc.save()
            frappe.msgprint(f"Issued article {self.article} to member {self.library_member}.")

        elif self.type == "Return":
            frappe.msgprint("Processing return on submit")
            # Handling article return
            doc = frappe.get_doc('Library Member', self.library_member)
            fine = 0  # Initialize the fine to 0

            for i in doc.issues_articles:
                if i.issued_article == self.article:
                    issue_date = getdate(i.issued_date)  # Convert to date object
                    return_date = getdate(self.date)  # Convert to date object

                    # Calculate days between issue date and return date
                    days_diff = (return_date - issue_date).days
                    frappe.msgprint(f"Days between issue and return: {days_diff}")

                    # If return date exceeds 7 days, impose a fine for late return
                    if days_diff > 7:
                        late_days = days_diff - 7
                        fine = late_days * 10  # Apply fine of 10 currency units per day
                        i.fine_amount = fine
                        frappe.msgprint(f"A fine of {fine} rupees has been imposed for late return.")

                    # Add fine details to the Fine Pay child table, including Member field
                    doc.append("fine_amount", {
                        "member": self.library_member, 
                        "article": self.article,
                        "return_date": self.date,
                        "fine_amount": fine  # Ensure the correct field name is used
                    })

                    frappe.msgprint(f"Added fine details for article {self.article} to Fine Pay table.")

                    # Remove the article from the issues_articles child table
                    doc.remove(i)
                    break

            doc.save()
            frappe.msgprint(f"Returned article {self.article} by member {self.library_member}.")

    def validate_issue(self):
        self.validate_membership()
        article = frappe.get_doc("Article", self.article)
        # Article cannot be issued if it is already issued
        if article.status == "Issued":
            frappe.throw("Article is already issued by another member")

    def validate_return(self):
        article = frappe.get_doc("Article", self.article)
        # Article cannot be returned if it is not issued first
        if article.status == "Available":
            frappe.throw("Article cannot be returned without being issued first")

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
