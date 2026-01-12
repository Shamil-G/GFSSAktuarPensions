import { FilterInputBinder } from '/static/js/pages/calc_pens/binders/filterInputBinder.js';
import { MenuBinder }      from '/static/js/pages/calc_pens/binders/menuBinder.js';
import { MenuPrintBinder } from '/static/js/pages/calc_pens/binders/menuPrintBinder.js';
import { HelperBinder } from '/static/js/binders/standart/helperBinder.js';


export const calcPensTabContext = {
    // Значения zone определяют id=""
    zones: {
        /*mainTableHelper: '#calc_pens_mainTableHelper',*/
        fragment: '#calc_pens_mainBody',
        filters: '#calc_pens_FilterZone'
    },

    binders: {
        /*mainTableHelper: [HelperBinder],*/
        filters: [FilterInputBinder, MenuBinder, MenuPrintBinder],
    },

    request: {
        fragment: {
            method: 'POST',
            url: ref_name => `/show-pens-fragment`
        },
    },

    bindScope: {
        filters: 'global'    // искать в document, независимо от fragment
    },

    loadStrategy: {
        filters: 'eager'
    }
};

export default calcPensTabContext;