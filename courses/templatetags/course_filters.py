from django import template

register = template.Library()

@register.filter(name='addclass')
def addclass(field, css_class):
    """
    Add a CSS class to a form field.
    
    Args:
        field: The form field to add the class to
        css_class: The CSS class to add
    
    Returns:
        The form field with the CSS class added
    """
    return field.as_widget(attrs={"class": css_class})

@register.filter(name='filter_rating')
def filter_rating(reviews, rating):
    """
    Filter reviews by a specific rating value.
    
    Args:
        reviews: A list of review objects
        rating: The rating value to filter by
        
    Returns:
        The count of reviews with the specified rating
    """
    return sum(1 for review in reviews if review.rating == int(rating))

@register.filter(name='subtract')
def subtract(value, arg):
    """
    Subtracts the arg from the value.
    
    Args:
        value: The initial value
        arg: The value to subtract
    
    Returns:
        value - arg
    """
    try:
        return value - arg
    except (ValueError, TypeError):
        return 0
    return sum(1 for review in reviews if review.rating == int(rating))

@register.filter(name='percentage')
def percentage(value, total):
    """
    Calculate percentage of value out of total.
    
    Args:
        value: The numerator
        total: The denominator
        
    Returns:
        The percentage as a float
    """
    try:
        if int(total) == 0:
            return 0
        return (int(value) / int(total)) * 100
    except (ValueError, ZeroDivisionError):
        return 0

@register.filter(name='endswith')
def endswith(text, ends):
    """
    Check if a string ends with a specific substring.
    
    Args:
        text: The string to check
        ends: The substring to check for at the end
        
    Returns:
        True if the string ends with the substring, False otherwise
    """
    if text is None:
        return False
    return text.endswith(ends)

@register.filter(name='filesizeformat')
def filesizeformat(bytes_value):
    """
    Format a file size in bytes to a human-readable format.
    
    Args:
        bytes_value: The file size in bytes
        
    Returns:
        A human-readable string representing the file size
    """
    try:
        bytes_value = float(bytes_value)
        kb = bytes_value / 1024
        if kb < 1024:
            return f"{kb:.1f} KB"
        mb = kb / 1024
        if mb < 1024:
            return f"{mb:.1f} MB"
        gb = mb / 1024
        return f"{gb:.1f} GB"
    except (ValueError, TypeError):
        return "0 KB"
