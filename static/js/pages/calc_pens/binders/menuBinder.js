import { TableLoader } from '/static/js/core/TableLoad.js';

export const MenuBinder = {
    role: 'menu-calc',
    massive: true,

    attach(dropdown, handler = null, force=false) {
        if (dropdown.__menuBound && !force) return;
        //if (force) console.log('🔁 MenuBinder: принудительная повторная привязка для', dropdown);
        dropdown.__menuBound = true;

        const button = dropdown.querySelector('.dropdown-button');
        const hiddenInput = dropdown.querySelector('input[type="hidden"]');
        const items = dropdown.querySelectorAll('.dropdown-content a');

        if (!button || !hiddenInput || items.length === 0) return;

        const labelSpan = button.querySelector('.label');
        const url = dropdown.dataset.url;
        const targetId = dropdown.dataset.target;
        const actionName = dropdown.dataset.action;

        items.forEach(item => {
            item.addEventListener('click', (event) => {
                event.preventDefault(); // 🔴 ОБЯЗАТЕЛЬНО

                const anchor = event.currentTarget; // 🔒 гарантирует, что это именно <a>

                //console.log("📦 MenuBinder.attach ANCHOR initialized");

                const value = anchor.dataset.value || anchor.textContent.trim();
                const label = anchor.dataset.label || value;

                // 🔹 Стандартное поведение
                hiddenInput.value = value;
                if (labelSpan) labelSpan.textContent = label;

                items.forEach(i => i.classList.remove('selected'));
                anchor.classList.add('selected');

                dropdown.dispatchEvent(new CustomEvent('menu-changed', {
                    bubbles: true,
                    detail: { value, label }
                }));

                // 🔹 Проверка на повторное значение
                //if (dropdown.__lastValue === value) {
                //    console.log(`⚠️ MenuBinder: duplicate value (${value}) — handler call skipped`);
                //    return;
                //}
                //dropdown.__lastValue = value;

                //console.log(`MenuBinder. Dropdown: ${value}`);

                if (actionName) {
                    //console.log("MenuBinder. actionName: ", actionName);
                    const fn = window[actionName] || API?.[actionName];
                    //console.log("MenuBinder. FN: ", fn);
                    if (typeof fn === 'function') {
                        fn(value, label, dropdown);
                        //console.log('MenuBinder. run function: ', value, label, dropdown);
                        //return;
                    } else {
                        console.warn(`❌ MenuBinder: handler '${actionName}' not found`);
                    }
                }

                // Не всегда при изменении пункта меню надо что то обновлять
                if (targetId && url) {
                    //console.log('MenuBinder. CALL TableLoader.load. targetId: ', targetId, ", URL: ", url, ", VALUE: ", value);
                    TableLoader.load(url, targetId, { value });
                }
                //else console.log('MenuBinder. SKIP  TableLoader.load. targetId: ', targetId, ", URL: ", url, ", VALUE: ", value);
            });
        });
    },

    attachAll(handler = null, zone = document) {
        const dropdowns = zone.querySelectorAll(`[data-role="${this.role}"]`);
        dropdowns.forEach(dropdown => {
            const tag = dropdown.tagName;
            if (!['DIV', 'SECTION'].includes(tag)) {
                console.warn(`⚠️ MenuBinder: skipping non-DIV element <${tag}>`, dropdown);
                return;
            }
            this.attach(dropdown, handler, true); // 🔁 всегда с force
        });
    }

};
