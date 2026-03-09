# Техническое задание: UspMusicBot - Telegram-бот для генерации музыки

## 1. Общее описание проекта

**Название проекта**: UspMusicBot
**Тип**: Telegram-бот с веб-интерфейсом (Web App)
**Цель**: Создание музыкальных треков с помощью AI на базе Suno API
**Референс**: [@gusli_aibot](https://t.me/gusli_aibot) (SoNata - Создать песню)

### 1.1 Основная концепция

UspMusicBot - это интеллектуальный помощник для создания профессиональных музыкальных треков за 1 минуту без специальных навыков. Пользователь может:

- Описать идею для песни (текстом или голосом) → получить готовый трек
- Предоставить готовый текст песни → выбрать стиль → получить трек с вокалом
- Сохранять созданные песни в персональные плейлисты
- Управлять балансом и покупать пакеты генераций

### 1.2 Целевая аудитория

- Контент-криейторы (блогеры, TikTok/YouTube авторы)
- Музыканты-любители и начинающие авторы
- Маркетологи (для создания джинглов и фоновой музыки)
- Пользователи, желающие создать персональную песню для подарка

---

## 2. Функциональные требования

### 2.1 MVP (Минимально жизнеспособный продукт)

#### 2.1.1 Генерация музыки по идее (текст → песня)

**Сценарий использования:**

1. Пользователь отправляет текстовое описание идеи для песни
   - Пример: "веселая песня про лето и море"
   - Или голосовое сообщение (транскрибируется через Whisper API)

2. Бот генерирует текст песни с помощью Claude API (Anthropic)
   - Промпт: "Создай текст песни на русском языке на тему: {user_idea}"
   - Результат: структурированный текст (куплеты, припев, бридж)

3. Бот предлагает 2-3 музыкальных стиля
   - Inline кнопки: "🎸 Pop Rock", "🎹 Electronic", "🎺 Jazz"
   - Стили определяются на основе темы песни

4. Пользователь выбирает стиль

5. Бот генерирует трек через Suno API
   - Запрос с параметрами: lyrics + style
   - Асинхронная обработка (45-90 секунд)

6. Бот отправляет готовый MP3 файл
   - Название трека, длительность
   - Кнопки: "💾 Сохранить в плейлист", "🔄 Создать еще"

**Технические детали:**

```python
# Пример запроса к Suno API
POST /api/custom_generate
{
    "gpt_description": "upbeat summer pop song",
    "lyrics": "[Verse 1]\nСолнце светит ярко...\n[Chorus]\nЛето, море, счастье!",
    "style": "pop rock",
    "make_instrumental": false
}

# Ответ (async)
{
    "task_id": "abc123",
    "status": "submitted"
}

# Polling статуса (каждые 5 секунд)
GET /api/tasks/abc123
{
    "status": "completed",
    "audio_url": "https://cdn.suno.ai/abc123.mp3",
    "duration": 180
}
```

#### 2.1.2 Генерация музыки по готовым текстам

**Сценарий использования:**

1. Пользователь выбирает режим "📝 Есть стихи"

2. Бот запрашивает текст песни
   - Пользователь отправляет готовый текст (макс. 3000 символов)
   - Валидация: проверка длины, кодировки UTF-8

3. Бот предлагает выбрать музыкальный стиль
   - Preset стили: Pop, Rock, Hip-hop, Jazz, Electronic, Classical
   - Или кастомный ввод: "Опиши свой стиль"

4. Пользователь выбирает или описывает стиль

5. Генерация трека через Suno API (аналогично п. 2.1.1)

6. Отправка готового MP3

**UI/UX:**

```
Бот: "📝 Отлично! Отправь мне текст своей песни.

Максимум 3000 символов.
Можно использовать разметку:
[Verse 1] - куплет
[Chorus] - припев
[Bridge] - бридж"

Пользователь: "
[Verse 1]
В небе звезды горят
Я иду по ночным улицам
...
"

Бот: "✨ Отличный текст! Теперь выбери стиль музыки:"
[🎸 Pop] [🎹 Electronic] [🎺 Jazz] [✏️ Свой стиль]
```

#### 2.1.3 Обработка голосовых сообщений

**Технический стек:**
- OpenAI Whisper API для транскрибации
- Автоматическое определение языка

**Сценарий:**

1. Пользователь отправляет голосовое сообщение

2. Бот показывает статус: "🎤 Слушаю..."

3. Транскрибация через Whisper API
   ```python
   import openai

   with open("voice.ogg", "rb") as audio_file:
       transcript = openai.Audio.transcribe(
           model="whisper-1",
           file=audio_file,
           language="ru"  # или auto-detect
       )
   ```

4. Бот отправляет результат транскрибации:
   ```
   "Вы сказали: 'создай песню про осень и дождь'

   Продолжаем?
   [✅ Да, создать] [✏️ Исправить текст]"
   ```

5. Продолжение по сценарию 2.1.1

**Технические требования:**
- Максимальная длина голосового: 5 минут
- Поддерживаемые форматы: OGG, MP3, WAV
- Качество транскрипции: 95%+ для чистой речи

#### 2.1.4 Система балансов и платежей

**Модель монетизации:**

| План | Стоимость | Кредиты | Стоимость за трек |
|------|-----------|---------|-------------------|
| **Бесплатно** | 0₽ | 3 трека | 0₽ |
| **Стартовый** | 299₽ | 10 треков | ~30₽ |
| **Популярный** | 799₽ | 30 треков | ~27₽ |
| **Профессионал** | 1,999₽ | 100 треков | ~20₽ |

**Платежные системы:**
- **YooKassa** (основная) - карты РФ, СБП
- **CryptoBot** (дополнительная) - USDT, TON, BTC

**Функциональность баланса:**

1. Просмотр текущего баланса
   ```
   💳 Ваш баланс

   Доступно треков: 5 🎵

   История:
   - 27.02.2026: +10 треков (Покупка "Стартовый")
   - 25.02.2026: -1 трек (Создание "Летняя песня")
   - 20.02.2026: +3 трека (Регистрация)
   ```

2. Покупка пакетов
   - Inline кнопки с вариантами пакетов
   - Выбор платежной системы
   - Создание платежа
   - Webhook для подтверждения оплаты
   - Автоматическое начисление кредитов

3. История транзакций
   - Список всех покупок
   - Статусы: pending, completed, failed
   - Возможность повторной оплаты при failed

**Технические детали YooKassa:**

```python
from yookassa import Configuration, Payment

Configuration.account_id = "shop_id"
Configuration.secret_key = "secret_key"

# Создание платежа
payment = Payment.create({
    "amount": {
        "value": "299.00",
        "currency": "RUB"
    },
    "confirmation": {
        "type": "redirect",
        "return_url": "https://t.me/UspMusicBot"
    },
    "capture": True,
    "description": "Пакет 'Стартовый' - 10 треков"
})

# Отправка ссылки пользователю
payment_url = payment.confirmation.confirmation_url
```

**Webhook обработка:**

```python
from yookassa.domain.notification import WebhookNotification

@app.post("/webhook/yookassa")
async def yookassa_webhook(request: dict):
    notification = WebhookNotification(request)
    payment = notification.object

    if payment.status == "succeeded":
        # Начислить кредиты пользователю
        user_id = payment.metadata.get("user_id")
        credits = payment.metadata.get("credits")
        await add_credits(user_id, credits)
```

#### 2.1.5 Плейлисты и история

**Функционал:**

1. **Мои песни** - список всех созданных треков
   ```
   🎵 Мои песни (12)

   1. "Летняя история" - 3:45
      27.02.2026, Pop Rock
      [▶️ Прослушать] [⬇️ Скачать]

   2. "Ночной город" - 2:30
      25.02.2026, Electronic
      [▶️ Прослушать] [⬇️ Скачать]

   [Далее →]
   ```

2. **Плейлисты** (опционально для v2.0)
   - Создание пользовательских плейлистов
   - Добавление/удаление треков
   - Шеринг плейлистов

3. **Повторное скачивание**
   - Кэширование Telegram file_id
   - Хранение URL на облаке (опционально)

**База данных:**

```sql
-- Таблица songs
CREATE TABLE songs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    title VARCHAR(255),
    lyrics TEXT,
    style VARCHAR(100),
    suno_task_id VARCHAR(255),
    telegram_file_id VARCHAR(255),
    audio_url TEXT,
    duration INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

---

### 2.2 Дополнительные функции (v2.0)

#### 2.2.1 Веб-интерфейс (Telegram Web App)

**Структура:**

```
Web App:
├── Главная
│   └── Большая кнопка "Создать песню"
├── Стихи (генерация текстов)
│   └── Claude AI для создания текстов
├── Песни (история созданных)
│   ├── Список треков
│   ├── Аудио-плеер
│   └── Фильтры (по дате, стилю)
├── Плейлист
│   ├── Создание плейлистов
│   └── Управление треками
├── Баланс
│   ├── Текущий баланс
│   ├── История транзакций
│   └── Покупка пакетов
└── Мастерские (будущее)
    ├── Поющий портрет
    ├── Создать фото
    └── Оживить фото
```

**Технический стек:**

- **Frontend**: React.js или Vue.js
- **Telegram WebApp SDK**: [@twa-dev/sdk](https://www.npmjs.com/package/@twa-dev/sdk)
- **Backend API**: FastAPI (REST endpoints)
- **Дизайн**: Оранжевая цветовая схема (как @gusli_aibot)

**Пример интеграции:**

```html
<!DOCTYPE html>
<html>
<head>
    <script src="https://telegram.org/js/telegram-web-app.js"></script>
</head>
<body>
    <div id="app"></div>
    <script>
        // Инициализация Telegram WebApp
        const tg = window.Telegram.WebApp;
        tg.expand();

        // Получение данных пользователя
        const user = tg.initDataUnsafe.user;
        console.log(user.id, user.username);

        // Отправка данных обратно в бота
        tg.sendData(JSON.stringify({
            action: 'create_song',
            lyrics: '...',
            style: 'pop'
        }));
    </script>
</body>
</html>
```

#### 2.2.2 Админ-панель

**Функционал:**

1. **Статистика**
   - Общее количество пользователей
   - Активные пользователи (DAU, MAU)
   - Количество созданных треков (всего, за сегодня, за месяц)
   - Доход (за день, месяц, всего)
   - График активности

2. **Управление пользователями**
   - Поиск по Telegram ID / username
   - Просмотр профиля пользователя
   - Редактирование баланса (начисление/списание)
   - Блокировка/разблокировка

3. **Рассылка**
   - Создание сообщения для рассылки
   - Выбор целевой аудитории (все, платящие, новые)
   - Предпросмотр сообщения
   - Планирование отправки
   - Статистика доставки

4. **Мониторинг API**
   - Использование Suno API (количество запросов, ошибки)
   - Rate limit статус
   - Стоимость генераций
   - Среднее время генерации

**UI (Telegram-based):**

```
🔐 Админ-панель

[📊 Статистика]
[👥 Пользователи]
[📢 Рассылка]
[🔧 Настройки]
[📈 Аналитика API]
```

#### 2.2.3 Реферальная система (v2.5)

**Механика:**

- Пользователь приглашает друга → получает +2 бесплатных трека
- Друг регистрируется по реферальной ссылке → получает +5 треков (вместо 3)
- Реферал делает первую покупку → реферер получает +5 треков

**Реализация:**

```python
# Генерация реферальной ссылки
referral_code = f"ref{user.id}"
referral_link = f"https://t.me/UspMusicBot?start={referral_code}"

# При /start ref123
if payload.startswith("ref"):
    referrer_id = int(payload[3:])
    # Начислить бонус рефереру
    await add_credits(referrer_id, 2)
    # Начислить бонус новому пользователю
    await add_credits(user.id, 5)
```

---

## 3. Технические требования

### 3.1 Архитектура системы

```
┌─────────────────────────────────────────────────────────┐
│                     UspMusicBot                         │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌──────────────┐    ┌──────────────┐                  │
│  │  Telegram    │◄───┤  Web App     │                  │
│  │  Bot API     │    │  (Frontend)  │                  │
│  └──────┬───────┘    └──────┬───────┘                  │
│         │                   │                           │
│         ▼                   ▼                           │
│  ┌─────────────────────────────────┐                   │
│  │      Bot Handler (aiogram)      │                   │
│  │  ┌───────────┐  ┌────────────┐  │                   │
│  │  │ Handlers  │  │   FSM      │  │                   │
│  │  │ /start    │  │ States     │  │                   │
│  │  │ /create   │  │ Management │  │                   │
│  │  │ /balance  │  │            │  │                   │
│  │  └───────────┘  └────────────┘  │                   │
│  └─────────┬───────────────────────┘                   │
│            │                                            │
│            ▼                                            │
│  ┌─────────────────────────────────┐                   │
│  │         Services Layer          │                   │
│  │  ┌──────────┐  ┌──────────┐     │                   │
│  │  │  Suno    │  │ Claude   │     │                   │
│  │  │  Client  │  │ AI       │     │                   │
│  │  └──────────┘  └──────────┘     │                   │
│  │  ┌──────────┐  ┌──────────┐     │                   │
│  │  │ Whisper  │  │ Payment  │     │                   │
│  │  │ API      │  │ Service  │     │                   │
│  │  └──────────┘  └──────────┘     │                   │
│  └─────────┬───────────────────────┘                   │
│            │                                            │
│            ▼                                            │
│  ┌─────────────────────────────────┐                   │
│  │      Database Layer (ORM)       │                   │
│  │   ┌─────────┐  ┌──────────┐     │                   │
│  │   │ SQLite  │  │  Redis   │     │                   │
│  │   │ (main)  │  │  (cache) │     │                   │
│  │   └─────────┘  └──────────┘     │                   │
│  └─────────────────────────────────┘                   │
│                                                         │
└─────────────────────────────────────────────────────────┘

        External Services
┌────────────────────────────────────────┐
│ • Suno API (AIMLAPI.com)               │
│ • Claude API (Anthropic)               │
│ • OpenAI Whisper API                   │
│ • YooKassa Payment API                 │
│ • CryptoBot Payment API                │
└────────────────────────────────────────┘
```

### 3.2 Стек технологий

#### Backend

```python
# requirements.txt

# Telegram Bot Framework
aiogram==3.15.0
aiohttp==3.10.11

# Database
sqlalchemy==2.0.36
aiosqlite==0.20.0
alembic==1.14.0          # Database migrations

# Redis (для кэширования и FSM)
redis==5.0.1
aioredis==2.0.1

# Configuration
python-dotenv==1.0.1
pydantic==2.10.5
pydantic-settings==2.6.1

# AI Services
anthropic==0.18.1        # Claude API
openai==1.55.3           # Whisper API
httpx==0.27.2            # Для Suno API запросов

# Payment Systems
yookassa==3.0.1
aiocryptopay==0.5.0      # CryptoBot

# Utilities
loguru==0.7.2
Pillow==11.0.0           # Для обработки изображений (будущее)

# FastAPI (для Web App API)
fastapi==0.115.6
uvicorn==0.34.0

# Testing
pytest==7.4.4
pytest-asyncio==0.23.3
pytest-cov==4.1.0
```

#### Frontend (Web App)

```json
{
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "@twa-dev/sdk": "^7.0.0",
    "axios": "^1.6.0",
    "react-router-dom": "^6.20.0",
    "styled-components": "^6.1.0"
  }
}
```

### 3.3 Структура проекта

```
UspMusicBot/
├── src/
│   ├── bot/
│   │   ├── __init__.py
│   │   ├── main.py              # Entry point
│   │   ├── keyboards.py         # Клавиатуры
│   │   ├── states.py            # FSM состояния
│   │   ├── texts.py             # Тексты сообщений
│   │   └── middleware.py        # Middleware (auth, logging)
│   │
│   ├── handlers/
│   │   ├── __init__.py
│   │   ├── start.py             # /start, приветствие
│   │   ├── song_creation.py     # Создание песен (main flow)
│   │   ├── lyrics.py            # Работа с текстами
│   │   ├── voice.py             # Голосовые сообщения
│   │   ├── playlists.py         # Плейлисты
│   │   ├── balance.py           # Баланс и платежи
│   │   ├── admin.py             # Админ-панель
│   │   └── callbacks.py         # Callback handlers
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── suno_client.py       # Suno API интеграция
│   │   ├── claude_client.py     # Claude AI для текстов
│   │   ├── whisper_client.py    # Whisper транскрипция
│   │   ├── payment_service.py   # Платежи (YooKassa + CryptoBot)
│   │   ├── storage_service.py   # Облачное хранилище (опционально)
│   │   └── analytics_service.py # Аналитика и метрики
│   │
│   ├── database/
│   │   ├── __init__.py
│   │   ├── engine.py            # SQLAlchemy setup
│   │   ├── models.py            # ORM модели
│   │   ├── crud.py              # CRUD операции
│   │   └── migrations/          # Alembic миграции
│   │       └── versions/
│   │
│   ├── webapp/                  # Web App (FastAPI)
│   │   ├── __init__.py
│   │   ├── api.py               # REST API endpoints
│   │   ├── auth.py              # Telegram auth validation
│   │   └── static/              # Frontend build
│   │
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── logger.py            # Loguru setup
│   │   ├── validators.py        # Валидация данных
│   │   └── helpers.py           # Вспомогательные функции
│   │
│   └── config.py                # Pydantic Settings
│
├── frontend/                    # Web App Frontend
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   └── App.jsx
│   ├── public/
│   ├── package.json
│   └── vite.config.js
│
├── assets/
│   ├── images/
│   └── templates/
│
├── tests/
│   ├── test_handlers/
│   ├── test_services/
│   └── test_database/
│
├── .env.example
├── .gitignore
├── requirements.txt
├── alembic.ini
├── docker-compose.yml
├── Dockerfile
├── README.md
└── TECHNICAL_SPECIFICATION.md
```

### 3.4 База данных

#### Схема SQLite (с возможностью миграции на PostgreSQL)

```sql
-- Таблица пользователей
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    telegram_id BIGINT UNIQUE NOT NULL,
    username VARCHAR(255),
    first_name VARCHAR(255),
    last_name VARCHAR(255),
    balance INTEGER DEFAULT 3,           -- Начальные 3 бесплатных трека
    total_generated INTEGER DEFAULT 0,   -- Всего созданных треков
    referrer_id INTEGER,                 -- Кто пригласил (для реферальной системы)
    language_code VARCHAR(10) DEFAULT 'ru',
    is_admin BOOLEAN DEFAULT FALSE,
    is_blocked BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_active_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (referrer_id) REFERENCES users(id)
);

