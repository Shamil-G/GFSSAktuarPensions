//import { BinderRegistry } from '/static/js/core/binderRegistry.js'
//import { FragmentBinder } from './fragmentBinder.js'

import * as TabUtil from '/static/js/_aux/tabUtil.js';

export function defaultTabInit(tabId, container) {
    // Анимация
    container.classList.add('fade-out');
    setTimeout(() => {
        container.classList.remove('fade-out');

        // Таймстамп
        const tsNode = container.querySelector(`#${tabId}Timestamp`);
        if (tsNode) {
            tsNode.textContent = `🕓 Загружено ${TabUtil.formatAge(Date.now())}`;
        }

        // Инициализация
        BinderRegistry.init(container);
        // MenuBinder.attachAll(container); // если нужно

    }, 150);
}

function setTimestamp(targetZone, tabId, html) {
    //console.log("TabRegistry. tabId: ", tabId, "\n\t\ttargetZone: ", targetZone);
    const timestampZone = TabUtil.getTimestampZone(targetZone, tabId);
    /*                if (typeof html === 'string' && cached?.html && html !== cached.html) {*/
    if (typeof html === 'string') {
        if (timestampZone) {
            //console.log("TabRegistry. Update timestampZone", Date.now());
            timestampZone.textContent = `Загружено: ${new Date().toLocaleTimeString()}`;
        } else {
            console.warn("TabRegistry. timestampZone не найден в ", html);
        }
    }
}

export const TabRegistry = {
    _tabs: {},

    register(tabId, { url, zoneSelector, onInit }) {
        this._tabs[tabId] = { url, zoneSelector, onInit };
    },

    get(tabId) {
        return this._tabs[tabId];
    },

    list() {
        return Object.entries(this._tabs).map(([tabId, { url, zoneSelector }]) => ({
            id: tabId,
            url,
            zoneSelector
        }));
    },

    async load(tabId, orderNum) {
        const entry = this._tabs[tabId];
        
        if (!entry) {
            console.warn(`Нет регистрации вкладки "${tabId}"`);
            return;
        }

        const { headers, body } = TabUtil.serializeParams({ order_num: orderNum});
        const targetZone = document.querySelector(entry.zoneSelector) || document.querySelector('.fragment-zone');

        try {
            //console.log("TabRegistry. START FETCH: ", Date.now());

            const res = await fetch(entry.url, { method: 'POST', headers, body });
            const html = await res.text();

            const cacheKey = TabUtil.getCacheKey(tabId, orderNum);
            let cached = TabUtil.tabCache[cacheKey];

            if (!cached || html != cached.html) {

                delete TabUtil.tabCache[cacheKey];
                TabUtil.addToCache(cacheKey, html);
                cached = TabUtil.tabCache[cacheKey];

                tabUtil.fadeInsert(targetZone, html);
                setTimestamp(targetZone, tabId);

                //console.log("TabRegistry. Finish LOAD.  target: ", tabId, ", URL: ", entry.url, ", headers: ", headers, ", body: ", body);
            }
            //return html; // ✅ теперь можно кэшировать

        } catch (err) {
            console.error('TabRegistry.load error:', err, " : ", Date.now());
            return null;
        }

    }
};
