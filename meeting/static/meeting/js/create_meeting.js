// Create Meeting Page JavaScript
document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('createMeetingForm');
    const uploadArea = document.getElementById('uploadArea');
    const recordingFileInput = document.getElementById('recordingFile');
    const browseBtn = document.getElementById('browseBtn');
    const fileInfo = document.getElementById('fileInfo');
    const transcriptTab = document.getElementById('transcript');
    const recordingFileDisplay = document.getElementById('recordingFile');
    const transcriptInput = document.getElementById('transcript');
    const meetingDateInput = document.getElementById('meetingDate');
    
    // Set default meeting date to now
    const now = new Date();
    now.setMinutes(now.getMinutes() - now.getTimezoneOffset());
    meetingDateInput.value = now.toISOString().slice(0, 16);

    // Browse button click
    browseBtn.addEventListener('click', (e) => {
        e.preventDefault();
        recordingFileInput.click();
    });

    // File input change
    recordingFileInput.addEventListener('change', handleFileSelect);

    // Upload area drag and drop
    uploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadArea.classList.add('dragover');
    });

    uploadArea.addEventListener('dragleave', () => {
        uploadArea.classList.remove('dragover');
    });

    uploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadArea.classList.remove('dragover');
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            recordingFileInput.files = files;
            handleFileSelect();
        }
    });

    // Handle file selection
    function handleFileSelect() {
        const file = recordingFileInput.files[0];
        if (file) {
            // Validate file
            const allowedExtensions = ['mp3', 'wav', 'mp4', 'webm', 'm4a'];
            const fileExtension = file.name.split('.').pop().toLowerCase();
            const maxSize = 100 * 1024 * 1024; // 100MB

            if (!allowedExtensions.includes(fileExtension)) {
                showToast(`File type not allowed. Please use: ${allowedExtensions.join(', ')}`, 'error');
                recordingFileInput.value = '';
                fileInfo.style.display = 'none';
                return;
            }

            if (file.size > maxSize) {
                showToast('File size too large. Maximum 100MB allowed.', 'error');
                recordingFileInput.value = '';
                fileInfo.style.display = 'none';
                return;
            }

            // Show file info
            document.getElementById('fileName').textContent = file.name;
            document.getElementById('fileSize').textContent = formatFileSize(file.size);
            fileInfo.style.display = 'block';

            // Switch to upload tab
            document.getElementById('upload-tab').click();
        }
    }

    // Form submission
    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        if (!form.checkValidity()) {
            return;
        }

        // Check which tab is active
        const activeTab = document.querySelector('.nav-link.active');
        const isGoogleMeetTab = activeTab.id === 'meeting-link-tab';

        if (isGoogleMeetTab) {
            // Handle Google Meet joining
            await handleGoogleMeetSubmit();
            return;
        }

        // Validate that either transcript or file is provided
        const transcript = transcriptInput.value.trim();
        const hasFile = recordingFileInput.files.length > 0;

        if (!transcript && !hasFile) {
            showToast('Please provide either a transcript or upload a recording file', 'error');
            return;
        }

        // Show loading state
        showLoadingState(true);

        try {
            // Create FormData for file upload
            const formData = new FormData();
            formData.append('title', document.getElementById('title').value);
            formData.append('meeting_type', document.getElementById('meetingType').value);
            formData.append('description', document.getElementById('description').value);
            formData.append('meeting_date', document.getElementById('meetingDate').value);

            if (transcript) {
                formData.append('transcript', transcript);
            }

            if (hasFile) {
                formData.append('recording_file', recordingFileInput.files[0]);
            }

            // Send request
            const response = await fetch('/api/meetings/', {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: formData
            });

            if (!response.ok) {
                const errorData = await response.json();
                const errorMessage = Object.values(errorData).flat().join(' ');
                throw new Error(errorMessage || 'Failed to create meeting');
            }

            const meeting = await response.json();
            showToast('Meeting created successfully!', 'success');

            // Redirect to meeting result page
            setTimeout(() => {
                window.location.href = `/meeting/${meeting.id}/`;
            }, 1500);

        } catch (error) {
            console.error('Error:', error);
            showToast(error.message || 'Failed to create meeting', 'error');
        } finally {
            showLoadingState(false);
        }
    });

    // Handle Google Meet submission
    async function handleGoogleMeetSubmit() {
        const meetingLink = document.getElementById('meetingLink').value.trim();
        
        if (!meetingLink) {
            showToast('Please enter a meeting link', 'error');
            return;
        }

        // Validate URL format
        try {
            new URL(meetingLink);
        } catch {
            showToast('Please enter a valid URL', 'error');
            return;
        }

        // Check if it's a supported platform
        const supportedPlatforms = ['meet.google.com', 'zoom.us', 'teams.microsoft.com'];
        if (!supportedPlatforms.some(platform => meetingLink.includes(platform))) {
            showToast('Supported platforms: Google Meet, Zoom, Microsoft Teams', 'error');
            return;
        }

        showLoadingState(true);

        try {
            const response = await fetch('/api/meetings/join_meeting/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({
                    title: document.getElementById('title').value,
                    meeting_type: document.getElementById('meetingType').value,
                    meeting_link: meetingLink,
                    duration_minutes: parseInt(document.getElementById('recordingDuration').value) || 60
                })
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || 'Failed to join meeting');
            }

            const meeting = await response.json();
            showToast(`Joined ${meeting.platform} meeting! Recording started...`, 'success');

            // Redirect to meeting result page
            setTimeout(() => {
                window.location.href = `/meeting/${meeting.id}/`;
            }, 1500);

        } catch (error) {
            console.error('Error:', error);
            showToast(error.message || 'Failed to join meeting', 'error');
        } finally {
            showLoadingState(false);
        }
    }

    function showLoadingState(isLoading) {
        const loadingContainer = document.getElementById('loadingContainer');
        const submitBtn = document.getElementById('submitBtn');

        if (isLoading) {
            loadingContainer.style.display = 'block';
            submitBtn.disabled = true;
        } else {
            loadingContainer.style.display = 'none';
            submitBtn.disabled = false;
        }
    }
});
