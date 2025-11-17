//import { BinderRegistry } from './binderRegistry.js';
import * as TabUtil from '/static/js/_aux/tabUtil.js';

// Фрагменты скачиваютя через TabLoader !!!
// Здесь только мастер - таблица:
// нет необходимости в указании  первичного ключа orderNum

export const TableLoader = {
    role: 'fragment',


    async load(url, targetId, params = {}) {
        //console.log("TableLoad. load: ", url, targetId, params);

        const target = document.getElementById(targetId);
        //console.log("targetId:", targetId, ", target:\n\t", target);

        if (!target) return null;

        const { headers, body } = TabUtil.serializeParams(params);

        try {
            const res = await fetch(url, { method: 'POST', headers, body });
            const html = await res.text();

            target.innerHTML = html;

            //console.log("TableLoad. LOAD.  target: ", targetId, ", URL: ", url, ", params: ", params);

            return html; // ✅ теперь можно кэшировать
        } catch (err) {
            console.error('TableLoad.load error:', err);
            return null;
        }
    }
};
