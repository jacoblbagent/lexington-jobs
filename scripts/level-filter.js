/* Level filter for the rendered jobs page.
   The renderer strips script, so this is injected after render by
   scripts/inject-level-filter.py. It reuses the location filter's markup and
   styles (scripts/location-filter.css) rather than shipping a second palette:
   same label, button, checkbox panel and footer presets.

   Visibility stays owned by the location filter, which already hides rows for
   the town selection and the favorites toggle. This script publishes a
   predicate on window.__ardenJobs and asks that filter to re-apply, so the two
   controls compose instead of fighting over the hidden attribute. */

(function () {
  'use strict';

  var table = document.querySelector('table.astryx-table');
  if (!table) return;

  var header = table.querySelector('thead th[data-column-key="level"]');
  var body = table.querySelector('tbody');
  var bar = document.querySelector('.loc-filter');
  if (!header || !body || !bar) return;

  var column = header.cellIndex;

  // A requirements sub-row has one full-width cell, so it is not a listing:
  // it is recorded as its listing's panel and follows that row's visibility.
  var entries = [];
  Array.prototype.forEach.call(body.rows, function (row) {
    if (row.hasAttribute('data-expansion-panel')) {
      if (entries.length) entries[entries.length - 1].panels.push(row);
      return;
    }
    var level = (row.cells[column] && row.cells[column].textContent || '').trim() || 'Not listed';
    entries.push({row: row, level: level, panels: []});
  });
  if (!entries.length) return;

  var counts = {};
  entries.forEach(function (entry) {
    counts[entry.level] = (counts[entry.level] || 0) + 1;
  });

  // Seniority order rather than count order: the column is the one thing a
  // reader scans down, and an alphabetical panel puts "Not listed" above
  // "Entry level".
  var ORDER = [
    'Internship (title)',
    'Internship',
    'Entry level (title)',
    'Entry level',
    'Associate',
    'Mid-Senior level',
    'Senior (title)',
    'Staff (title)',
    'Director',
    'Not listed',
  ];
  var levels = Object.keys(counts).sort(function (a, b) {
    var ia = ORDER.indexOf(a);
    var ib = ORDER.indexOf(b);
    if (ia === -1) ia = ORDER.length;
    if (ib === -1) ib = ORDER.length;
    return ia - ib || a.localeCompare(b, 'en');
  });

  // Everything is on at first paint: no level is wrong to look at, and the
  // entry-only view is one preset away.
  var selected = {};
  levels.forEach(function (level) {
    selected[level] = true;
  });

  var label = document.createElement('span');
  label.className = 'loc-filter-label';
  label.id = 'lvl-filter-label';
  label.textContent = 'Level';

  var field = document.createElement('div');
  field.className = 'loc-filter-field';

  var button = document.createElement('button');
  button.type = 'button';
  button.id = 'lvl-filter-button';
  button.className = 'loc-filter-button';
  button.setAttribute('aria-expanded', 'false');
  button.setAttribute('aria-controls', 'lvl-filter-panel');

  var value = document.createElement('span');
  value.className = 'loc-filter-value';

  // The chevron is inline SVG for the same reason the location filter's is:
  // the webfont is stripped, so a glyph would land in a fallback face.
  var chevron = document.createElement('span');
  chevron.className = 'loc-filter-chevron';
  chevron.setAttribute('aria-hidden', 'true');
  chevron.innerHTML =
    '<svg viewBox="0 0 8 5" width="10" height="6" focusable="false">' +
    '<path d="M0 0h8L4 5Z"/>' +
    '</svg>';

  button.appendChild(value);
  button.appendChild(chevron);

  var panel = document.createElement('div');
  panel.className = 'loc-filter-panel';
  panel.id = 'lvl-filter-panel';
  panel.hidden = true;
  panel.setAttribute('role', 'group');
  panel.setAttribute('aria-labelledby', 'lvl-filter-label');

  var options = document.createElement('div');
  options.className = 'loc-filter-options';

  levels.forEach(function (level) {
    var option = document.createElement('label');
    option.className = 'loc-filter-option';

    var box = document.createElement('input');
    box.type = 'checkbox';
    box.className = 'loc-filter-check';
    box.value = level;
    box.checked = true;

    var name = document.createElement('span');
    name.className = 'loc-filter-town';
    name.textContent = level;

    var count = document.createElement('span');
    count.className = 'loc-filter-num';
    count.textContent = counts[level];

    option.appendChild(box);
    option.appendChild(name);
    option.appendChild(count);
    options.appendChild(option);
  });

  var footer = document.createElement('div');
  footer.className = 'loc-filter-footer';

  var entryButton = document.createElement('button');
  entryButton.type = 'button';
  entryButton.className = 'loc-filter-action';
  entryButton.textContent = 'Entry level';

  var allButton = document.createElement('button');
  allButton.type = 'button';
  allButton.className = 'loc-filter-action';
  allButton.textContent = 'All';

  footer.appendChild(entryButton);
  footer.appendChild(allButton);

  panel.appendChild(options);
  panel.appendChild(footer);

  field.appendChild(button);
  field.appendChild(panel);

  // Sits in the existing filter bar, between the location button and the live
  // count, so both dropdowns read as one control row. The favorites checkbox
  // inserts itself at the same point later, which puts it after this one.
  var count = bar.querySelector('.loc-filter-count');
  bar.insertBefore(field, count);
  bar.insertBefore(label, field);

  function chosen() {
    return levels.filter(function (level) {
      return selected[level];
    });
  }

  function summary(names) {
    if (!names.length || names.length === levels.length) return 'All levels';
    if (names.length <= 2) return names.join(', ');
    return names[0] + ' +' + (names.length - 1) + ' more';
  }

  var shared = (window.__ardenJobs = window.__ardenJobs || {});

  function apply() {
    var names = chosen();
    // Like the location filter: an empty set would hide every row with nothing
    // left to explain it, so it reads as unfiltered.
    var filtering = names.length > 0 && names.length < levels.length;

    shared.levelActive = filtering;
    shared.levelFilter = filtering
      ? function (row) {
          for (var i = 0; i < entries.length; i += 1) {
            if (entries[i].row === row) return !!selected[entries[i].level];
          }
          return true;
        }
      : null;

    var text = summary(names);
    value.textContent = text;
    button.setAttribute('aria-label', 'Level: ' + text);
    button.classList.toggle('loc-filter-active', filtering);

    if (typeof shared.refresh === 'function') shared.refresh();
  }

  function syncBoxes() {
    Array.prototype.forEach.call(panel.querySelectorAll('.loc-filter-check'), function (box) {
      box.checked = !!selected[box.value];
    });
  }

  function place() {
    var rect = button.getBoundingClientRect();
    var width = 232;
    var margin = 6;
    var edge = 8;

    panel.style.left =
      Math.round(Math.max(edge, Math.min(rect.left, window.innerWidth - width - edge))) + 'px';

    var below = window.innerHeight - rect.bottom - margin - edge;
    var above = rect.top - margin - edge;
    var room = below >= above ? below : above;
    options.style.maxHeight = Math.max(96, Math.min(288, room - 56)) + 'px';

    var height = panel.offsetHeight;
    var top = below >= height || below >= above ? rect.bottom + margin : rect.top - margin - height;
    panel.style.top = Math.round(Math.max(edge, top)) + 'px';
  }

  function open() {
    panel.hidden = false;
    button.setAttribute('aria-expanded', 'true');
    place();
    var checked = panel.querySelector('.loc-filter-check:checked');
    (checked || panel.querySelector('.loc-filter-check')).focus();
  }

  function close(returnFocus) {
    if (panel.hidden) return;
    panel.hidden = true;
    button.setAttribute('aria-expanded', 'false');
    if (returnFocus) button.focus();
  }

  button.addEventListener('click', function () {
    if (panel.hidden) open();
    else close(true);
  });

  panel.addEventListener('change', function (event) {
    var box = event.target;
    if (!box.classList.contains('loc-filter-check')) return;
    selected[box.value] = box.checked;
    apply();
  });

  // The two presets the reader actually wants: junior roles only, or the whole
  // list back.
  entryButton.addEventListener('click', function () {
    levels.forEach(function (level) {
      selected[level] = /^(Internship|Entry level)/.test(level);
    });
    syncBoxes();
    apply();
    close(true);
  });

  allButton.addEventListener('click', function () {
    levels.forEach(function (level) {
      selected[level] = true;
    });
    syncBoxes();
    apply();
    close(true);
  });

  panel.addEventListener('keydown', function (event) {
    if (event.key === 'Escape') {
      event.stopPropagation();
      close(true);
    }
  });

  document.addEventListener('pointerdown', function (event) {
    if (panel.hidden) return;
    if (panel.contains(event.target) || button.contains(event.target)) return;
    close(false);
  });

  window.addEventListener('resize', function () {
    if (!panel.hidden) place();
  });
  window.addEventListener(
    'scroll',
    function () {
      if (!panel.hidden) place();
    },
    {passive: true}
  );

  apply();
})();
