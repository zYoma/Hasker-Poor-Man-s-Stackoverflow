from django.core.paginator import Paginator


def get_paginator(request, objs, objs_per_page):
    """ Пагинатор для использования в различных представлениях. """
    get_copy = request.GET.copy()
    parameters = get_copy.pop('page', True) and get_copy.urlencode()
    paginator = Paginator(objs, objs_per_page)
    last_page = paginator.num_pages
    page_number = request.GET.get('page', 1)
    page = paginator.get_page(page_number)
    is_paginator = page.has_other_pages()
    if page.has_previous():
        prev_url = '?page={}'.format(page.previous_page_number())
    else:
        prev_url = ''

    if page.has_next():
        next_url = '?page={}'.format(page.next_page_number())
    else:
        next_url = ''

    return is_paginator, prev_url, next_url, parameters, last_page, page
