import { MenuPrintBinder } from '/static/js/pages/base_pension/binders/menuPrintBinder.js';
import { RunBinder } from '/static/js/pages/base_pension/binders/runBinder.js';
import { HelperBinder } from '/static/js/binders/standart/helperBinder.js';


export const basePensionTabContext = {
    // Значения zone определяют id=""
    zones: {
        /*mainTableHelper: '#calc_pens_mainTableHelper',*/
        fragment: '#base_pension_mainBody',
        running: '#command_zone'
    },

    binders: {
        /*mainTableHelper: [HelperBinder],*/
        running: [MenuPrintBinder, RunBinder],
    },

    request: {
        fragment: {
            method: 'POST',
            url: ref_name => `/show-base_pension-fragment`
        },
    },

    bindScope: {
        filters: 'global'    // искать в document, независимо от fragment
    },

    loadStrategy: {
        filters: 'eager'
    }
};

export default basePensionTabContext;