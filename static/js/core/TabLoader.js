//import { BinderRegistry } from './TabContext.js';
// Загрузка фрагмента/Таба - при иерархической структуре проекта

//  Метод	        Назначение	                                Источник URL	        Привязка биндеров
//  loadCustomZone	Ручная загрузка конкретной зоны по URL	    передаётся напрямую	    attachZoneBinders(tabName, zoneKey)
//  loadZone	    Загрузка зоны по конфигу request	        из getRequest(...)	    attachBinders(tabName)(можно фильтровать)
//  load	        Загрузка основной зоны fragment	            из getRequest(...)	    attachBinders(tabName)
import { getCacheKey, loadFromCache, addToCache, fadeInsert } from '/static/js/_aux/tabUtil.js';

export class TabLoader {
    constructor(tabContext) {
        this.tabContext = tabContext;
    }

    async loadCustomZone(tabName, zoneKey, url, body = null, method = 'POST') {
        console.log("loadCustomZone. tabName: ", tabName, "\n\t\t\tzoneKey: ", zoneKey, "\n\t\t\turl: ", url );
        const zone = this.tabContext.getZone(tabName, zoneKey);
        console.log("loadCustomZone. zone: ", zone);
        console.log("loadCustomZone. zone: ", this.tabContext.getTabNames());
        if (!zone) {
            console.warn(`TabLoader: zone "${zoneKey}" for "${tabName}" not found`);
            return;
        }

        try {
            const response = await fetch(url, {
                method,
                headers: method === 'POST' ? { 'Content-Type': 'application/json' } : {},
                body: method === 'POST' ? JSON.stringify(body) : null
            });

            if (!response.ok) {
                console.error(`TabLoader: failed to load "${tabName}" zone "${zoneKey}" — ${response.status}`);
                return;
            }

            const html = await response.text();
            zone.innerHTML = html;

            this.tabContext.attachZoneBinders(tabName, zoneKey); // точечная привязка
        } catch (err) {
            console.error(`TabLoader: error loading "${tabName}" zone "${zoneKey}"`, err);
        }
    }

    async loadZone(tabName, zoneKey, orderNum, use_cache = true) {
        const zone = this.tabContext.getZone(tabName, zoneKey);
        if (!zone) {
            console.warn(`TabLoader: zone "${zoneKey}" for "${tabName}" not found`);
            return;
        }
        if (use_cache && loadFromCache(tabName, orderNum, zoneKey)) return;

        const req = this.tabContext.getRequest(tabName, zoneKey, orderNum);

        //console.log("TabLoader: loadZone, REQ: ", req);
        
        if (!req || !req.url) {
            console.warn(`TabLoader: invalid request config for "${tabName}" zone "${zoneKey}"`);
            return;
        }

        try {
            const response = await fetch(req.url, {
                method: req.method,
                headers: req.method === 'POST' ? { 'Content-Type': 'application/json' } : {},
                body: req.method === 'POST' ? JSON.stringify(req.body) : null
            });
            
            if (!response.ok) {
                console.error(`TabLoader: failed to load "${tabName}" zone "${zoneKey}" — ${response.status}`);
                return;
            }
            const html = await response.text();

            fadeInsert(zone, html);
            //zone.innerHTML = html;

            const cacheKey = getCacheKey(tabName, orderNum, zoneKey);
            addToCache(cacheKey, html);
            //this.tabContext.attachBinders(tabName); // можно фильтровать по zoneKey, если нужно
        } catch (err) {
            console.error(`TabLoader: error loading "${tabName}" zone "${zoneKey}"`, err);
        }
    }

    // ... 
    async load(tabName, orderNum) {
        const entry = this.tabContext.getEntry(tabName);
        if (!entry) {
            console.warn(`TabLoader: tab "${tabName}" not found`);
            return;
        }

        const zone = this.tabContext.getZone(tabName, 'fragment');
        if (!zone) {
            console.warn(`TabLoader: zone for "${tabName}" not found`);
            return;
        }

        const req = this.tabContext.getRequest(tabName, orderNum);
        if (!req || !req.url) {
            console.warn(`TabLoader: invalid request config for "${tabName}"`);
            return;
        }

        try {
            const response = await fetch(req.url, {
                method: req.method,
                headers: req.method === 'POST' ? { 'Content-Type': 'application/json' } : {},
                body: req.method === 'POST' ? JSON.stringify(req.body) : null
            });

            if (!response.ok) {
                console.error(`TabLoader: failed to load "${tabName}" — ${response.status}`);
                return;
            }

            const html = await response.text();
            zone.innerHTML = html;

            this.tabContext.attachBinders(tabName);
        } catch (err) {
            console.error(`TabLoader: error loading "${tabName}"`, err);
        }
    }

    unload(tabName) {
        const entry = this.tabContext.getEntry(tabName);
        if (!entry || !entry.zones) return;

        for (const selector of Object.values(entry.zones)) {
            const zone = typeof selector === 'string' ? document.querySelector(selector) : null;
            if (zone) zone.innerHTML = '';
        }

        this.tabContext.detachBinders(tabName);
    }


}
