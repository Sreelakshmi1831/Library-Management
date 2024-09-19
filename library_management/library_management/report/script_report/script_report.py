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
        },
        {
            'fieldname': 'journal',
            'label': _('Journal (Shelf)'),
            'fieldtype': 'Select',
            'options': 'Motivation\nFantasy\nHorror\nFeelgood\nInvestigation thriller\nThriller\nSuspense\nPsycho thrillers\nSports\nComedy',
            'width': 150
        },
        {
            'fieldname': 'row_number',
            'label': _('Row Number'),
            'fieldtype': 'Int',
            'width': 100
        },
        {
            'fieldname': 'journal_prefix_row_number',
            'label': _('Journal Prefix Row Number'),
            'fieldtype': 'Data',
            'width': 150
        }
    ]

    # Create conditions dictionary based on filters
    conditions = {}

    if filters.get("author"):
        conditions["author"] = filters.get("author")

    if filters.get("article"):
        conditions["name"] = filters.get("article")  

    if filters.get("status"):
        conditions["status"] = filters.get("status")

    if filters.get("journal"):
        conditions["journal"] = filters.get("journal")

    # Fetch data from the Article doctype and include row number
    data = frappe.db.get_list(
        "Article",
        filters=conditions,
        fields=["author", "name as article", "status", "journal as journal", "row_number", "journal_prefix_row_number"],
        order_by="journal asc, row_number asc"  # Sort by journal and then by row number
    )

    return columns, data
