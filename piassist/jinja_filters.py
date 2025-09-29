from flask import Blueprint

jinja_filters = Blueprint('jinja_filter', __name__)

@jinja_filters.app_template_filter()
# def format_currency(value):
#     if value:
#         return "${:,.2f}".format(value)
# In jinja_filters.py
def format_currency(value):
    try:
        # Ensure the value is a number (either int or float)
        if value is None:
            return "$0.00"  # Return a default value if None
        value = float(value)  # Convert to float if it's not already a number
        return "${:,.2f}".format(value)
    except (ValueError, TypeError):
        return "$0.00"  # Return a default value if the value is invalid
