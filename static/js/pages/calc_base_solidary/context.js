import { FilterInputBinder } from '/static/js/pages/calc_pens/binders/filterInputBinder.js';
import { MenuCalcBinder }      from '/static/js/pages/calc_base_solidary/binders/menuCalcBinder.js';
import { MenuPrintBinder } from '/static/js/pages/calc_base_solidary/binders/menuPrintBinder.js';
import { HelperBinder } from '/static/js/binders/standart/helperBinder.js';


export const calcBaseSolidaryTabContext = {
    // Значения zone определяют id=""
    zones: {
        mainTableHelper: '#calc_base_solidary_mainTableHelper',
        fragment: '#calc_base_solidary_mainBody',
        menues: '#calc_base_solidary_MenuZone'
    },

    binders: {
        mainTableHelper: [HelperBinder],
        menues: [MenuCalcBinder, MenuPrintBinder]
    },

    request: {
        calculate: {
            method: 'POST',
            url: `/calculate_base_solidary`
        },
        fragment: {
            method: 'POST',
            url: `/reload_base_solidary`
        },
        print: {
            method: 'GET',
            url: `/print_base_solidary`
        },
    },

    bindScope: {
        filters: 'global'    // искать в document, независимо от fragment
    },

    loadStrategy: {
        filters: 'eager'
    }
};

export default calcBaseSolidaryTabContext;