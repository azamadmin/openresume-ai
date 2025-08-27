// Resume Doctor.Ai - Clean Dashboard JavaScript

document.addEventListener('DOMContentLoaded', function() {
    console.log('🤖 Resume Doctor.Ai Dashboard Loaded');
    
    // Check authentication
    const token = localStorage.getItem('dr_resume_token');
    if (!token) {
        console.log('❌ No token found, redirecting to login');
        window.location.href = 'us10_login.html';
        return;
    }

    // Verify token is valid by making a test API call
    verifyTokenAndProceed();
    
    // Add event listeners
    addEventListeners();
});

function verifyTokenAndProceed() {
    const token = localStorage.getItem('dr_resume_token');

    // Make a simple API call to verify token validity
    fetch(`${API_BASE_URL}/api/dashboard_stats`, {
        method: 'GET',
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        }
    })
    .then(response => {
        if (response.status === 401) {
            // Token is invalid, clear it and redirect to login
            console.log('❌ Token invalid, clearing and redirecting to login');
            clearTokens();
            window.location.href = 'us10_login.html';
            return;
        }
        // Token is valid, proceed with dashboard initialization
        initializeDashboard();
    })
    .catch(error => {
        console.error('Error verifying token:', error);
        // On network error, still try to initialize dashboard
        initializeDashboard();
    });
}

function clearTokens() {
    localStorage.removeItem('dr_resume_token');
    localStorage.removeItem('dr_resume_refresh_token');
    localStorage.removeItem('dr_resume_user');
}

function initializeDashboard() {
    console.log('✅ Dashboard initialized');

    // Load user data
    const userData = JSON.parse(localStorage.getItem('dr_resume_user') || '{}');
    updateUserGreeting(userData);

    // Load dashboard stats
    loadDashboardStats();

    // Load recent scan history
    loadRecentScanHistory();

    // Load saved resumes and job descriptions
    loadSavedResumes();
    loadSavedJobDescriptions();

    // DO NOT auto-load suggestions - user must manually select resume and generate suggestions
    console.log('📝 Suggestions will be generated only when user clicks the buttons');

    // Hide suggestions section initially
    const suggestionsSection = document.getElementById('suggestions-section');
    if (suggestionsSection) {
        suggestionsSection.style.display = 'none';
    }
}

function addEventListeners() {
    // Navigation items
    const navItems = document.querySelectorAll('.nav-item');
    navItems.forEach(item => {
        item.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Remove active class from all items
            navItems.forEach(nav => nav.classList.remove('active'));
            
            // Add active class to clicked item
            this.classList.add('active');
            
            console.log('Navigation clicked:', this.textContent);
        });
    });
    
    // Stat cards hover effects
    const statCards = document.querySelectorAll('.stat-card');
    statCards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-4px)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(-2px)';
        });
    });
}

function updateUserGreeting(userData) {
    console.log('👤 Updating user greeting with data:', userData);

    // Update welcome title with user's first name
    const welcomeTitleElement = document.querySelector('.welcome-title');
    if (welcomeTitleElement && userData.first_name) {
        welcomeTitleElement.textContent = `Welcome back, ${userData.first_name}`;
        console.log(`✅ Updated welcome title to: Welcome back, ${userData.first_name}`);
    } else {
        console.log('❌ Could not update welcome title - element or first_name not found');
        console.log('Element found:', !!welcomeTitleElement);
        console.log('First name:', userData.first_name);
    }

    // Also update any user greeting elements if they exist
    const greetingElement = document.querySelector('.user-greeting');
    if (greetingElement && userData.first_name) {
        greetingElement.textContent = `Hi, ${userData.first_name}!`;
    }
}

function loadDashboardStats() {
    // Fetch real data from API
    const token = localStorage.getItem('dr_resume_token');

    fetch(`${API_BASE_URL}/api/dashboard_stats`, {
        method: 'GET',
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        }
    })
    .then(response => {
        if (response.status === 401) {
            clearTokens();
            window.location.href = 'us10_login.html';
            return;
        }
        return response.json();
    })
    .then(data => {
        if (!data) return; // Handle case where response was 401
        if (data.success) {
            const stats = data.stats;
            // Update stat cards with real data
            updateStatCard(0, stats.total_resumes || 0);
            updateStatCard(1, stats.total_job_descriptions || 0);
            updateStatCard(2, stats.total_scans || 0);
        } else {
            console.error('Failed to load dashboard stats:', data.message);
            // Show zeros if API fails
            updateStatCard(0, 0);
            updateStatCard(1, 0);
            updateStatCard(2, 0);
        }
    })
    .catch(error => {
        console.error('Error loading dashboard stats:', error);
        // Show zeros if API fails
        updateStatCard(0, 0);
        updateStatCard(1, 0);
        updateStatCard(2, 0);
    });
}

function updateStatCard(index, value) {
    const statCards = document.querySelectorAll('.stat-card');
    if (statCards[index]) {
        const numberElement = statCards[index].querySelector('.stat-number');
        if (numberElement) {
            // Animate number counting up
            animateNumber(numberElement, 0, value, 1000);
        }
    }
}

