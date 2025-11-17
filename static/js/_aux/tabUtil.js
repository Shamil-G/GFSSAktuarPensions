import { PageManager } from '/static/js/core/PageContext.js';

export const tabCache = {};
const tabCacheOrder = [];

// Предлагаем обновить данные, если прошло 20 минут
// 20 минут = 20 * кол-во секунд * кол-во миллисекунд
const REFRESH_RECOMMENDED_THRESHOLD = 30 * 60 * 1000; 
// Удаляем из кэша принудительно, если прошло 2 часа
const CACHE_LIFETIME = 2 * 60 * 60 * 1000; // 2 часа в мс
// В кэше храним 512 документов
const MAX_CACHE_SIZE = 512;
//////////////////////////////////////////////////////////////////////////////
export function getOrderNum() {
    return document.getElementById('sharedOrderNum')?.value || '';
}
export function setSharedOrderNum(orderNum) {
    const shared = document.getElementById('sharedOrderNum');
    if (shared) {
        shared.value = orderNum;
        return orderNum;
    } else {
        console.warn('⚠️ setOrderNum: элемент sharedOrderNum не найден');
        return 0;
    }
}
export function getCurrentTabId() {
    return document.getElementById('sharedTabId')?.value || 'pretrial';
}
export function getTimestampZone(targetZone, tabName) {
    //return targetZone.querySelector(`#${tabName}Timestamp`);
    return targetZone.querySelector(`#footTimestamp`);
}
export function getCacheKey(tabName, orderNum, zoneKey = 'content') {
    const cacheKey = `${PageManager.get().pageName}_${tabName}_${zoneKey}_${orderNum}`;
    return `${PageManager.get().pageName}_${tabName}_${zoneKey}_${orderNum}`;
}
export function getTargetZone(tabName, zoneKey) {
    /*  const config = TabConfig[id];*/
    const zone = PageManager.get().getZone(tabName, zoneKey);
    return zone;
}
//////////////////////////////////////////////////////////////////////////////
export function formatAge(timestamp) {
    const now = Date.now();
    const delta = now - timestamp;

    const mins = Math.floor(delta / 60000);
    if (mins < 1) return 'только что';
    if (mins < 60) return `${mins} мин назад`;
    const hrs = Math.floor(mins / 60);
    return `${hrs} ч назад`;
}
/////////////////////////////////////////////////////////////////////////////
export function addToCache(key, html) {
    const now = Date.now();

    // Удалим старые
    for (const [k, v] of Object.entries(tabCache)) {
        if (now - v.timestamp > CACHE_LIFETIME) {
            delete tabCache[k];
            const index = tabCacheOrder.indexOf(k);
            if (index !== -1) tabCacheOrder.splice(index, 1);
        }
    }

    // Ограничение по размеру
    if (tabCacheOrder.length >= MAX_CACHE_SIZE) {
        const oldestKey = tabCacheOrder.shift();
        delete tabCache[oldestKey];
    }

    // Добавим свежий
    tabCache[key] = { html, timestamp: now };
    tabCacheOrder.push(key);
}
//////////////////////////////////////////////////////////////////////////////
export function updateRefreshButton(tabName, cached_timestamp) {
    const age = Date.now() - cached_timestamp;

    const refreshTarget = document.getElementById(`${tabName}RefreshButton`);

    //console.log("updateRefreshButton. refreshTarget: ", refreshTarget);

    if (!refreshTarget) return;

    //console.log("updateRefreshButton. age: ", age, " : ", REFRESH_RECOMMENDED_THRESHOLD);

    if (age > REFRESH_RECOMMENDED_THRESHOLD) {
        refreshTarget.textContent = '🔁 Рекомендуем обновить';
        refreshTarget.classList.add('recommend');
        refreshTarget.title = `Загружено ${formatAge(cached_timestamp)} назад`;
    } else {
        refreshTarget.textContent = '🔄 Обновить';
        refreshTarget.classList.remove('recommend');
        refreshTarget.title = `Обновлено ${formatAge(cached_timestamp)} назад`;
    }
}
export function showLoadedAge(targetZone, tabName) {
    //let timestampZone = document.getElementById(`${tabName}Timestamp`)
    let timestampZone = getTimestampZone(targetZone, tabName);
    //console.log("showLoadedAge. targetZone: ", targetZone, "tabName: ", tabName);
    if (timestampZone) {
        const key_cache = getCacheKey(tabName, getOrderNum())
        if (key_cache) {
            const cach = tabCache[key_cache];
            timestampZone.textContent = `🕓 Загружено ${formatAge(cach.timestamp)}`;
        }
    }
}
///////////////////////////////////////////////////////////////////////////
export function loadFromCache(tabName, orderNum, zoneKey = 'content') {
    // Попробовать вытащить из кэша
    const cacheKey = getCacheKey(tabName, orderNum, zoneKey);
    const cached = tabCache[cacheKey];

    if (cached?.html) {
        const cached = tabCache[cacheKey];

        const targetZone = PageManager.get().getZone(tabName, zoneKey);
        if (!targetZone) {
            console.warn("loadFromCache. targetZone. ", targetZone);
            return false;
        }
        targetZone.innerHTML = cached.html;

        updateRefreshButton(tabName, cached.timestamp);
        showLoadedAge(targetZone, tabName);

        //console.log("LOADED from CACHE ", cacheKey);
        return true;
    }
    return false;
}
//////////////////////////////////////////////////////////////////////////////
// На случай продолжительной загрузки данных надо выводить снизу сообщение
export function showTabLoader(tableFragment, start) {
    if (!tableFragment) return;

    let tfoot = tableFragment.querySelector('tfoot');
    // Если данных еще нет, то фрагмент пустой, без tfoot
    if (tfoot) {
        const centerSpan = tfoot.querySelector(`#footer-center`);
        if (centerSpan) {
            centerSpan.textContent = start === 1 ? 'Загрузка...' : '';
        }
    }
}
////////////////////////////////////////////////////////////
export function showLoadingMessage(tabName) {
    const contentZone = getTargetZone(tabName);
    if (!contentZone) return;

    const footerCenter = contentZone.querySelector('#footer-center');

    if (footerCenter) {
        // Таблица уже загружена — выводим сообщение в центр футера
        footerCenter.textContent = '⏳ Идёт загрузка...';
    } else {
        // Таблицы ещё нет — выводим сообщение на всю зону
        contentZone.innerHTML = `<div class="tab-loading-full" style="text-align: center; padding: 1em; font-style: italic; color: #666;">
            ⏳ Идёт загрузка...</div>`;
    }
}
//////////////////////////////////////////////////
export function serializeParams(params) {
    const isJson = Object.values(params).some(v =>
        typeof v === 'object' && v !== null
    );
    const headers = {
        'X-Requested-With': 'XMLHttpRequest',
        'Content-Type': isJson ? 'application/json' : 'application/x-www-form-urlencoded'
    };
    const body = isJson
        ? JSON.stringify(params)
        : new URLSearchParams(params).toString();

    return { headers, body };
}
//////////////////////////////////////////////////////////////////////////////
export function fadeInsert(contentZone, htmlString) {
    return new Promise(resolve => {
        contentZone.classList.add('fade-out');

        setTimeout(() => {
            const temp = document.createElement('div');
            temp.innerHTML = htmlString;

            const fragment = document.createDocumentFragment();
            while (temp.firstChild) {
                fragment.appendChild(temp.firstChild);
            }

            contentZone.innerHTML = '';
            contentZone.appendChild(fragment);
            contentZone.classList.remove('fade-out');

            resolve();
        }, 300);
    });
}
