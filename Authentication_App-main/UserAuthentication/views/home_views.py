from django.shortcuts import render
from django.views.decorators.cache import never_cache

from UserAuthentication.decorators import login_required


@login_required
@never_cache  # so the browser back-button never shows a cached authenticated page after logout
def home(request):
    page_1_data = [
        ("Subtab 1", "Content for Subtab 1 of Page 1"),
        ("Subtab 2", "Content for Subtab 2 of Page 1"),
        ("Subtab 3", "Content for Subtab 3 of Page 1"),
        ("Subtab 4", "Content for Subtab 4 of Page 1"),
        ("Subtab 5", "Content for Subtab 5 of Page 1"),
    ]

    page_2_data = [
        ("Subtab 1", "Content for Subtab 1 of Page 2"),
        ("Subtab 2", "Content for Subtab 2 of Page 2"),
        ("Subtab 3", "Content for Subtab 3 of Page 2"),
        ("Subtab 4", "Content for Subtab 4 of Page 2"),
        ("Subtab 5", "Content for Subtab 5 of Page 2"),
    ]

    context = {
        'page_1_data': page_1_data,
        'page_2_data': page_2_data,
    }
    return render(request, 'UserAuthentication/home.html', context=context)