function animateNumber(element, start, end, duration) {
    const startTime = performance.now();
    
    function update(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);
        
        // Easing function for smooth animation
        const easeOutQuart = 1 - Math.pow(1 - progress, 4);
        const current = Math.round(start + (end - start) * easeOutQuart);
        
        element.textContent = current;
        
        if (progress < 1) {
            requestAnimationFrame(update);
        }
    }
    
    requestAnimationFrame(update);
}

function loadRecentScanHistory() {
    // Fetch real recent activity from API
    const token = localStorage.getItem('dr_resume_token');

    fetch(`${API_BASE_URL}/api/recent_activity`, {
        method: 'GET',
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        console.log('📊 Recent activity data:', data);

        if (data.success && data.recent_activity && data.recent_activity.recent_scans && data.recent_activity.recent_scans.length > 0) {
            // Use the most recent scan
            const recentScan = data.recent_activity.recent_scans[0];
            console.log('📋 Most recent scan:', recentScan);

            const scanData = {
                fileName: recentScan.resume_title || 'Resume',
                jobDescription: `${recentScan.job_title || 'Job Description'} • ${recentScan.company_name || 'Company'}`,
                scanDate: new Date(recentScan.created_at).toLocaleDateString(),
                matchPercentage: Math.round(recentScan.match_score || 0),
                keywordCount: `${recentScan.match_score || 0}%`,
                keywordBreakdown: [] // Will be populated from detailed analysis if needed
            };

            console.log('📊 Formatted scan data:', scanData);
            updateScanCard(scanData);
        } else {
            console.log('📭 No recent scans found, showing empty state');
            // Show "no data" state
            updateScanCardEmpty();
        }
    })
    .catch(error => {
        console.error('Error loading recent scan history:', error);
        updateScanCardEmpty();
    });
}

function updateScanCard(scanData) {
    // Update file name
    const fileNameElement = document.querySelector('.file-name');
    if (fileNameElement) {
        fileNameElement.textContent = scanData.fileName;
    }
    
    // Update job description
    const jobDescElement = document.querySelector('.job-description');
    if (jobDescElement) {
        jobDescElement.textContent = scanData.jobDescription;
    }
    
    // Update scan date
    const scanDateElement = document.querySelector('.scan-date');
    if (scanDateElement) {
        scanDateElement.textContent = scanData.scanDate;
    }
    
    // Update match percentage
    const matchPercentageElement = document.querySelector('.match-percentage');
    if (matchPercentageElement) {
        matchPercentageElement.textContent = `${scanData.matchPercentage} %`;
    }
    
    // Update keyword count
    const keywordCountElement = document.querySelector('.keyword-count');
    if (keywordCountElement) {
        keywordCountElement.textContent = scanData.keywordCount;
    }
    
    // Update keyword breakdown
    updateKeywordBreakdown(scanData.keywordBreakdown);
}

function updateKeywordBreakdown(keywords) {
    const keywordItems = document.querySelectorAll('.keyword-item');
    
    keywords.forEach((keyword, index) => {
        if (keywordItems[index]) {
            const percentageElement = keywordItems[index].querySelector('.keyword-percentage');
            const labelElement = keywordItems[index].querySelector('.keyword-label');
            
            if (percentageElement) {
                percentageElement.textContent = `${keyword.percentage} %`;
            }
            
            if (labelElement) {
                labelElement.textContent = keyword.keyword;
            }
        }
    });
}

function updateScanCardEmpty() {
    // Update file name
    const fileNameElement = document.querySelector('.file-name');
    if (fileNameElement) {
        fileNameElement.textContent = 'No resumes uploaded yet';
    }

    // Update job description
    const jobDescElement = document.querySelector('.job-description');
    if (jobDescElement) {
        jobDescElement.textContent = 'Upload a resume and job description to see analysis';
    }

    // Update scan date
    const scanDateElement = document.querySelector('.scan-date');
    if (scanDateElement) {
        scanDateElement.textContent = '-';
    }

    // Update match percentage
    const matchPercentageElement = document.querySelector('.match-percentage');
    if (matchPercentageElement) {
        matchPercentageElement.textContent = '0 %';
    }

    // Update keyword count
    const keywordCountElement = document.querySelector('.keyword-count');
    if (keywordCountElement) {
        keywordCountElement.textContent = '0 keywords';
    }

    // Clear keyword breakdown
    const keywordItems = document.querySelectorAll('.keyword-item');
    keywordItems.forEach(item => {
        const percentageElement = item.querySelector('.keyword-percentage');
        const labelElement = item.querySelector('.keyword-label');

        if (percentageElement) {
            percentageElement.textContent = '0 %';
        }

        if (labelElement) {
            labelElement.textContent = 'No data';
        }
    });
}

