// Dashboard Converted from React to Vanilla JavaScript

// Mock data (equivalent to dashboardMockData.ts)
const mockData = {
    user: {
        name: "there",
        greeting: "Hi, there!"
    },
    stats: {
        resumes: 3,
        jobDescriptions: 2,
        scans: 1
    },
    recentScans: [
        {
            id: 1,
            fileName: "Md_Moin_Ashrai_2_1.docx",
            description: "Job Description from Dashboard at 1 Unknown Company",
            timestamp: "2016 212 207-ft6 pm",
            matchPercentage: 28.48,
            keywordCount: 9.55,
            categories: [
                { name: "Tustrated", percentage: 10.34 },
                { name: "Exhilones", percentage: 100 },
                { name: "Office", percentage: 4.35 }
            ]
        }
    ]
};

// DOM Elements
let selectedFile = null;
let uploading = false;

// Initialize the dashboard
document.addEventListener('DOMContentLoaded', function() {
    initializeDashboard();
    setupEventListeners();
    renderScanHistory();
});

function initializeDashboard() {
    // Update user greeting and welcome message
    document.getElementById('userGreeting').textContent = mockData.user.greeting;
    document.getElementById('welcomeTitle').textContent = `Welcome back, ${mockData.user.name}`;
    
    // Update stats
    document.getElementById('resumesCount').textContent = mockData.stats.resumes;
    document.getElementById('jobDescriptionsCount').textContent = mockData.stats.jobDescriptions;
    document.getElementById('scansCount').textContent = mockData.stats.scans;
}

function setupEventListeners() {
    // Navigation buttons
    document.querySelectorAll('.nav-button').forEach(button => {
        button.addEventListener('click', function() {
            document.querySelectorAll('.nav-button').forEach(btn => btn.classList.remove('active'));
            this.classList.add('active');
            console.log(`Navigating to: ${this.textContent.trim()}`);
        });
    });

    // Tab switching for resume upload section
    document.querySelectorAll('.resume-upload-section .tab-button').forEach(button => {
        button.addEventListener('click', function() {
            const tabName = this.dataset.tab;
            switchResumeTab(tabName);
        });
    });

    // Tab switching for job description section
    document.querySelectorAll('.job-description-section .tab-button').forEach(button => {
        button.addEventListener('click', function() {
            const tabName = this.dataset.tab;
            switchJobDescriptionTab(tabName);
        });
    });

    // File input handling
    const fileInput = document.getElementById('fileInput');
    const uploadBtn = document.getElementById('uploadBtn');
    const uploadStatus = document.getElementById('uploadStatus');

    fileInput.addEventListener('change', function(e) {
        if (e.target.files && e.target.files[0]) {
            selectedFile = e.target.files[0];
            uploadBtn.disabled = false;
            uploadStatus.textContent = `Selected: ${selectedFile.name}`;
            uploadStatus.className = 'upload-status';
        }
    });

    // Upload button
    uploadBtn.addEventListener('click', handleUpload);

    // Job description input
    const jobDescriptionInput = document.getElementById('jobDescriptionInput');
    const saveJobBtn = document.getElementById('saveJobBtn');

    jobDescriptionInput.addEventListener('input', function() {
        saveJobBtn.disabled = !this.value.trim();
    });

    saveJobBtn.addEventListener('click', function() {
        const description = jobDescriptionInput.value.trim();
        if (description) {
            console.log('Saving job description:', description);
            // Here you would typically send to backend
            alert('Job description saved and keywords extracted!');
        }
    });

    // Action buttons
    document.getElementById('generateBasicBtn').addEventListener('click', function() {
        console.log('Generating basic suggestions...');
        alert('Generating basic suggestions...');
    });

    document.getElementById('generatePremiumBtn').addEventListener('click', function() {
        console.log('Generating premium suggestions...');
        alert('Generating premium suggestions...');
    });

    // Drag and drop functionality
    const dropZone = document.getElementById('dropZone');
    
    dropZone.addEventListener('dragover', function(e) {
        e.preventDefault();
        this.style.borderColor = '#3b82f6';
        this.style.backgroundColor = 'rgba(59, 130, 246, 0.1)';
    });

    dropZone.addEventListener('dragleave', function(e) {
        e.preventDefault();
        this.style.borderColor = '#cbd5e1';
        this.style.backgroundColor = '';
    });

    dropZone.addEventListener('drop', function(e) {
        e.preventDefault();
        this.style.borderColor = '#cbd5e1';
        this.style.backgroundColor = '';
        
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            const file = files[0];
            if (file.type === 'application/pdf' || 
                file.type === 'application/msword' || 
                file.type === 'application/vnd.openxmlformats-officedocument.wordprocessingml.document') {
                selectedFile = file;
                fileInput.files = files;
                uploadBtn.disabled = false;
                document.getElementById('uploadStatus').textContent = `Selected: ${file.name}`;
            } else {
                alert('Please select a PDF, DOC, or DOCX file.');
            }
        }
    });
}

