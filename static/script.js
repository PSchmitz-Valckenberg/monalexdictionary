document.addEventListener('DOMContentLoaded', () => {
  const searchForm = document.getElementById('searchForm');
  const searchInput = document.getElementById('searchInput');

  if (!searchForm || !searchInput) {
    return;
  }

  searchForm.addEventListener('submit', (event) => {
    if (!searchInput.value.trim()) {
      event.preventDefault();
      searchInput.focus();
    }
  });
});
