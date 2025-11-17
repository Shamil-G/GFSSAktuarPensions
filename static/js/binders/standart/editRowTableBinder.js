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
            const field = edit_btn.dataset.field;

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

            if (!id || !field) {
                console.warn('❌ EditBinder: missing id or field');
                return;
            }
            this.save(id, field)
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
        //console.log('EditField. startEdit. id:', id, 'field:', field);
        const row = document.querySelector(`tr[data-order="${id}"]`);
        const input = row?.querySelector(`input[name="${field}"]`);
        //console.log('EditField. startEdit. id:', id, 'field:', field, 'row:', row, 'input:', input);
        if (!input) return;

        input.removeAttribute('readonly');
        input.classList.add('editing');

        row.querySelector(`.edit-btn[data-field="${field}"]`)?.style.setProperty('display', 'none');
        row.querySelector(`.save-btn[data-field="${field}"]`)?.style.setProperty('display', 'inline-block');
        row.querySelector(`.cancel-btn[data-field="${field}"]`)?.style.setProperty('display', 'inline-block');
    },

    cancelEdit(id, field) {
        //console.log('EditField. cancelEdit. id:', id, 'field:', field);
        const row = document.querySelector(`tr[data-order="${id}"]`);
        const input = row?.querySelector(`input[name="${field}"]`);
        if (!input) return;

        input.setAttribute('readonly', true);
        input.classList.remove('editing');

        row.querySelector(`.edit-btn[data-field="${field}"]`)?.style.setProperty('display', 'inline-block');
        row.querySelector(`.save-btn[data-field="${field}"]`)?.style.setProperty('display', 'none');
        row.querySelector(`.cancel-btn[data-field="${field}"]`)?.style.setProperty('display', 'none');
    },

    async save(id, field) {
        //console.log('EditField. save. id:', id, 'field:', field);
        const row = document.querySelector(`tr[data-order="${id}"]`);
        const input = row?.querySelector(`input[name="${field}"]`);
        if (!input) return;

        const value = input.value;

        if (input.__lastValue === value) {
            console.log(`⚠️ EditField. save skipped — значение не изменилось: ${value}`);
            return;
        }

        input.__lastValue = value;

        try {
            const res = await fetch(`/update-field`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ id, field, value })
            });
            if (!res.ok) {
                console.error(`❌ Failed to save ${field} for ${id}:`, res.status, await res.text());
                throw new Error(`Request failed with status ${res.status}`);
            }

            const result = await res.json();
            console.log(`✅ ${field} saved sum: ${value} for orderNum: ${id}:`, result);

            // Закроем видимость кнопок edit & cancel
            this.cancelEdit(id, field);
        } catch (err) {
            console.error(`❌ Failed to save ${field} for ${id}:`, err);
            alert('Error on saving ' + field);
        }
    }
};
