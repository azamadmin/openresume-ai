// Resume Doctor.Ai - Simple Login JavaScript

document.addEventListener('DOMContentLoaded', function() {
    console.log('🤖 Resume Doctor.Ai Login Page Loaded');
    
    // Check if user is already logged in
    const token = localStorage.getItem('dr_resume_token');
    if (token) {
        verifyTokenAndRedirect();
        return;
    }
    
    // Get form elements
    const form = document.getElementById('loginForm');
    const loginBtn = document.getElementById('loginBtn');
    const alertContainer = document.getElementById('alertContainer');
    
    // Handle form submission
    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        clearAlerts();
        
        const formData = new FormData(form);
        const data = {
            email: formData.get('email').trim(),
            password: formData.get('password')
        };
        
        // Validate form
        const validationErrors = validateForm(data);
        if (validationErrors.length > 0) {
            showAlert('error', 'Please fix the following errors:', validationErrors);
            return;
        }
        
        setLoading(true);
        
        try {
            const response = await fetch(`${API_BASE_URL}/api/login`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data),
                credentials: 'include'
            });
            
            const result = await response.json();
            
            if (result.success) {
                showAlert('success', result.message);
                
                // Store tokens
                localStorage.setItem('dr_resume_token', result.tokens.access_token);
                localStorage.setItem('dr_resume_refresh_token', result.tokens.refresh_token);
                localStorage.setItem('dr_resume_user', JSON.stringify(result.user));
                
                console.log('✅ Login successful, redirecting...');
                
                // Redirect to dashboard
                setTimeout(() => { 
                    window.location.href = 'us10_dashboard.html'; 
                }, 1000);
                
            } else {
                showAlert('error', result.message);
            }
            
        } catch (error) {
            console.error('Login error:', error);
            showAlert('error', 'Network error. Please check your connection and try again.');
        } finally {
            setLoading(false);
        }
    });
});

// Verify existing token and redirect if valid
async function verifyTokenAndRedirect() {
    try {
        const token = localStorage.getItem('dr_resume_token');
        const response = await fetch(`${API_BASE_URL}/api/profile`, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            credentials: 'include'
        });
        
        if (response.ok) {
            console.log('✅ Valid token found, redirecting to dashboard');
            window.location.href = 'us10_dashboard.html';
        } else {
            console.log('❌ Invalid token, clearing storage');
            clearTokens();
        }
    } catch (error) {
        console.error('Token verification error:', error);
        clearTokens();
    }
}

// Clear stored tokens
function clearTokens() {
    localStorage.removeItem('dr_resume_token');
    localStorage.removeItem('dr_resume_refresh_token');
    localStorage.removeItem('dr_resume_user');
}

// Validate form data
function validateForm(data) {
    const errors = [];
    
    if (!data.email) {
        errors.push('Email is required');
    } else if (!isValidEmail(data.email)) {
        errors.push('Please enter a valid email address');
    }
    
    if (!data.password) {
        errors.push('Password is required');
    }
    
    return errors;
}

// Check if email is valid
function isValidEmail(email) {
    const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
    return emailRegex.test(email);
}

// Show alert message
function showAlert(type, message, errors = []) {
    const alertContainer = document.getElementById('alertContainer');
    
    let alertHTML = `<div class="alert alert-${type}">`;
    alertHTML += `<strong>${message}</strong>`;
    
    if (errors.length > 0) {
        alertHTML += '<ul style="margin: 8px 0 0 20px;">';
        errors.forEach(error => {
            alertHTML += `<li>${error}</li>`;
        });
        alertHTML += '</ul>';
    }
    
    alertHTML += '</div>';
    
    alertContainer.innerHTML = alertHTML;
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

// Clear alert messages
function clearAlerts() {
    document.getElementById('alertContainer').innerHTML = '';
}

// Set loading state
function setLoading(loading) {
    const loginBtn = document.getElementById('loginBtn');
    
    if (loading) {
        loginBtn.disabled = true;
        loginBtn.classList.add('loading');
        loginBtn.textContent = 'Signing In...';
    } else {
        loginBtn.disabled = false;
        loginBtn.classList.remove('loading');
        loginBtn.textContent = 'Login';
    }
}