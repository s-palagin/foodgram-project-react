## FOODGRAM - "Продуктовый помощник"
Сервис позволяет публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список "Избранное", а перед походом в магазин - скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.

![workflow](https://github.com/s-palagin/foodgram-project-react/actions/workflows/main.yml/badge.svg)

[![Python](https://img.shields.io/badge/-Python-464646?style=flat-square&logo=Python)](https://www.python.org/) [![Django](https://img.shields.io/badge/-Django-464646?style=flat-square&logo=Django)](https://www.djangoproject.com/) [![Django REST Framework](https://img.shields.io/badge/-Django%20REST%20Framework-464646?style=flat-square&logo=Django%20REST%20Framework)](https://www.django-rest-framework.org/) [![PostgreSQL](https://img.shields.io/badge/-PostgreSQL-464646?style=flat-square&logo=PostgreSQL)](https://www.postgresql.org/) [![Nginx](https://img.shields.io/badge/-NGINX-464646?style=flat-square&logo=NGINX)](https://nginx.org/ru/) [![gunicorn](https://img.shields.io/badge/-gunicorn-464646?style=flat-square&logo=gunicorn)](https://gunicorn.org/) [![docker](https://img.shields.io/badge/-Docker-464646?style=flat-square&logo=docker)](https://www.docker.com/) [![Docker-compose](https://img.shields.io/badge/-Docker%20compose-464646?style=flat-square&logo=Docker)](https://www.docker.com/) [![GitHub%20Actions](https://img.shields.io/badge/-GitHub%20Actions-464646?style=flat-square&logo=GitHub%20actions)](https://github.com/features/actions) [![Yandex.Cloud](https://img.shields.io/badge/-Yandex.Cloud-464646?style=flat-square&logo=Yandex.Cloud)](https://cloud.yandex.ru/)
##  Запуск проекта в Docker контейнере

* Установите Docker.

Параметры запуска описаны в файлах `docker-compose.yml` и `nginx.conf` которые находятся в директории `infra/`.
* Cоздайте файл `.env` в директории `/infra/` с содержанием:
```
SECRET_KEY=секретный ключ django
DB_ENGINE=django.db.backends.postgresql
DB_NAME=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432
DEBUG=False
```
* Запустите docker compose:
```bash
docker-compose up -d --build
```
> После сборки запускаются 3 контейнера:
> 1. контейнер базы данных **db**
> 2. контейнер приложения **backend**
> 3. контейнер web-сервера **nginx**
* Примените миграции:
```bash
docker-compose exec backend python manage.py migrate
```
* Загрузите ингредиенты:
```bash
docker-compose exec backend python manage.py loaddata data/ingredients.json
```
* Создайте администратора:
```bash
docker-compose exec backend python manage.py createsuperuser
```
* Соберите статику:
```bash
docker-compose exec backend python manage.py collectstatic --noinput
```

##  Пользовательские роли в проекте
1. Анонимный пользователь
2. Аутентифицированный пользователь
3. Администратор
###  Анонимные пользователи могут:
1. Просматривать список рецептов;
2. Просматривать отдельные рецепты;
3. Фильтровать рецепты по тегам;
4. Создавать аккаунт.
###  Аутентифицированные пользователи могут:
1. Получать данные о своей учетной записи;
2. Изменять свой пароль;
3. Просматривать, публиковать, удалять и редактировать свои рецепты;
4. Добавлять понравившиеся рецепты в избранное и удалять из избранного;
5. Добавлять рецепты в список покупок и удалять из списка;
6. Подписываться и отписываться на авторов;
7. Скачать список покупок
### Администраторы могут:
1. Получить доступ к административной панели;
2. Изменять пароль любого пользователя;
3. Создавать/блокировать/удалять аккаунты пользователей;
4. Редактировать/удалять  **любые**  рецепты;
5. Добавлять/удалять/редактировать ингредиенты;
6. Добавлять/удалять/редактировать теги.

###  Сайт

Сайт доступен по ссылке:

[Foodgram](http://foodgram-project.ddns.net/)

###  Документация к API

API документация доступна по ссылке (создана с помощью redoc):

[Foodgram/redoc](http://foodgram-project.ddns.net/api/docs/)