function loadSavedResumes() {
    const token = localStorage.getItem('dr_resume_token');

    fetch(`${API_BASE_URL}/api/resumes`, {
        method: 'GET',
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        const resumeSelectDiv = document.getElementById('resume-select');
        if (data.success && data.resumes && data.resumes.length > 0) {
            resumeSelectDiv.innerHTML = data.resumes.map(resume => `
                <div class="saved-item" data-id="${resume.id}">
                    <div class="saved-item-name">${resume.title || 'Untitled Resume'}</div>
                    <div class="saved-item-date">Uploaded: ${new Date(resume.created_at).toLocaleDateString()}</div>
                </div>
            `).join('');
        } else {
            resumeSelectDiv.innerHTML = '<div class="saved-placeholder">No saved resumes yet. Upload your first resume above!</div>';
        }
    })
    .catch(error => {
        console.error('Error loading saved resumes:', error);
        document.getElementById('resume-select').innerHTML = '<div class="saved-placeholder">Error loading resumes</div>';
    });
}

function loadSavedJobDescriptions() {
    const token = localStorage.getItem('dr_resume_token');

    fetch(`${API_BASE_URL}/api/job_descriptions`, {
        method: 'GET',
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        const jobSelectDiv = document.getElementById('job-select');
        if (data.success && data.job_descriptions && data.job_descriptions.length > 0) {
            jobSelectDiv.innerHTML = data.job_descriptions.map(job => `
                <div class="saved-item" data-id="${job.id}">
                    <div class="saved-item-name">${job.title || 'Untitled Job'}</div>
                    <div class="saved-item-date">Created: ${new Date(job.created_at).toLocaleDateString()}</div>
                </div>
            `).join('');
        } else {
            jobSelectDiv.innerHTML = '<div class="saved-placeholder">No saved job descriptions yet. Create your first job description above!</div>';
        }
    })
    .catch(error => {
        console.error('Error loading saved job descriptions:', error);
        document.getElementById('job-select').innerHTML = '<div class="saved-placeholder">Error loading job descriptions</div>';
    });
}

function loadSavedResumes() {
    const token = localStorage.getItem('dr_resume_token');

    fetch(`${API_BASE_URL}/api/resumes`, {
        method: 'GET',
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        const resumeSelectDiv = document.getElementById('resume-select');
        if (data.success && data.resumes && data.resumes.length > 0) {
            resumeSelectDiv.innerHTML = data.resumes.map(resume => `
                <div class="saved-item" data-id="${resume.id}">
                    <div class="saved-item-name">${resume.title || 'Untitled Resume'}</div>
                    <div class="saved-item-date">Uploaded: ${new Date(resume.created_at).toLocaleDateString()}</div>
                </div>
            `).join('');
        } else {
            resumeSelectDiv.innerHTML = '<div class="saved-placeholder">No saved resumes yet. Upload your first resume above!</div>';
        }
    })
    .catch(error => {
        console.error('Error loading saved resumes:', error);
        document.getElementById('resume-select').innerHTML = '<div class="saved-placeholder">Error loading resumes</div>';
    });
}

function loadSavedJobDescriptions() {
    const token = localStorage.getItem('dr_resume_token');

    fetch(`${API_BASE_URL}/api/job_descriptions`, {
        method: 'GET',
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        const jobSelectDiv = document.getElementById('job-select');
        if (data.success && data.job_descriptions && data.job_descriptions.length > 0) {
            jobSelectDiv.innerHTML = data.job_descriptions.map(job => `
                <div class="saved-item" data-id="${job.id}">
                    <div class="saved-item-name">${job.title || 'Untitled Job'}</div>
                    <div class="saved-item-date">Created: ${new Date(job.created_at).toLocaleDateString()}</div>
                </div>
            `).join('');
        } else {
            jobSelectDiv.innerHTML = '<div class="saved-placeholder">No saved job descriptions yet. Create your first job description above!</div>';
        }
    })
    .catch(error => {
        console.error('Error loading saved job descriptions:', error);
        document.getElementById('job-select').innerHTML = '<div class="saved-placeholder">Error loading job descriptions</div>';
    });
}

// Utility functions
function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    
    // Style the notification
    Object.assign(notification.style, {
        position: 'fixed',
        top: '20px',
        right: '20px',
        padding: '12px 20px',
        borderRadius: '8px',
        color: 'white',
        fontWeight: '500',
        zIndex: '1000',
        transform: 'translateX(100%)',
        transition: 'transform 0.3s ease'
    });
    
    // Set background color based on type
    const colors = {
        info: '#3b82f6',
        success: '#10b981',
        warning: '#f59e0b',
        error: '#ef4444'
    };
    notification.style.backgroundColor = colors[type] || colors.info;
    
    // Add to page
    document.body.appendChild(notification);
    
    // Animate in
    setTimeout(() => {
        notification.style.transform = 'translateX(0)';
    }, 100);
    
    // Remove after 3 seconds
    setTimeout(() => {
        notification.style.transform = 'translateX(100%)';
        setTimeout(() => {
            document.body.removeChild(notification);
        }, 300);
    }, 3000);
}

