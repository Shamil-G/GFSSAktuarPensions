/////////////////////////////////////////////////
export function addHelperIcon(td) {
    if (td.querySelector('.help-icon')) return;

    const icon = document.createElement('span');
    icon.className = 'help-icon';
    icon.textContent = 'ℹ️';

    icon.addEventListener('click', () => {
        const topic = td.dataset.help;
        fetch(`/help_fragment?topic=${topic}`)
            .then(res => res.text())
            .then(html => {
                const cleaned = html.trim();
                if (!cleaned) {
                    showPopover(icon, '<em>Нет информации по этой подсказке</em>');
                } else {
                    showPopover(icon, html);
                }
            });
    });

    td.appendChild(icon);
}