function switchResumeTab(tabName) {
    // Update tab buttons
    document.querySelectorAll('.resume-upload-section .tab-button').forEach(btn => {
        btn.classList.remove('active');
    });
    document.querySelector(`.resume-upload-section .tab-button[data-tab="${tabName}"]`).classList.add('active');

    // Show/hide tab content
    document.getElementById('uploadTab').classList.toggle('hidden', tabName !== 'upload');
    document.getElementById('selectTab').classList.toggle('hidden', tabName !== 'select');
}

function switchJobDescriptionTab(tabName) {
    // Update tab buttons
    document.querySelectorAll('.job-description-section .tab-button').forEach(btn => {
        btn.classList.remove('active');
    });
    document.querySelector(`.job-description-section .tab-button[data-tab="${tabName}"]`).classList.add('active');

    // Show/hide tab content
    document.getElementById('enterTab').classList.toggle('hidden', tabName !== 'enter');
    document.getElementById('savedTab').classList.toggle('hidden', tabName !== 'saved');
}

async function handleUpload() {
    if (!selectedFile) {
        document.getElementById('uploadStatus').textContent = 'Please select a file to upload.';
        document.getElementById('uploadStatus').className = 'upload-status error';
        return;
    }

    uploading = true;
    const uploadBtn = document.getElementById('uploadBtn');
    const uploadStatus = document.getElementById('uploadStatus');
    
    uploadBtn.disabled = true;
    uploadBtn.textContent = 'Uploading...';
    uploadStatus.textContent = 'Uploading file...';
    uploadStatus.className = 'upload-status';

    try {
        // Simulate API call
        await new Promise(resolve => setTimeout(resolve, 2000));
        
        // Simulate successful upload
        uploadStatus.textContent = 'Resume uploaded and processed successfully!';
        uploadStatus.className = 'upload-status success';
        selectedFile = null;
        document.getElementById('fileInput').value = '';
        
        // Update stats
        mockData.stats.resumes++;
        document.getElementById('resumesCount').textContent = mockData.stats.resumes;
        
    } catch (error) {
        uploadStatus.textContent = 'Upload failed. Please try again.';
        uploadStatus.className = 'upload-status error';
    } finally {
        uploading = false;
        uploadBtn.disabled = true;
        uploadBtn.textContent = 'Upload Resume';
    }
}

function renderScanHistory() {
    const scanHistoryList = document.getElementById('scanHistoryList');
    
    mockData.recentScans.forEach(scan => {
        const scanCard = createScanHistoryCard(scan);
        scanHistoryList.appendChild(scanCard);
    });
}

function createScanHistoryCard(scan) {
    const card = document.createElement('div');
    card.className = 'scan-history-card';
    
    // Determine match percentage class
    let matchClass = 'poor';
    if (scan.matchPercentage >= 80) matchClass = 'excellent';
    else if (scan.matchPercentage >= 60) matchClass = 'good';
    else if (scan.matchPercentage >= 40) matchClass = 'fair';
    
    card.innerHTML = `
        <div class="scan-header">
            <div class="scan-info">
                <div class="scan-file-name">
                    <span class="scan-file-icon">📄</span>
                    ${scan.fileName}
                </div>
                <div class="scan-description">${scan.description}</div>
                <div class="scan-timestamp">${scan.timestamp}</div>
            </div>
            <div class="scan-metrics">
                <div class="match-percentage ${matchClass}">
                    ${scan.matchPercentage}%
                </div>
                <div class="keyword-count">${scan.keywordCount} keywords</div>
            </div>
        </div>
        <div class="category-breakdown">
            ${scan.categories.map(category => `
                <div class="category-item">
                    <div class="category-percentage">${category.percentage}%</div>
                    <div class="category-name">${category.name}</div>
                </div>
            `).join('')}
        </div>
    `;
    
    return card;
}

// Utility functions
function getToken() {
    return localStorage.getItem('access_token');
}

// Export functions for potential external use
window.DashboardApp = {
    initializeDashboard,
    handleUpload,
    renderScanHistory,
    mockData
};