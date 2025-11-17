import { showHelperPopover } from '/static/js/_aux/popoverEngine.js';

export const HelperBinder = {
    role: 'helper',

    attach(cell) {
        if (!cell || cell.__helperBinder) return;
        cell.__helperBinder = true;

        if (cell.querySelector('.help-icon')) return;

        const icon = document.createElement('span');
        icon.className = 'help-icon';
        icon.textContent = 'ℹ️';
        icon.title = 'Нажмите для справки';

        icon.addEventListener('click', () => {
            const topic = cell.dataset.help;
            fetch(`/help_fragment?topic=${topic}`)
                .then(res => res.text())
                .then(html => {
                    const cleaned = html.trim();
                    showHelperPopover(icon, cleaned || '<em>Нет информации по этой подсказке</em>');
                });
        });

        cell.appendChild(icon);
    },

    attachAll(zone = document) {
        const cells = zone.querySelectorAll('[data-role="helper"][data-help]');
        //console.log(`[HelperBinder] attachAll: zone =`, zone, `\n\tcells =`, cells);

        cells.forEach(cell => this.attach(cell));
    }
};
