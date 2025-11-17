import { TabContext } from './TabContext.js';
import { TabLoader } from './TabLoader.js';
//import { TabTreeRegistry } from '../tabTreeRegistry.js';
import * as TabUtil from '/static/js/_aux/tabUtil.js';

//Метод	Назначение
//initialize()	Загружает tabTree, инициализирует TabContext, создаёт TabLoader
//loadTab()	Загружает фрагмент по стратегии и orderNum
//loadCustom()	Загружает произвольный URL в зону, с привязкой биндеров
//getZone()	Возвращает DOM - элемент зоны
//getRequest()	Возвращает конфигурацию запроса для зоны
//attachZoneBinders()	Привязывает биндеры к конкретной зоне
//list()	Возвращает список табов по стратегии загрузки

export const PageManager = {
    current: null,
    async set(name) {
        if (this.current?.destroy) {
            this.current.destroy();
        }
        const context = new PageContext(name);
        await context.initialize(); // сразу инициализируем
        this.current = context;
        return this.current;
    },
    get() {
        return this.current;
    }
};

export class PageContext {
    constructor(pageName, tabTree = null) {
        this.pageName = pageName;
        this.tabTree = null;
        this.tabContext = null;
        this.loader = null;
    }

    destroy() {
        console.log('PageContext Destroying for', this.pageName);
        this.tabContext?.destroy?.(); // если TabContext поддерживает очистку
        this.tabContext = null;

        this.tabTree?.destroy?.(); // если TabContext поддерживает очистку
        this.tabTree = null;

        this.tabTree = null;
    }

    async initialize() {
        console.log('PageContext: initializing for', this.pageName);

        this.tabTree = await PageContext.resolveTabTree(this.pageName);;
        //this.tabTree = await TabTreeRegistry.resolve(this.pageName);
        this.tabContext = new TabContext(this.tabTree);

        await this.tabContext.load(); // или initialize(), если есть

        this.loader = new TabLoader(this.tabContext);
        this.attachZoneBinders();

        console.log('PageContext: initialized');
    }

    static async resolveTabTree(pageName) {
        try {
            const module = await import(`/static/js/pages/${pageName}/tabTree.js`);
            return module.tabTree ?? {};
        } catch (err) {
            console.error(`❌ PageContext: failed to load tabTree for "${pageName}"`, err);
            return {};
        }
    }

    getZone(tabName, zoneKey) {
        if (!this.tabContext) {
            console.warn('❌ tabContext не инициализирован');
            return null;
        }
        const zone = this.tabContext.getZone(tabName, zoneKey);
        if (!zone) {
            console.warn(`❌ Зона "${zoneKey}" не найдена в табе "${tabName}"`);
        }
        return zone;
    }

    getRequest(tabName, orderNum, zoneKey = 'fragment') {
        const entry = this.tabContext.getEntry(tabName);
        const req = entry?.request?.[zoneKey];
        if (!req) return null;

        const method = req.method || 'GET';
        const url = typeof req.url === 'function' ? req.url(orderNum) : req.url;
        const body = req.params ? req.params(orderNum) : null;

        return { method, url, body };
    }

    async loadTab(tabName, orderNum, zoneKey = 'fragment') {
        const entry = this.tabContext.getEntry(tabName);
        if (!entry?.zones?.[zoneKey]) return;
        await this.loader.loadZone(tabName, zoneKey, orderNum);
    }

    async loadCustom(tabName, zoneKey, url, body = null, method = 'POST') {
        const zone = this.getZone(tabName, zoneKey);
        if (!zone) {
            console.warn(`PageContext: zone "${zoneKey}" not found for tab "${tabName}"`);
            return;
        }

        try {
            const response = await fetch(url, {
                method,
                headers: method === 'POST' ? { 'Content-Type': 'application/json' } : {},
                body: method === 'POST' ? JSON.stringify(body) : null
            });

            if (!response.ok) {
                console.error(`PageContext: failed to load "${tabName}" zone "${zoneKey}" — ${response.status}`);
                return;
            }

            const html = await response.text();
            zone.innerHTML = html;

            this.tabContext.attachZoneBinders(tabName, zoneKey);
        } catch (err) {
            console.error(`PageContext: error loading "${tabName}" zone "${zoneKey}"`, err);
        }
    }

