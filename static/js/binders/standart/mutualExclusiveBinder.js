import { showTooltipPopover } from '/static/js/_aux/popoverEngine.js';

export const MutualExclusiveBinder = {
    role: 'mutual-exclusive',

    attach(wrapper) {
        if (!wrapper || wrapper.__mutualExclusiveBinder) return;
        wrapper.__mutualExclusiveBinder = true;

        const inputA = wrapper.querySelector('[data-role="inputA"]');
        const inputB = wrapper.querySelector('[data-role="inputB"]');

        const infoA = wrapper.getAttribute('data-info-a') || '';
        const infoB = wrapper.getAttribute('data-info-b') || '';

        if (!inputA || !inputB) return;

        inputA.addEventListener('input', () => {
            inputB.disabled = !!inputA.value;
            if (inputA.value) inputB.value = '';
            if (infoA) showTooltipPopover(inputA, infoA);
        });

        inputB.addEventListener('input', () => {
            inputA.disabled = !!inputB.value;
            if (inputB.value) inputA.value = '';
            if (infoB) showTooltipPopover(inputB, infoB);
        });
    },

    attachAll(zone = document) {
        const wrappers = zone.querySelectorAll('[data-mutual-exclusive]');
        //console.log(`[MutualExclusiveBinder] attachAll: zone =`, zone, `\n\twrappers =`, wrappers);

        wrappers.forEach(wrapper => this.attach(wrapper));
    }
};

