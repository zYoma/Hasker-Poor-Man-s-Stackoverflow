# Hasker

#### Приложение написано в качестве учебного проекта.
Q&A сайт, аналог stackoverflow.com

### Стек
- python 3.8
- nginx
- uwsgi
- postgres


### Запуск
Перед запуском создать файл .env c переменными окружения и выполнить миграции. Добавить IP в ALLOWED_HOSTS.

``` make prod_up ```

### Остановка
``` make prod_down ```

### Запуск миграций 
``` make app_migrate ```


### Переменные окружения

| Название| Описание                                  | Пример значения                                                    |
|---|-------------------------------------------|--------------------------------------------------------------------|
| SECRET_KEY | соль для паролей                          | django-insecure-nl#-cslak8w0^o#t6plm1i55py)##258$#216r_m1=n4=eng8_ |
| DEBUG | флаг включенного дебага                   | true                                                               |
| POSTGRES_PASSWORD | пороль от БД                              | passwird                                                           |
| POSTGRES_DB | название БД                               | postgres                                                           |
| POSTGRES_USER | пользователь БД                           | postgres                                                           |
| POSTGRES_HOST | хост БД                                   | db                                                                 |
| POSTGRES_PORT | порт БД                                   | 5432                                                               |
| NGINX_PUBLIC_PORT | порт на котором nginx будет ждать запросы | 80                                                                 |
| EMAIL | почта от которой будут приходить письма   | ma@gmail.com                                                       |
| EMAIL_HOST_PASSWORD | пароль от почты                           | pass                                                               |
| DOCKER_COMPOSE_FILE | путь до докер композ файла.               | docker-compose.yml                                                 |
| SERVICE_NAME | название сервиса в докер композ файле     | web                                                                |

