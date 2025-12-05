import { TableLoader } from '/static/js/core/TableLoad.js';

export const MenuPrintBinder = {
    role: 'menu-print',

    attach(dropdown, force=false) {
        if (dropdown.__menuPrintBound && !force) return;
        dropdown.__menuPrintBound = true;

        const items = dropdown.querySelectorAll('.dropdown-content a');
        const url = dropdown.dataset.url;

        if (!url || items.length === 0) return;

        items.forEach(item => {
            item.addEventListener('click', (event) => {
                event.preventDefault();

                const anchor = event.currentTarget;
                const value = anchor.dataset.value || anchor.textContent.trim();

                // Формируем URL с GET‑параметром
                const url = `${dropdown.dataset.url}?value=${encodeURIComponent(value)}`;
                console.log("menu-print. URL:" , url);

                // 🔹 Загружаем документ в новое окно
                const printWindow = window.open(url, '_blank');

                // 🔹 Ждём загрузки и вызываем печать
                printWindow.onload = () => {
                    printWindow.print();
                };
            });
        });
    },

    attachAll(zone = document) {
        const dropdowns = zone.querySelectorAll(`[data-role="${this.role}"]`);
        dropdowns.forEach(dropdown => {
            this.attach(dropdown, true);
        });
    }
};
