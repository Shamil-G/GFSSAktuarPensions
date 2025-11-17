import { showTooltipPopover } from '/static/js/_aux/popoverEngine.js';

export const TooltipBinder = {
  role: 'tooltip',
    attach(el) {
        if (el.__tooltipBinder) {
            //console.warn('⚠️ TooltipBinder: double bind', el);
            //console.trace(); // покажет стек вызова
            return;
        }
        el.__tooltipBinder = true;

        if (!el?.dataset?.tooltip || el.dataset.tooltipBound === 'true') return;
        el.dataset.tooltipBound = 'true';

        el.addEventListener('mouseenter', () => {
            showTooltipPopover(el, el.dataset.tooltip);
        });
  },

  attachAll(zone = document) {
    zone.querySelectorAll('[data-tooltip]').forEach(el => this.attach(el));
  }
};