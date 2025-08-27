// Resume Doctor AI - Scan History Page JavaScript

// Global variables
let currentPage = 1;
let currentSort = 'created_at_desc';
let currentFilter = '';

document.addEventListener('DOMContentLoaded', function() {
    console.log('📊 Scan History Page Loaded');
    
    // Check authentication
    verifyTokenAndProceed();
    
    // Add event listeners
    addEventListeners();
});

function verifyTokenAndProceed() {
    const token = localStorage.getItem('dr_resume_token');
    
    if (!token) {
        console.log('❌ No token found, redirecting to login');
        window.location.href = 'us10_login.html';
        return;
    }
    
    // Verify token and load scan history
    loadScanHistory();
}

function addEventListeners() {
    // Sort select
    const sortSelect = document.getElementById('sort-select');
    if (sortSelect) {
        sortSelect.addEventListener('change', function() {
            currentSort = this.value;
            currentPage = 1;
            loadScanHistory();
        });
    }
    
    // Score filter
    const scoreFilter = document.getElementById('score-filter');
    if (scoreFilter) {
        scoreFilter.addEventListener('change', function() {
            currentFilter = this.value;
            currentPage = 1;
            loadScanHistory();
        });
    }
}

function loadScanHistory() {
    console.log('📊 Loading scan history...');
    
    const token = localStorage.getItem('dr_resume_token');
    const loadingState = document.getElementById('scan-history-loading');
    const historyList = document.getElementById('scan-history-list');
    const emptyState = document.getElementById('scan-history-empty');
    
    // Show loading state
    if (loadingState) loadingState.style.display = 'block';
    if (historyList) historyList.style.display = 'none';
    if (emptyState) emptyState.style.display = 'none';
    
    // Parse sort parameters
    const [sortBy, sortOrder] = currentSort.split('_');
    const actualSortBy = sortBy === 'score' ? 'overall_score' : sortBy;
    
    // Build query parameters
    const params = new URLSearchParams({
        page: currentPage,
        per_page: 10,
        sort_by: actualSortBy,
        sort_order: sortOrder
    });
    
    if (currentFilter) {
        params.append('filter_score', currentFilter);
    }
    
    fetch(`${API_BASE_URL}/api/history?${params}`, {
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
        
        console.log('📊 Scan history response:', data);
        
        // Hide loading state
        if (loadingState) loadingState.style.display = 'none';
        
        if (data.success && data.scan_history && data.scan_history.length > 0) {
            displayScanHistory(data.scan_history);
            updatePagination(data.pagination);
        } else {
            // Show empty state
            if (emptyState) emptyState.style.display = 'block';
            hidePagination();
        }
    })
    .catch(error => {
        console.error('Error loading scan history:', error);
        
        // Hide loading state and show empty state
        if (loadingState) loadingState.style.display = 'none';
        if (emptyState) {
            emptyState.style.display = 'block';
            emptyState.querySelector('p').textContent = 'Failed to load scan history. Please try again.';
        }
        
        showNotification('Failed to load scan history', 'error');
    });
}

function displayScanHistory(scanHistory) {
    const historyList = document.getElementById('scan-history-list');
    if (!historyList) return;
    
    historyList.style.display = 'block';
    historyList.innerHTML = '';
    
    scanHistory.forEach(scan => {
        const scanElement = createScanHistoryElement(scan);
        historyList.appendChild(scanElement);
    });
}

