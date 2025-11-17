import { TableLoader } from '/static/js/core/TableLoad.js';

// В первой строке мастер-таблицы есть поля-фильтры
// изменение которых приводит к мзменению содержания
// мастер-таблицы и ассоциироанных slave таблиц
// Здесь мы привязываемся ко всем INPUT-BUTTON элементам
// вложенным в помеченные зоны и в обработчике событий
// вызываем загрузку фрагментов:
// FragmentBinder.load(url, targetId, { value: node_value });

// Фильтруем по INPUT field: ИИН

export const FilterIinBinder = {
    role: 'filter-iin',
    massive: true,

    attach(el) {
        if(!el) return;
        if (el.__filter_iin) return;
        el.__filter_iin = true;

        const tag = el.tagName;
        //console.log(`${this.role}: tag =`, el.tagName);

        // Привязка keydown к INPUT
        if (tag === 'INPUT') {
            const url = el.dataset.url;
            const targetId = el.dataset.target;

            if (!url || !targetId) {
                console.warn('❌ FilterIinBinder: missing url or targetId on INPUT', el);
                return;
            }

            if (!el.__fragmentKeydownBound) {
                //console.log('filter-iin. binding to keyDown');
                el.__fragmentKeydownBound = true;
                el.addEventListener('keydown', (event) => {
                    //console.log('filter-iin. keyDown event!');
                    if (event.key === 'Enter') {
                        event.preventDefault();
                        const value = el.value.trim();
                        if (value === el.__lastValue) return;
                        el.__lastValue = value;
                        TableLoader.load(url, targetId, { value });
                    }
                });
            }

            return; // завершить, не привязываем click
        }

        // Привязка click к BUTTON или A
        const isInteractive = ['BUTTON', 'A'].includes(tag);
        if (isInteractive) {
            const url = el.dataset.url;
            const targetId = el.dataset.target;
            const input = el.closest('td')?.querySelector('input');

            if (!url || !targetId || !input) {
                console.warn('❌ FilterIinBinder: missing url, targetId, or input', el);
                return;
            }

            el.addEventListener('click', (event) => {
                event.preventDefault();
                const value = input.value.trim();
                if (value === input.__lastValue) return;
                input.__lastValue = value;
                //console.log('filter-iin. addEventListener to ', input);
                TableLoader.load(url, targetId, { value });
            });
        }
    },

    attachAll(zone = document) {
        const triggers = zone.querySelectorAll(`[data-role="${this.role}"]`);
        triggers.forEach(el => {
/*            console.log(`FilterIinBinder.attachAll: tag = ${el.tagName}`);*/
            this.attach(el);
        });
    }

};
