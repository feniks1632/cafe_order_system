from django import template


register = template.Library()

@register.filter
def format_price(value) -> str:
    """
    Форматирует цену с двумя десятичными знаками.
    """
    try:
        return f"{float(value):.2f}"
    except (ValueError, TypeError):
        return "0.00"