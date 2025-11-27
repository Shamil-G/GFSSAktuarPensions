import { PageManager } from '/static/js/core/PageContext.js';

// Редактируем значения ячеек в каждой записи
export const EditRowTableBinder = {
    role: 'edit-row',

    attach(row) {
        if (row.__EditRowTableBinder) return;
        row.__EditRowTableBinder = true;

        row.addEventListener('click', (e) => {
            //console.log("edit-row. listener edit ...");
            const edit_btn = e.target.closest('.edit-btn');
            if (!edit_btn || !row.contains(edit_btn)) return;

            e.stopPropagation();

            const id = edit_btn.dataset.id;
            //console.log("edit-row. ID: ", id);
            //const year = edit_btn.dataset.year;
            //console.log("edit-row. year: ", year);
            const field = edit_btn.dataset.field;
            //console.log("edit-row. field: ", field);


            if (!id || !field) {
                console.warn('❌ EditBinder: missing id or field');
                return;
            }

            this.startEdit(id, field);
        });
        row.addEventListener('click', (e) => {
            //console.log("edit-row. listener cancel ...");
            const cancel_btn = e.target.closest('.cancel-btn');
            if (!cancel_btn || !row.contains(cancel_btn)) return;

            e.stopPropagation();

            const id = cancel_btn.dataset.id;
            const field = cancel_btn.dataset.field;
            //const year = cancel_btn.dataset.year;
            console.log("cancel edit-row. id: ", id);


            if (!id || !field) {
                console.warn('❌ EditBinder: missing id or field');
                return;
            }

            this.cancelEdit(id, field)
        });
        row.addEventListener('click', (e) => {
            //console.log("edit-row. listener save ...");
            const save_btn = e.target.closest('.save-btn');
            if (!save_btn || !row.contains(save_btn)) return;

            e.stopPropagation();

            const id = save_btn.dataset.id;
            const field = save_btn.dataset.field;
            //const year = save_btn.dataset.year;
            const value = save_btn.dataset.value;

            //console.log("ADDEventListener. SAVE edit-row. year: ", year);

            if (!id || !field) {
                console.warn('❌ EditBinder: missing id or field');
                return;
            }
            this.save(id, field, value)
        });
    },

    attachAll(zone = document) {
        const containers = zone.matches?.(`[data-role~="${this.role}"]`)
            ? [zone]
            : Array.from(zone.querySelectorAll(`[data-role~="${this.role}"]`));

        //console.log("EditRowTableBinder\n\t\t\tzone:\t", zone, "\n\t\t\tcontainers:\t", containers);
        containers.forEach(container => this.attach(container));
    }
    ,

    startEdit(id, field) {
        const row = document.querySelector(`tr[data-role="edit-row"][data-id="${id}"]`);
        if (!row) {
            console.warn(`❌ startEdit: строка с id="${id}" не найдена`);
            return;
        }
        const input = row?.querySelector(`input[name="${field}"]`);
        if (!input) {
            console.warn(`❌ startEdit: поле "${field}" не найдено`);
            return;
        }
        //console.log('EditField. startEdit. id:', id, 'field:', field, 'row:', row, 'input:', input);

        input.removeAttribute('readonly');
        input.classList.add('editing');
        input.focus();

        row.querySelector(`.edit-btn[data-field="${field}"]`)?.style.setProperty('display', 'none');
        row.querySelector(`.save-btn[data-field="${field}"]`)?.style.setProperty('display', 'inline-block');
        row.querySelector(`.cancel-btn[data-field="${field}"]`)?.style.setProperty('display', 'inline-block');
    },

    cancelEdit(id, field) {
        //console.log('EditField. cancelEdit. id:', id, 'field:', field);
        const row = document.querySelector(`tr[data-role="edit-row"][data-id="${id}"]`);
        if (!row) {
            console.warn(`❌ cancelEdit: строка с id="${id}" не найдена`);
            return;
        }
        const input = row?.querySelector(`input[name="${field}"]`);
        if (!input) {
            console.warn(`❌ cancelEdit: поле "${field}" не найдено`);
            return;
        };

        input.setAttribute('readonly', true);
        input.classList.remove('editing');

        row.querySelector(`.edit-btn[data-field="${field}"]`)?.style.setProperty('display', 'inline-block');
        row.querySelector(`.save-btn[data-field="${field}"]`)?.style.setProperty('display', 'none');
        row.querySelector(`.cancel-btn[data-field="${field}"]`)?.style.setProperty('display', 'none');
    },

    async save(id, field) {
        const context = PageManager?.get();

        const row = document.querySelector(`tr[data-role="edit-row"][data-id="${id}"]`);
        if (!row) {
            console.warn(`❌ save: строка с id="${id}" не найдена`);
            return;
        }

        const input = row?.querySelector(`input[name="${field}"]`);
        if (!input) {
            console.warn(`❌ save: поле "${field}" не найдено`);
            return;
        }

        const value = input.value;
        if (input.__lastValue === value) {
            console.log(`⚠️ EditField. save skipped — значение не изменилось: ${value}`);
            return;
        }

        input.__lastValue = value;

        // Получаем запрос с уже встроенным body
        const req = context.getRequest('coeff_ref._context', 'save_row_coeff', id, field, value);
        if (!req || !req.url || !req.body) {
            console.warn('❌ Некорректный REQUEST:', req);
            return;
        }

        //console.log('📡 SAVE REQUEST:', req);

        try {
            const res = await fetch(req.url, {
                method: req.method,
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(req.body)
            });

            if (!res.ok) {
                const errorText = await res.text();
                console.error(`❌ Failed to save ${field} for ${id}:`, res.status, errorText);
                throw new Error(`Request failed with status ${res.status}`);
            }

            const result = await res.json();
            //console.log(`✅ ${field} saved: ${value} for ${id}/${year}`, result);

            this.cancelEdit(id,field);
        } catch (err) {
            console.error(`❌ Exception during save ${field} for ${id}:`, err);
            alert(`Ошибка при сохранении поля "${field}"`);
        }
    }

};
