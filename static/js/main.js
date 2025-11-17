import { TableLoader } from './core/TableLoad.js';
import { TabContext } from './core/TabContext.js';
import { PageManager, PageContext } from './core/PageContext.js';

import * as TabUtil from '/static/js/_aux/tabUtil.js';


///////////////////////////////////////////////////////////////
// По выбранному TAB загружаем его содержимое
// id - это имя зоны - Таб, например, "pretrial"
/**
* Загружаем закладку по имени и уникальому номеру строки в мастер таблице.
* @param {string} tabName  - Имя закладки
* @param {string} orderNum - Уникальный номер строки 
*/
function loadTabContent(tabName, orderNum) {
    if (!orderNum) return;

    const contentZone = TabUtil.getTargetZone(tabName);
    if (!contentZone) {
        console.error(`❌ Зона "${config.zoneSelector}" не найдена`);
        return;
    }

    // Проверка: если уже загружено для этого orderNum, не загружать повторно
    if (contentZone.dataset.loadedOrderNum === orderNum) return;

    // ⏳ Загрузка...
    TabUtil.showLoadingMessage(tabName);

    //TabUtil.showTabLoader(contentZone, 1);
    TabRegistry.load(tabName, orderNum).then(() => {
        TabUtil.showLoadedAge(contentZone, tabName);
        contentZone.dataset.loadedOrderNum = orderNum;
    });
}
///////////////////////////////////////////////////////////////
// Главная таблица переплат в LIST_OVERPAYMENTS.HTML
// Когда щелкаем мышкой по записям TR надо менять фильтр orderNum для TABS
/**
* Фильтр для закладок.
* @param {string} orderNum - Уникальный номер строки 
*/
function filterByOrder(orderNum) {
    // Установить общее поле
    if(!TabUtil.setSharedOrderNum(orderNum)) return;

    // После клика мышкой - делаем подсветку выбранной строки
    const rows = document.querySelectorAll('table tbody tr[data-order]');
    rows.forEach(row => {
        row.classList.toggle('active-row', row.dataset.order === orderNum);
    });

    const tabName = TabUtil.getCurrentTabId();
    if (!TabUtil.loadFromCache(tabName, orderNum)) {
        PageManager.get().onTabSwitch(tabName);
    }
}
////////////////////////////////////////////////////////////////////////
//
// НЕ ИСПОЛЬЗУЕТСЯ !!!
//
// Вызывалось по data-action="filterByPeriod"
// 
// Теперь меню вызывается data-role="menu", которое по завершениии
// Вызывает загрузку таблицы по data-url=""
function filterByPeriod_alien(period_value, label, dropdown) {
    // Фильтрация по вашему атрибуту
    if (dropdown.getAttribute('data-track') === 'true') {
        const url = dropdown.getAttribute('data-url')
        if (!url) {
            console.log('FilterByPeriod without URL: ', dropdown)
            return
        }
        TableLoader.load(url, 'court_mainBody', { value: period_value });
    }
}
// Переходим с одного tab на другой и должны показываться соответствующие панели
// Функция переключения между вкладками с выборкой его содержимого
// Функция привязывается в list_overpayments.html 
/**
* Переключает активную вкладку.
* @param {string} tabName - Имя вкладки
*/
function showTab(tabName) {
    const sharedTab = document.getElementById('sharedTabId');
    if (sharedTab) sharedTab.value = tabName;

    const zone = document.querySelector(`[data-tab="${tabName}"]`);

    if (!zone) {
        console.log("showTab. zone ", zone);
    }
    console.log("+++ showTab. zone\n", zone);
    // Скрыть все панели
    zone.querySelectorAll('.tab-panel').forEach(panel => {
        panel.classList.remove('active');
    });
    // Показать нужную панель
    const targetPanel = zone.getElementById(tabName);
    if (targetPanel) {
        targetPanel.classList.add('active');
    }

    // Убрать активность со всех кнопок
    zone.querySelectorAll('.tab-buttons .tab').forEach(btn => {
        btn.classList.remove('active');
    });

    // Активировать соответствующую кнопку
    const tabButtons = zone.querySelectorAll('.tab-buttons .tab');
    tabButtons.forEach(btn => {
        if (btn.getAttribute('onclick')?.includes(tabName)) {
            btn.classList.add('active');
        }
    });
    if (!TabUtil.loadFromCache(tabName, TabUtil.getOrderNum())) {
        loadTabContent(tabName, TabUtil.getOrderNum());
        TabContext.activate(tabName, zone);
        page?.loadTabContent(tabName, zone);
    }
}

(async () => {
    console.log('Start PageContext:');

    const scriptTag = document.getElementById('pageScript');
    const pageName = scriptTag?.dataset.page || 'unknown';
    console.log('Активная страница:', pageName);

    await PageManager.set(pageName);

    console.log('Tabs in page:', PageManager.get().list());

    setTimeout(() => {
        console.log('Script finished');
    }, 1000);
})();

const globalAPI = {
    filterByOrder,
    showTab,
    PageManager
};

window.API = globalAPI;