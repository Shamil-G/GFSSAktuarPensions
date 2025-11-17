// Вешается на второе tbody в основной таблице
// Первое tbody - шапка с фильтрами
// Второе tbody - данные

export const RowClickBinder = {
    role: 'row-click',

    attach(el) {
        if (!el || el.__rowClickBinder) return;
        el.__rowClickBinder = true;

        const actionName = el.dataset.action;

        //console.log("RowClickBinder. actionName\n\t\t\tel:\t", actionName);

        el.addEventListener('click', event => {
            const tag = event.target.tagName;
            const ignoreTags = ['INPUT', 'BUTTON', 'SELECT', 'TEXTAREA', 'LABEL']

            //console.log("RowClickBinder. listener tag:\t", tag);

            if (ignoreTags.includes(tag)) {
                return;
            }

            const row = event.target.closest('.clickable-row');
            if (!row || !el.contains(row)) return;

            const orderNum = row.dataset.order;
            if (!orderNum || !actionName) return;

            const handler = window[actionName] || API?.[actionName];
            if (typeof handler === 'function') {
                handler(orderNum, row);
                //console.log('ROW_CLICK →', actionName, orderNum);
            } else {
                console.warn(`❌ RowClickBinder: handler '${actionName}' not found`);
            }
        });
    },

    attachAll(zone = document) {
        //console.log("RowClickBinder. attachAll\n\t\t\tel:\t", zone);

        const containers = zone.matches?.(`[data-role~="${this.role}"]`)
            ? [zone]
            : Array.from(zone.querySelectorAll(`[data-role~="${this.role}"]`));

        //console.log("RowClickBinder. attachAll\n\t\t\tzone:\t", zone, "\n\t\t\tcontainers:\t", containers);
        containers.forEach(el => this.attach(el));
    }
};
