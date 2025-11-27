//import { MenuBinder } from '/static/js/pages/big_ref/binders/menuBinder.js';
//import { HelperBinder } from '/static/js/binders/standart/helperBinder.js';
import { EditRowTableBinder } from '/static/js/pages/coeff_ref/binders/editRowTableBinder.js';
//import { FilterActiveCloseRefundBinder } from '/static/js/binders/filters/filterActiveCloseRefundBinder.js';


export const coeffRefTabContext = {
    // Значения zone определяют id=""
    zones: {
        fragment: '#coeff_ref_mainBody',
    },

    binders: {
        fragment: [EditRowTableBinder], //RowClickBinder, 
    },

    request: {
        save_row_coeff: {
            method: 'POST',
            url: (id, year, field) => `/save-coeff-value`,
            params: (id, field, value) => ({ id,  field, value })
        }
    },

    bindScope: {
        filters: 'global'    // искать в document, независимо от fragment
    },

    loadStrategy: {
        filters: 'eager'
    }
};

export default coeffRefTabContext;