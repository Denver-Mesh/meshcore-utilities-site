// Modal functions for hex grid
function _buildInfoCard(repeater) {
    return `
        <div class="hex-info-card">
            <div class="hex-info-header">
                <span class="hex-id-badge hex-used-badge">${repeater.id}</span>
                <span class="hex-state-badge hex-state-${repeater.status}">${repeater.status_value}</span>
            </div>
            <h2 class="hex-info-title">${repeater.name}</h2>
            <div class="hex-info-grid">
                <div class="hex-info-item">
                    <span class="hex-info-label">📍 Location</span>
                    <span class="hex-info-value">${repeater.location}</span>
                </div>
                <div class="hex-info-item">
                    <span class="hex-info-label">🕐 Last Heard</span>
                    <span class="hex-info-value">${repeater.last_heard}</span>
                </div>
            </div>
            <div class="hex-info-contact">
                <a href="${repeater.contact_url}" class="hex-contact-btn">Add Contact</a>
            </div>
        </div>
    `
}

function showRepeaterInfo(hexId, repeater) {
    const modal = document.getElementById('hex-modal');
    const modalBody = document.getElementById('hex-modal-body');

    modalBody.innerHTML = _buildInfoCard(repeater);
    modal.style.display = 'block';
    modal.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

function showDuplicateInfo(hexId, repeaters) {
    const modal = document.getElementById('hex-modal');
    const modalBody = document.getElementById('hex-modal-body');

    let entriesHtml = '';
    repeaters.forEach((repeater, idx) => {
        entriesHtml += _buildInfoCard(repeater);
    });

    modalBody.innerHTML = `
        <div class="hex-info-card">
            <div class="hex-info-header">
                <span class="hex-id-badge hex-duplicate-badge">${hexId}</span>
                <span class="hex-warning-badge">⚠️ DUPLICATE CONFLICT</span>
            </div>
            <p class="hex-duplicate-warning">Multiple repeaters are using the same ID. This must be resolved!</p>
            <div class="hex-duplicates-container">
                ${entriesHtml}
            </div>
        </div>
    `;

    modal.style.display = 'block';
    modal.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

document.addEventListener('DOMContentLoaded', function() {
    // Search functionality
    const searchInput = document.getElementById('hex-search');
    const searchClear = document.getElementById('hex-search-clear');
    const searchResults = document.getElementById('hex-search-results');
    const hexTable = document.getElementById('repeater-hex-grid');

    if (!searchInput || !hexTable) return;

    // Store original repeater data in data attributes
    const cells = hexTable.querySelectorAll('td[onclick]');

    searchInput.addEventListener('input', function() {
        const query = this.value.trim().toLowerCase();

        // Show/hide clear button
        if (query.length > 0) {
            searchClear.style.display = 'block';
        } else {
            searchClear.style.display = 'none';
            clearSearch();
            return;
        }

        // Perform search
        if (query.length >= 2) {
            performSearch(query);
        }
    });

    searchClear.addEventListener('click', function() {
        searchInput.value = '';
        searchClear.style.display = 'none';
        clearSearch();
        searchInput.focus();
    });

    function performSearch(query) {
        let matchCount = 0;
        let totalSearchable = 0;

        cells.forEach(cell => {
            const onclick = cell.getAttribute('onclick');

            // Skip free cells
            if (cell.classList.contains("hex-free")) {
                cell.classList.add('hex-dimmed');
                return;
            }

            // NOT: totalSearchable is the number of possible cells, not the number of repeaters (duplicates count as 1)

            // Extract the info JSON from onclick
            let matched = false;

            // For single repeaters:  showRepeaterInfo or showBackboneInfo
            if (onclick.includes('showRepeaterInfo') || onclick.includes('showBackboneInfo')) {
                // Extract JSON between the quotes after the hex ID
                const regex = /show(?:Repeater|Backbone)Info\("([^"]+)",\s*({[^}]+})\)/;
                const match = onclick.match(regex);
                if (match && match[2]) {
                    const infoStr = match[2].replace(/&quot;/g, '"');
                    try {
                        const info = JSON.parse(infoStr);
                        matched = searchInInfo(info, query);
                    } catch (e) {
                        console.error('Parse error for single:', e, infoStr);
                    }
                }

                totalSearchable++;
            }

            // For duplicates: showDuplicateInfo
            if (onclick.includes('showDuplicateInfo')) {
                // Extract JSON array
                const regex = /showDuplicateInfo\("([^"]+)",\s*(\[[^\]]+\])\)/;
                const match = onclick.match(regex);
                if (match && match[2]) {
                    const infoStr = match[2].replace(/&quot;/g, '"');
                    try {
                        const infoArray = JSON.parse(infoStr);
                        matched = infoArray.some(info => searchInInfo(info, query));
                    } catch (e) {
                        console.error('Parse error for duplicate:', e, infoStr);
                    }
                }

                totalSearchable++;  // This counts as one searchable entry
            }

            if (matched) {
                cell.classList.add('hex-highlighted');
                cell.classList.remove('hex-dimmed');
                matchCount++;
            } else {
                cell.classList.add('hex-dimmed');
                cell.classList.remove('hex-highlighted');
            }
        });

        // Update results
        if (matchCount > 0) {
            searchResults.textContent = `Found ${matchCount} matching repeater${matchCount !== 1 ? 's' :  ''} out of ${totalSearchable}`;
            searchResults.style.color = '#a8d68c';
        } else {
            searchResults.textContent = `No matches found for "${query}"`;
            searchResults.style.color = '#ff9999';
        }
    }

    function searchInInfo(info, query) {
        const searchableFields = [
            info.name,
            info.location,
            info.antenna,
            info.state,
            info.height_metre,
            info.power_watt
        ];

        return searchableFields.some(field => {
            if (field === undefined || field === null) return false;
            return String(field).toLowerCase().includes(query);
        });
    }

    function clearSearch() {
        cells.forEach(cell => {
            cell.classList.remove('hex-highlighted', 'hex-dimmed');
        });
        searchResults.textContent = '';
    }
});
