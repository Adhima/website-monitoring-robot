const tabs = document.querySelectorAll('.nav-tab a');

tabs.forEach(tab => {
  tab.addEventListener('click', () => {
    // Ganti active tab
    tabs.forEach(t => t.classList.remove('active-tab'));
    tab.classList.add('active-tab');

    // Ambil nama kategori
    const kategori = tab.id.replace('tab-', '');

    // Sembunyikan semua section
    document.querySelectorAll('.kategori-section').forEach(sec => {
      sec.classList.add('d-none');
    });

    // Tampilkan hanya yang dipilih
    const activeSection = document.getElementById(`section-${kategori}`);
    if (activeSection) {
      activeSection.classList.remove('d-none');
    }
  });
});

      function setupCheckboxEvents(tabId) {
        const selectAll = document.getElementById(`select-all-${tabId}`);
        const checkboxes = document.querySelectorAll(`.row-check-${tabId}`);
        if (selectAll) {
          selectAll.addEventListener('change', () => {
            checkboxes.forEach(cb => cb.checked = selectAll.checked);
          });
        }
      }

      function downloadSelected(tabId) {
        const selected = document.querySelectorAll(`.row-check-${tabId}:checked`);
        alert(`Download ${selected.length} file dari menu ${tabId}`);
      }

      function hapusSelected(tabId) {
        const selected = document.querySelectorAll(`.row-check-${tabId}:checked`);
        alert(`Hapus ${selected.length} file dari menu ${tabId}`);
      }

      ['anomali', 'penambat', 'bantalan', 'kemiringan'].forEach(setupCheckboxEvents);

document.getElementById("confirm-logout").addEventListener("click", function () {
window.location.href = "/logout";
});