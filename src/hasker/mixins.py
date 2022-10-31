from typing import Optional

from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, reverse


class RatingMixin:
    def change_rating(self, is_like):
        # Изменяем рейтинг в соответствии с оценкой
        self.rating = self.rating + 1 if is_like else self.rating - 1
        self.save(update_fields=['rating'])

    def rollback_rating(self, is_like):
        # Снимаем предыдущую оценку пользователя
        self.rating = self.rating - 1 if is_like else self.rating + 1
        self.save(update_fields=['rating'])


class RatingViewMixin:
    object_model = None
    rating_model = None
    field_name: Optional[str] = None

    def post(self, request, id):
        from .views import Answer  # circular import)
        obj = get_object_or_404(self.object_model, id=id)
        user = request.user
        like = request.POST.get('like')
        likes = {'poz': True, 'neg': False}
        like = likes[like]

        data_for_get = {self.field_name: obj, 'user': user}
        rating, created = self.rating_model.objects.get_or_create(
            **data_for_get,
            defaults={'is_like': like, **data_for_get},
        )
        if created:
            obj.change_rating(rating.is_like)
        # При изменении оценки
        elif rating.is_like != like:
            # Снимаем предыдущую оценку пользователя
            obj.rollback_rating(rating.is_like)
            # сохраняем новую оценку
            rating.is_like = like
            rating.save()
            obj.change_rating(rating.is_like)

        redirect_obj_id = obj.question.id if self.object_model is Answer else obj.id
        return redirect(reverse('hasker:answer_url', kwargs={'id': redirect_obj_id}))


class CustomPaginator:
    per_page: Optional[int] = None

    def get_paginator_objects(self, *args, **kwargs):
        raise NotImplementedError

    def get_context_data(self, *args, **kwargs):
        objects = self.get_paginator_objects(*args, **kwargs)
        is_paginator, prev_url, next_url, parameters, last_page, page = self.get_paginator(
            objects,
            self.per_page
        )
        return {
            'objects': page,
            'is_paginator': is_paginator,
            'prev_url': prev_url,
            'next_url': next_url,
            'parameters': parameters,
            'page_end': last_page,
        }

    def get_paginator(self, objs, objs_per_page):
        """ Пагинатор для использования в различных представлениях. """
        get_copy = self.request.GET.copy()
        parameters = get_copy.pop('page', True) and get_copy.urlencode()
        paginator = Paginator(objs, objs_per_page)
        last_page = paginator.num_pages
        page_number = self.request.GET.get('page', 1)
        page = paginator.get_page(page_number)
        is_paginator = page.has_other_pages()

        prev_redirect_page = page.previous_page_number() if page.has_previous() else ''
        prev_url = '?page={}'.format(prev_redirect_page)

        next_redirect_page = page.next_page_number() if page.has_next() else ''
        next_url = '?page={}'.format(next_redirect_page)

        return is_paginator, prev_url, next_url, parameters, last_page, page
