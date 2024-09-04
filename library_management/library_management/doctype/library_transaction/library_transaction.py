# Copyright (c) 2024, sreelakshmi and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class LibraryTransaction(Document):
    def before_submit(self):
        if self.type == "Issue":
            self.validate_issue()
            self.validate_maximum_limit()
            # set the article status to be Issued
            article = frappe.get_doc("Article", self.article)
            article.status = "Issued"
            article.save()

        elif self.type == "Return":
            self.validate_return()
            # set the article status to be Available
            article = frappe.get_doc("Article", self.article)
            article.status = "Available"
            article.save()
            
    def on_submit(self):
        if self.type == "Issue":
            doc = frappe.get_doc('Library Member', self.library_member)
            doc.append("issues_articles", {
                "issued_article": self.article,
                "issued_date": self.date
            })
            doc.save()
          
        elif self.type == "Return":
            doc = frappe.get_doc('Library Member' , self.library_member)
            for i in doc.issues_articles:
                if i.issued_article== self.article:
                    frappe.db.delete("Issued Articles", i.name)
                    break
            doc.save()       

    def validate_issue(self):
        self.validate_membership()
        article = frappe.get_doc("Article", self.article)
        # article cannot be issued if it is already issued
        if article.status == "Issued":
            frappe.throw("Article is already issued by another member")

    def validate_return(self):
        article = frappe.get_doc("Article", self.article)
        # article cannot be returned if it is not issued first
        if article.status == "Available":
            frappe.throw("Article cannot be returned without being issued first")

    def validate_membership(self):
        # check if a valid membership exist for this library member
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
    def custom_query(doctype, txt, searchfield, start, page_len, filters):
        today = frappe.utils.getdate()
        valid_members = frappe.db.sql(f"""SELECT library_member from tabLibrary Membership WHERE from_date <= {today} and to_date >= {today} and library_member like {'%' + txt + '%'}""")
        print(valid_members)
            
        return valid_members
