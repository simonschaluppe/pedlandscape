document.addEventListener('DOMContentLoaded', function() {
    const checkboxes = document.querySelectorAll('.keyword-checkbox');
    checkboxes.forEach(checkbox => {
        checkbox.addEventListener('change', updateTiles);
    });

    function updateTiles() {
        const selectedKeywords = Array.from(checkboxes)
            .filter(checkbox => checkbox.checked)
            .map(checkbox => checkbox.getAttribute('data-keyword'));

        const tiles = document.querySelectorAll('.tile');
        tiles.forEach(tile => {
            const category = tile.getAttribute('data-category');
            if (selectedKeywords.includes(category)) {
                tile.classList.remove('greyed-out');
            } else {
                tile.classList.add('greyed-out');
            }
        });
    }
});
