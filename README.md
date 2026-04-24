# kaggle-claude-plugin

Claude Code plugin для мониторинга Kaggle-соревнований: автоматический импорт, ML-классификация через Claude, Telegram-уведомления.

## Архитектура

Python-скрипты (`tools/`) владеют credentials и API-логикой. Claude выполняет только ML-логику: классификацию соревнований и перевод описаний. Credentials никогда не попадают в контекст Claude.

```
/kaggle-import:
  fetch_competitions.py (Kaggle API) → JSON → Claude классифицирует → save_classifications.py → SQLite

/kaggle-notify:
  get_pending.py (SQLite) → JSON → Claude переводит → send_telegram.py (Telegram API)
```

## Требования

- Python 3.10+
- Claude Code CLI
- Kaggle API ключ: kaggle.com → Settings → API → Create New Token
- Telegram Bot: создать через @BotFather, узнать chat_id через @userinfobot

## Установка

### 1. Клонировать репозиторий

```bash
git clone <repo-url> ~/kaggle-claude-plugin
cd ~/kaggle-claude-plugin
```

### 2. Запустить установщик

```bash
bash install.sh
```

Скрипт выполняет 4 шага автоматически:
1. Создаёт `.venv` и устанавливает зависимости (`kaggle`, `python-dotenv`, `requests`)
2. Создаёт `tools/.credentials` из шаблона
3. Копирует 5 скилов в `~/.claude/skills/`
4. Добавляет `SessionStart` хук в `~/.claude/settings.json` — без перезаписи существующих хуков

### 3. Заполнить credentials

```bash
nano tools/.credentials
```

```env
KAGGLE_USERNAME=your_kaggle_username
KAGGLE_KEY=your_kaggle_api_key

TELEGRAM_BOT_TOKEN=123456789:AAxxxxx
TELEGRAM_CHAT_ID=-1001234567890
```

**Где взять:**
- `KAGGLE_USERNAME` + `KAGGLE_KEY` → скачать `kaggle.json` на странице Settings → API, взять значения оттуда
- `TELEGRAM_BOT_TOKEN` → @BotFather → `/newbot`
- `TELEGRAM_CHAT_ID` → добавить бота в чат → написать сообщение → открыть `https://api.telegram.org/bot<TOKEN>/getUpdates`, найти `"chat": {"id": ...}`

### 4. Перезапустить Claude Code

Хуки загружаются при старте. После перезапуска плагин готов к работе.

### Проверка установки

```bash
.venv/bin/python tools/status.py
# {"total": 0, "pending_notify": 0, "shown": 0, ...}

.venv/bin/python tools/check_schedule.py
# {"should_import": true, "hours_since_last": null, ...}
```

## Использование

Все команды работают в любом проекте — скилы установлены глобально.

### `/kaggle-import` — загрузить и классифицировать

Запрашивает Kaggle API, Claude классифицирует каждое соревнование и сохраняет не-Other в базу.

```
Загружено 87 соревнований.
Классифицировано: CLASSIC ML — 31, LLM/NLP — 18, CV — 22, Other — 16.
Сохранено новых: 5 | Обновлено: 66 | Пропущено (Other): 16
```

Метки классификации:
- `CLASSIC ML` — табличные данные, градиентный бустинг, feature engineering
- `LLM/NLP` — языковые модели, текстовые задачи, RAG
- `CV` — изображения, видео, детекция объектов, сегментация
- `Other` — остальное (не сохраняется)

### `/kaggle-notify` — отправить уведомления в Telegram

Берёт ближайшие по дедлайну `pending_notify` соревнования (до 5), Claude переводит описания на русский, отправляет форматированные HTML-сообщения в Telegram и помечает как `shown`.

Пример сообщения:
```
Kaggle соревнование:

Title: CommonLit — Evaluate Student Summaries
Link: https://www.kaggle.com/competitions/commonlit-evaluate-student-summaries
Deadline: 2026-08-15
Theme: LLM/NLP

Описание:
Задача — автоматически оценивать качество кратких изложений школьников.
Метрика: RMSE по содержанию и формулировке.
```

### `/kaggle-status` — статус пайплайна

```
📊 Kaggle Assistant Status
──────────────────────────
Всего сохранено:    71
  Ожидают отправки: 12
  Отправлено:       59

По категориям:
  CLASSIC ML:  28
  LLM/NLP:     24
  CV:          19

Последний импорт: 2026-04-24 14:30 (3.2ч назад)
  Загружено: 87 | Новых сохранено: 5
```

### `/kaggle-review` — интерактивный просмотр

Показывает список `pending_notify` соревнований. По каждому:
- `s` — перевести и отправить в Telegram сейчас
- `k` — оставить в очереди
- `r` — переклассифицировать
- `x` — выйти

### `/kaggle-classify` — исправить классификацию

```
/kaggle-classify "Optiver - Trading at the Close"
```

Исправляет тип соревнования без повторного импорта. Статус уведомления не меняется.

## SessionStart хук

При каждом запуске Claude Code хук проверяет время последнего импорта. Если прошло более 24 часов — в начало сессии добавляется напоминание:

```
[kaggle-assistant] Последний импорт был 26.3ч назад. В базе 3 ожидают отправки.
Рекомендую выполнить /kaggle-import для обновления списка соревнований.
```

## Структура проекта

```
kaggle-claude-plugin/
├── install.sh                  # Установщик
├── install_hook.py             # Добавляет хук в ~/.claude/settings.json
├── requirements.txt            # kaggle, python-dotenv, requests
├── manifest.json               # Метаданные плагина
├── skills/
│   ├── kaggle-import/SKILL.md
│   ├── kaggle-classify/SKILL.md
│   ├── kaggle-notify/SKILL.md
│   ├── kaggle-status/SKILL.md
│   └── kaggle-review/SKILL.md
├── hooks/
│   ├── session_start.py        # Проверяет расписание, инжектирует контекст
│   └── hooks.json              # Шаблон конфигурации хука
└── tools/
    ├── db.py                   # SQLite схема и хелперы
    ├── fetch_competitions.py   # Kaggle API → JSON stdout
    ├── save_classifications.py # Классифицированный JSON → SQLite
    ├── get_pending.py          # pending_notify конкурсы → JSON stdout
    ├── mark_shown.py           # Пометить соревнование как shown
    ├── send_telegram.py        # Отправка HTML-сообщения в Telegram
    ├── check_schedule.py       # Проверка расписания импорта
    ├── status.py               # Агрегированная статистика
    └── .credentials.example   # Шаблон credentials
```

## Удаление

```bash
# Скилы
rm -rf ~/.claude/skills/kaggle-{import,classify,notify,review,status}

# Хук — удалить вручную из ~/.claude/settings.json:
# найти блок с "session_start.py" и удалить его из массива SessionStart
```

## Безопасность

Файл `tools/.credentials` добавлен в `.gitignore` и никогда не попадает в git. `PreToolUse` хук (при желании) можно настроить для блокировки прямого чтения `.credentials` Claude-ом — см. CLAUDE.md.
