import { TableLoader } from '/static/js/core/TableLoad.js';
import { TabContext } from '/static/js/core/TabContext.js';
import { PageManager, PageContext } from '/static/js/core/PageContext.js';
import * as TabUtil from '/static/js/_aux/tabUtil.js';

(async () => {
    console.log('Start Main Page Context:');

    const scriptTag = document.getElementById('pageScript');
    const pageName = scriptTag?.dataset.page || 'unknown';
    console.log('Активная страница:', pageName);
    if (pageName){
        await PageManager.set(pageName);

        console.log('Tabs in Main page:', PageManager.get().list());

        setTimeout(() => {
            console.log('Script finished');
        }, 1000);
    }
})();

const globalAPI = {
    //filterByOrder,
    //showTab,
    PageManager
};

window.API = globalAPI;
