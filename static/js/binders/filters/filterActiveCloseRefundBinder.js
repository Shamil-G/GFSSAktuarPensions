import { TableLoader } from '/static/js/core/TableLoad.js';

// В первой строке мастер-таблицы есть поля-фильтры
// изменение которых приводит к мзменению содержания
// мастер-таблицы и ассоциироанных slave таблиц
// Здесь мы привязываемся ко всем INPUT-BUTTON элементам
// вложенным в помеченные зоны и в обработчике событий
// вызываем загрузку фрагментов:
//
// TableLoader.load(url, targetId, { value: node_value });
//
// Закрытые долги и не закрытые долги

export const FilterActiveCloseRefundBinder = {
    role: 'filter-active-close',
    massive: true,

    attach(el) {
        if (!el) return; // Передана пустая зона ?!
        if (el.__filter_active_close) return;
        el.__filter_active_close = true;

        //console.log('FragmentToggleBinder: double bind', el);
        //console.trace(); // покажет стек вызова

        const tag = el.tagName;
        //console.log(`${this.role}: tag =`, el.tagName);

        const url = el.dataset.url;
        const targetId = el.dataset.target;

        if (!url || !targetId) {
            console.warn('❌ filter-active-close: missing URL or targetId. URL: ', url);
            console.warn('❌ filter-active-close: missing URL or targetId. targetId: ', targetId);
            console.warn('❌ filter-active-close: missing URL or targetId. el: ', el);
            return;
        }

        const input = el.querySelector('input[type="hidden"]') || el.closest('td')?.querySelector('input[type="hidden"]');
        const icon = el.querySelector('.icon') || el.querySelector('span') || el;

        const iconActive = el.dataset.iconActive || '🟡';
        const iconClosed = el.dataset.iconClosed || '✅';

        if (!input || !icon) {
            console.warn('❌ filter-active-close: missing input or icon', el);
            return;
        }

        if (el.__fragmentToggleBound) return;
        el.__fragmentToggleBound = true;

        el.addEventListener('click', (event) => {
            event.preventDefault();

            const current = input.value;
            const next = current === 'active' ? 'closed' : 'active';

            input.value = next;
            icon.textContent = next === 'active' ? iconActive : iconClosed;

            TableLoader.load(url, targetId, { value: next });
            console.log("ADDED CLICK LISTENER. TOGGLE →", next);
        });
    },

    attachAll(zone = document) {
        const toggles = zone.querySelectorAll(`[data-role="${this.role}"]`);
        toggles.forEach(el => this.attach(el));
    }
};
