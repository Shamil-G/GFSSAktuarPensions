export const MenuScenarioBinder = {
    role: 'menu-scenario',
    massive: true,

    attach(dropdown, handler = null, force = false) {
        console.log('menuScenarioBound start')
        if (dropdown.__menuScenarioBound && !force) return;
        dropdown.__menuScenarioBound = true;
        console.log('menuScenarioBound continue')

        const button = dropdown.querySelector('.dropdown-button');
        const hiddenInput = dropdown.querySelector('input[type="hidden"]');
        const labelSpan = button?.querySelector('.label');

        // делегирование: один обработчик на весь dropdown
        dropdown.addEventListener('click', async (event) => {
            const anchor = event.target.closest('.dropdown-content a');
            if (!anchor) return;
            event.preventDefault();

            const value = anchor.dataset.value || anchor.textContent.trim();
            const label = anchor.dataset.label || value;
            const url = dropdown.dataset.url || anchor.dataset.url;

            hiddenInput.value = value;
            if (labelSpan) labelSpan.textContent = label;

            dropdown.querySelectorAll('.dropdown-content a')
                .forEach(i => i.classList.remove('selected'));
            anchor.classList.add('selected');

            dropdown.dispatchEvent(new CustomEvent('menu-changed', {
                bubbles: true,
                detail: { value, label }
            }));

            if (dropdown.__lastValue === value) {
                console.log(`⚠️ duplicate value (${value}) — skipped`);
                return;
            }
            dropdown.__lastValue = value;

            const payload = { value: value, label: label };
            console.log(`1. Menu-Scenario. Dropdown: ${JSON.stringify(payload)}. URL: ${url}`);

            try {
                const res = await fetch(url, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });
                console.log(`1. Menu-Scenario. Dropdown: ${JSON.stringify(payload)}. URL: ${url}, res: ${res}`);

                if (!res.ok) {
                    const errorText = await res.text();
                    console.error(`❌ Failed:`, res.status, errorText);
                    throw new Error(`Request failed with status ${res.status}`);
                }

                const result = await res.json();
                console.log(`✅ saved:`, result);

                // Напишем название сценария
                document.getElementById('scenarioLabel').dataset.scenario = value;
                document.getElementById('scenarioName').textContent = label;

                // редирект на первую страницу
                window.location.href = "/"; 

                if (typeof handler === 'function') {
                    handler(result, dropdown);
                }
            } catch (err) {
                console.error(`❌ Exception during save:`, err);
                alert(`Ошибка при сохранении`);
            }
        });
    },

    attachAll(handler = null, zone = document) {
        console.log('Menu-Scenario attachAll  start')
        const dropdowns = zone.querySelectorAll(`[data-role="${this.role}"]`);
        dropdowns.forEach(dropdown => {
            this.attach(dropdown, handler, true);
        });
    }
};
