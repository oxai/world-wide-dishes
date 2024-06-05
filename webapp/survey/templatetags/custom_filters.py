from django import template
import ast

register = template.Library()

@register.filter
def parse_list_string(value):
    try:
        # Safely evaluate the string representation of the list
        value_list = ast.literal_eval(value)
        # Check if the result is indeed a list
        if isinstance(value_list, list):
            # Join the list into a comma-separated string
            return ', '.join(element.replace('_', ' ') for element in value_list)
    except:
        # In case of any error, return the original value
        return value

    return value

@register.filter
def parse_occasion(value):
    try:
        if value == "Both":
            return "Regularly and Special Occasions"
    except:
        # In case of any error, return the original value
        return value

    return value
