export const BinderRegistry = {
    binders: {},
    register(role, binder, options = {}) {
        if (!role || typeof role !== 'string') {
            console.warn('❗️ Miss role on registering:', role);
            return;
        }
        if (!binder || typeof binder !== 'object') {
            console.warn('❗️ Miss BINDER for role:', role);
            return;
        }
        this.binders[role] = {
            ...binder,
            massive: options.massive === true
        }
/*        console.log(`✅ Binder registered for role: ${role}`);*/
    },
    // documetn - this is default value
    init(target = document) {

        if (!(target instanceof Element || target instanceof Document)) {
            console.warn('❌ BinderRegistry.init: target is not a DOM Element', target);
            return;
        }

        const root = target instanceof Document ? target.body : target;

        Object.entries(this.binders).forEach(([role, binder]) => {
            if (role === 'fragment') return; // ❌ исключаем фрагмент-биндер
            if (typeof binder.attachAll === 'function') {
                binder.attachAll(root);
            }
        });
    },
    getBindersForZone(zoneKey) {
        return Object.entries(this.binders)
            .filter(([_, binder]) => binder.zone === zoneKey)
            .map(([_, binder]) => binder);
    },

    get(role) {
        return this.binders[role];
    },

    listRoles() {
        return Object.keys(this.binders);
    }
};

