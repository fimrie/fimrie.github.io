document.addEventListener('DOMContentLoaded', function () {
  document.querySelectorAll('[role="tablist"]').forEach(function (tablist) {
    var tabs = Array.from(tablist.querySelectorAll('[role="tab"]'));
    var panels = tabs.map(function (tab) {
      return document.getElementById(tab.getAttribute('aria-controls'));
    });

    // Leave the full publication list available if the tabs cannot initialize.
    if (!tabs.length || panels.some(function (panel) { return !panel; })) {
      return;
    }

    function activateTab(tab) {
      tabs.forEach(function (item, index) {
        var selected = item === tab;
        var panel = panels[index];

        item.setAttribute('aria-selected', String(selected));
        item.tabIndex = selected ? 0 : -1;
        item.classList.toggle('active', selected);
        panel.hidden = !selected;
        panel.classList.toggle('active', selected);
      });
    }

    function tabFromUrl() {
      return tabs.find(function (tab) {
        return window.location.hash === '#' + tab.getAttribute('aria-controls');
      });
    }

    function selectTab(tab, replaceHistory) {
      activateTab(tab);
      var hash = '#' + tab.getAttribute('aria-controls');
      if (window.location.hash !== hash) {
        window.history[replaceHistory ? 'replaceState' : 'pushState'](null, '', hash);
      }
    }

    function scrollToPublications() {
      tablist.closest('.docs-section').scrollIntoView({ block: 'start' });
    }

    function restoreTab() {
      var tab = tabFromUrl();
      if (tab) {
        activateTab(tab);
        // Keep the heading and category controls visible when following a link.
        scrollToPublications();
      } else {
        activateTab(tabs[0]);
      }
    }

    tabs.forEach(function (tab, index) {
      tab.addEventListener('click', function () {
        selectTab(tab, false);
      });

      tab.addEventListener('keydown', function (event) {
        var nextIndex;

        switch (event.key) {
          case 'ArrowRight':
            nextIndex = (index + 1) % tabs.length;
            break;
          case 'ArrowLeft':
            nextIndex = (index - 1 + tabs.length) % tabs.length;
            break;
          case 'Home':
            nextIndex = 0;
            break;
          case 'End':
            nextIndex = tabs.length - 1;
            break;
          default:
            return;
        }

        event.preventDefault();
        // Arrow-key navigation updates the link without adding a history entry.
        selectTab(tabs[nextIndex], true);
        tabs[nextIndex].focus();
      });
    });

    activateTab(tabFromUrl() || tabs[0]);
    tablist.hidden = false;
    window.addEventListener('hashchange', restoreTab);
    if (tabFromUrl()) {
      // Run after the browser's initial fragment jump and image layout.
      window.addEventListener('load', function () {
        window.requestAnimationFrame(function () {
          if (tabFromUrl()) {
            scrollToPublications();
          }
        });
      });
    }
  });
});
