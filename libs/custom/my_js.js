document.addEventListener('DOMContentLoaded', function () {
  document.querySelectorAll('[role="tablist"]').forEach(function (tablist) {
    var tabs = Array.from(tablist.querySelectorAll('[role="tab"]'));

    function activateTab(tab) {
      tabs.forEach(function (item) {
        var selected = item === tab;
        var panel = document.getElementById(item.getAttribute('aria-controls'));

        item.setAttribute('aria-selected', String(selected));
        item.tabIndex = selected ? 0 : -1;
        item.classList.toggle('active', selected);
        panel.hidden = !selected;
        panel.classList.toggle('active', selected);
      });
    }

    tabs.forEach(function (tab, index) {
      tab.addEventListener('click', function () {
        activateTab(tab);
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
        activateTab(tabs[nextIndex]);
        tabs[nextIndex].focus();
      });
    });
  });
});
