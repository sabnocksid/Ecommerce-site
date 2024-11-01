from django import template

register = template.Library()

@register.filter
def div(value, arg):
    return float(value) / arg if arg != 0 else 0.0

@register.filter
def multiply(value, arg):
    return float(value) * arg

@register.filter
def star_rating(value):
    if value is None or value < 0:
        return "No ratings yet"

    full_stars = int(value)  # Count of full stars
    half_star = 1 if value - full_stars >= 0.5 else 0  # Half star if applicable
    empty_stars = 5 - full_stars - half_star  # Remaining empty stars

    full_star_icon = '<i class="fa-solid fa-star"></i>'
    half_star_icon = '<i class="fa-solid fa-star-half"></i>'
    empty_star_icon = '<i class="fa-regular fa-star"></i>'

    return (full_star_icon * full_stars + half_star_icon * half_star + empty_star_icon * empty_stars)