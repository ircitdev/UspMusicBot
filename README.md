# UspMusicBot - AI Music Generation Telegram Bot

<div align="center">

🎵 **Создавай музыку за 1 минуту с помощью AI** 🎵

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org)
[![aiogram](https://img.shields.io/badge/aiogram-3.15-blue.svg)](https://docs.aiogram.dev)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

</div>

## 📖 Описание

**UspMusicBot** - это интеллектуальный Telegram-бот для создания профессиональных музыкальных треков с помощью AI. Бот использует Suno API для генерации музыки, Claude API для создания текстов песен и OpenAI Whisper для транскрибации голосовых сообщений.

### Возможности

- 🎤 **Генерация музыки по идее** - опишите идею или запишите голосовое сообщение
- 📝 **Генерация музыки по готовым текстам** - предоставьте свой текст песни
- 🎵 **Широкий выбор стилей** - Pop, Rock, Hip-hop, Jazz, Electronic и многое другое
- 💾 **Плейлисты** - сохраняйте и управляйте созданными треками
- 💳 **Система балансов** - покупка пакетов генераций через YooKassa и CryptoBot
- 🌐 **Web App** - полнофункциональный веб-интерфейс

### Референс

Проект вдохновлен ботом [@gusli_aibot](https://t.me/gusli_aibot) (SoNata - Создать песню).

---

## 🚀 Быстрый старт

### Требования

- Python 3.11+
- Redis 7+
- SQLite (или PostgreSQL для production)
- API ключи:
  - Telegram Bot Token
  - Suno API (через AIMLAPI.com)
  - Claude API (Anthropic)
  - OpenAI API (для Whisper)
  - YooKassa (опционально)

### Установка

1. Клонируйте репозиторий:
```bash
git clone https://github.com/uspmusicbot/UspMusicBot.git
cd UspMusicBot
```

2. Создайте виртуальное окружение:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate  # Windows
```

3. Установите зависимости:
```bash
pip install -r requirements.txt
```

4. Скопируйте `.env.example` в `.env` и заполните переменные:
```bash
cp .env.example .env
nano .env
```

5. Примените миграции базы данных:
```bash
alembic upgrade head
```

6. Запустите бота:
```bash
python -m src.bot.main
```

---

## 🏗️ Архитектура

```
UspMusicBot/
├── src/
│   ├── bot/              # Telegram bot logic
│   ├── handlers/         # Command & callback handlers
│   ├── services/         # External API integrations
│   ├── database/         # ORM models & CRUD
│   ├── webapp/           # FastAPI Web App
│   └── utils/            # Utilities
├── frontend/             # React Web App
├── assets/               # Images & templates
├── tests/                # Unit & integration tests
└── docs/                 # Documentation
```

Подробная архитектура описана в [TECHNICAL_SPECIFICATION.md](TECHNICAL_SPECIFICATION.md).

---

## 📚 Документация

- [Техническое задание](TECHNICAL_SPECIFICATION.md)
- [API Documentation](docs/API.md) (TODO)
- [Deployment Guide](docs/DEPLOYMENT.md) (TODO)
- [Contributing Guidelines](CONTRIBUTING.md) (TODO)

---

## 🔑 Получение API ключей

### 1. Telegram Bot Token

1. Найдите [@BotFather](https://t.me/BotFather) в Telegram
2. Отправьте `/newbot` и следуйте инструкциям
3. Скопируйте полученный токен в `.env`:
   ```
   BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
   ```

### 2. Suno API (через AIMLAPI)

1. Перейдите на [aimlapi.com](https://aimlapi.com)
2. Зарегистрируйтесь и создайте API ключ
3. Добавьте в `.env`:
   ```
   SUNO_API_KEY=your_api_key
   ```

### 3. Claude API (Anthropic)

1. Перейдите на [console.anthropic.com](https://console.anthropic.com)
2. Создайте аккаунт и получите API ключ
3. Добавьте в `.env`:
   ```
   ANTHROPIC_API_KEY=sk-ant-api03-xxxxx
   ```

### 4. OpenAI API (Whisper)

1. Перейдите на [platform.openai.com](https://platform.openai.com)
2. Создайте API ключ
3. Добавьте в `.env`:
   ```
   OPENAI_API_KEY=sk-xxxxx
   ```

### 5. YooKassa (опционально)

1. Зарегистрируйтесь на [yookassa.ru](https://yookassa.ru)
2. Получите `shop_id` и `secret_key`
3. Настройте webhook URL
4. Добавьте в `.env`:
   ```
   YOOKASSA_SHOP_ID=123456
   YOOKASSA_SECRET_KEY=test_xxxxx
   ```

---

## 🐳 Docker

Запуск с помощью Docker Compose:

```bash
docker-compose up -d
```

Проверка логов:

```bash
docker-compose logs -f bot
```

Остановка:

```bash
docker-compose down
```

---

## 🧪 Тестирование

Запуск всех тестов:

```bash
pytest
```

С покрытием кода:

```bash
pytest --cov=src --cov-report=html
```

Запуск конкретного теста:

```bash
pytest tests/test_handlers/test_song_creation.py
```

---

## 📊 Метрики и мониторинг

Бот логирует все события в:
- `logs/uspmusicbot_{time}.log` - основные логи
- База данных `analytics_daily` - дневная статистика

Просмотр логов в реальном времени:

```bash
tail -f logs/uspmusicbot_*.log
```

---

## 🛠️ Разработка

### Создание новой миграции

```bash
alembic revision --autogenerate -m "Description of changes"
alembic upgrade head
```

### Форматирование кода

```bash
black src/
isort src/
```

### Линтинг

```bash
flake8 src/
mypy src/
```

---

## 🤝 Contributing

Мы приветствуем вклад в проект! Пожалуйста, прочитайте [CONTRIBUTING.md](CONTRIBUTING.md) перед отправкой PR.

### Процесс контрибуции:

1. Fork репозитория
2. Создайте feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit изменения (`git commit -m 'Add some AmazingFeature'`)
4. Push в branch (`git push origin feature/AmazingFeature`)
5. Откройте Pull Request

---

## 📝 Changelog

См. [CHANGELOG.md](CHANGELOG.md) для истории изменений.

---

## 📄 Лицензия

Этот проект лицензирован под MIT License - см. [LICENSE](LICENSE) для деталей.

---

## 👥 Команда

- **Lead Developer**: [@your_telegram](https://t.me/your_telegram)
- **Support**: support@uspmusicbot.ru

---

## 🌟 Благодарности

- [aiogram](https://github.com/aiogram/aiogram) - Telegram Bot framework
- [Suno AI](https://suno.com) - Music generation API
- [Anthropic](https://www.anthropic.com) - Claude AI
- [OpenAI](https://openai.com) - Whisper API
- [@gusli_aibot](https://t.me/gusli_aibot) - Inspiration

---

## 📞 Поддержка

Если у вас возникли вопросы или проблемы:

- 📧 Email: support@uspmusicbot.ru
- 💬 Telegram: [@UspMusicBot](https://t.me/UspMusicBot)
- 🐛 Issues: [GitHub Issues](https://github.com/uspmusicbot/UspMusicBot/issues)

---

<div align="center">

**Создано с ❤️ командой UspMusicBot**

[Документация](TECHNICAL_SPECIFICATION.md) • [Telegram](https://t.me/UspMusicBot) • [GitHub](https://github.com/uspmusicbot/UspMusicBot)

</div>
