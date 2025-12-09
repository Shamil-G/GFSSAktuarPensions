import { PageManager, PageContext } from '/static/js/core/PageContext.js';

(async () => {
    console.log('Start Base Page Context:');

    const scriptTag = document.getElementById('pageBaseScript');
    const pageName = scriptTag?.dataset.page || 'unknown';
    console.log('Активная страница:', pageName);

    await PageManager.set(pageName);

    console.log('Tabs in Base Page:', PageManager.get().list());

    setTimeout(() => {
        console.log('Script finished');
    }, 1000);
})();

const globalAPI = {
    //filterByOrder,
    //showTab,
    PageManager
};

window.API = globalAPI;