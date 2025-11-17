import { FilterIinBinder } from '/static/js/binders/filters/filterIINBinder.js';
import { FilterActiveCloseRefundBinder } from '/static/js/binders/filters/filterActiveCloseRefundBinder.js';

import { MenuBinder } from '/static/js/binders/standart/menuBinder.js';
import { MutualExclusiveBinder } from '/static/js/binders/standart/mutualExclusiveBinder.js';
import { RowClickBinder } from '/static/js/binders/standart/rowClickBinder.js';
import { EditRowTableBinder } from '/static/js/binders/standart/editRowTableBinder.js';

import { TabSwitchBinder } from '/static/js/core/TabSwitchBinder.js';

//import { FragmentBinder } from '/static/js/core/TableLoad.js';
import { HelperBinder } from '/static/js/binders/standart/helperBinder.js';


export const courtTabContext = {
    zones: {
        mainTableHelper: '#court_mainTable',
        fragment: '#court_mainBody',
        filters: '#court_filterZone',
        tabs: '#court_tabs',
        tabs_content: '#court_tabs_content'
    },
    
    binders: {
        mainTableHelper: [HelperBinder],
        fragment: [EditRowTableBinder, RowClickBinder], //RowClickBinder, 
        filters: [FilterIinBinder, FilterActiveCloseRefundBinder, MenuBinder],
        tabs: [ TabSwitchBinder ],
        tabs_content: [MenuBinder, MutualExclusiveBinder]
    },

    request: {
        fragment: {
            method: 'POST',
            url: orderNum => `/filter-period-overpayments`
        },
        filters: {
            method: 'POST',
            url: '/court_filters',
            params: () => ({}) // 👈 пустой объект, если нет orderNum
        }
    },

    bindScope: {
        filters: 'global',    // искать в document, независимо от fragment
        fragment: 'global',     // искать только в загруженном фрагменте
        tabs: 'local',
        tabs_content: 'local'
    },

    loadStrategy: {
        fragment: 'eager',
        filters: 'eager',
        tabs: 'eager',
        tabs_content: 'eager'
    }
};

export default courtTabContext;