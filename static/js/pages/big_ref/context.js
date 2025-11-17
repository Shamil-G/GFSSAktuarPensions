import { MenuBinder } from '/static/js/binders/standart/menuBinder.js';
import { HelperBinder } from '/static/js/binders/standart/helperBinder.js';

export const bigRefTabContext = {
    // Значения zone определяют id=""
    zones: {
        mainTableHelper: '#big_ref_mainHelper',
        fragment: '#big_ref',
        menu: '#big_ref_MenuZone'
    },

    binders: {
        mainTableHelper: [HelperBinder],
        menu: [MenuBinder],
    },

    request: {
        fragment: {
            method: 'POST',
            url: orderNum => `/filter-period-big-ref`
        },
        filters: {
            method: 'POST',
            url: '/big_ref_filters',
            params: () => ({}) // 👈 пустой объект, если нет orderNum
        }
    },

    bindScope: {
        filters: 'global'    // искать в document, независимо от fragment
    },

    loadStrategy: {
        filters: 'eager'
    }
};

export default bigRefTabContext;