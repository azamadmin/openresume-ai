// Resume Doctor AI - Modern Dashboard JavaScript

document.addEventListener('DOMContentLoaded', function() {
    console.log('🤖 Resume Doctor AI Dashboard Loaded');
    
    // Initialize dashboard
    initializeDashboard();
    
    // Add event listeners
    addEventListeners();
});

function initializeDashboard() {
    console.log('✅ Dashboard initialized');
    
    // Load user data
    const userData = JSON.parse(localStorage.getItem('dr_resume_user') || '{}');
    updateUserGreeting(userData);
    
    // Load dashboard stats with animation
    loadDashboardStats();
    
    // Initialize progress cards
    initializeProgressCards();
    
    // Load recent scan history
    loadRecentScanHistory();
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
            
            const route = this.getAttribute('data-route');
            console.log('Navigation clicked:', route);
            
            // Here you would typically handle route changes
            handleNavigation(route);
        });
    });
    
    // Progress cards
    const progressCards = document.querySelectorAll('.progress-card');
    progressCards.forEach(card => {
        card.addEventListener('click', function() {
            console.log('Progress card clicked');
            // Handle progress card interaction
        });
    });
    
    // Stat cards hover effects
    const statCards = document.querySelectorAll('.stat-card');
    statCards.forEach(card => {
        card.addEventListener('click', function() {
            const label = this.querySelector('.stat-label').textContent;
            console.log('Stat card clicked:', label);
            // Handle stat card click
        });
    });
    
    // Filter select
    const filterSelect = document.querySelector('.filter-select');
    if (filterSelect) {
        filterSelect.addEventListener('change', function() {
            console.log('Filter changed:', this.value);
            filterScanHistory(this.value);
        });
    }
    
    // Refresh button
    const refreshBtn = document.querySelector('.refresh-btn');
    if (refreshBtn) {
        refreshBtn.addEventListener('click', function() {
            console.log('Refresh clicked');
            loadRecentScanHistory();
            showNotification('Scan history refreshed', 'success');
        });
    }
    
    // Action buttons
    const enterNewBtn = document.querySelector('.action-btn.primary');
    const selectSavedBtn = document.querySelector('.action-btn.secondary');
    
    if (enterNewBtn) {
        enterNewBtn.addEventListener('click', function() {
            console.log('Enter new job description');
            handleEnterNewJob();
        });
    }
    
    if (selectSavedBtn) {
        selectSavedBtn.addEventListener('click', function() {
            console.log('Select saved job description');
            handleSelectSavedJob();
        });
    }
    
    // View all progress button
    const viewAllBtn = document.querySelector('.view-all-btn');
    if (viewAllBtn) {
        viewAllBtn.addEventListener('click', function() {
            console.log('View all progress clicked');
            // Handle view all progress
        });
    }
}

function handleNavigation(route) {
    // Handle different navigation routes
    switch(route) {
        case 'overview':
            // Show overview content
            break;
        case 'projects':
            // Show projects content
            break;
        case 'analytics':
            // Show analytics content
            break;
        case 'settings':
            // Show settings content
            break;
        default:
            console.log('Unknown route:', route);
    }
}

function updateUserGreeting(userData) {
    const welcomeTitle = document.querySelector('.welcome-title');
    if (welcomeTitle && userData.name) {
        welcomeTitle.textContent = `Welcome back, ${userData.name}`;
    }
}

function loadDashboardStats() {
    // Mock data - in real app, this would come from API
    const stats = {
        resumes: 3,
        jobDescriptions: 2,
        scans: 1
    };
    
    // Update stat cards with animation
    const statCards = document.querySelectorAll('.stat-card');
    statCards.forEach((card, index) => {
        const numberElement = card.querySelector('.stat-number');
        const labelElement = card.querySelector('.stat-label');
        
        if (numberElement && labelElement) {
            const label = labelElement.textContent.toLowerCase();
            let value = 0;
            
            if (label.includes('resume')) value = stats.resumes;
            else if (label.includes('job') || label.includes('description')) value = stats.jobDescriptions;
            else if (label.includes('scan')) value = stats.scans;
            
            // Animate number counting up
            animateNumber(numberElement, 0, value, 1000 + (index * 200));
        }
    });
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

function initializeProgressCards() {
    // Animate progress bars on load
    const progressFills = document.querySelectorAll('.progress-fill');
    progressFills.forEach((fill, index) => {
        const width = fill.style.width;
        fill.style.width = '0%';
        
        setTimeout(() => {
            fill.style.width = width;
        }, 500 + (index * 100));
    });
}

function loadRecentScanHistory() {
    // Mock data - in real app, this would come from API
    const scanData = {
        fileName: "Md_Moin_Ashraf_2_1.docx",
        scanStatus: "Scan Complete",
        keywordCount: "5/30 keywords",
        jobDescription: "Job Description: Frontend Developer • Acme Corp ...",
        scanDate: "23 Aug 2025 • 3:29",
        matchPercentage: 26.48,
        keywordBreakdown: [
            { category: "Technical", percentage: 10.34 },
            { category: "Soft Skills", percentage: 100 },
            { category: "Other", percentage: 4.35 }
        ]
    };
    
    // Update the scan card with real data
    updateScanCard(scanData);
}

function updateScanCard(scanData) {
    // Update file name
    const fileNameElement = document.querySelector('.file-name');
    if (fileNameElement) {
        fileNameElement.textContent = scanData.fileName;
    }
    
    // Update scan status
    const scanStatusElement = document.querySelector('.scan-status');
    if (scanStatusElement) {
        scanStatusElement.textContent = scanData.scanStatus;
    }
    
    // Update keyword count
    const keywordCountElement = document.querySelector('.keyword-count');
    if (keywordCountElement) {
        keywordCountElement.textContent = scanData.keywordCount;
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
        matchPercentageElement.textContent = `${scanData.matchPercentage}% Match`;
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
                percentageElement.textContent = `${keyword.percentage}%`;
            }
            
            if (labelElement) {
                labelElement.textContent = keyword.category;
            }
        }
    });
}

