(function () {
  'use strict';

  const filterButtons = [...document.querySelectorAll('[data-filter]')];
  const industryCards = [...document.querySelectorAll('[data-kind]')];
  const filterSummary = document.querySelector('#filter-summary');
  const locale = (typeof globalThis !== 'undefined' && globalThis.QAZ_LOCALE) || null;
  const filterSummarySource = 'Показано {visible} из {total} направлений';

  function renderFilterSummary() {
    if (!filterSummary) return;
    const visible = industryCards.filter((card) => !card.hidden).length;
    const template = locale?.t?.(filterSummarySource) || filterSummarySource;
    filterSummary.textContent = template
      .replace('{visible}', String(visible))
      .replace('{total}', String(industryCards.length));
  }

  filterButtons.forEach((button) => {
    button.addEventListener('click', () => {
      const filter = button.dataset.filter;
      filterButtons.forEach((item) => {
        const active = item === button;
        item.classList.toggle('is-active', active);
        item.classList.toggle('av-chip--selected', active);
        item.setAttribute('aria-pressed', String(active));
      });
      industryCards.forEach((card) => {
        card.hidden = filter !== 'all' && card.dataset.kind !== filter;
      });
      renderFilterSummary();
    });
  });

  locale?.onChange?.(renderFilterSummary);
  Promise.resolve(locale?.loadCatalog?.(document)).then(() => {
    renderFilterSummary();
  });
  renderFilterSummary();
}());
