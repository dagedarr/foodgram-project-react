# foodgram
![example workflow](https://github.com/dagedarr/foodgram-project-react/actions/workflows/main.yml/badge.svg)

# Примеры запросов:
admin-login : arnat
admin-password : arnat


http://158.160.44.148/
http://158.160.44.148/api/
http://158.160.44.148/admin/

    
Продуктовый помощник - сайт, на котором пользователи будут публиковать рецепты, добавлять чужие рецепты в избранное и подписываться на публикации других авторов. Сервис «Список покупок» позволит пользователям создавать список продуктов, которые нужно купить для приготовления выбранных блюд. 

# Установка

1. Клонируйте репозиторий
```
git clone https://github.com/dagedarr/foodgram-project-react.git

cd foodgram-project-react/
```
Если вы не используете Git, то вы можете просто скачать исходный код репозитория в ZIP-архиве и распаковать его на свой компьютер.

2. Создайте виртуальное окружение и активируйте его
```
python -m venv venv
source venv/bin/activate
```
3. Установите зависимости
```
pip install -r requirements.txt
```

4. Запустите docker-compose 
```
cd ../infra
docker-compose up -d --build 
```

5. Выполните по очереди команды
```
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
docker-compose exec web python manage.py collectstatic --no-input
docker-compose exec web python manage.py loaddata
```
Откройте браузер и перейдите по адресу http://127.0.0.1:8000/admin/. Введите имя пользователя и пароль администратора, чтобы войти в панель управления.

# Готово!
Вы успешно установили Проект foodgram и готовы начать его использовать!
