# API для сокращения ссылок

Это API позволяет создавать, управлять и отслеживать короткие ссылки. Оно поддерживает как зарегистрированных, так и незарегистрированных пользователей. API предоставляет возможность создавать кастомные алиасы, устанавливать время жизни ссылок и привязывать ссылки к проектам. Если ссылкой не пользуются, то она будет удалена.

## Запуск проекта

Для запуска проекта необходимо выполнить следующие команды (Должен быть установлен Docker и Docker Compose):

```
# Клонируем репозиторий
git clone https://github.com/KuBaN658/shorten-links.git

# Переходим в директорию проекта
cd shorten-links/

# Копируем файл .env_example в .env и вводим необходимые переменные окружения
cp .env_example .env
nano .env

# Запускаем сборку контейнеров
docker-compose build

# Запускаем контейнеры
docker-compose up
```

## Эндпоинты

### Авторизация пользователя

**POST** `/auth/jwt/login`

**Параметры:**

- `username` - email
- `password` - пароль

**Пример запроса:**

```
curl -X 'POST' \
  'http://localhost:8000/auth/jwt/login' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -d 'username=sam%40example.com&password=pass'
```

**Пример ответа:**
```
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoiOTIyMWZmYzktNjQwZi00MzcyLTg2ZDMtY2U2NDJjYmE1NjAzIiwiYXVkIjoiZmFzdGFwaS11c2VyczphdXRoIiwiZXhwIjoxNTcxNTA0MTkzfQ.M10bjOe45I5Ncu_uXvOmVV8QxnL-nZfcH96U90JaocI",
  "token_type": "bearer"
}
```

**POST** `/auth/jwt/logout` - Выход из системы

**Пример запроса:**
```
curl -X 'POST' \
  'http://localhost:8000/auth/jwt/logout' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1ODRlZDk1Mi0zNzVhLTQ2ZDktYWMzYi1kZWYxNzM2Njk5OTkiLCJhdWQiOlsiZmFzdGFwaS11c2VyczphdXRoIl0sImV4cCI6MTc0Mjc0NDE4M30.YMaDd0aRdsWV3bj_MFHu0ETp0dVPPC0aZgt5SyCOoJo' \
  -d ''
```

### Регистрация пользователя

**POST** `/auth/register`

**Параметры:**

- `email` - email
- `password` - пароль

**Пример запроса:**
```
curl -X 'POST' \
  'http://localhost:8000/auth/register' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "email": "bob@example.com",
  "password": "pass",
  "is_active": true,
  "is_superuser": false,
  "is_verified": false
}'
```

**Пример ответа:**
```
{
  "id": "584ed952-375a-46d9-ac3b-def173669999",
  "email": "ann@example.com",
  "is_active": true,
  "is_superuser": false,
  "is_verified": false
}
```

### Создание короткой ссылки

**POST** `/links/shorten`

Создает короткую ссылку. Поддерживает кастомные алиасы и установку времени жизни ссылки. Если ссылкой не пользуются, то она будет удалена (Это время можно определить в файле .env при сборке контейнеров).

**Параметры:**
- `url`: Оригинальный URL.
- `alias`: Кастомный алиас (опционально, если не указать сгенерируется).
- `lifetime_seconds`: Время жизни ссылки в секундах (опционально, по умолчанию 300).
- `project`: Проект, к которому принадлежит ссылка (опционально).

**Пример запроса:**

```
curl -X 'POST' \
  'http://localhost:8000/links/shorten' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1ODRlZDk1Mi0zNzVhLTQ2ZDktYWMzYi1kZWYxNzM2Njk5OTkiLCJhdWQiOlsiZmFzdGFwaS11c2VyczphdXRoIl0sImV4cCI6MTc0Mjc0NDE4M30.YMaDd0aRdsWV3bj_MFHu0ETp0dVPPC0aZgt5SyCOoJo' \
  -H 'Content-Type: application/json' \
  -d '{
  "url": "string",
  "lifetime_seconds": 300,
  "description": "string",
  "alias": "string",
  "project": "string"
}'
```

**Пример ответа:**
```
{
  "status": "Shorten_link created",
  "saved_link": {
    "alias": "7827229b",
    "id": 23,
    "last_clicked_at": null,
    "project": null,
    "created_at": "2025-03-23T15:14:36.312321",
    "user_id": "584ed952-375a-46d9-ac3b-def173669999",
    "url": "https://string",
    "clicks": 0,
    "expires_at": "2025-03-23T15:19:36.316439",
    "task_id": "222ccf16-00a0-48b6-8ff0-7c056589f387"
  }
}
```

### Поиск по оригинальному URL

**GET** `/links/search`

Поиск всех коротких ссылок по оргинальному url, доступно и для не зарегистрированных пользователей. Показывает короткие ссылки всех пользователей.

**Параметры:**
- `original_url`: Оригинальный URL

**Пример запроса:**

