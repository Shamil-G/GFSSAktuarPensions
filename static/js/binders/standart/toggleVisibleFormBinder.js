//import * as TabUtil from '/static/js//tabUtil.js';
import { PageManager } from '/static/js/core/PageContext.js';

export const ToggleVisibleFormBinder = {
    role: 'toggle-visible-form',
    massive: true,

    attach(el) {
        if (!el) return; // Передана пустая зона ?!
        if (el.____toggleVisbleFormBinder) return;
        el.____toggleVisbleFormBinder = true;

        //console.log('FragmentToggleBinder: double bind', el);
        //console.trace(); // покажет стек вызова

        const tabName = el.dataset.tab;
        if (!tabName) {
            console.warn("tabName undefined");
            return;
        }
        el.addEventListener('click', (event) => {
            event.preventDefault();
            const btnTarget = event.target;
            const tabName = btnTarget.dataset.tab;
            const formName = btnTarget.dataset.form;
            const containerName = formName + 'Container';
            //console.log("Click on role: ", this.role, "\n\t\t\tevent.target:\t",
            //    "\n\t\t\tformName:\t", formName, "\n\t\t\tcontainerName:\t", containerName,
            //    "\n\t\t\ttabName:\t", tabName
            //);

            const container = document.getElementById(containerName);
            const form = document.getElementById(formName);

            if (!container) {
                console.warn("ToggleVisibleForm. Container is empty!");
                return;
            }
            //console.log("Click container: ", container);

            if (form) {
                // Если форма уже загружена — удалим
                container.innerHTML = '';
                // Изменим название кнопки на Добавить
                if (btnTarget) {
                    btnTarget.textContent = btnTarget.dataset.labelAdd;
                }
            }
            else {
                // Загружаем HTML по fetch
                const orderNum = document.getElementById('sharedOrderNum')?.value || '';
                if (!orderNum) {
                    console.log("--- toggle-visible-form. orderNum is empty!");
                    return;
                }
                fetch(`/form_fragment?form=${tabName}`)
                //fetch(`/form_fragment?form=${tabName}&order_num=${TabUtil.getOrderNum()}`)
                    .then(response => response.text())
                    .then(html => {
                        container.innerHTML = html;

                        const form = document.getElementById(formName);

                        if (form) {
                            PageManager.get().attachZoneBinders(tabName, 'form');

                            // На форме есть "action="/add_", но надо добавить поле order_num
                            // Мы переопределяем поведение submit на форме со свойством "action"
                            form.addEventListener('submit', async event => {
                                // ❗ Не даём браузеру самому перезагрузить страницу
                                event.preventDefault();

                                const form = event.target;
                                const formData = new FormData(form);

                                formData.append('order_num', orderNum);
                                //console.log("ToggleVisibleForm. SUBMIT. order_num:\t", orderNum, "\n\t\t\tformData:\t", formData)
                                try {
                                    const response = await fetch(form.action, {
                                        method: 'POST',
                                        body: formData
                                    });

                                    if (!response.ok) throw new Error(`HTTP ${response.status}`);
                                    const result = await response.json();

                                    console.log('[FormSubmit] Успешный ответ:', result);
                                    // 🔸 Здесь можно обновить UI, скрыть форму, показать статус и т.д.
                                    const tabName = form.closest('[data-tab]')?.dataset.tab;
                                    const refreshBtn = document.querySelector(`[data-role="refresh-content"][data-tab="${tabName}"]`);
                                    if (refreshBtn) {
                                        refreshBtn.click();
                                    } else {
                                        console.warn(`Кнопка обновления не найдена для tabName = ${tabName}`);
                                    }
                                } catch (err) {
                                    console.error('[FormSubmit] Ошибка отправки:', err);
                                    // 🔸 Покажите ошибку пользователю, если нужно
                                }

                            });
                        };

                        if (btnTarget) {
                            btnTarget.textContent = btnTarget.dataset.labelClose;
                        }

                    })
                    .catch(error => console.error('Error load fragment form: ${tabName}:', error));
            }
        });
    },

    attachAll(zone = document) {
        const isTrigger = zone.matches?.(`[data-role="${this.role}"]`);
        const triggers = isTrigger ? [zone] : zone.querySelectorAll(`[data-role="${this.role}"]`);
        triggers.forEach(el => {
            this.attach(el);
        });
    }
}