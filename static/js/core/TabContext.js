//import { BinderRegistry } from './BinderRegistry.js';

// Инициализируем ТАБ-ы
export class TabContext {
    constructor(tabTree, rootPath = []) {
        this.tabTree = tabTree;
        this.rootPath = rootPath;
        this.flatMap = new Map();
    }

    register(tabName, config) {
        this.flatMap.set(tabName, config);
    }

    async load() {
        const entries = Object.entries(this.tabTree);
        console.log('TabContext.load: tabTree =', this.tabTree);
        console.log('TabContext.load: entries =', entries);

        for (const [key, loader] of entries) {
            if (typeof loader !== 'function') {
                console.warn(`❌ TabContext: loader for "${key}" is not a function`);
                continue;
            }
            const module = await loader();
            const entry = module.default || module;

            this.flatMap.set(key, entry);
        }
    }


    async initialize() {
        await this._loadRecursive(this.tabTree, this.rootPath);
        console.log("TabContext. initialize. flatMap: ", this.flatMap);
    }

    async _loadRecursive(tree, parentPath = []) {
        console.log("TabContext. recursive: ", tree, ", parentPath: ", parentPath)
        for (const [key, value] of Object.entries(tree)) {
            const path = [...parentPath, key];
            const tabName = path.join('.');

            if (typeof value === 'function') {
                try {
                    const contextModule = await value();
                    const config = contextModule.default;
                    this.flatMap.set(tabName, { tabName, ...config });
                    console.log("TabContext. function: ", tree, ", parentPath: ", parentPath)
                }
                catch (err) {
                    console.error(`TabContext. Error load zone ${tabName}`)
                }
            } else
            if (typeof value === 'object') {
                console.log("TabContext. object: ", value)
                if (value._context) {
                    try {
                        console.log("TabContext. value context: ", value._context)
                        const contextModule = await value._context();
                        const config = contextModule.default;
                        this.flatMap.set(tabName, { tabName, ...config });
                    }
                    catch (err) {
                        console.error(`TabContext. Error load zone ${tabName}`)
                    }
                }
                await this._loadRecursive(value, path);
            }
        }
    }

    getTabNames() {
        return Array.from(this.flatMap.keys());
    }

    getEntry(tabName) {
        return this.flatMap.get(tabName);
    }

    getZone(tabName, zoneKey = 'fragment') {

        //console.log('entry:', this.getEntry(tabName));

        const entry = this.flatMap.get(tabName);
        if (!entry || !entry.zones) return null;

        const selector = entry.zones[zoneKey];
        if (!selector || typeof selector !== 'string') return null;

        const scope = entry.bindScope?.[zoneKey] || 'local';

        if (scope === 'global') {
            return document.querySelector(selector);
        }

        if (zoneKey === 'fragment') {
            return document.querySelector(selector);
        }

        const fragmentSelector = entry.zones?.fragment;
        const fragmentRoot = fragmentSelector ? document.querySelector(fragmentSelector) : null;

        return fragmentRoot?.querySelector(selector) || document.querySelector(selector);
    }


    getBinders(tabName) {
        const entry = this.getEntry(tabName);
        return entry?.binders || [];
    }

    getRequest(tabName, zoneKey, orderNum) {
        const entry = this.getEntry(tabName);
        if (!entry) {
            console.warn(`[TabContext] Tab "${tabName}" not registered`);
            return null;
        }

        const zoneRequest = entry.request?.[zoneKey];
        if (!zoneRequest) {
            console.warn(`[TabContext] Request config for zone "${zoneKey}" in tab "${tabName}" not found`);
            return null;
        }

        // Принудительно используем POST
        const method = 'POST';
        const url = zoneRequest.url;

        if (!url) {
            console.warn(`[TabContext] URL for zone "${zoneKey}" in tab "${tabName}" is missing`);
            return null;
        }

        const body = typeof zoneRequest.params === 'function'
            ? zoneRequest.params(orderNum)
            : zoneRequest.params;

        return {
            method,
            url,
            body
        };
    }

    getZones (name) {
        const ctx = this.flatMap?.get(`${name}._context`);
        return ctx?.zones || {};
    };

    registerAll() {
        for (const [tabName, entry] of this.flatMap.entries()) {
            const req = entry.request;
            if (req?.url && entry.zoneSelector) {
                TabRegistry.register(tabName, {
                    url: typeof req.url === 'function' ? req.url(0) : req.url,
                    zoneSelector: entry.zoneSelector
                });
            }
        }
    }

}
