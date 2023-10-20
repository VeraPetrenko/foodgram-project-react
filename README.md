# Foodgram
Проект Foodgram предназначен для публикации и просмотра рецептов, составления списка покупок.

### Установка:
Клонировать репозиторий и перейти в него в командной строке:

```
git@github.com:VeraPetrenko/foodgram-project-react.git
cd foodgram
```

```
Запустить проект локально:
```
docker compose -f docker-compose.yml
```

Запустить проект на удаленном сервере:
- Перейти в директорию foodgram, выполнить команды по запуску контейнеров, применить миграции и собрать статику:
```
cd foodgram
sudo docker compose -f docker-compose.yml pull
sudo docker compose -f docker-compose.yml down
sudo docker compose -f docker-compose.yml up -d
sudo docker compose -f docker-compose.yml exec backend python manage.py migrate
sudo docker compose -f docker-compose.yml exec backend python manage.py collectstatic
sudo docker compose -f docker-compose.yml exec backend cp -r /app/static/. /backend_static/static/

```

Сайт будет доступен по домену:
<https://foodgram.serveftp.com/>

### Основные технологии
- django3.2.3
- djangorestframework 3.12.4
- noip.com
- gunicorn
- nginx

### Авторы
Vera Petrenko & Yandex Practicum