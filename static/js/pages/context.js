// pages/context.js
import { MenuScenarioBinder } from '/static/js/core/menuScenarioBinder.js';

export const globalContext = {
    zones: {
        scenarioMenu: '#scenario_FilterZone'
    },
    binders: {
        scenarioMenu: [MenuScenarioBinder]
    }
};
