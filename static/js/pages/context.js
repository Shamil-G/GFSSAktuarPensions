// pages/context.js
import { MenuScenarioBinder } from '/static/js/core/MenuScenarioBinder.js';

export const globalContext = {
    zones: {
        scenarioMenu: '#scenario_FilterZone'
    },
    binders: {
        scenarioMenu: [MenuScenarioBinder]
    }
};
