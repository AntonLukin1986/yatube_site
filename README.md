# YaTube

## _Социальная сеть_

### В данном проекте авторы могут размещать свои посты на различную тематику, а посетители имеют возможность следить за любимыми авторами, лайкать и комментировать их публикации

### Технологии

- Python 3.9.9
- Django 2.2.19
- Django Rest Framework 3.12.4
- sorl-thumbnail 12.7.0

### Как запустить проект

Клонировать репозиторий и перейти в него в командной строке:

```
git clone https://github.com/AntonLukin1986/yatube_site.git
```

```
cd yatube_site
```

Cоздать и активировать виртуальное окружение:

```
python -m venv venv
```

```
source venv/Scripts/activate
```

Установить зависимости из файла requirements.txt:

```
pip install -r requirements.txt
```

Выполнить миграции:

```
python manage.py migrate
```

В папке с файлом manage.py выполнить команду для запуска локального сервера:

```
python manage.py runserver
```

## API для YaTube

В данном проекте реализована возможности взаимодействия с социальной сетью  **YaTube** через **API** интерфейс.

### Примеры запросов в формате json

Получение списка всех публикаций. Поддерживается указание параметров *limit* и *offset*:

```
http://127.0.0.1:8000/api/v1/posts/
```

```
{
  "count": 123,
  "next": "http://api.example.org/accounts/?offset=400&limit=100",
  "previous": "http://api.example.org/accounts/?offset=200&limit=100",
  "results": [
    {
      "id": 0,
      "author": "Автор",
      "text": "Текст поста",
      "pub_date": "2021-10-14T20:41:29.648Z",
      "image": "Картинка",
      "group": 0
    }
  ]
}
```

Добавление нового комментария к публикации:

```
http://127.0.0.1:8000/api/v1/posts/{post_id}/comments/
```

```
{
  "text": "Комментарий"
}
```

Подписка на автора поста:

```
http://127.0.0.1:8000/api/v1/follow/
```

```
{
  "user": "Пользователь",
  "following": "Автор"
}
```

### Автор

_Антон Лукин_ [AntonLukin1986](https://github.com/AntonLukin1986)

Ознакомиться с работающим проектом можно по [ссылке](http://shahter86.pythonanywhere.com/)
