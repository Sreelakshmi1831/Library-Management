// Copyright (c) 2024, sreelakshmi and contributors
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
            "options": "\nAvailable\nIssued\nReturn",  // Add relevant status options here
            "default": "Available"
        }
    ]
};
