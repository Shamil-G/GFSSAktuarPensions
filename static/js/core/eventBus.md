# 📡 EventBus — Архитектурная шина событий

Масштабируемый механизм для управления пользовательскими событиями через `CustomEvent`. Позволяет изолировать источники и обработчики, передавать контекст, ретранслировать события между зонами и логировать всё происходящее.

---

## 1. 🧩 Назначение

`EventBus` служит для:

- генерации семантически осмысленных событий (`row-click`, `tab-changed`, `filter-applied`)
- изоляции источников и обработчиков
- передачи контекста через `event.detail`
- ретрансляции событий между зонами
- логирования и отладки архитектурных взаимодействий

Он заменяет прямые вызовы `addEventListener('click', ...)` на декларативную модель событий.

---

## 2. ⚙️ Описание функций

### `EventBus.on(eventName, handler, zone = document)`
Подписка на событие в указанной зоне.
```js
EventBus.on('row-click', (event) => {
    console.log('ROW_CLICK:', event.detail);
});
```

### `EventBus.off(eventName, handler, zone = document)`
Отписка от событий
```js
EventBus.off('row-click', handler);
```

### `EventBus.once(eventName, handler, zone = document)`
Одноразовая подписка — автоматически удаляется после первого вызова

```js
EventBus.once('data-loaded', (event) => {
    console.log('Данные загружены:', event.detail);
});
```

### `EventBus.emit(eventName, detail = {}, zone = document)`
Инициирует событие с произвольным контекстом.

```js
EventBus.emit('tab-changed', { name: 'orders' });
```

### `EventBus.scope(zone)`
Создаёт scoped-шину событий, привязанную к конкретной зоне.

```js
const localBus = EventBus.scope(document.getElementById('sidebar'));
localBus.emit('filter-applied', { field: 'status', value: 'pending' })
```

### `EventBus.forward(fromZone, toZone, eventName)`
Ретранслирует событие между зонами.

```js
EventBus.forward(tableBody, sidebarPanel, 'row-selected');
```

### `EventBus.debug = true`
Включает логирование всех операций.

```js
EventBus.debug = true;
```

--- 

## 3. 📘 Примеры вызова функций

### Клик по строке
```js
row.addEventListener('click', () => {
    EventBus.emit('row-click', { id: row.dataset.order });
});
```

### Обработка выбора в меню
```js
EventBus.on('menu-changed', (event) => {
    const { value, label } = event.detail;
    FragmentBinder.load('/fragment/orders', 'tableBody', { status: value });
});
```

### Централизованная маршрутизация
```js
EventBus.on('tab-changed', (event) => {
    TabManager.select(event.detail.name);
});
```

---

## 4. 🧬 Примеры встройки в data-role

### Вызов события из элемента с ролью
```html
<td data-role="row" onclick="EventBus.emit('row-click', { id: this.dataset.order })">
    Заказ №123
</td>
```

### Привязка обработчика к роли
```js
document.querySelectorAll('[data-role="row"]').forEach(el => {
    EventBus.on('row-click', (event) => {
        if (event.detail.id === el.dataset.order) {
            el.classList.add('selected');
        }
    });
});
```

### Делегирование через BinderRegistry
```js
BinderRegistry.register('row', {
    attach(el) {
        el.addEventListener('click', () => {
            EventBus.emit('row-click', { id: el.dataset.order });
        });
    }
});
```