    list({ strategy = 'all', zoneKey = null } = {}) {
        const prefix = this.pageName + '.';
        const all = this.tabContext.getTabNames().filter(name => name.startsWith(prefix));

        return all.filter(name => {
            const entry = this.tabContext.getEntry(name);
            if (!entry?.loadStrategy) return false;

            if (strategy === 'all') return true;

            if (typeof entry.loadStrategy === 'string') {
                return entry.loadStrategy === strategy;
            }

            if (zoneKey && typeof entry.loadStrategy === 'object') {
                return entry.loadStrategy[zoneKey] === strategy;
            }

            return false;
        });
    }

    attachBinders(tabName) {
        this.tabContext.attachBinders(tabName);
    }

    attachZoneBinders(tabName = null, zoneKey = null) {
        const tabNames = tabName ? [tabName] : this.tabContext.getTabNames();
        //console.log("attachZoneBinders. tabNames: ", tabNames, '\n\t\t\tthis.tabContext.getTabNames(): ', this.tabContext.getTabNames());

        tabNames.forEach(name => {
            //console.log("attachZoneBinders. name: ", name);
            const entry = this.tabContext.getEntry(name);
            const zones = zoneKey ? [zoneKey] : Object.keys(entry?.zones || {});

            //console.log("entry: ", entry, "\n\t\t\tzones: ", zones)

            zones.forEach(key => {
                const zone = this.getZone(name, key);
                if (!zone) {
                    console.warn(`❌ Зона "${key}" не найдена в табе "${name}"`);
                    return;
                }

                // 🔄 Получаем биндеры из entry, а не из BinderRegistry
                const binders = entry.binders?.[key] || [];

                //console.log("attachZoneBinders. key: ", key, "\n\t\t\tbinders: ", binders)

                binders.forEach(binder => {
                    //console.log("attachZoneBinders:\n\ttabName:\t", name,
                    //    ",\tzone(zoneKey):\t", key, "\n\ttypeof binder:\t", typeof binder?.attachAll,
                    //    ",\tbinder:\t", binder);
                    if (typeof binder?.attachAll === 'function') {
                        //console.log("attachZoneBinders. function ...")
                        binder.attachAll(zone);
                    } else {
                        console.warn('❌ Binder без метода attach:', binder);
                        console.trace();
                    }
                });
            });
        });
    }

    onTabSwitch(tabName) {
        const zoneNames = {
            tabs: this.pageName + '_tabs', content: this.pageName + '_tabs_content'
        }
        //console.log("zoneNames: ", zoneNames);

        const tabsZone = document.getElementById(zoneNames.tabs);
        const contentZone = document.getElementById(zoneNames.content);

        //console.log('tabsZone:\t', tabsZone, "contentZone:\t", contentZone);

        if (!tabsZone || !contentZone) {
            console.warn(`onTabSwitch: зоны tabs или tabs_content не найдены`);
            return;
        }

        const sharedTab = document.getElementById('sharedTabId');
        if (sharedTab) sharedTab.value = tabName;

        // 🔹 Переключение кнопок в зоне tabs
        tabsZone.querySelectorAll('[data-tab]').forEach(btn => {
            const isActive = btn.dataset.tab === tabName;
            btn.classList.toggle('active', isActive);
        });

        // 🔹 Переключение панелей в зоне tabs_content
        //console.log('[TabLoader] zone parent:', contentZone);
        contentZone.querySelectorAll('.tab-panel').forEach(panel => {
            const isActive = panel.dataset.tab === tabName;
            panel.classList.toggle('active', isActive);
            //console.log("TAB-PANEL:", panel, "\n\t\t\tisActive: ", isActive, " : ", tabName );
            //console.log("TAB-PANEL. tabName: ", tabName, isActive);
            panel.setAttribute('aria-hidden', isActive ? 'false' : 'true');
        });

        const targetPanel = contentZone.querySelector(`.tab-panel[data-tab="${tabName}"]`);
        if (!targetPanel) {
            console.warn(`onTabSwitch: панель с id="${tabName}" не найдена`);
            return;
        }

        // 🔹 Загрузка данных
        const orderNum = TabUtil.getOrderNum();
        //console.log("targetPanel: ", targetPanel);
        if (!TabUtil.loadFromCache(tabName, orderNum)) {

            //console.log("this.tabContext: ", orderNum);

            //
            const loader = new TabLoader(this.tabContext);
            loader.loadZone(tabName, 'content', TabUtil.getOrderNum());

            //this.loadTabContent?.(tabName, targetPanel, orderNum);
        }

        // 🔹 Активация контекста
        //TabContext.activate(tabName, targetPanel);
    }
}
