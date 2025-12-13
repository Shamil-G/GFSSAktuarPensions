import { TableLoader } from '/static/js/core/TableLoad.js';
import { PageManager } from '/static/js/core/PageContext.js';
import { io } from '/static/js/core/socket.io.esm.min.js';


export const MenuBinder = {
    role: 'menu-calc',
    massive: true,

    resolveFragment(context, fragment_url, targetId) {
        let url = fragment_url?.trim() || null;
        if (!url) {
            const req = context.getRequest("calc_pens._context", "fragment");
            url = req?.url;
        }

        let target = targetId?.trim() || null;
        if (!target) {
            const entry = context.tabContext.getEntry("calc_pens._context");
            target = entry?.zones?.fragment?.replace('#', '');
        }

        return { url, target };
    },

    loadFragment(fragment_url, targetId) {
        const context = PageManager?.get();
        const { url, target } = this.resolveFragment(context, fragment_url, targetId);
        if (!url || !target) return;
        TableLoader.load(url, target, {});
    },

    attach(dropdown, handler = null, force = false) {
        if (dropdown.__menuBound && !force) return;
        dropdown.__menuBound = true;

        const button = dropdown.querySelector('.dropdown-button');
        console.log("Нашли кнопку: ", button);
        const hiddenInput = dropdown.querySelector('input[type="hidden"]');
        const items = dropdown.querySelectorAll('.dropdown-content a');

        console.log('MenuCalcBinder. hiddenInput: ', hiddenInput, ', items: ', items)

        if (!hiddenInput || items.length === 0) return;

        // const labelSpan = button.querySelector('.label');
        const fragment_url = dropdown.dataset.fragment;
        const action_url = dropdown.dataset.action;
        const targetId = dropdown.dataset.target;
        const taskName = dropdown.dataset.task;
        const work_url = dropdown.dataset.workUrl;


        console.log('MenuCalcBinder. Target:', targetId, ', FRAGMENT_URL:', fragment_url, ', action_url: ', action_url, ', taskName:', taskName, 'work_url: ', work_url);

        items.forEach(item => {
            item.addEventListener('click', (event) => {
                event.preventDefault();
                dropdown.classList.add("disabled");

                const anchor = event.currentTarget; // 🔒 гарантирует, что это именно <a>
                const value = anchor.dataset.value || 'filter';
                const workUrl = dropdown.dataset.workUrl;
                const sessionScenario = dropdown.dataset.sessionScenario;

                dropdown.classList.add("disabled");
                button.disabled = true;
                items.forEach(i => i.style.pointerEvents = "none");

                const statusEl = document.getElementById('status');
                if (statusEl) statusEl.textContent = "Задача '" + taskName + "' выполняется...";

                if (action_url) {
                    try {
                        const body = { taskName: taskName, scenario: sessionScenario, value: value, work_url: work_url }
                        console.log('*** MENU-CALC. BODY: ', body);
                        fetch(action_url, {
                            method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) })
                    }
                    catch (err) {
                        console.error('❌ Ошибка при fetch:', err);
                        if (statusEl) statusEl.textContent = "Ошибка выполнения " + err;
                    }
                }

                //this.loadFragment(fragment_url, targetId);

                //if (statusEl) statusEl.textContent = "";
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
        // 🔹 Подписка на WebSocket события
        if (!this.__socketBound) {
            const socket = io("http://localhost:5081", {
                transports: ["websocket"],
                withCredentials: false
            });
            socket.on("task_finished", (data) => {
                const { task_id, taskName, result } = data;

                console.log('TASK FINISHED. DATA: ', data, ', task_id: ', task_id, ', task_name: ', taskName, ', result: ', result)

                // обновляем статус
                if (result.status == 'success')
                    document.getElementById('status').textContent = `Задача '${taskName}' завершена успешно`;
                else
                    document.getElementById('status').textContent = `Задача '${taskName}' завершена сошибкой. Ошибка: ${result.message}`;

                const dropdown = document.querySelector(`[data-task="${taskName}"]`);
                if (dropdown) {
                    dropdown.classList.remove("disabled");

                    const button = dropdown.querySelector('.dropdown-button');
                    if (button) button.disabled = false;

                    const items = dropdown.querySelectorAll('.dropdown-content a'); // ← заново ищем
                    items.forEach(i => i.style.pointerEvents = "auto");
                }
                // при необходимости перерисовываем таблицу
                const targetId = dropdown?.dataset.target;
                const url = dropdown?.dataset.fragment;
                console.log('Для обновления фрагмента используем. URL: ', url, ', targetId: ', targetId, ', Result: ', result);
                if (targetId && url) {
                    console.log('Обновляем данные. URL: ', url, ', targetId: ', targetId, ', Result: ', result);
                    TableLoader.load(url, targetId, { value: result });
                }
            });
            this.__socketBound = true; // чтобы не подписываться повторно
        }
    }

};
