"""
render_page was previously a simple_tag that built an entire block of HTML
by concatenating Python f-strings. That bypassed Django's autoescaping
(an XSS risk the moment page_title/tab_data ever come from user input or a
database) and made the markup impossible to edit with normal HTML tooling.

Converted to an inclusion_tag: the Python side now only prepares a context
dict, and the actual markup lives in partials/_tab_widget.html where it
belongs, with normal autoescaping applied to every value.
"""

from django import template

register = template.Library()


@register.inclusion_tag('UserAuthentication/partials/_tab_widget.html')
def render_page(page_title, tab_data, active=False):
    """
    Render one horizontal-tab's content: a title plus a set of vertical
    Bootstrap pill sub-tabs.

    tab_data: list of (subtab_title, subtab_content) tuples.
    active: whether this pane should be shown by default (i.e. it's the
            first/selected horizontal tab).
    """
    return {
        'page_title': page_title,
        'page_title_slug': page_title.replace(" ", "-").lower(),
        'tab_data': tab_data,
        'active': active,
    }
