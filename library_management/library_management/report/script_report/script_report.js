frappe.query_reports["Script Report"] = {
    "filters": [
        {
            "fieldname": "author",
            "label": __("Author"),
            "fieldtype": "Data",
            "default": ""
        },
        {
            "fieldname": "article",
            "label": __("Article"),
            "fieldtype": "Data",
            "default": ""
        },
        {
            "fieldname": "status",
            "label": __("Status"),
            "fieldtype": "Select",
            "options": "\nAvailable\nIssued\nReturn",
            "default": "Available"
        },
        {
            "fieldname": "journal",
            "label": __("Journal"),
            "fieldtype": "Select",
            "options": "\nMotivation\nFantasy\nHorror\nFeelgood\nInvestigation thriller\nThriller\nSuspense\nPsycho thrillers\nSports\nComedy",
            "default": ""
        },
        {
            "fieldname": "sort_by_row",
            "label": __("Sort by  Row Number"),
            "fieldtype": "Check",
            "default": 1  // Default to sorting by row number
        }
    ]
};
