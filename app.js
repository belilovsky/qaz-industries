(function () {
  'use strict';

  const filterButtons = [...document.querySelectorAll('[data-filter]')];
  const industryCards = [...document.querySelectorAll('[data-kind]')];
  const filterSummary = document.querySelector('#filter-summary');

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
      const visible = industryCards.filter((card) => !card.hidden).length;
      if (filterSummary) {
        filterSummary.textContent = `Показано ${visible} из ${industryCards.length} направлений`;
      }
    });
  });
}());
