# Sber Tigers Telegram Bot

Sber Tigers Telegram Bot - это проект команды Pi Byte весеннего семестра 2024 года, представляющий собой telegram-бот с возможностью поиска наиболее похожего тигра, отправкой его описания, а также интересных фактов.

## Содержание

- [Особенности](#особенности)
- [Требования](#требования)
- [Установка](#установка)
- [Запуск](#запуск)
- [Поддержка](#поддержка)

## Особенности

- Проект разбит на микросервисы
- Возможно использование сервиса фотографий без интерфейса бота
- Конфигурирование проекта под ваши фото/описания/факты
- В основе поиска ближайшего похожего фото модель DinoV2
- Размещение в Docker

## Требования

- Python 3.12
- Docker
- QDrant
- Telegram Bot API Token

## Установка

### Шаг 1: Клонирование репозитория

```bash
git clone https://github.com/Onnya/tigers-bot.git
cd tigers-bot
```

### Шаг 2: Настройка Docker

Если у вас еще не установлен Docker, следуйте инструкциям по установке на официальном сайте Docker.

### Шаг 3: Конфигурация переменных окружения бота

Перейдите в директорию бота и создайте .env файл для конфигурации переменных окружения бота:


```bash
cd bot/
cat .env.example >> .env
vim .env
```

Заполните содержимое файла .env актуальными для вас данными: 

```env
TOKEN=your_telegram_token
```

### Шаг 4: Наполнение json с интересными фактами

Создайте файл facts.json и заполните его актуальными для вас данными:

```bash
cat facts.json.example >> facts.json
vim facts.json
```

### Шаг 5: Наполнение json с описаниями фотографий

Создайте файл photos_info.json и заполните его актуальными для вас данными:

```bash
cd ../photo_service
cat photos_info.json.example >> photos_info.json
vim photos_info.json
```

### Шаг 6: Настройка docker-compose

Настройте docker-compose в соответствии с вашими данными:

```bash
cd ..
vim docker-compose.yml
```

```docker-compose.yml
version: '3.8'

services:
  flask_app:
    build:
      context: ./photo_service
      dockerfile: Dockerfile
    ports:
      - "5000:5000"
    volumes:
      - path/to/your/photos/folder:/app/photos
    environment:
      - RELOAD_VECTORS=${RELOAD_VECTORS:-false}
      - CLEAR_DB=${CLEAR_DB:-false}
    depends_on:
      - qdrant
    networks:
      - bot_network

  telegram_bot:
    build:
      context: ./bot
      dockerfile: Dockerfile
    depends_on:
      - flask_app
    networks:
      - bot_network

  qdrant:
    image: qdrant/qdrant
    ports:
      - "6333:6333"
      - "6334:6334"
    volumes:
      - path/to/your/qdrant/folder:/qdrant/storage
    networks:
      - bot_network

networks:
  bot_network:
    driver: bridge

volumes:
  qdrant_data:
```

## Запуск

Первый запуск необходимо осуществить с помощью:

```bash
RELOAD_VECTORS=true docker compose up --build
```

При необходимости заполнить qdrant векторами новых фотографий, используйте флаг

```bash
RELOAD_VECTORS=true docker compose up --build
```

Если необходимо при этом предварительно очистить qdrant, используйте:

```bash
RELOAD_VECTORS=true CLEAR_DB=true docker compose up --build
```

В случае, если фотографии уже загружены в qdrant и нужно просто заново собрать проект, используйте:

```bash
docker compose up --build
```

## Поддержка

Если у вас возникли вопросы или проблемы, создайте issue на [GitHub](https://github.com/Onnya/tigers-bot/issues).