-- Таблица песен
CREATE TABLE songs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    title VARCHAR(255),
    lyrics TEXT,                         -- Текст песни
    prompt VARCHAR(500),                 -- Исходный промпт пользователя
    style VARCHAR(100),                  -- Музыкальный стиль
    suno_task_id VARCHAR(255),           -- Task ID в Suno API
    telegram_file_id VARCHAR(255),       -- Telegram file_id для повторной отправки
    audio_url TEXT,                      -- URL аудио файла
    duration INTEGER,                    -- Длительность в секундах
    generation_cost INTEGER DEFAULT 1,   -- Стоимость генерации (кредиты)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Индексы для songs
CREATE INDEX idx_songs_user_id ON songs(user_id);
CREATE INDEX idx_songs_created_at ON songs(created_at);

-- Таблица плейлистов (опционально для v2.0)
CREATE TABLE playlists (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    is_public BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Таблица связи плейлист-песни (many-to-many)
CREATE TABLE playlist_songs (
    playlist_id INTEGER NOT NULL,
    song_id INTEGER NOT NULL,
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (playlist_id, song_id),
    FOREIGN KEY (playlist_id) REFERENCES playlists(id) ON DELETE CASCADE,
    FOREIGN KEY (song_id) REFERENCES songs(id) ON DELETE CASCADE
);

-- Таблица транзакций
CREATE TABLE transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    payment_id VARCHAR(255) UNIQUE,      -- ID платежа от провайдера
    provider VARCHAR(50),                -- yookassa, cryptobot
    credits_amount INTEGER NOT NULL,     -- Количество купленных кредитов
    price_amount DECIMAL(10,2),          -- Сумма платежа
    price_currency VARCHAR(10),          -- RUB, USDT, TON
    status VARCHAR(50) DEFAULT 'pending', -- pending, completed, failed, refunded
    metadata TEXT,                       -- JSON с дополнительными данными
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Индекс для transactions
CREATE INDEX idx_transactions_user_id ON transactions(user_id);
CREATE INDEX idx_transactions_status ON transactions(status);

-- Таблица кэша текстов песен (опционально)
CREATE TABLE lyrics_cache (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    prompt VARCHAR(500),
    generated_lyrics TEXT,
    style_suggestions TEXT,              -- JSON массив стилей
    used BOOLEAN DEFAULT FALSE,          -- Использовался ли для генерации
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Таблица аналитики (для админ-панели)
CREATE TABLE analytics_daily (
    date DATE PRIMARY KEY,
    new_users INTEGER DEFAULT 0,
    active_users INTEGER DEFAULT 0,
    songs_generated INTEGER DEFAULT 0,
    revenue_rub DECIMAL(10,2) DEFAULT 0,
    revenue_crypto DECIMAL(10,2) DEFAULT 0,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### SQLAlchemy модели (models.py)

```python
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, DECIMAL
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database.engine import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    telegram_id = Column(Integer, unique=True, nullable=False, index=True)
    username = Column(String(255))
    first_name = Column(String(255))
    last_name = Column(String(255))
    balance = Column(Integer, default=3)
    total_generated = Column(Integer, default=0)
    referrer_id = Column(Integer, ForeignKey("users.id"))
    language_code = Column(String(10), default="ru")
    is_admin = Column(Boolean, default=False)
    is_blocked = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())
    last_active_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    songs = relationship("Song", back_populates="user")
    transactions = relationship("Transaction", back_populates="user")
    referrals = relationship("User", backref="referrer", remote_side=[id])

class Song(Base):
    __tablename__ = "songs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    title = Column(String(255))
    lyrics = Column(Text)
    prompt = Column(String(500))
    style = Column(String(100))
    suno_task_id = Column(String(255))
    telegram_file_id = Column(String(255))
    audio_url = Column(Text)
    duration = Column(Integer)
    generation_cost = Column(Integer, default=1)
    created_at = Column(DateTime, default=func.now(), index=True)

    # Relationship
    user = relationship("User", back_populates="songs")

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    payment_id = Column(String(255), unique=True)
    provider = Column(String(50))
    credits_amount = Column(Integer, nullable=False)
    price_amount = Column(DECIMAL(10, 2))
    price_currency = Column(String(10))
    status = Column(String(50), default="pending", index=True)
    metadata = Column(Text)
    created_at = Column(DateTime, default=func.now())
    completed_at = Column(DateTime)

    # Relationship
    user = relationship("User", back_populates="transactions")
```

---

### 3.5 API интеграции

#### 3.5.1 Suno API

**Провайдер**: AIMLAPI.com (рекомендуется) или SunoAPI.org

**Процесс регистрации:**

1. Перейти на [aimlapi.com](https://aimlapi.com)
2. Зарегистрироваться (GitHub/Google/Email)
3. Перейти в Dashboard → API Keys
4. Создать новый API ключ
5. Добавить ключ в `.env`: `SUNO_API_KEY=...`

**Эндпоинты:**

```python
# services/suno_client.py

import httpx
from typing import Optional, Dict

class SunoClient:
    BASE_URL = "https://api.aimlapi.com/v1"

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

    async def generate_song(
        self,
        lyrics: str,
        style: str,
        prompt: Optional[str] = None,
        make_instrumental: bool = False
    ) -> Dict:
        """
        Генерация песни через Suno API

        Returns:
            {
                "task_id": "abc123",
                "status": "submitted"
            }
        """
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.BASE_URL}/generate",
                json={
                    "gpt_description": prompt or f"{style} song",
                    "lyrics": lyrics,
                    "style": style,
                    "make_instrumental": make_instrumental
                },
                headers=self.headers,
                timeout=30.0
            )
            response.raise_for_status()
            return response.json()

    async def get_task_status(self, task_id: str) -> Dict:
        """
        Проверка статуса генерации

        Returns:
            {
                "task_id": "abc123",
                "status": "completed|processing|failed",
                "audio_url": "https://...",
                "duration": 180
            }
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.BASE_URL}/tasks/{task_id}",
                headers=self.headers,
                timeout=10.0
            )
            response.raise_for_status()
            return response.json()

    async def wait_for_completion(
        self,
        task_id: str,
        max_wait: int = 120,
        poll_interval: int = 5
    ) -> Optional[Dict]:
        """
        Ожидание завершения генерации с polling

        Args:
            task_id: ID задачи
            max_wait: Максимальное время ожидания (секунды)
            poll_interval: Интервал опроса (секунды)

        Returns:
            Данные готовой песни или None при timeout
        """
        import asyncio

        elapsed = 0
        while elapsed < max_wait:
            result = await self.get_task_status(task_id)

            if result["status"] == "completed":
                return result
            elif result["status"] == "failed":
                raise Exception(f"Generation failed: {result.get('error')}")

            await asyncio.sleep(poll_interval)
            elapsed += poll_interval

        return None  # Timeout
```

**Pricing API (AIMLAPI):**

- Регистрация: 300 бесплатных кредитов
- 1 песня ≈ 10-15 кредитов
- Пополнение: $5, $10, $50, $100, $500 (чем больше, тем выгоднее)

**Rate Limits:**

- Free tier: 10 requests/minute
- Paid tier: 100+ requests/minute

#### 3.5.2 Claude API (Anthropic)

**Использование**: Генерация текстов песен

**Регистрация:**

1. Перейти на [console.anthropic.com](https://console.anthropic.com)
2. Создать аккаунт
3. Получить API ключ в Settings → API Keys
4. Добавить в `.env`: `ANTHROPIC_API_KEY=sk-ant-...`

**Пример использования:**

```python
# services/claude_client.py

from anthropic import AsyncAnthropic

class ClaudeClient:
    def __init__(self, api_key: str):
        self.client = AsyncAnthropic(api_key=api_key)

    async def generate_lyrics(
        self,
        prompt: str,
        language: str = "ru",
        style: str = "pop"
    ) -> Dict[str, str]:
        """
        Генерация текста песни

        Returns:
            {
                "lyrics": "...",
                "title": "...",
                "suggested_styles": ["pop", "rock", "electronic"]
            }
        """
        system_prompt = f"""Ты профессиональный автор песен.
Создай текст песни на языке: {language}.
Музыкальный стиль: {style}.

Структура песни:
[Verse 1]
...текст куплета...

[Chorus]
...припев...

[Verse 2]
...второй куплет...

[Chorus]
...припев...

[Bridge]
...бридж (опционально)...

[Outro]
...концовка...

Требования:
- Текст должен быть эмоциональным и запоминающимся
- Используй рифмы и ритм
- Длина: 2-3 куплета, припев повторяется 2-3 раза
- Максимум 3000 символов
"""

        response = await self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2000,
            system=system_prompt,
            messages=[
                {
                    "role": "user",
                    "content": f"Создай песню на тему: {prompt}"
                }
            ]
        )

        lyrics = response.content[0].text

        # Извлечь название (первая строка обычно название)
        lines = lyrics.strip().split('\n')
        title = lines[0].strip('#').strip() if lines else "Без названия"

        return {
            "lyrics": lyrics,
            "title": title,
            "suggested_styles": self._suggest_styles(prompt, style)
        }

    def _suggest_styles(self, prompt: str, base_style: str) -> list:
        """Предложить музыкальные стили на основе промпта"""
        # Упрощенная логика, можно улучшить с помощью Claude
        style_map = {
            "веселый": ["pop", "dance", "disco"],
            "грустный": ["ballad", "acoustic", "indie"],
            "энергичный": ["rock", "electronic", "hip-hop"],
            "романтичный": ["r&b", "soul", "jazz"],
            "летний": ["reggae", "tropical house", "pop"],
        }

        for keyword, styles in style_map.items():
            if keyword in prompt.lower():
                return styles[:3]

        return [base_style, "pop", "acoustic"]
```

**Pricing:**

- Claude Sonnet 4: ~$3 за 1M input tokens, ~$15 за 1M output tokens
- Генерация одного текста песни: ~$0.01-0.02
- Monthly spend limit: можно настроить в консоли

#### 3.5.3 OpenAI Whisper API

**Использование**: Транскрибация голосовых сообщений

**Регистрация:**

1. Перейти на [platform.openai.com](https://platform.openai.com)
2. Создать аккаунт
3. Добавить платежный метод
4. Получить API ключ в API Keys
5. Добавить в `.env`: `OPENAI_API_KEY=sk-...`

**Пример использования:**

```python
# services/whisper_client.py

from openai import AsyncOpenAI
from pathlib import Path

class WhisperClient:
    def __init__(self, api_key: str):
        self.client = AsyncOpenAI(api_key=api_key)

    async def transcribe_voice(
        self,
        audio_path: Path,
        language: str = "ru"
    ) -> str:
        """
        Транскрибация голосового сообщения

        Args:
            audio_path: Путь к аудио файлу
            language: Код языка (ru, en, etc.)

        Returns:
            Распознанный текст
        """
        with open(audio_path, "rb") as audio_file:
            transcript = await self.client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                language=language
            )

        return transcript.text
```

**Pricing:**

- Whisper API: $0.006 за минуту аудио
- Голосовое сообщение 1 минута = $0.006

#### 3.5.4 YooKassa Payment API

**Регистрация:**

1. Перейти на [yookassa.ru](https://yookassa.ru)
2. Зарегистрироваться как ИП/ООО
3. Получить shop_id и secret_key в настройках
4. Настроить webhook URL для уведомлений
5. Добавить в `.env`:
   ```
   YOOKASSA_SHOP_ID=123456
   YOOKASSA_SECRET_KEY=test_...
   YOOKASSA_WEBHOOK_SECRET=whsec_...
   ```

**Реализация:**

```python
# services/payment_service.py

from yookassa import Configuration, Payment
from decimal import Decimal

class YooKassaService:
    def __init__(self, shop_id: str, secret_key: str):
        Configuration.account_id = shop_id
        Configuration.secret_key = secret_key

    async def create_payment(
        self,
        amount: Decimal,
        description: str,
        user_id: int,
        credits: int,
        return_url: str = "https://t.me/UspMusicBot"
    ) -> str:
        """
        Создать платеж

        Returns:
            URL для оплаты
        """
        payment = Payment.create({
            "amount": {
                "value": str(amount),
                "currency": "RUB"
            },
            "confirmation": {
                "type": "redirect",
                "return_url": return_url
            },
            "capture": True,
            "description": description,
            "metadata": {
                "user_id": str(user_id),
                "credits": str(credits)
            }
        })

        return payment.confirmation.confirmation_url

    async def check_payment_status(self, payment_id: str) -> Dict:
        """Проверить статус платежа"""
        payment = Payment.find_one(payment_id)
        return {
            "id": payment.id,
            "status": payment.status,
            "paid": payment.paid,
            "amount": payment.amount.value
        }
```

**Webhook обработка:**

```python
# webapp/api.py (FastAPI endpoint)

from fastapi import Request, HTTPException
from yookassa.domain.notification import WebhookNotification

@app.post("/webhook/yookassa")
async def yookassa_webhook(request: Request):
    """Обработка webhook от YooKassa"""

    # Проверка подписи
    body = await request.body()
    signature = request.headers.get("X-Yookassa-Signature")

    # Валидация (упрощенно, в реальности нужна полная проверка)
    if not signature:
        raise HTTPException(status_code=400, detail="No signature")

    # Парсинг уведомления
    notification = WebhookNotification(await request.json())
    payment = notification.object

    if payment.status == "succeeded":
        # Начислить кредиты
        user_id = int(payment.metadata["user_id"])
        credits = int(payment.metadata["credits"])

        async with get_db() as db:
            user = await db.get(User, user_id)
            user.balance += credits

            # Создать запись в транзакциях
            transaction = Transaction(
                user_id=user_id,
                payment_id=payment.id,
                provider="yookassa",
                credits_amount=credits,
                price_amount=Decimal(payment.amount.value),
                price_currency="RUB",
                status="completed",
                completed_at=func.now()
            )
            db.add(transaction)
            await db.commit()

        # Уведомить пользователя
        await bot.send_message(
            user_id,
            f"✅ Оплата успешна! Начислено {credits} треков."
        )

    return {"status": "ok"}
```

**Pricing YooKassa:**

- Комиссия: 2.8% + 10₽ за транзакцию (для ООО/ИП)
- Без абонентской платы
- Вывод на расчетный счет 1-2 рабочих дня

---

## 4. UI/UX дизайн

### 4.1 Цветовая схема

**Основной цвет**: Оранжевый (#FF6B35)
**Вторичный цвет**: Темно-синий (#003366)
**Акцент**: Белый (#FFFFFF)
**Фон**: Светло-серый (#F5F5F5)

### 4.2 Экраны бота (Telegram)

#### Экран 1: Приветствие (/start)

```
🎵 Привет, {first_name}!

Я бот, который поможет тебе создать крутой трек за 1 минуту!

Не нужны специальные навыки — просто пришли идею, я я сделаю все остальное.
Можешь даже 🎤 записать голосовое - я пойму!

✨ Как начать?

1️⃣ Опиши идею для песни - я напишу текст и предложу песню в разных стилях
или
2️⃣ Предложи текст песни, стиль - я создам для тебя профессиональный трек с вокалом!

Жми Создать песню 🔥 и давай творить музыку вместе! 🔥

Доступно треков: 3 🎵

[🎵 Создать песню]
[💡 Есть идея] [📝 Есть стихи]
[💳 Баланс] [📋 Мои песни]
```

#### Экран 2: Режим "Есть идея"

```
💡 Отлично! Опиши идею для песни.

Например:
- "Веселая песня про лето и море"
- "Грустная баллада о расставании"
- "Энергичный рок-трек про свободу"

Или просто 🎤 запиши голосовое сообщение!

[« Назад]
```

#### Экран 3: Генерация текста

```
⏳ Создаю текст песни на тему: "веселая песня про лето и море"

Это займет около 10 секунд...

[Генерация текста... 🎼]
```

#### Экран 4: Предпросмотр текста и выбор стиля

```
✨ Вот что получилось!

📝 Название: "Летняя волна"

[Verse 1]
Солнце светит ярко над волной
Песок между пальцев, ветер со мной
Смех и радость, музыка играет
Это лето никогда не забываем

[Chorus]
Летняя волна несет нас вдаль
Беззаботность и радость, забудь про печаль
Танцуем до утра под звездным небом
Это наше лето, мы здесь и теперь

[Verse 2]
Закаты алые, рассветы золотые
Каждый момент как картина живые
...

Теперь выбери стиль музыки:

[🎸 Pop Rock] [🎹 Electronic Pop] [🎺 Tropical House]
[✏️ Свой стиль]

[✏️ Изменить текст] [« Назад]
```

#### Экран 5: Генерация музыки

```
🎵 Создаю трек в стиле Pop Rock...

⏱ Это займет около 60-90 секунд
Пока можешь выпить кофе ☕️

[████████░░░░░░░░] 60%

Не закрывай бота, скоро будет готово!
```

#### Экран 6: Готовый трек

```
🎉 Готово! Твоя песня:

🎵 "Летняя волна"
⏱ Длительность: 3:24
🎸 Стиль: Pop Rock

[▶️ Прослушать] (отправляется MP3 файл)

💾 Трек сохранен в раздел "Мои песни"
Осталось треков: 2 🎵

[🔄 Создать еще] [📋 Мои песни] [💳 Купить треки]
```

#### Экран 7: Баланс

```
💳 Ваш баланс

Доступно треков: 2 🎵
Всего создано: 1 🎵

📊 История:
• 27.02.2026: -1 трек (Создание "Летняя волна")
• 27.02.2026: +3 трека (Регистрация)

💰 Купить треки:

[🎁 Стартовый]
10 треков - 299₽
~30₽ за трек

[🔥 Популярный]
30 треков - 799₽
~27₽ за трек
★ ВЫГОДНО!

[💎 Профессионал]
100 треков - 1,999₽
~20₽ за трек
★ САМОЕ ВЫГОДНОЕ!

[« Назад]
```

### 4.3 Web App дизайн

**Главная страница:**

```
┌─────────────────────────────────────┐
│  ← UspMusicBot               ☰      │
├─────────────────────────────────────┤
│                                     │
│     🎵 SoNata - дари эмоцИИ        │
│                                     │
│         ╭─────────────╮             │
│         │    🎵       │             │
│         │  создать    │  ← Кликабельная
│         │   ПЕСНЮ     │    кнопка (оранжевая)
│         ╰─────────────╯             │
│                                     │
│  Доступно: 2 трека                 │
│                                     │
├─────────────────────────────────────┤
│  📄      🎵      📋      💳         │
│ Стихи   Песни  Плейлист Баланс     │
└─────────────────────────────────────┘
```

**Страница "Мои песни":**

```
┌─────────────────────────────────────┐
│  ← Мои песни (12)           🔍      │
├─────────────────────────────────────┤
│                                     │
│  🎵 Летняя волна                    │
│  Pop Rock • 3:24                    │
│  27.02.2026                         │
│  [▶️] [⬇️] [💾 В плейлист]         │
│  ─────────────────────────────────  │
│                                     │
│  🎵 Ночной город                    │
│  Electronic • 2:45                  │
│  25.02.2026                         │
│  [▶️] [⬇️] [💾 В плейлист]         │
│  ─────────────────────────────────  │
│                                     │
│  [Загрузить еще...]                 │
│                                     │
├─────────────────────────────────────┤
│  📄      🎵      📋      💳         │
└─────────────────────────────────────┘
```

---

## 5. Безопасность и compliance

### 5.1 Авторизация

**Telegram WebApp:**

```python
import hashlib
import hmac

def validate_telegram_auth(init_data: str, bot_token: str) -> bool:
    """
    Валидация данных от Telegram WebApp

    Args:
        init_data: строка initData от Telegram.WebApp
        bot_token: токен бота

    Returns:
        True если данные валидны
    """
    try:
        parsed = dict(x.split('=') for x in init_data.split('&'))
        received_hash = parsed.pop('hash')

        data_check_string = '\n'.join(
            f"{k}={v}" for k, v in sorted(parsed.items())
        )

        secret_key = hmac.new(
            "WebAppData".encode(),
            bot_token.encode(),
            hashlib.sha256
        ).digest()

        calculated_hash = hmac.new(
            secret_key,
            data_check_string.encode(),
            hashlib.sha256
        ).hexdigest()

        return calculated_hash == received_hash
    except Exception:
        return False
```

### 5.2 Защита от спама

**Rate limiting (Redis):**

```python
import redis.asyncio as aioredis

class RateLimiter:
    def __init__(self, redis_client: aioredis.Redis):
        self.redis = redis_client

    async def check_rate_limit(
        self,
        user_id: int,
        action: str,
        max_requests: int = 5,
        window: int = 60
    ) -> bool:
        """
        Проверка rate limit

        Args:
            user_id: ID пользователя
            action: Тип действия (generate_song, etc.)
            max_requests: Максимум запросов
            window: Временное окно (секунды)

        Returns:
            True если лимит не превышен
        """
        key = f"rate_limit:{user_id}:{action}"

        current = await self.redis.incr(key)

        if current == 1:
            await self.redis.expire(key, window)

        return current <= max_requests
```

**Anti-spam middleware:**

```python
from aiogram import BaseMiddleware

class AntiSpamMiddleware(BaseMiddleware):
    def __init__(self, rate_limiter: RateLimiter):
        self.rate_limiter = rate_limiter

    async def __call__(self, handler, event, data):
        user_id = event.from_user.id

        if not await self.rate_limiter.check_rate_limit(user_id, "message"):
            await event.answer("⚠️ Слишком много запросов. Подожди минуту.")
            return

        return await handler(event, data)
```

### 5.3 Валидация входных данных

```python
from pydantic import BaseModel, Field, validator

class SongGenerationRequest(BaseModel):
    lyrics: str = Field(..., max_length=3000)
    style: str = Field(..., max_length=100)
    user_id: int

    @validator('lyrics')
    def validate_lyrics(cls, v):
        # Удалить лишние пробелы
        v = ' '.join(v.split())

        # Проверить на запрещенные слова (опционально)
        forbidden_words = ["spam", "xxx", ...]
        if any(word in v.lower() for word in forbidden_words):
            raise ValueError("Текст содержит запрещенные слова")

        return v

    @validator('style')
    def validate_style(cls, v):
        allowed_styles = [
            "pop", "rock", "hip-hop", "jazz", "electronic",
            "classical", "country", "r&b", "indie"
        ]

        if v.lower() not in allowed_styles:
            # Разрешить кастомные стили, но с длиной до 100 символов
            if len(v) > 100:
                raise ValueError("Стиль слишком длинный")

        return v
```

### 5.4 Логирование и мониторинг

```python
from loguru import logger

# Настройка loguru
logger.add(
    "logs/uspmusicbot_{time}.log",
    rotation="1 day",
    retention="30 days",
    level="INFO",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} | {message}"
)

# Использование
logger.info(f"User {user_id} generated song: {song_id}")
logger.warning(f"Rate limit exceeded for user {user_id}")
logger.error(f"Suno API error: {error_msg}")
```

---

## 6. Метрики и аналитика

### 6.1 Ключевые метрики

**KPI Dashboard (для админ-панели):**

1. **Пользователи:**
   - Всего пользователей
   - Новых пользователей (сегодня, неделя, месяц)
   - DAU (Daily Active Users)
   - MAU (Monthly Active Users)
   - Retention rate (Day 1, Day 7, Day 30)

2. **Контент:**
   - Всего треков создано
   - Треков за сегодня/неделю/месяц
   - Среднее количество треков на пользователя
   - Популярные стили музыки

3. **Финансы:**
   - Выручка (сегодня, месяц, всего)
   - ARPU (Average Revenue Per User)
   - Конверсия в платящих (%)
   - LTV (Lifetime Value)

4. **Технические:**
   - Среднее время генерации трека
   - Процент успешных генераций
   - Ошибки API (Suno, Claude, Whisper)
   - Uptime бота

### 6.2 Интеграция аналитики

**Google Analytics 4 (опционально для Web App):**

```javascript
// frontend/src/services/analytics.js

import ReactGA from 'react-ga4';

export const initGA = () => {
  ReactGA.initialize('G-XXXXXXXXXX');
};

export const trackPageView = (page) => {
  ReactGA.send({ hitType: 'pageview', page });
};

export const trackEvent = (category, action, label) => {
  ReactGA.event({
    category,
    action,
    label
  });
};

// Использование
trackEvent('Song', 'Generate', 'Pop Rock');
```

**Custom аналитика (база данных):**

```python
# services/analytics_service.py

class AnalyticsService:
    async def track_song_generation(
        self,
        user_id: int,
        style: str,
        duration: int,
        success: bool
    ):
        """Трекинг генерации песни"""
        await db.execute(
            """
            INSERT INTO analytics_events
            (user_id, event_type, event_data, created_at)
            VALUES (?, ?, ?, ?)
            """,
            (
                user_id,
                "song_generated",
                json.dumps({"style": style, "duration": duration, "success": success}),
                datetime.now()
            )
        )

    async def get_daily_stats(self, date: date) -> Dict:
        """Получить статистику за день"""
        result = await db.fetch_one(
            "SELECT * FROM analytics_daily WHERE date = ?",
            (date,)
        )
        return dict(result) if result else {}
```

---

## 7. План разработки

### Phase 1: MVP Backend (2-3 недели)

**Week 1:**
- ✅ Настройка окружения (Python, SQLite, Redis)
- ✅ Создание базовой структуры проекта
- ✅ Реализация database моделей (SQLAlchemy)
- ✅ Интеграция Telegram Bot (aiogram)
- ✅ Реализация /start команды и приветствия
- ✅ FSM states для conversation flow

**Week 2:**
- ✅ Интеграция Suno API client
- ✅ Интеграция Claude API для генерации текстов
- ✅ Реализация основного флоу: идея → текст → стиль → музыка
- ✅ Обработка асинхронной генерации (polling)
- ✅ Сохранение треков в базу данных

**Week 3:**
- ✅ Интеграция Whisper API для голосовых
- ✅ Реализация режима "Есть стихи"
- ✅ Система балансов (начисление/списание)
- ✅ Базовая интеграция YooKassa
- ✅ Тестирование и багфиксы

### Phase 2: Платежи и монетизация (1 неделя)

**Week 4:**
- ✅ Полная интеграция YooKassa (создание платежей)
- ✅ Webhook обработка для подтверждения оплаты
- ✅ Интеграция CryptoBot
- ✅ История транзакций
- ✅ UI для покупки пакетов

### Phase 3: Web App Frontend (2 недели)

**Week 5:**
- ✅ Настройка React проекта
- ✅ Интеграция Telegram WebApp SDK
- ✅ Создание главной страницы
- ✅ Страница "Мои песни" с плеером
- ✅ Аутентификация через Telegram

**Week 6:**
- ✅ Страница "Баланс" и покупка пакетов
- ✅ Страница "Стихи" (генерация текстов)
- ✅ Адаптивный дизайн (mobile/desktop)
- ✅ Деплой Web App

### Phase 4: Админ-панель и аналитика (1 неделя)

**Week 7:**
- ✅ Админ-команды в Telegram боте
- ✅ Статистика пользователей
- ✅ Управление балансами
- ✅ Рассылка сообщений
- ✅ Мониторинг API usage

### Phase 5: Тестирование и деплой (1 неделя)

**Week 8:**
- ✅ Unit tests (pytest)
- ✅ Integration tests
- ✅ Load testing (генерация 100+ треков)
- ✅ Настройка production сервера
- ✅ Docker контейнеризация
- ✅ CI/CD pipeline
- ✅ Публичный запуск

---

## 8. Деплой и инфраструктура

### 8.1 Docker

**Dockerfile:**

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Установка зависимостей
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копирование кода
COPY src/ ./src/
COPY assets/ ./assets/
COPY .env .env

# Запуск бота
CMD ["python", "-m", "src.bot.main"]
```

**docker-compose.yml:**

```yaml
version: '3.8'

services:
  bot:
    build: .
    container_name: uspmusicbot
    restart: unless-stopped
    env_file:
      - .env
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    depends_on:
      - redis

  redis:
    image: redis:7-alpine
    container_name: uspmusicbot_redis
    restart: unless-stopped
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  webapp:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    container_name: uspmusicbot_webapp
    restart: unless-stopped
    ports:
      - "3000:3000"
    environment:
      - REACT_APP_API_URL=https://api.uspmusicbot.ru

volumes:
  redis_data:
```

### 8.2 Nginx конфигурация

```nginx
# /etc/nginx/sites-available/uspmusicbot

server {
    listen 80;
    server_name uspmusicbot.ru www.uspmusicbot.ru;

    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name uspmusicbot.ru www.uspmusicbot.ru;

    ssl_certificate /etc/letsencrypt/live/uspmusicbot.ru/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/uspmusicbot.ru/privkey.pem;

    # Web App Frontend
    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # API Backend
    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # Webhook от YooKassa
    location /webhook/yookassa {
        proxy_pass http://localhost:8000/webhook/yookassa;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 8.3 Systemd сервис

```ini
# /etc/systemd/system/uspmusicbot.service

[Unit]
Description=UspMusicBot Telegram Bot
After=network.target

[Service]
Type=simple
User=uspmusicbot
WorkingDirectory=/home/uspmusicbot/UspMusicBot
ExecStart=/home/uspmusicbot/UspMusicBot/venv/bin/python -m src.bot.main
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

---

## 9. Приложения

### 9.1 Переменные окружения (.env.example)

```bash
# Telegram Bot
BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
BOT_USERNAME=UspMusicBot

# Admin IDs (через запятую)
ADMIN_IDS=123456789,987654321

# Suno API
SUNO_API_KEY=your_suno_api_key_here
SUNO_API_URL=https://api.aimlapi.com/v1

# Claude API (Anthropic)
ANTHROPIC_API_KEY=sk-ant-api03-xxxxx

# OpenAI Whisper
OPENAI_API_KEY=sk-xxxxx

# Payment Systems
YOOKASSA_SHOP_ID=123456
YOOKASSA_SECRET_KEY=test_xxxxx
YOOKASSA_WEBHOOK_SECRET=whsec_xxxxx

CRYPTOBOT_TOKEN=xxxxx

# Database
DATABASE_URL=sqlite+aiosqlite:///data/uspmusicbot.db

# Redis
REDIS_URL=redis://localhost:6379/0

# Web App
WEBAPP_URL=https://uspmusicbot.ru
API_URL=https://api.uspmusicbot.ru

# Logging
LOG_LEVEL=INFO

# Features (опционально)
ENABLE_REFERRAL_SYSTEM=true
FREE_TIER_CREDITS=3
MAX_LYRICS_LENGTH=3000
```

### 9.2 Зависимости (requirements.txt)

```
# Telegram Bot
aiogram==3.15.0
aiohttp==3.10.11

# Database
sqlalchemy==2.0.36
aiosqlite==0.20.0
alembic==1.14.0

# Redis
redis==5.0.1
aioredis==2.0.1

# Configuration
python-dotenv==1.0.1
pydantic==2.10.5
pydantic-settings==2.6.1

# AI Services
anthropic==0.18.1
openai==1.55.3
httpx==0.27.2

# Payment
yookassa==3.0.1
aiocryptopay==0.5.0

# Utilities
loguru==0.7.2
Pillow==11.0.0

# FastAPI
fastapi==0.115.6
uvicorn==0.34.0

# Testing
pytest==7.4.4
pytest-asyncio==0.23.3
pytest-cov==4.1.0
```

---

## 10. Контакты и поддержка

**Разработчик**: UspMusicBot Team
**Email**: support@uspmusicbot.ru
**Telegram**: @UspMusicBot
**GitHub**: https://github.com/uspmusicbot/UspMusicBot

---

**Дата создания ТЗ**: 27 февраля 2026
**Версия**: 1.0
**Статус**: Готово к разработке

---

## Чек-лист готовности к разработке

- [x] Определены функциональные требования MVP
- [x] Выбран технологический стек
- [x] Исследованы API (Suno, Claude, Whisper)
- [x] Разработана архитектура системы
- [x] Спроектирована база данных
- [x] Определена модель монетизации
- [x] Подготовлены UI/UX макеты
- [x] Составлен план разработки
- [x] Описаны требования к безопасности
- [x] Подготовлена инфраструктура деплоя

**Следующий шаг**: Начало разработки Phase 1 (MVP Backend)
