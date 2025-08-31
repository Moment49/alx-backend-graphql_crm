#!/bin/bash
# ============================================================
# This script removes inactive customers from the CRM system.
# Inactive customers are defined as those who have not placed
# any orders in the last 12 months.
#
# The script is intended to be run as a cron job periodically.
# It logs the number of deleted customers along with a timestamp
# to a log file for auditing purposes.
# ============================================================

# Path to the Python virtual environment
PATH_ENV="/home/momentum49/alx-backend-graphql_crm/venv/bin/activate"

# Activate the virtual environment
source "$PATH_ENV"

# Path to Django's manage.py
PATH_MANGE="/home/momentum49/alx-backend-graphql_crm/manage.py"

# Run the cleanup logic inside Django shell
python3 "$PATH_MANGE" shell -c "
from crm.models import Customer
from datetime import timedelta, date

# Log file to store cleanup results
LOG_FILE = '/home/momentum49/alx-backend-graphql_crm/crm/cron_jobs/tmp/customer_cleanup_log.txt'

# Calculate the cutoff date: one year ago from today
one_year_ago = date.today() - timedelta(days=365)

# Query all customers who have NOT placed orders in the last year
cust_without_orders = Customer.objects.exclude(orders__order_date__date__gte=one_year_ago)

# Delete those customers and capture the number deleted
deleted_cus_count, _ = cust_without_orders.delete()

# Append the result with timestamp to the log file
with open(LOG_FILE, 'a') as f:
    f.write(f'{date.today()} - Deleted {deleted_cus_count} customers\n')
"