// Resume Analysis Functions
function handleLogout() {
    if (confirm('Are you sure you want to logout?')) {
        // Clear stored data
        localStorage.removeItem('dr_resume_token');
        localStorage.removeItem('dr_resume_user');
        
        // Show notification
        showNotification('Logged out successfully', 'success');
        
        // Redirect to login page after a short delay
        setTimeout(() => {
            window.location.href = 'us10_login.html';
        }, 1000);
    }
}

function switchTab(section, tab) {
    // Remove active class from all tabs in the section
    const sectionElement = document.querySelector(`.${section}-section`);
    const tabs = sectionElement.querySelectorAll('.tab-btn');
    const panes = sectionElement.querySelectorAll('.tab-pane');
    
    tabs.forEach(t => t.classList.remove('active'));
    panes.forEach(p => p.classList.remove('active'));
    
    // Add active class to clicked tab and corresponding pane
    event.target.classList.add('active');
    document.getElementById(`${section}-${tab}`).classList.add('active');
}

function triggerFileUpload() {
    document.getElementById('resume-file').click();
}

function handleFileSelect(event) {
    const file = event.target.files[0];
    if (file) {
        console.log('📁 File selected:', file.name, file.type, file.size);

        const allowedTypes = ['application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'];
        if (allowedTypes.includes(file.type)) {
            showNotification(`Uploading "${file.name}"...`, 'info');
            const formData = new FormData();
            formData.append('resume', file);

            const token = localStorage.getItem('dr_resume_token');
            console.log('🔑 Using token:', token ? token.substring(0, 20) + '...' : 'NO TOKEN');

            if (!token) {
                showNotification('No authentication token found. Please log in again.', 'error');
                setTimeout(() => {
                    window.location.href = 'us10_login.html';
                }, 2000);
                return;
            }

            console.log('📤 Starting upload to:', `${API_BASE_URL}/api/upload_resume`);

            fetch(`${API_BASE_URL}/api/upload_resume`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`
                },
                body: formData
            })
            .then(response => {
                console.log('📊 Upload response status:', response.status);
                console.log('📄 Upload response headers:', Object.fromEntries(response.headers.entries()));

                if (response.status === 401) {
                    // Token is invalid, clear it and redirect to login
                    console.log('❌ Upload failed: Token invalid, redirecting to login');
                    clearTokens();
                    showNotification('Session expired. Please log in again.', 'error');
                    setTimeout(() => {
                        window.location.href = 'us10_login.html';
                    }, 2000);
                    return;
                }

                if (response.status === 500) {
                    console.log('❌ Server error (500)');
                    return response.text().then(text => {
                        console.log('📄 Server error response:', text);
                        try {
                            const errorData = JSON.parse(text);
                            throw new Error(`Server error: ${errorData.message || 'Internal server error'}`);
                        } catch (parseError) {
                            throw new Error(`Server error: ${text}`);
                        }
                    });
                }

                if (!response.ok) {
                    console.log(`❌ HTTP error: ${response.status}`);
                    return response.text().then(text => {
                        console.log('📄 Error response:', text);
                        throw new Error(`HTTP error! status: ${response.status} - ${text}`);
                    });
                }

                return response.json();
            })
            .then(result => {
                console.log('✅ Upload result:', result);
                if (result && result.success) {
                    showNotification('Resume uploaded and keywords extracted!', 'success');
                    console.log('📄 Resume ID:', result.resume?.id);
                    console.log('🔍 Keywords extracted:', result.keywords_extracted);

                    // Refresh the dashboard data
                    loadDashboardStats();
                    loadSavedResumes();
                    loadRecentScanHistory();

                    // Calculate matching score if both resume and JD exist
                    calculateMatchingScoreIfReady();

                    // DO NOT auto-load suggestions - user must click the buttons manually
                    console.log('📝 Resume uploaded successfully. User can now generate suggestions manually.');
                } else if (result) {
                    console.log('❌ Upload failed:', result.message);
                    showNotification(result.message || 'Upload failed', 'error');
                } else {
                    console.log('❌ No result received');
                    showNotification('Upload failed: No response received', 'error');
                }
            })
            .catch(error => {
                console.error('❌ Upload error:', error);
                console.error('❌ Error stack:', error.stack);
                showNotification(`Upload failed: ${error.message}`, 'error');
            });
        } else {
            showNotification('Please select a PDF, DOC, or DOCX file', 'error');
        }
    }
}

function handleDragOver(event) {
    event.preventDefault();
    event.currentTarget.style.borderColor = '#94a3af';
    event.currentTarget.style.background = 'rgba(255, 255, 255, 0.1)';
}

function handleDrop(event) {
    event.preventDefault();
    event.currentTarget.style.borderColor = '#cbd5e1';
    event.currentTarget.style.background = 'transparent';
    
    const files = event.dataTransfer.files;
    if (files.length > 0) {
        const file = files[0];
        const allowedTypes = ['application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'];
        
        if (allowedTypes.includes(file.type)) {
            showNotification(`File "${file.name}" uploaded successfully`, 'success');
            console.log('File dropped:', file.name, file.type, file.size);
        } else {
            showNotification('Please drop a PDF, DOC, or DOCX file', 'error');
        }
    }
}

function toggleSaveButton() {
    const textarea = document.querySelector('.job-textarea');
    const saveBtn = document.querySelector('.save-btn');
    
    if (textarea.value.trim().length > 0) {
        saveBtn.disabled = false;
    } else {
        saveBtn.disabled = true;
    }
}

function saveJobDescription() {
    const textarea = document.querySelector('.job-textarea');
    const jobDescription = textarea.value.trim();

    if (!jobDescription) {
        showNotification('Please enter a job description', 'error');
        return;
    }

    const token = localStorage.getItem('dr_resume_token');

    // Show loading state
    showNotification('Saving job description...', 'info');

    fetch(`${API_BASE_URL}/api/upload_jd`, {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            title: 'Job Description',
            company_name: 'Company',
            job_text: jobDescription
        })
    })
    .then(response => {
        if (response.status === 401) {
            clearTokens();
            window.location.href = 'us10_login.html';
            return;
        }
        return response.json();
    })
    .then(data => {
        if (!data) return;

        if (data.success) {
            showNotification('Job description saved and keywords extracted!', 'success');

            // Refresh dashboard data
            loadSavedJobDescriptions();

            // Clear the textarea
            textarea.value = '';
            toggleSaveButton();

            // DO NOT auto-calculate matching score - user must click the button manually
            console.log('📝 Job description saved successfully. User can now calculate matching score manually.');
        } else {
            showNotification(data.message || 'Failed to save job description', 'error');
        }
    })
    .catch(error => {
        console.error('Error saving job description:', error);
        showNotification('Failed to save job description', 'error');
    });
}

// Matching Score Calculation
function generateMatchingScore() {
    console.log('🎯 User clicked Calculate Matching Score');

    // Show matching score section first
    const matchingSection = document.getElementById('matching-score-section');
    if (matchingSection) {
        matchingSection.style.display = 'block';
    }

    // Show loading state (we can add this later)
    showNotification('Calculating matching score...', 'info');

    calculateMatchingScoreIfReady();
}

function calculateMatchingScoreIfReady() {
    console.log('🎯 Checking if ready to calculate matching score...');

    const token = localStorage.getItem('dr_resume_token');

    // Get latest resume and job description
    Promise.all([
        fetch(`${API_BASE_URL}/api/resumes`, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            }
        }).then(response => response.json()),

        fetch(`${API_BASE_URL}/api/job_descriptions`, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            }
        }).then(response => response.json())
    ])
    .then(([resumesData, jdData]) => {
        if (resumesData.success && jdData.success &&
            resumesData.resumes.length > 0 && jdData.job_descriptions.length > 0) {

            const latestResume = resumesData.resumes[0];
            const latestJD = jdData.job_descriptions[0];

            // Check if both have keywords extracted
            if (latestResume.keywords_extracted && latestJD.keywords_extracted) {
                console.log(`🎯 Calculating matching score for resume ${latestResume.id} vs JD ${latestJD.id}`);

                // Calculate matching score
                fetch(`${API_BASE_URL}/api/calculate_match`, {
                    method: 'POST',
                    headers: {
                        'Authorization': `Bearer ${token}`,
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        resume_id: latestResume.id,
                        job_description_id: latestJD.id
                    })
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        console.log('✅ Matching score calculated:', data);

                        // Show matching score section with the calculated data
                        showMatchingScore({
                            overall_score: data.detailed_scores.overall_score,
                            technical_score: data.detailed_scores.technical_score,
                            soft_skills_score: data.detailed_scores.soft_skills_score,
                            other_keywords_score: data.detailed_scores.other_keywords_score,
                            matched_keywords: data.keyword_analysis.matched_keywords,
                            total_resume_keywords: data.keyword_analysis.total_resume_keywords,
                            total_jd_keywords: data.keyword_analysis.total_jd_keywords
                        });

                        showNotification('Matching score calculated successfully!', 'success');
                    } else {
                        console.error('Failed to calculate matching score:', data.message);
                        showNotification('Failed to calculate matching score', 'error');
                    }
                })
                .catch(error => {
                    console.error('Error calculating matching score:', error);
                    showNotification('Error calculating matching score', 'error');
                });
            } else {
                console.log('⏳ Keywords not extracted yet for both resume and JD');
            }
        } else {
            console.log('📭 No resume or job description found');
        }
    })
    .catch(error => {
        console.error('Error checking for resume/JD:', error);
    });
}

// Suggestions Functions
let currentSuggestions = {
    basic: [],
    premium: []
};

function loadLatestSuggestions() {
    const token = localStorage.getItem('dr_resume_token');

    fetch(`${API_BASE_URL}/api/latest_suggestions`, {
        method: 'GET',
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        }
    })
    .then(response => {
        if (response.status === 401) {
            clearTokens();
            window.location.href = 'us10_login.html';
            return;
        }
        return response.json();
    })
    .then(data => {
        if (!data) return;

        console.log('🔍 Latest suggestions response:', data);

        if (data.success) {
            currentSuggestions.basic = data.suggestions || [];
            console.log('📝 Basic suggestions loaded:', currentSuggestions.basic.length, 'suggestions');

            // Show suggestions section first
            const suggestionsSection = document.getElementById('suggestions-section');
            if (suggestionsSection) {
                suggestionsSection.style.display = 'block';
                console.log('✅ Suggestions section made visible');
            }

            if (currentSuggestions.basic.length > 0) {
                displaySuggestions(currentSuggestions.basic, 'basic');
                showBasicSuggestions(); // Ensure basic tab is active
                console.log('✅ Suggestions displayed and basic tab activated');
            } else {
                console.log('⚠️ No suggestions to display');
                showEmptySuggestions('No suggestions available yet. Upload both a resume and job description to get suggestions.');
            }
        } else {
            console.log('❌ Suggestions API failed:', data.message);
            // Show empty state but still make section visible
            const suggestionsSection = document.getElementById('suggestions-section');
            if (suggestionsSection) {
                suggestionsSection.style.display = 'block';
            }
            showEmptySuggestions(data.message);
        }
    })
    .catch(error => {
        console.error('Error loading suggestions:', error);
        showEmptySuggestions('Failed to load suggestions');
    });
}

function generateBasicSuggestions() {
    console.log('⭐ User clicked Generate Basic Suggestions');

    // Show suggestions section first
    const suggestionsSection = document.getElementById('suggestions-section');
    if (suggestionsSection) {
        suggestionsSection.style.display = 'block';
    }

    showSuggestionsLoading();

    const token = localStorage.getItem('dr_resume_token');

    // Get the user's resumes and job descriptions
    Promise.all([
        fetch(`${API_BASE_URL}/api/resumes`, {
            headers: { 'Authorization': `Bearer ${token}` }
        }).then(r => r.json()),
        fetch(`${API_BASE_URL}/api/job_descriptions`, {
            headers: { 'Authorization': `Bearer ${token}` }
        }).then(r => r.json())
    ])
    .then(([resumesData, jdData]) => {
        if (resumesData.success && jdData.success &&
            resumesData.resumes.length > 0 && jdData.job_descriptions.length > 0) {

            const latestResume = resumesData.resumes[0];
            const latestJD = jdData.job_descriptions[0];

            console.log(`📝 Generating basic suggestions for resume ${latestResume.id} vs JD ${latestJD.id}`);

            return fetch(`${API_BASE_URL}/api/basic_suggestions`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    resume_id: latestResume.id,
                    job_description_id: latestJD.id
                })
            });
        } else {
            throw new Error('Please upload both a resume and job description first');
        }
    })
    .then(response => response.json())
    .then(data => {
        console.log('🎯 Basic suggestions response:', data);
        if (data.success) {
            currentSuggestions.basic = data.suggestions || [];
            console.log('📊 Basic suggestions stored:', currentSuggestions.basic.length);
            displaySuggestions(currentSuggestions.basic, 'basic');
            showBasicSuggestions(); // Switch to basic view
            showNotification(`Generated ${currentSuggestions.basic.length} basic suggestions`, 'success');
        } else {
            console.error('❌ Basic suggestions failed:', data.message);
            showNotification(data.message || 'Failed to generate basic suggestions', 'error');
            hideSuggestionsLoading();
        }
    })
    .catch(error => {
        console.error('Error generating basic suggestions:', error);
        showNotification(error.message || 'Failed to generate basic suggestions', 'error');
        hideSuggestionsLoading();
    });
}

function generatePremiumSuggestions() {
    console.log('💎 User clicked Generate Premium Suggestions');

    // Show suggestions section first
    const suggestionsSection = document.getElementById('suggestions-section');
    if (suggestionsSection) {
        suggestionsSection.style.display = 'block';
    }

    showSuggestionsLoading();

    const token = localStorage.getItem('dr_resume_token');

    // Get the user's resumes and job descriptions
    Promise.all([
        fetch(`${API_BASE_URL}/api/resumes`, {
            headers: { 'Authorization': `Bearer ${token}` }
        }).then(r => r.json()),
        fetch(`${API_BASE_URL}/api/job_descriptions`, {
            headers: { 'Authorization': `Bearer ${token}` }
        }).then(r => r.json())
    ])
    .then(([resumesData, jdData]) => {
        if (resumesData.success && jdData.success &&
            resumesData.resumes.length > 0 && jdData.job_descriptions.length > 0) {

            const latestResume = resumesData.resumes[0];
            const latestJD = jdData.job_descriptions[0];

            console.log(`🤖 Generating premium AI suggestions for resume ${latestResume.id} vs JD ${latestJD.id}`);

            return fetch(`${API_BASE_URL}/api/premium_suggestions`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    resume_id: latestResume.id,
                    job_description_id: latestJD.id
                })
            });
        } else {
            throw new Error('Please upload both a resume and job description first');
        }
    })
    .then(response => response.json())
    .then(data => {
        console.log('🎯 Premium suggestions response:', data);
        if (data.success) {
            currentSuggestions.premium = data.suggestions || [];
            console.log('📊 Premium suggestions stored:', currentSuggestions.premium.length);
            displaySuggestions(currentSuggestions.premium, 'premium');
            showPremiumSuggestions(); // Switch to premium view
            showNotification(`Generated ${currentSuggestions.premium.length} premium AI suggestions`, 'success');
        } else {
            console.error('❌ Premium suggestions failed:', data.message);
            showNotification(data.message || 'Failed to generate premium suggestions', 'error');
            hideSuggestionsLoading();
        }
    })
    .catch(error => {
        console.error('Error generating premium suggestions:', error);
        showNotification(error.message || 'Failed to generate premium suggestions', 'error');
        hideSuggestionsLoading();
    });
}

function showBasicSuggestions() {
    document.getElementById('basic-toggle').classList.add('active');
    document.getElementById('premium-toggle').classList.remove('active');

    if (currentSuggestions.basic.length > 0) {
        displaySuggestions(currentSuggestions.basic, 'basic');
    } else {
        showEmptySuggestions('Click "Generate Basic Suggestions" to get AI-powered suggestions');
    }
}

function showPremiumSuggestions() {
    document.getElementById('basic-toggle').classList.remove('active');
    document.getElementById('premium-toggle').classList.add('active');

    if (currentSuggestions.premium.length > 0) {
        displaySuggestions(currentSuggestions.premium, 'premium');
    } else {
        showEmptySuggestions('Click "Generate Premium Suggestions" to get advanced AI-powered suggestions');
    }
}

function displaySuggestions(suggestions, type) {
    console.log(`🎨 Displaying ${suggestions.length} ${type} suggestions`);
    console.log('🔍 Suggestions data:', suggestions);

    const suggestionsSection = document.getElementById('suggestions-section');
    const suggestionsList = document.getElementById('suggestions-list');
    const emptyState = document.getElementById('suggestions-empty');
    const loadingState = document.getElementById('suggestions-loading');

    console.log('🔍 DOM elements found:', {
        suggestionsSection: !!suggestionsSection,
        suggestionsList: !!suggestionsList,
        emptyState: !!emptyState,
        loadingState: !!loadingState
    });

    if (!suggestionsSection) {
        console.error('❌ Suggestions section not found in DOM');
        return;
    }

    if (!suggestionsList) {
        console.error('❌ Suggestions list not found in DOM');
        return;
    }

    // Hide loading and empty states
    if (loadingState) loadingState.style.display = 'none';
    if (emptyState) emptyState.style.display = 'none';

    // Show suggestions section
    suggestionsSection.style.display = 'block';
    console.log('✅ Suggestions section made visible');

    if (suggestions.length === 0) {
        console.log('📭 No suggestions to display, showing empty state');
        if (emptyState) emptyState.style.display = 'block';
        suggestionsList.style.display = 'none';
        return;
    }

    // Show suggestions list and clear existing suggestions
    suggestionsList.style.display = 'block';
    suggestionsList.innerHTML = '';
    console.log('✅ Suggestions list made visible and cleared');

    // Display suggestions
    suggestions.forEach((suggestion, index) => {
        console.log(`📝 Creating suggestion ${index + 1}:`, suggestion.title);
        const suggestionElement = createSuggestionElement(suggestion);
        suggestionsList.appendChild(suggestionElement);
        console.log(`✅ Added suggestion ${index + 1} to DOM`);
    });

    console.log('✅ All suggestions displayed');
    console.log('🔍 Final suggestions list HTML:', suggestionsList.innerHTML.substring(0, 200) + '...');
}

function createSuggestionElement(suggestion) {
    const div = document.createElement('div');
    div.className = 'suggestion-item';

    const priorityClass = suggestion.priority || 'medium';

    div.innerHTML = `
        <div class="suggestion-header">
            <span class="suggestion-priority ${priorityClass}">${priorityClass}</span>
        </div>
        <h4 class="suggestion-title">${suggestion.title}</h4>
        <p class="suggestion-description">${suggestion.description}</p>
        <div class="suggestion-action">${suggestion.action}</div>
        ${suggestion.keywords ? `
            <div class="suggestion-keywords">
                ${suggestion.keywords.map(keyword => `<span class="keyword-tag">${keyword}</span>`).join('')}
            </div>
        ` : ''}
    `;

    return div;
}

function showSuggestionsLoading() {
    const suggestionsSection = document.getElementById('suggestions-section');
    const loadingState = document.getElementById('suggestions-loading');
    const suggestionsList = document.getElementById('suggestions-list');
    const emptyState = document.getElementById('suggestions-empty');

    suggestionsSection.style.display = 'block';
    loadingState.style.display = 'block';
    suggestionsList.style.display = 'none';
    emptyState.style.display = 'none';
}

function hideSuggestionsLoading() {
    const loadingState = document.getElementById('suggestions-loading');
    const suggestionsList = document.getElementById('suggestions-list');

    loadingState.style.display = 'none';
    suggestionsList.style.display = 'block';
}

function showEmptySuggestions(message) {
    const suggestionsSection = document.getElementById('suggestions-section');
    const emptyState = document.getElementById('suggestions-empty');
    const loadingState = document.getElementById('suggestions-loading');
    const suggestionsList = document.getElementById('suggestions-list');

    loadingState.style.display = 'none';
    suggestionsList.style.display = 'none';
    emptyState.style.display = 'block';

    if (message) {
        emptyState.querySelector('p').textContent = message;
    }
}

// Matching Score Functions
function showMatchingScore(matchingData) {
    console.log('🎯 Showing matching score:', matchingData);

    const matchingSection = document.getElementById('matching-score-section');
    if (matchingSection) {
        matchingSection.style.display = 'block';

        // Update overall score
        const overallScore = Math.round(matchingData.overall_score || 0);
        updateOverallScore(overallScore);

        // Update detailed scores
        updateDetailedScores({
            technical: Math.round(matchingData.technical_score || 0),
            softSkills: Math.round(matchingData.soft_skills_score || 0),
            otherKeywords: Math.round(matchingData.other_keywords_score || 0)
        });

        // Update keyword analysis
        updateKeywordAnalysis({
            matched: matchingData.matched_keywords || 0,
            resume: matchingData.total_resume_keywords || 0,
            jobDescription: matchingData.total_jd_keywords || 0
        });

        // Scroll to matching score section
        matchingSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
}

function updateOverallScore(score) {
    const scoreValueElement = document.getElementById('overall-score-value');
    const progressElement = document.getElementById('overall-progress');
    const categoryElement = document.getElementById('score-category');

    if (scoreValueElement) {
        scoreValueElement.textContent = `${score}%`;
    }

    if (progressElement) {
        progressElement.style.setProperty('--progress', score);
    }

    if (categoryElement) {
        const category = getScoreCategory(score);
        categoryElement.textContent = category.label;
        categoryElement.className = `score-category ${category.class}`;
    }
}

function updateDetailedScores(scores) {
    // Technical Skills
    const technicalScoreElement = document.getElementById('technical-score');
    const technicalFillElement = document.getElementById('technical-fill');
    if (technicalScoreElement) technicalScoreElement.textContent = `${scores.technical}%`;
    if (technicalFillElement) {
        setTimeout(() => {
            technicalFillElement.style.width = `${scores.technical}%`;
        }, 300);
    }

    // Soft Skills
    const softSkillsScoreElement = document.getElementById('soft-skills-score');
    const softSkillsFillElement = document.getElementById('soft-skills-fill');
    if (softSkillsScoreElement) softSkillsScoreElement.textContent = `${scores.softSkills}%`;
    if (softSkillsFillElement) {
        setTimeout(() => {
            softSkillsFillElement.style.width = `${scores.softSkills}%`;
        }, 500);
    }

    // Other Keywords
    const otherKeywordsScoreElement = document.getElementById('other-keywords-score');
    const otherKeywordsFillElement = document.getElementById('other-keywords-fill');
    if (otherKeywordsScoreElement) otherKeywordsScoreElement.textContent = `${scores.otherKeywords}%`;
    if (otherKeywordsFillElement) {
        setTimeout(() => {
            otherKeywordsFillElement.style.width = `${scores.otherKeywords}%`;
        }, 700);
    }
}

function updateKeywordAnalysis(keywords) {
    const matchedElement = document.getElementById('matched-keywords');
    const resumeElement = document.getElementById('resume-keywords');
    const jdElement = document.getElementById('jd-keywords');

    if (matchedElement) matchedElement.textContent = keywords.matched;
    if (resumeElement) resumeElement.textContent = keywords.resume;
    if (jdElement) jdElement.textContent = keywords.jobDescription;
}

function getScoreCategory(score) {
    if (score >= 80) {
        return { label: 'Excellent Match', class: 'excellent' };
    } else if (score >= 60) {
        return { label: 'Good Match', class: 'good' };
    } else if (score >= 40) {
        return { label: 'Fair Match', class: 'fair' };
    } else {
        return { label: 'Needs Improvement', class: 'poor' };
    }
}

function hideMatchingScore() {
    const matchingSection = document.getElementById('matching-score-section');
    if (matchingSection) {
        matchingSection.style.display = 'none';
    }
}

// Export functions for global access
window.DashboardApp = {
    showNotification,
    updateUserGreeting,
    loadDashboardStats,
    loadRecentScanHistory,
    showMatchingScore,
    hideMatchingScore
};

// Make functions globally accessible
window.handleLogout = handleLogout;
window.switchTab = switchTab;
window.triggerFileUpload = triggerFileUpload;
window.handleFileSelect = handleFileSelect;
window.handleDragOver = handleDragOver;
window.handleDrop = handleDrop;
window.toggleSaveButton = toggleSaveButton;
window.saveJobDescription = saveJobDescription;
window.generateBasicSuggestions = generateBasicSuggestions;
window.generatePremiumSuggestions = generatePremiumSuggestions;
window.showBasicSuggestions = showBasicSuggestions;
window.showPremiumSuggestions = showPremiumSuggestions;