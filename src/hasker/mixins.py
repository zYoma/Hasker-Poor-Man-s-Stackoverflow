from typing import Optional

import base64
from django.core.files.base import ContentFile
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


class MockAvatarMixin:
    @staticmethod
    def get_mock_avatar():
        avatar_base64 = 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAYAAADgdz34AAAABHNCSVQIC' \
                        'AgIfAhkiAAAAAlwSFlzAAAApgAAAKYB3X3/OAAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vu' \
                        'PBoAAANCSURBVEiJtZZPbBtFFMZ/M7ubXdtdb1xSFyeilBapySVU8h8OoFaooFSqiihIVIpQBKci6KEg9Q6H9kov' \
                        'IHoCIVQJJCKE1ENFjnAgcaSGC6rEnxBwA04Tx43t2FnvDAfjkNibxgHxnWb2e/u992bee7tCa00YFsffekFY+nUzFtj' \
                        'W0LrvjRXrCDIAaPLlW0nHL0SsZtVoaF98mLrx3pdhOqLtYPHChahZcYYO7KvPFxvRl5XPp1sN3adWiD1ZAqD6XY' \
                        'K1b/dvE5IWryTt2udLFedwc1+9kLp+vbbpoDh+6TklxBeAi9TL0taeWpdmZzQDry0AcO+jQ12RyohqqoYoo8RDwJrU' \
                        '+qXkjWtfi8Xxt58BdQuwQs9qC/afLwCw8tnQbqYAPsgxE1S6F3EAIXux2oQFKm0ihMsOF71dHYx+f3NND68ghCu1YI' \
                        'oePPQN1pGRABkJ6Bus96CutRZMydTl+TvuiRW1m3n0eDl0vRPcEysqdXn+jsQPsrHMquGeXEaY4Yk4wxWcY5V/9scq' \
                        'OMOVUFthatyTy8QyqwZ+kDURKoMWxNKr2EeqVKcTNOajqKoBgOE28U4tdQl5p5bwCw7BWquaZSzAPlwjlithJtp3p' \
                        'TImSqQRrb2Z8PHGigD4RZuNX6JYj6wj7O4TFLbCO/Mn/m8R+h6rYSUb3ekokRY6f/YukArN979jcW+V/S8g0eT/' \
                        'N3VN3kTqWbQ428m9/8k0P/1aIhF36PccEl6EhOcAUCrXKZXXWS3XKd2vc/TRBG9O5ELC17MmWubD2nKhUKZa26Ba' \
                        '2+D3P+4/MNCFwg59oWVeYhkzgN/JDR8deKBoD7Y+ljEjGZ0sosXVTvbc6RHirr2reNy1OXd6pJsQ+gqjk8VWFYmHr' \
                        'wBzW/n+uMPFiRwHB2I7ih8ciHFxIkd/3Omk5tCDV1t+2nNu5sxxpDFNx+huNhVT3/zMDz8usXC3ddaHBj1GHj/As0' \
                        '8fwTS7Kt1HBTmyN29vdwAw+/wbwLVOJ3uAD1wi/dUH7Qei66PfyuRj4Ik9is+hglfbkbfR3cnZm7chlUWLdwmprt' \
                        'CohX4HUtlOcQjLYCu+fzGJH2QRKvP3UNz8bWk1qMxjGTOMThZ3kvgLI5AzFfo379UAAAAASUVORK5CYII='
        img_data = avatar_base64.split(',', maxsplit=1)[1]
        return ContentFile(base64.decodestring(img_data.encode()), name='temp.jpeg')


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
        if page.has_previous():
            prev_url = '?page={}'.format(page.previous_page_number())
        else:
            prev_url = ''

        if page.has_next():
            next_url = '?page={}'.format(page.next_page_number())
        else:
            next_url = ''

        return is_paginator, prev_url, next_url, parameters, last_page, page
