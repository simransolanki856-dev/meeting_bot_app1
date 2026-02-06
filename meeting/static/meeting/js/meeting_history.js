// Meeting History Page JavaScript
let currentPage = 1;
let currentSearch = '';
let currentFilter = '';

document.addEventListener('DOMContentLoaded', function() {
    const searchBtn = document.getElementById('searchBtn');
    const searchInput = document.getElementById('searchInput');
    const filterType = document.getElementById('filterType');

    // Load initial meetings
    loadMeetings();

    // Search functionality
    searchBtn.addEventListener('click', () => {
        currentSearch = searchInput.value.trim();
        currentPage = 1;
        loadMeetings();
    });

    searchInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            searchBtn.click();
        }
    });

    // Filter functionality
    filterType.addEventListener('change', () => {
        currentFilter = filterType.value;
        currentPage = 1;
        loadMeetings();
    });

    window.loadMeetings = loadMeetings;

    async function loadMeetings() {
        const loadingContainer = document.getElementById('loadingContainer');
        const meetingsContainer = document.getElementById('meetingsContainer');
        const emptyContainer = document.getElementById('emptyContainer');
        const errorContainer = document.getElementById('errorContainer');

        loadingContainer.style.display = 'block';
        meetingsContainer.style.display = 'none';
        emptyContainer.style.display = 'none';
        errorContainer.style.display = 'none';

        try {
            let url = `/api/meetings/?page=${currentPage}`;

            if (currentSearch) {
                url += `&search=${encodeURIComponent(currentSearch)}`;
            }

            if (currentFilter) {
                url += `&meeting_type=${encodeURIComponent(currentFilter)}`;
            }

            const response = await fetch(url);
            if (!response.ok) throw new Error('Failed to load meetings');

            const data = await response.json();
            displayMeetings(data);

        } catch (error) {
            console.error('Error:', error);
            loadingContainer.style.display = 'none';
            errorContainer.style.display = 'block';
            document.getElementById('errorText').textContent = error.message;
        }
    }

    function displayMeetings(data) {
        const loadingContainer = document.getElementById('loadingContainer');
        const meetingsContainer = document.getElementById('meetingsContainer');
        const emptyContainer = document.getElementById('emptyContainer');
        const meetingsTable = document.getElementById('meetingsTable');
        const paginationContainer = document.getElementById('paginationContainer');
        const pagination = document.getElementById('pagination');

        loadingContainer.style.display = 'none';

        if (data.results.length === 0) {
            meetingsContainer.style.display = 'none';
            emptyContainer.style.display = 'block';
            return;
        }

        meetingsContainer.style.display = 'block';
        emptyContainer.style.display = 'none';

        // Clear and populate table
        meetingsTable.innerHTML = '';
        data.results.forEach(meeting => {
            const row = document.createElement('tr');
            const statusBadgeClass = {
                'completed': 'badge-success',
                'processing': 'badge-warning',
                'pending': 'badge-info',
                'failed': 'badge-danger'
            }[meeting.status] || 'badge-info';

            row.innerHTML = `
                <td>
                    <a href="/meeting/${meeting.id}/" class="text-decoration-none">
                        ${escapeHtml(meeting.title)}
                    </a>
                </td>
                <td>${escapeHtml(meeting.meeting_type_display)}</td>
                <td>${formatDate(meeting.meeting_date)}</td>
                <td>
                    <span class="badge ${statusBadgeClass}">
                        ${escapeHtml(meeting.status_display)}
                    </span>
                </td>
                <td>${formatDate(meeting.created_at)}</td>
                <td>
                    <div class="btn-group btn-group-sm" role="group">
                        <a href="/meeting/${meeting.id}/" class="btn btn-outline-primary" title="View">
                            <i class="fas fa-eye"></i>
                        </a>
                        <button class="btn btn-outline-danger" onclick="deleteMeetingRow(${meeting.id})" title="Delete">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                </td>
            `;
            meetingsTable.appendChild(row);
        });

        // Setup pagination
        pagination.innerHTML = '';
        if (data.previous) {
            const prevBtn = document.createElement('li');
            prevBtn.className = 'page-item';
            prevBtn.innerHTML = `<a class="page-link" href="#" onclick="goToPage(${currentPage - 1}); return false;">Previous</a>`;
            pagination.appendChild(prevBtn);
        }

        // Add page numbers
        const totalPages = Math.ceil(data.count / 10);
        for (let i = Math.max(1, currentPage - 1); i <= Math.min(totalPages, currentPage + 1); i++) {
            const pageBtn = document.createElement('li');
            pageBtn.className = `page-item ${i === currentPage ? 'active' : ''}`;
            pageBtn.innerHTML = `<a class="page-link" href="#" onclick="goToPage(${i}); return false;">${i}</a>`;
            pagination.appendChild(pageBtn);
        }

        if (data.next) {
            const nextBtn = document.createElement('li');
            nextBtn.className = 'page-item';
            nextBtn.innerHTML = `<a class="page-link" href="#" onclick="goToPage(${currentPage + 1}); return false;">Next</a>`;
            pagination.appendChild(nextBtn);
        }

        paginationContainer.style.display = totalPages > 1 ? 'block' : 'none';
    }

    function escapeHtml(text) {
        const map = {
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#039;'
        };
        return text ? String(text).replace(/[&<>"']/g, m => map[m]) : '';
    }
});

// Global functions for pagination
function goToPage(page) {
    currentPage = page;
    loadMeetings();
    window.scrollTo(0, 0);
}

async function deleteMeetingRow(id) {
    if (confirm('Are you sure you want to delete this meeting?')) {
        try {
            const response = await fetch(`/api/meetings/${id}/`, {
                method: 'DELETE',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken')
                }
            });

            if (!response.ok) throw new Error('Failed to delete meeting');

            showToast('Meeting deleted successfully', 'success');
            loadMeetings();

        } catch (error) {
            console.error('Error:', error);
            showToast('Failed to delete meeting', 'error');
        }
    }
}
