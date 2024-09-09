from __future__ import unicode_literals
import frappe
from frappe import _

def execute(filters=None):
    # Define the columns for the report
    columns = [
        {
            'fieldname': 'author',
            'label': _('Author'),
            'fieldtype': 'Data',
            'width': 150
        },
        {
            'fieldname': 'article',
            'label': _('Article'),
            'fieldtype': 'Data',
            'width': 150
        },
        {
            'fieldname': 'status',
            'label': _('Status'),
            'fieldtype': 'Select',
            'options': 'Available\nIssued\nReturn',
            'width': 100
        }
    ]

    
    conditions = {}
    
    if filters.get("author"):
        conditions["author"] = filters.get("author")

    if filters.get("article"):
        conditions["name"] = filters.get("article")  

    if filters.get("status"):
        conditions["status"] = filters.get("status")

    
    data = frappe.db.get_list(
        "Article", 
        filters=conditions,  
        fields=["author", "name as article", "status"], 
        as_list=False  
    )

    return columns, data
