## Документация по Игровому Серверу

---

### 🎮 Обзор Системы
Сервер реализует пошаговую игру на сетке, где вы управляете агентом. Каждый запрос `/command` продвигает игру на один шаг. Основные компоненты:
- **Агент** (ваш персонаж)
- **NPC** (неигровые персонажи)
- **Ресурсы** (для сбора)
- **Препятствия** (непроходимые объекты)

---

### 🌍 Игровой Мир
#### Параметры поля
| Параметр       | Диапазон      | Описание                          |
|----------------|---------------|-----------------------------------|
| Размер поля    | 10x10 - 100x100 | Квадратная карта                |
| Координаты     | (0,0) - (N-1,N-1) | (0,0) - верхний левый угол      |

#### Сущности на карте
| Тип         | Количество | Особенности                     |
|-------------|------------|---------------------------------|
| **Агент**   | 1          | Управляется вами               |
| **NPC**     | до 1000    | Двигаются случайно             |
| **Ресурсы** | до 1000    | Дают очки при сборе            |
| **Препятствия** | до 30% поля | Блокируют движение            |

---

### ⚙️ Основные Механики
#### 1️⃣ Управление агентом
- **Движение**: `up`, `down`, `left`, `right`
- **Ограничения**:
  - Нельзя выходить за границы карты
  - Нельзя ходить на NPC/препятствия
- **Штраф за нарушение**: 
  - -10 очков 
  - Автоматическое возрождение агента

#### 2️⃣ Атака
- Поражает всех NPC в соседних клетках (вверх/вниз/влево/вправо)
- **Награда**: +10 очков за каждого NPC

#### 3️⃣ Сбор ресурсов
- Автоматически при входе на клетку с ресурсом
- **Награда**: +5 очков

#### 4️⃣ Движение NPC
- Включается при инициализации (`npc_movement=true`)
- Каждый NPC двигается случайно, избегая других объектов

---

### 📊 Система Очков
| Действие          | Изменение очков |
|-------------------|-----------------|
| Сбор ресурса      | +5              |
| Убийство NPC      | +10             |
| Респавн агента    | -10             |

---

### 👀 Видимость
- **Радиус обзора**: Задается при старте игры (5-100 клеток)
- Видны только объекты в круговой зоне вокруг агента (включая диагонали)

---

## 📡 API Endpoints

### 1️⃣ Инициализация игры
`POST /init`
```json
{
  "field_size": 50,
  "npc_count": 100,
  "resource_count": 200,
  "obstacle_percent": 15,
  "npc_movement": true,
  "agent_vision_radius": 5
}
```
**Ответ**: 
```json
{
  "status": "game_initialized",
  "parameters": { /* ваши настройки */ }
}
```

---

### 2️⃣ Отправка команд
`POST /command`
```json
// Для движения:
{"command": "move", "direction": "left"}

// Для атаки:
{"command": "attack"}
```

**Ответ**:
```json
{
  "width": 50,
  "height": 50,
  "score": 115,
  "respawns": 1,
  "agent": {"x": 10, "y": 5},
  "visible_entities": {
    "npcs": [{"x": 12, "y": 5}],
    "resources": [{"x": 8, "y": 5}],
    "obstacles": [{"x": 5, "y": 5}]
  }
}
```

---

### 3️⃣ Дополнительные методы
| Метод | Endpoint       | Описание                     |
|-------|----------------|------------------------------|
| GET   | `/full-state`  | Полное состояние игры        |
| GET   | `/status`      | Текущий статус сервера       |

---

## ⚠️ Типовые ошибки
- `400 Bad Request`: Неправильные параметры команды
- `404 Not Found`: Игра не инициализирована
- `409 Conflict`: Игра уже запущена

---

## 🔄 Логика шага игры
1. Прием команды от игрока
2. Обработка действия агента (движение/атака)
3. Движение NPC (если включено)
4. Проверка сбора ресурсов
5. Расчет видимой зоны
6. Формирование ответа

---

> 💡 Совет: Начните с вызова `/init`, затем отправляйте команды через `/command`.