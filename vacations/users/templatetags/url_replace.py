from django import template

register = template.Library()

@register.simple_tag
def url_replace(request, field, value):
    q = request.GET.copy()

    q.pop(field, None)

    q[field] = value
    return q.urlencode()