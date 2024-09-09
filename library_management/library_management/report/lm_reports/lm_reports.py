# Copyright (c) 2024, sreelakshmi and contributors
# For license information, please see license.txt

import frappe

def execute(filters=None):
    # Define the columns for the report
    columns = [
        {
            'fieldname': 'full_name',
            'label': 'Full Name',
            'fieldtype': 'Data'
        }, 
        {
            'fieldname': 'first_name',
            'label': 'First Name',
            'fieldtype': 'Data'
        },
        {
            'fieldname': 'email_address',
            'label': 'Email Address',
            'fieldtype': 'Data'
        },
        {
            'fieldname': 'library_member',
            'label': 'Library Member',
            'fieldtype': 'Link',
            'options': 'Library Member'
        },
        {
            'fieldname': 'membership_id',
            'label': 'Membership ID',
            'fieldtype': 'Data'
        },
        {
            'fieldname': 'from_date',
            'label': 'From Date',
            'fieldtype': 'Date'
        },
        {
            'fieldname': 'to_date',
            'label': 'To Date',
            'fieldtype': 'Date'
        },
        {
            'fieldname': 'paid',
            'label': 'Paid',
            'fieldtype': 'Data'
        },
        {
            'fieldname': 'phone',
            'label': 'Phone',
            'fieldtype': 'Data'
        },
        {
            'fieldname': 'article',
            'label': 'Article',
            'fieldtype': 'Data'
        },
        {
            'fieldname': 'status',
            'label': 'Status',
            'fieldtype': 'Data'
        },
        {
            'fieldname': 'transaction_date',
            'label': 'Transaction Date',
            'fieldtype': 'Date'
        },
        {
            'fieldname': 'payment_amount',
            'label': 'Payment Amount',
            'fieldtype': 'Currency'
        },
        {
            'fieldname': 'payment_method',
            'label': 'Payment Method',
            'fieldtype': 'Select'
        }
    ]
    
    # Base SQL query
    query = """
        SELECT
            lm.first_name AS first_name,
            lm.full_name AS full_name,
            lms.name AS membership_id,
            lms.from_date AS from_date,
            lms.to_date AS to_date,
            lms.paid AS paid,
            lm.email_address AS email_address,
            lm.phone AS phone,
            lt.library_member AS library_member,
            lt.article AS article,
            lt.type AS status,
            lt.date AS transaction_date,
            lt.amended_from AS amended_from,
            lp.payment_amount AS payment_amount,
            lp.payment_method AS payment_method
        FROM `tabLibrary Member` lm
        LEFT JOIN `tabLibrary Membership` lms
            ON lm.name = lms.library_member
        LEFT JOIN `tabLibrary Transaction` lt
            ON lm.name = lt.library_member
        LEFT JOIN `tabLibrary Payment` lp
            ON lm.name = lp.library_member
    """
    
    # Apply filters if any
    if filters:
        conditions = []
        if filters.get('first_name'):
            conditions.append(f"lm.first_name LIKE '%{filters.get('first_name')}%'")
        if filters.get('email_address'):
            conditions.append(f"lm.email_address LIKE '%{filters.get('email_address')}%'")
        if filters.get('phone'):
            conditions.append(f"lm.phone LIKE '%{filters.get('phone')}%'")
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
    
    # Execute the SQL query
    data = frappe.db.sql(query, as_dict=True)
    
    return columns, data
