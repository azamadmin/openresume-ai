// Dr. Resume US-10 Account Settings JavaScript

document.addEventListener('DOMContentLoaded', function() {
    console.log('🩺 Dr. Resume Account Settings Loaded (US-10)');
    
    // Check authentication
    checkAuthentication();
    
    // Load user info
    loadUserInfo();
    
    // Load account information
    loadAccountInfo();
    
    // Set up form handlers
    setupFormHandlers();
});

async function checkAuthentication() {
    const token = localStorage.getItem('dr_resume_token');
    
    if (!token) {
        console.log('❌ No token found, redirecting to login');
        window.location.href = 'us10_login.html';
        return;
    }
    
    try {
        // Verify token by calling protected endpoint
        const response = await fetch(`${API_BASE_URL}/api/profile`, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            credentials: 'include' // Include credentials for CORS
        });
        if (!response.ok) {
            if (response.status === 401) {
                alert('Session expired. Please log in again.');
                localStorage.removeItem('dr_resume_token');
                localStorage.removeItem('dr_resume_refresh_token');
                window.location.href = 'us10_login.html';
                return;
            }
            throw new Error('Token verification failed');
        }
        const result = await response.json();
        if (!result.success) {
            throw new Error('Invalid token response');
        }
        console.log('✅ Token verified successfully');
    } catch (error) {
        console.error('❌ Authentication failed:', error);
        localStorage.removeItem('dr_resume_token');
        localStorage.removeItem('dr_resume_refresh_token');
        window.location.href = '/login';
    }
}

async function loadUserInfo() {
    const token = localStorage.getItem('dr_resume_token');
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/profile`, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            credentials: 'include' // Include credentials for CORS
        });
        
        if (response.ok) {
            const result = await response.json();
            if (result.success && result.user) {
                const user = result.user;
                document.getElementById('welcomeMessage').textContent = `Welcome, ${user.first_name}`;
            }
        }
    } catch (error) {
        console.error('Error loading user info:', error);
    }
}

async function loadAccountInfo() {
    const token = localStorage.getItem('dr_resume_token');
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/account_info`, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            credentials: 'include' // Include credentials for CORS
        });
        
        if (response.ok) {
            const result = await response.json();
            if (result.success && result.user) {
                populateAccountForm(result.user);
            }
        } else {
            showAlert('Failed to load account information', 'error');
        }
    } catch (error) {
        console.error('Error loading account info:', error);
        showAlert('Error loading account information', 'error');
    }
}

function populateAccountForm(user) {
    // Populate personal info form
    document.getElementById('firstName').value = user.first_name || '';
    document.getElementById('lastName').value = user.last_name || '';
    document.getElementById('email').value = user.email || '';
    
    // Populate account status
    document.getElementById('accountType').textContent = user.role ? user.role.charAt(0).toUpperCase() + user.role.slice(1) : 'Basic';
    document.getElementById('memberSince').textContent = user.created_at ? formatDate(user.created_at) : '-';
    document.getElementById('lastLogin').textContent = user.last_login ? formatDate(user.last_login) : 'Never';
    document.getElementById('totalResumes').textContent = user.resume_count || 0;
    
    // Show upgrade section if user is basic
    if (user.role === 'basic') {
        document.getElementById('upgradeSection').style.display = 'block';
    }
}

function setupFormHandlers() {
    // Personal info form
    document.getElementById('personalInfoForm').addEventListener('submit', handlePersonalInfoUpdate);
    
    // Password form
    document.getElementById('passwordForm').addEventListener('submit', handlePasswordChange);
    
    // Delete form
    document.getElementById('deleteForm').addEventListener('submit', function(e) {
        e.preventDefault();
        deleteAccount();
    });
}

async function handlePersonalInfoUpdate(event) {
    event.preventDefault();
    
    const formData = new FormData(event.target);
    const data = Object.fromEntries(formData.entries());
    
    // Remove empty current_password if no email change
    const originalEmail = document.getElementById('email').defaultValue;
    if (data.email === originalEmail && !data.current_password) {
        delete data.current_password;
    }
    
    const token = localStorage.getItem('dr_resume_token');
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/update_account`, {
            method: 'PUT',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data),
            credentials: 'include' // Include credentials for CORS
        });
        
        const result = await response.json();
        
        if (result.success) {
            showAlert('Account information updated successfully!', 'success');
            // Clear password field
            document.getElementById('currentPasswordInfo').value = '';
            // Reload account info
            loadAccountInfo();
        } else {
            showAlert(result.message || 'Failed to update account information', 'error');
        }
        
    } catch (error) {
        console.error('Error updating account:', error);
        showAlert('Error updating account information', 'error');
    }
}

async function handlePasswordChange(event) {
    event.preventDefault();
    
    const formData = new FormData(event.target);
    const data = Object.fromEntries(formData.entries());
    
    // Validate password confirmation
    if (data.new_password !== data.confirm_password) {
        showAlert('New password and confirmation do not match', 'error');
        return;
    }
    
    const token = localStorage.getItem('dr_resume_token');
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/change_password`, {
            method: 'PUT',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data),
            credentials: 'include' // Include credentials for CORS
        });
        
        const result = await response.json();
        
        if (result.success) {
            showAlert('Password changed successfully!', 'success');
            // Clear form
            document.getElementById('passwordForm').reset();
        } else {
            showAlert(result.message || 'Failed to change password', 'error');
        }
        
    } catch (error) {
        console.error('Error changing password:', error);
        showAlert('Error changing password', 'error');
    }
}

function resetPersonalInfo() {
    loadAccountInfo(); // Reload original values
    document.getElementById('currentPasswordInfo').value = '';
}

function resetPasswordForm() {
    document.getElementById('passwordForm').reset();
}

function showDeleteConfirmation() {
    document.getElementById('deleteModal').style.display = 'flex';
}

function hideDeleteConfirmation() {
    document.getElementById('deleteModal').style.display = 'none';
    document.getElementById('deleteForm').reset();
}

async function deleteAccount() {
    const password = document.getElementById('deletePassword').value;
    const confirmDeletion = document.getElementById('confirmDeletion').checked;
    
    if (!password) {
        showAlert('Password is required', 'error');
        return;
    }
    
    if (!confirmDeletion) {
        showAlert('Please confirm that you understand this action cannot be undone', 'error');
        return;
    }
    
    const token = localStorage.getItem('dr_resume_token');
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/delete_account`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                password: password,
                confirm_deletion: confirmDeletion
            }),
            credentials: 'include' // Include credentials for CORS
        });
        
        const result = await response.json();
        
        if (result.success) {
            showAlert('Account has been deactivated. You will be logged out.', 'success');
            setTimeout(() => {
                logout();
            }, 2000);
        } else {
            showAlert(result.message || 'Failed to delete account', 'error');
        }
        
    } catch (error) {
        console.error('Error deleting account:', error);
        showAlert('Error deleting account', 'error');
    }
}

function upgradeToPremium() {
    showAlert('Premium upgrade feature coming soon!', 'info');
}

function logout() {
    localStorage.removeItem('dr_resume_token');
    localStorage.removeItem('dr_resume_refresh_token');
    window.location.href = '/login';
}

function showAlert(message, type = 'info') {
    const alertContainer = document.getElementById('alertContainer');
    
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type}`;
    alertDiv.innerHTML = `
        <span>${message}</span>
        <button class="alert-close" onclick="this.parentElement.remove()">&times;</button>
    `;
    
    alertContainer.appendChild(alertDiv);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (alertDiv.parentElement) {
            alertDiv.remove();
        }
    }, 5000);
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });
}