function filterScanHistory(filterValue) {
    // In a real app, this would filter the scan history based on the selected value
    console.log('Filtering scan history by:', filterValue);
    
    // Mock implementation - you would typically make an API call here
    showNotification(`Filtered by: ${filterValue}`, 'info');
}

function handleEnterNewJob() {
    // Create a modal or navigate to job description input
    const modal = createJobDescriptionModal();
    document.body.appendChild(modal);
}

function handleSelectSavedJob() {
    // Show saved job descriptions
    showNotification('Select from saved job descriptions', 'info');
}

function createJobDescriptionModal() {
    const modal = document.createElement('div');
    modal.className = 'modal-overlay';
    modal.innerHTML = `
        <div class="modal-content">
            <div class="modal-header">
                <h3>Enter Job Description</h3>
                <button class="modal-close">&times;</button>
            </div>
            <div class="modal-body">
                <textarea 
                    placeholder="Paste the job description here..."
                    rows="8"
                    class="job-textarea"
                ></textarea>
            </div>
            <div class="modal-footer">
                <button class="btn-cancel">Cancel</button>
                <button class="btn-submit">Submit</button>
            </div>
        </div>
    `;
    
    // Add modal styles
    const style = document.createElement('style');
    style.textContent = `
        .modal-overlay {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0, 0, 0, 0.5);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 1000;
        }
        .modal-content {
            background: white;
            border-radius: 12px;
            width: 90%;
            max-width: 600px;
            max-height: 80vh;
            overflow: hidden;
        }
        .modal-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 20px;
            border-bottom: 1px solid #e5e7eb;
        }
        .modal-close {
            background: none;
            border: none;
            font-size: 24px;
            cursor: pointer;
            color: #6b7280;
        }
        .modal-body {
            padding: 20px;
        }
        .job-textarea {
            width: 100%;
            border: 1px solid #d1d5db;
            border-radius: 8px;
            padding: 12px;
            font-family: inherit;
            resize: vertical;
        }
        .modal-footer {
            display: flex;
            gap: 12px;
            justify-content: flex-end;
            padding: 20px;
            border-top: 1px solid #e5e7eb;
        }
        .btn-cancel, .btn-submit {
            padding: 10px 20px;
            border-radius: 8px;
            font-weight: 500;
            cursor: pointer;
            border: none;
        }
        .btn-cancel {
            background: #f3f4f6;
            color: #374151;
        }
        .btn-submit {
            background: #667eea;
            color: white;
        }
    `;
    document.head.appendChild(style);
    
    // Add event listeners
    modal.querySelector('.modal-close').addEventListener('click', () => {
        document.body.removeChild(modal);
        document.head.removeChild(style);
    });
    
    modal.querySelector('.btn-cancel').addEventListener('click', () => {
        document.body.removeChild(modal);
        document.head.removeChild(style);
    });
    
    modal.querySelector('.btn-submit').addEventListener('click', () => {
        const textarea = modal.querySelector('.job-textarea');
        if (textarea.value.trim()) {
            console.log('Job description submitted:', textarea.value);
            showNotification('Job description submitted successfully!', 'success');
            document.body.removeChild(modal);
            document.head.removeChild(style);
        } else {
            showNotification('Please enter a job description', 'warning');
        }
    });
    
    // Close on overlay click
    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            document.body.removeChild(modal);
            document.head.removeChild(style);
        }
    });
    
    return modal;
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
        zIndex: '1001',
        transform: 'translateX(100%)',
        transition: 'transform 0.3s ease',
        maxWidth: '300px'
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
            if (document.body.contains(notification)) {
                document.body.removeChild(notification);
            }
        }, 300);
    }, 3000);
}

// Mobile menu toggle (for responsive design)
function toggleSidebar() {
    const sidebar = document.querySelector('.sidebar');
    sidebar.classList.toggle('open');
}

// Export functions for global access
window.DashboardApp = {
    showNotification,
    updateUserGreeting,
    loadDashboardStats,
    loadRecentScanHistory,
    toggleSidebar
};