import * as TabUtil from '/static/js/_aux/tabUtil.js';
import { PageManager } from '/static/js/core/PageContext.js';

export const RefreshDirectContentTabBinder = {
    role: 'refresh-content',
    massive: true,

    attach(el) {
        if (!el) return; // Передана пустая зона ?!
        if (el.____refreshDirectContentTabBinder) return;
        el.____refreshDirectContentTabBinder = true;

        //console.log('FragmentToggleBinder: double bind', el);
        //console.trace(); // покажет стек вызова

        const tabName = el.dataset.tab;
        if (!tabName) {
            console.warn("tabName undefined");
            return;
        }
        //console.log(`----------- refresh-content: ${this.role}: tabName =`, tabName);

        el.addEventListener('click', (event) => {
            event.preventDefault();

            const orderNum = TabUtil.getOrderNum();
            if (!orderNum) return;

            const cacheKey = TabUtil.getCacheKey(tabName, orderNum);
            delete TabUtil.tabCache[cacheKey];

            PageManager.get()?.onTabSwitch(tabName);
        });
    },

    attachAll(zone = document) {
        const isTrigger = zone.matches?.(`[data-role="${this.role}"]`);
        const triggers = isTrigger ? [zone] : zone.querySelectorAll(`[data-role="${this.role}"]`);
        //console.log("---------- refresh-content. attachAll. ZONE: ", zone)
        //console.log("---------- refresh-content. attachAll. triggers: ", triggers)
        triggers.forEach(el => {
            this.attach(el);
        });
    }
}