```
curl -X 'GET' \
  'http://localhost:8000/links/search?original_url=mail.ru' \
  -H 'accept: application/json'
```

**Пример ответа:**
```
[
  {
    "alias": "mmm",
    "id": 21,
    "last_clicked_at": "2025-03-23T14:40:07.019092",
    "project": "string",
    "created_at": "2025-03-23T14:39:43.813712",
    "user_id": "584ed952-375a-46d9-ac3b-def173669999",
    "url": "https://mail.ru",
    "clicks": 2,
    "expires_at": "2025-03-23T14:44:43.817463",
    "task_id": "23906810-bf30-4400-88b6-b883eab0e67b"
  }
]
```

### Переход на оригинальный URL

**GET** `/links/{short_code}`

Перенаправляет пользователя на оригинальный URL

**Параметры:**
- `short_code`: Короткая ссылка

**Пример запроса:**

```
curl -X 'GET' \
  'http://localhost:8000/links/git' \
  -H 'accept: application/json'
```

### Замена оригинального URL

**PUT** `/links/{short_code}`

Заменяет оригинальный URL

**Параметры:**
- `short_code`: Короткая ссылка
- `url`: Новый оригинальный URL

**Пример запроса:**

```
curl -X 'PUT' \
  'http://localhost:8000/links/git' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1ODRlZDk1Mi0zNzVhLTQ2ZDktYWMzYi1kZWYxNzM2Njk5OTkiLCJhdWQiOlsiZmFzdGFwaS11c2VyczphdXRoIl0sImV4cCI6MTc0Mjc0NDE4M30.YMaDd0aRdsWV3bj_MFHu0ETp0dVPPC0aZgt5SyCOoJo' \
  -H 'Content-Type: application/json' \
  -d '{
  "url": "mail.ru"
}'
```

**Пример ответа:**
```
{
  "detail": "Link ggg updated",
  "updated_link": {
    "alias": "ggg",
    "id": 20,
    "last_clicked_at": "2025-03-23T14:37:41.512518",
    "project": "string",
    "created_at": "2025-03-23T14:36:56.584373",
    "user_id": "584ed952-375a-46d9-ac3b-def173669999",
    "url": "https://mail.ru",
    "clicks": 3,
    "expires_at": "2025-03-23T14:41:56.586625",
    "task_id": "9d618242-c29f-45be-a005-b7572e01d897"
  }
}
```

### Удаление связи

**DELETE** `/links/delete/{short_code}`

Удаляет связь

**Параметры:**
- `short_code`: Короткая ссылка

**Пример запроса:**

```
curl -X 'DELETE' \
  'http://localhost:8000/links/delete/git%20' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1ODRlZDk1Mi0zNzVhLTQ2ZDktYWMzYi1kZWYxNzM2Njk5OTkiLCJhdWQiOlsiZmFzdGFwaS11c2VyczphdXRoIl0sImV4cCI6MTc0Mjc0NDE4M30.YMaDd0aRdsWV3bj_MFHu0ETp0dVPPC0aZgt5SyCOoJo'
```

### Статистика по ссылке

**GET** `/links/{short_code}/stats`

Просмотр статистики по короткой ссылке

**Параметры:**
- `short_code`: Короткая ссылка

**Пример запроса:**
```
curl -X 'GET' \
  'http://localhost:8000/links/git/stats' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1ODRlZDk1Mi0zNzVhLTQ2ZDktYWMzYi1kZWYxNzM2Njk5OTkiLCJhdWQiOlsiZmFzdGFwaS11c2VyczphdXRoIl0sImV4cCI6MTc0Mjc0NDE4M30.YMaDd0aRdsWV3bj_MFHu0ETp0dVPPC0aZgt5SyCOoJo'
```

**Пример ответа:**
```
{
  "original_url": "https://mail.ru",
  "created_at": "2025-03-23T14:39:43.813712",
  "clicks": 2,
  "last_clicked_at": "2025-03-23T14:40:07.019092"
}
```

### Ссылки проекта

**GET** `/links/my/{project}`

Просмотр связей своего проекта

**Параметры:**
- `project`: Название проекта 

**Пример запроса:**
```
curl -X 'GET' \
  'http://localhost:8000/links/my/string' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1ODRlZDk1Mi0zNzVhLTQ2ZDktYWMzYi1kZWYxNzM2Njk5OTkiLCJhdWQiOlsiZmFzdGFwaS11c2VyczphdXRoIl0sImV4cCI6MTc0Mjc0NDE4M30.YMaDd0aRdsWV3bj_MFHu0ETp0dVPPC0aZgt5SyCOoJo'
```

**Пример ответа:**
```
[
  {
    "alias": "mmm",
    "id": 21,
    "last_clicked_at": "2025-03-23T14:40:07.019092",
    "project": "string",
    "created_at": "2025-03-23T14:39:43.813712",
    "user_id": "584ed952-375a-46d9-ac3b-def173669999",
    "url": "https://mail.ru",
    "clicks": 2,
    "expires_at": "2025-03-23T14:44:43.817463",
    "task_id": "23906810-bf30-4400-88b6-b883eab0e67b"
  }
]
```

