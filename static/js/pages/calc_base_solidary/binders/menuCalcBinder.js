import { TableLoader } from '/static/js/core/TableLoad.js';
import { PageManager } from '/static/js/core/PageContext.js';



export const MenuCalcBinder = {
    role: 'menu-calc',
    massive: true,

    resolveFragment(context, fragment_url, targetId) {
        let url = fragment_url?.trim() || null;
        if (!url) {
            const req = context.getRequest("calc_base_solidary._context", "fragment");
            url = req?.url;
        }

        let target = targetId?.trim() || null;
        if (!target) {
            const entry = context.tabContext.getEntry("calc_base_solidary._context");
            target = entry?.zones?.fragment?.replace('#','');
        }

        return { url, target };
    },

    loadFragment(fragment_url, targetId) {
        const context = PageManager?.get();
        const { url, target } = this.resolveFragment(context, fragment_url, targetId);
        if (!url || !target) return;
        TableLoader.load(url, target, {});
    },

    attach(dropdown, handler = null, force=false) {
        const button = dropdown.querySelector('button'); // теперь ищем просто кнопку

        if (!button) return;


        const labelSpan = button.querySelector('.label');
        const fragment_url = dropdown.dataset.fragment;
        const action_url = dropdown.dataset.action;
        const targetId = dropdown.dataset.target;
        const taskName = dropdown.dataset.task;

        console.log('menu-calc. MenuCalcBinder. Target:', targetId, ', URL:', fragment_url, ', action_url: ', action_url, ', taskName:', taskName);

        button.addEventListener('click', (event) => {
            event.preventDefault();

            const statusEl = document.getElementById('status');
            if (statusEl) statusEl.textContent = "Задача '" + taskName + "' выполняется...";

            if (action_url) {
                try {
                    fetch(action_url, { method: 'POST' })
                }
                catch (err) {
                    console.error('❌ Ошибка при fetch:', err);
                    if (statusEl) statusEl.textContent = "Ошибка выполнения " + err ;
                }
            }

            this.loadFragment(fragment_url, targetId);

            if (statusEl) statusEl.textContent = "";
        });
    },

    attachAll(handler = null, zone = document) {
        const dropdowns = zone.querySelectorAll(`[data-role="${this.role}"]`);
        dropdowns.forEach(dropdown => {
            const tag = dropdown.tagName;
            if (!['DIV', 'SECTION'].includes(tag)) {
                console.warn(`⚠️ MenuCalcBinder: skipping non-DIV element <${tag}>`, dropdown);
                return;
            }
            this.attach(dropdown, handler, true);
        });
    }
};
