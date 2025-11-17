export function showHelperPopover(target, html) {
  const old = document.querySelector('.popover');
  if (old) old.remove();

  const pop = document.createElement('div');
  pop.className = 'popover';

  const close = document.createElement('span');
  close.className = 'popover-close';
  close.textContent = '×';
  close.title = 'Закрыть';
  close.onclick = () => pop.remove();
  pop.appendChild(close);

  const content = document.createElement('div');
  content.className = 'popover-content';
  content.innerHTML = html;
  pop.appendChild(content);

  document.body.appendChild(pop);

  const rect = target.getBoundingClientRect();
  const popWidth = pop.offsetWidth;
  const screenWidth = window.innerWidth;

  let left = rect.left + window.scrollX;
  if (left + popWidth > screenWidth) {
    left = screenWidth - popWidth - 12;
  }

  pop.style.top = `${rect.bottom + window.scrollY + 6}px`;
  pop.style.left = `${Math.max(left, 6)}px`;

  setTimeout(() => {
    document.addEventListener('click', function outsideClick(e) {
      if (!pop.contains(e.target) && e.target !== target) {
        pop.remove();
        document.removeEventListener('click', outsideClick);
      }
    });
  }, 0);
}
///////////////////////////////////////////////////
export function showTooltipPopover(target, html) {
  const old = document.querySelector('.popover');
  if (old) old.remove();

  const pop = document.createElement('div');
  pop.className = 'popover tooltip';
  pop.innerHTML = `<div class="popover-content">${html}</div>`;
  document.body.appendChild(pop);

  const rect = target.getBoundingClientRect();
  const popWidth = pop.offsetWidth;
  const screenWidth = window.innerWidth;

  let left = rect.left + window.scrollX;
  if (left + popWidth > screenWidth) {
    left = screenWidth - popWidth - 12;
  }

  pop.style.position = 'absolute';
  pop.style.top = `${rect.bottom + window.scrollY + 6}px`;
  pop.style.left = `${Math.max(left, 6)}px`;

  // 🎯 Удаление при уходе мыши
  const remove = () => pop.remove();
  target.addEventListener('mouseleave', remove, { once: true });
  pop.addEventListener('mouseleave', remove, { once: true });
}


