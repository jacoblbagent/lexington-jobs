/* Experience filter for the rendered jobs page.

   The renderer strips script, so this is injected after render by
   scripts/inject-experience-filter.py, together with src/experience.json (the
   curated list of listings whose posting asks for three or more years).
   Offset by default: the page opens showing every listing, and one checkbox
   drops the roles that want 3+ years so the rest reads as the roles open to
   less experience.

   Visibility stays owned by the location filter. This script publishes a
   predicate on window.__ardenJobs and asks that filter to re-apply, so the
   town, level, favorites and experience controls compose instead of fighting
   over the hidden attribute. */

(function () {
  'use strict';

  var table = document.querySelector('table.astryx-table');
  var data = document.getElementById('arden-experience-data');
  if (!table || !data) return;

  var flagged;
  try {
    flagged = JSON.parse(data.textContent || '{}');
  } catch (error) {
    return;
  }

  var body = table.querySelector('tbody');
  var titleHeader = table.querySelector('thead th[data-column-key="title"]');
  var bar = document.querySelector('.loc-filter');
  if (!body || !titleHeader || !bar) return;

  var titleIndex = titleHeader.cellIndex;

  // Same key as the star and the requirements panel: the number at the end of
  // the posting URL, so a rebuild keeps the flag attached.
  function idOf(row) {
    var link = row.cells[titleIndex] && row.cells[titleIndex].querySelector('a');
    if (!link) return null;
    var found = /-(\d{5,})\/?(?:[?#].*)?$/.exec(link.getAttribute('href') || '');
    return found ? found[1] : null;
  }

  // A requirements sub-row has one full-width cell; it follows its listing.
  var entries = [];
  Array.prototype.forEach.call(body.rows, function (row) {
    if (row.hasAttribute('data-expansion-panel')) {
      if (entries.length) entries[entries.length - 1].panels.push(row);
      return;
    }
    var id = idOf(row);
    var info = id ? flagged[id] : null;
    entries.push({
      row: row,
      id: id,
      years: info ? info.minYears : 0,
      evidence: info ? info.evidence : '',
      panels: [],
    });
  });
  if (!entries.length) return;

  var total = entries.filter(function (entry) {
    return entry.years >= 3;
  }).length;

  var label = document.createElement('label');
  label.className = 'exp-filter';
  label.title =
    total + ' of ' + entries.length + ' listings ask for 3 or more years of experience';

  var box = document.createElement('input');
  box.type = 'checkbox';
  box.id = 'exp-filter-check';
  box.className = 'exp-filter-check';

  var text = document.createElement('span');
  text.className = 'exp-filter-label';
  text.textContent = 'Skip 3+ years';

  var count = document.createElement('span');
  count.className = 'exp-filter-num';
  count.textContent = total;

  label.appendChild(box);
  label.appendChild(text);
  label.appendChild(count);

  // In the shared bar the live count reads last, so the checkbox goes before
  // it. Injected after the favorites checkbox, which inserts at the same point.
  bar.insertBefore(label, bar.querySelector('.loc-filter-count'));

  var state = (window.__ardenJobs = window.__ardenJobs || {});

  box.addEventListener('change', function () {
    state.experienceActive = box.checked;
    if (typeof state.refresh === 'function') state.refresh();
    else applyOwn();
  });

  // Fallback for a page without the location filter: hide the 3+ years rows.
  function applyOwn() {
    entries.forEach(function (entry) {
      var hidden = state.experienceActive && entry.years >= 3;
      entry.row.hidden = hidden;
      entry.panels.forEach(function (panel) {
        panel.hidden = hidden;
      });
    });
  }

  // Off on first paint: nothing is hidden until the box is checked.
  state.experienceActive = false;
  state.experienceFilter = function (row) {
    for (var i = 0; i < entries.length; i += 1) {
      if (entries[i].row === row) return entries[i].years < 3;
    }
    return true;
  };

  // The evidence line rides on the row as a tooltip, so a reader can see why a
  // role was hidden without opening the posting.
  entries.forEach(function (entry) {
    if (entry.years < 3 || !entry.evidence) return;
    entry.row.title = 'Requires ' + entry.years + '+ years: ' + entry.evidence;
  });
})();
