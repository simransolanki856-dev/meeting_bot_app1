// Meeting Result Page JavaScript
document.addEventListener('DOMContentLoaded', function() {
    const loadingContainer = document.getElementById('loadingContainer');
    const summaryContainer = document.getElementById('summaryContainer');
    const errorContainer = document.getElementById('errorContainer');
    const downloadTxtBtn = document.getElementById('downloadTxtBtn');
    const downloadPdfBtn = document.getElementById('downloadPdfBtn');
    const deleteBtn = document.getElementById('deleteBtn');

    // Load meeting data
    loadMeeting();

    async function loadMeeting() {
        if (!meetingId) {
            showError('Invalid meeting ID');
            return;
        }
        try {
            const response = await fetch(`/api/meetings/${meetingId}/`);
            if (!response.ok) throw new Error('Failed to load meeting');

            const meeting = await response.json();
            displayMeeting(meeting);

        } catch (error) {
            console.error('Error:', error);
            showError(error.message || 'Failed to load meeting');
        }
    }

    function displayMeeting(meeting) {
        loadingContainer.style.display = 'none';
        summaryContainer.style.display = 'block';

        // Update header
        document.getElementById('meetingTitle').textContent = meeting.title;
        document.getElementById('meetingType').textContent = meeting.meeting_type_display;
        document.getElementById('meetingDate').textContent = formatDate(meeting.meeting_date);

        // Update summary tab
        document.getElementById('summaryText').textContent = meeting.summary || 'No summary available';

        // Update key points
        const keypointsList = document.getElementById('keypointsList');
        keypointsList.innerHTML = '';
        (meeting.key_points || []).forEach(point => {
            const li = document.createElement('li');
            li.className = 'list-group-item';
            li.textContent = typeof point === 'string' ? point : JSON.stringify(point);
            keypointsList.appendChild(li);
        });

        if ((meeting.key_points || []).length === 0) {
            const li = document.createElement('li');
            li.className = 'list-group-item text-muted';
            li.textContent = 'No key points available';
            keypointsList.appendChild(li);
        }

        // Update decisions
        const decisionsList = document.getElementById('decisionsList');
        decisionsList.innerHTML = '';
        (meeting.decisions || []).forEach(decision => {
            const li = document.createElement('li');
            li.className = 'list-group-item';
            li.textContent = typeof decision === 'string' ? decision : JSON.stringify(decision);
            decisionsList.appendChild(li);
        });

        if ((meeting.decisions || []).length === 0) {
            const li = document.createElement('li');
            li.className = 'list-group-item text-muted';
            li.textContent = 'No decisions available';
            decisionsList.appendChild(li);
        }

        // Update action items
        const actionItemsTable = document.getElementById('actionItemsTable');
        actionItemsTable.innerHTML = '';
        (meeting.action_items || []).forEach(item => {
            const row = document.createElement('tr');
            const task = typeof item === 'string' ? item : item.task || '';
            const owner = (typeof item === 'object' ? item.owner : '') || 'N/A';
            const dueDate = (typeof item === 'object' ? item.due_date : '') || 'N/A';

            row.innerHTML = `
                <td>${escapeHtml(task)}</td>
                <td>${escapeHtml(owner)}</td>
                <td>${escapeHtml(dueDate)}</td>
            `;
            actionItemsTable.appendChild(row);
        });

        if ((meeting.action_items || []).length === 0) {
            const row = document.createElement('tr');
            row.innerHTML = '<td colspan="3" class="text-muted text-center">No action items available</td>';
            actionItemsTable.appendChild(row);
        }

        // Update agenda
        const agendaContent = document.getElementById('agendaContent');
        agendaContent.innerHTML = '';
        if (meeting.agenda && (meeting.agenda || []).length > 0) {
            (meeting.agenda || []).forEach(item => {
                const topic = typeof item === 'string' ? item : item.topic || '';
                const description = (typeof item === 'object' ? item.description : '') || '';

                const div = document.createElement('div');
                div.className = 'mb-3';
                div.innerHTML = `
                    <h5>${escapeHtml(topic)}</h5>
                    <p class="text-muted">${escapeHtml(description) || 'No description'}</p>
                `;
                agendaContent.appendChild(div);
            });
        } else {
            const div = document.createElement('div');
            div.className = 'text-muted';
            div.textContent = 'No agenda items available';
            agendaContent.appendChild(div);
        }

        // Update transcript
        document.getElementById('transcriptText').textContent = meeting.transcript || 'No transcript available';

        // Set up button handlers
        setupButtonHandlers(meeting);
    }

    function setupButtonHandlers(meeting) {
        downloadTxtBtn.addEventListener('click', () => downloadSummary(meeting, 'txt'));
        deleteBtn.addEventListener('click', () => deleteMeeting(meeting.id));
    }

    async function downloadSummary(meeting, format) {
        try {
            const response = await fetch(`/api/meetings/${meeting.id}/download_summary/`);
            if (!response.ok) throw new Error('Failed to download summary');

            const data = await response.json();
            downloadText(data.content, `${meeting.title}_summary.txt`);
            showToast('Summary downloaded successfully', 'success');

        } catch (error) {
            console.error('Error:', error);
            showToast('Failed to download summary', 'error');
        }
    }

    async function deleteMeeting(id) {
        if (confirm('Are you sure you want to delete this meeting? This action cannot be undone.')) {
            try {
                const response = await fetch(`/api/meetings/${id}/`, {
                    method: 'DELETE',
                    headers: {
                        'X-CSRFToken': getCookie('csrftoken')
                    }
                });

                if (!response.ok) throw new Error('Failed to delete meeting');

                showToast('Meeting deleted successfully', 'success');
                setTimeout(() => {
                    window.location.href = '/history/';
                }, 1500);

            } catch (error) {
                console.error('Error:', error);
                showToast('Failed to delete meeting', 'error');
            }
        }
    }

    function showError(message) {
        loadingContainer.style.display = 'none';
        errorContainer.style.display = 'block';
        document.getElementById('errorText').textContent = message;
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
