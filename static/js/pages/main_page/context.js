import { MenuScenarioBinder } from '/static/js/pages/main_page/binders/menuBinder.js';

export const mainPageContext = {
    // Значения zone определяют id=""
    zones: {
        filters: '#scenario_FilterZone'
    },

    binders: {
        filters: [MenuScenarioBinder],
    },

    bindScope: {
        filters: 'global'    // искать в document, независимо от fragment
    },

    loadStrategy: {
        filters: 'eager'
    }
};

export default mainPageContext;