### Удаленные ссылки

**GET** `/links/history/old_links`

Просмотр удаленных ссылок, можно посмотреть только свои ссылки. Доступно только зарегистрированным пользователям.

**Параметры:**
- `project`: Название проекта 

**Пример запроса:**
```
curl -X 'GET' \
  'http://localhost:8000/links/history/old_links' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1ODRlZDk1Mi0zNzVhLTQ2ZDktYWMzYi1kZWYxNzM2Njk5OTkiLCJhdWQiOlsiZmFzdGFwaS11c2VyczphdXRoIl0sImV4cCI6MTc0Mjc0NDE4M30.YMaDd0aRdsWV3bj_MFHu0ETp0dVPPC0aZgt5SyCOoJo'
```

**Пример ответа:**
```
[
  {
    "alias": "mmm",
    "id": 21,
    "last_clicked_at": "2025-03-23T14:40:07.019092",
    "project": "string",
    "created_at": "2025-03-23T14:39:43.813712",
    "user_id": "584ed952-375a-46d9-ac3b-def173669999",
    "url": "https://mail.ru",
    "clicks": 2,
    "expires_at": "2025-03-23T14:44:43.817463",
    "task_id": "23906810-bf30-4400-88b6-b883eab0e67b"
  }
]
```


## Описание базы данных (В проекте используется `PostreSQL`)

База данных состоит из двух основных таблиц: `shorten_links` и `old_shorten_links`. Эти таблицы используются для хранения информации о коротких ссылках, их статистике и истории удаленных ссылок.

### Таблица `user`

Таблица `user` хранит информацию о пользователях.

| Название поля       | Тип данных       | Описание                                                                 |
|----------------------|------------------|-------------------------------------------------------------------------|
| `id`                | `uuid`            | Уникальный идентификатор записи (первичный ключ).         |
| `created_at`               | `DateTime`           | Дата и вермя регистрации пользователя.                                 |
| `email`             | `String`         | Email пользователя, испольуется для авторизации.                             |
| `hashed_password`        | `String`       | Хэшированный пароль пользователя.              |
| `is_active`           | `Bool`  | Является ли пользователь активным.           |
| `is_superuser`            | `Bool`            | Является ли пользователь администратором.                        |
| `is_verified`   | `Bool` | Является ли пользователь верифицированным.                           |

### Таблица `shorten_links`

Таблица `shorten_links` хранит информацию о созданных коротких ссылках.

| Название поля       | Тип данных       | Описание                                                                 |
|----------------------|------------------|-------------------------------------------------------------------------|
| `id`                | `int`            | Уникальный идентификатор записи (первичный ключ, автоинкремент).         |
| `url`               | `Text`           | Оригинальный URL, который был сокращен.                                 |
| `alias`             | `String(255)`    | Уникальный алиас (короткий код) для ссылки.                             |
| `created_at`        | `DateTime`       | Дата и время создания записи (по умолчанию текущее время).              |
| `user_id`           | `Optional[str]`  | Идентификатор пользователя, создавшего ссылку (внешний ключ).           |
| `clicks`            | `int`            | Количество переходов по ссылке (по умолчанию 0).                        |
| `last_clicked_at`   | `Optional[DateTime]` | Дата и время последнего перехода по ссылке.                           |
| `expires_at`        | `DateTime`       | Дата и время истечения срока действия ссылки.                           |
| `project`           | `Optional[str]`  | Название проекта, к которому принадлежит ссылка.                        |
| `task_id`           | `str`            | Идентификатор задачи для удаления ссылки по истечении срока действия.   |


### Таблица `old_shorten_links`

Таблица `old_shorten_links` хранит информацию об удаленных коротких ссылках.

| Название поля       | Тип данных       | Описание                                                                 |
|----------------------|------------------|-------------------------------------------------------------------------|
| `id`                | `int`            | Уникальный идентификатор записи (первичный ключ, автоинкремент).         |
| `url`               | `Text`           | Оригинальный URL, который был сокращен.                                 |
| `alias`             | `String(255)`    | Алиас (короткий код) для ссылки.                                        |
| `created_at`        | `DateTime`       | Дата и время создания записи.                                           |
| `user_id`           | `Optional[int]`  | Идентификатор пользователя, создавшего ссылку (внешний ключ).           |
| `clicks`            | `int`            | Количество переходов по ссылке.                                         |
| `last_clicked_at`   | `Optional[DateTime]` | Дата и время последнего перехода по ссылке.                           |
| `deleted_at`        | `DateTime`       | Дата и время удаления ссылки.              |
| `project`           | `Optional[str]`  | Название проекта, к которому принадлежала ссылка.                       |