function createScanHistoryElement(scan) {
    const scanDiv = document.createElement('div');
    scanDiv.className = 'scan-history-item';
    
    const scoreCategory = getScoreCategory(scan.match_score);
    const scanDate = new Date(scan.created_at).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
    
    scanDiv.innerHTML = `
        <div class="scan-item-header">
            <div class="scan-item-info">
                <h3 class="scan-item-title">${scan.resume.title || 'Untitled Resume'}</h3>
                <p class="scan-item-subtitle">${scan.job_description.title || 'Untitled Job'} • ${scan.job_description.company_name || 'Unknown Company'}</p>
            </div>
            <div class="scan-item-score">
                <div class="score-circle ${scoreCategory.class}">
                    <span class="score-value">${Math.round(scan.match_score)}%</span>
                </div>
                <span class="score-label">${scoreCategory.label}</span>
            </div>
        </div>
        
        <div class="scan-item-details">
            <div class="detail-item">
                <span class="detail-label">Technical Skills:</span>
                <span class="detail-value">${Math.round(scan.technical_score)}%</span>
            </div>
            <div class="detail-item">
                <span class="detail-label">Soft Skills:</span>
                <span class="detail-value">${Math.round(scan.soft_skills_score)}%</span>
            </div>
            <div class="detail-item">
                <span class="detail-label">Other Keywords:</span>
                <span class="detail-value">${Math.round(scan.other_keywords_score)}%</span>
            </div>
            <div class="detail-item">
                <span class="detail-label">Keywords Matched:</span>
                <span class="detail-value">${scan.matched_keywords}/${scan.total_jd_keywords}</span>
            </div>
        </div>
        
        <div class="scan-item-footer">
            <span class="scan-date">📅 ${scanDate}</span>
            <span class="scan-algorithm">Algorithm: ${scan.algorithm_used}</span>
        </div>
    `;
    
    return scanDiv;
}

function getScoreCategory(score) {
    if (score >= 80) {
        return { label: 'Excellent', class: 'excellent' };
    } else if (score >= 60) {
        return { label: 'Good', class: 'good' };
    } else if (score >= 40) {
        return { label: 'Fair', class: 'fair' };
    } else {
        return { label: 'Poor', class: 'poor' };
    }
}

function updatePagination(pagination) {
    const paginationSection = document.getElementById('pagination-section');
    const paginationInfo = document.getElementById('pagination-info-text');
    const prevBtn = document.getElementById('prev-page');
    const nextBtn = document.getElementById('next-page');
    
    if (!paginationSection) return;
    
    if (pagination.total_pages > 1) {
        paginationSection.style.display = 'block';
        
        // Update info text
        const start = ((pagination.page - 1) * pagination.per_page) + 1;
        const end = Math.min(pagination.page * pagination.per_page, pagination.total_items);
        if (paginationInfo) {
            paginationInfo.textContent = `Showing ${start}-${end} of ${pagination.total_items} results`;
        }
        
        // Update buttons
        if (prevBtn) prevBtn.disabled = !pagination.has_prev;
        if (nextBtn) nextBtn.disabled = !pagination.has_next;
        
        // Update page numbers
        updatePageNumbers(pagination);
    } else {
        paginationSection.style.display = 'none';
    }
}

function updatePageNumbers(pagination) {
    const pageNumbers = document.getElementById('page-numbers');
    if (!pageNumbers) return;
    
    pageNumbers.innerHTML = '';
    
    for (let i = 1; i <= pagination.total_pages; i++) {
        const pageBtn = document.createElement('button');
        pageBtn.className = `page-number ${i === pagination.page ? 'active' : ''}`;
        pageBtn.textContent = i;
        pageBtn.onclick = () => goToPage(i);
        pageNumbers.appendChild(pageBtn);
    }
}

function changePage(direction) {
    currentPage += direction;
    loadScanHistory();
}

function goToPage(page) {
    currentPage = page;
    loadScanHistory();
}

function hidePagination() {
    const paginationSection = document.getElementById('pagination-section');
    if (paginationSection) {
        paginationSection.style.display = 'none';
    }
}

// Utility functions
function clearTokens() {
    localStorage.removeItem('dr_resume_token');
    localStorage.removeItem('dr_resume_refresh_token');
    localStorage.removeItem('dr_resume_user');
}

function logout() {
    clearTokens();
    window.location.href = 'us10_login.html';
}

function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;
    
    // Style the notification
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 12px 24px;
        border-radius: 8px;
        color: white;
        font-weight: 500;
        z-index: 1000;
        transform: translateX(100%);
        transition: transform 0.3s ease;
    `;
    
    // Set background color based on type
    const colors = {
        success: '#10b981',
        error: '#ef4444',
        warning: '#f59e0b',
        info: '#3b82f6'
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
