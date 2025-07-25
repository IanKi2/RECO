# Grid Strategy Simulator - Среда для Обучения Ботов

## Обзор проекта
**Grid Strategy Simulator** — это серверная реализация тактической игры на сетке, созданная как тестовая среда для разработки и обучения алгоритмов ИИ. Проект предоставляет предсказуемую, конфигурируемую среду с чёткими правилами, идеальную для экспериментов с игровыми стратегиями и алгоритмами управления агентами.

## Ключевые особенности
- **Детерминированная среда**: Поведение полностью предсказуемо при одинаковом seed
- **Простой API**: Легкая интеграция с алгоритмами обучения
- **Конфигурируемые параметры**: Настройка сложности через параметры мира
- **Изолированное окружение**: Минимальные внешние зависимости
- **Полная видимость состояния**: Возможность получения полного состояния игры

## Структура проекта
```
simulator/
├── src/
│   ├── simulation/
│   │   ├── game_objects.py     # Определение классов игровых объектов
│   │   ├── game_logic.py       # Реализация игровой механики
│   │   ├── validation.py       # Валидация входных данных
│   │   └── main.py             # Flask-сервер (API)
│   │
│   └── vizualizator.py         # Инструмент визуализации состояния
│
├── docs/
│   ├── DOCUMENTATION.md        # Руководство пользователя
│   └── SPECIFICATION.md        # Техническая спецификация
│
└── qa/
    ├── TASTCASE.md             # Тест кейсы
    └── TEST_PLAN.md            # Тест план
    
```

## Требования
- Python 3.8+
- Установленные зависимости:
  ```bash
  pip install perlin-noise numpy flask requests
  ```

## Быстрый старт

### Запуск сервера
```bash
cd simulator/src/simulation
python main.py
```

## Визуализация
Для отладки алгоритмов включен инструмент консольной визуализации:
```bash
python simulator/src/vizualizator.py
```

Инструмент отображает:
- Позицию агента и его направление
- Распределение NPC, ресурсов и препятствий
- Текущие игровые показатели (очки, количество респавнов)

## Документация
Подробная документация доступна в директории `docs`:
- **[DOCUMENTATION.md](docs/DOCUMENTATION.md)** - Руководство по использованию API
- **[SPECIFICATION.md](docs/SPECIFICATION.md)** - Технические детали реализации
