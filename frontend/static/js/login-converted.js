// Login Form Converted from React to Vanilla JavaScript

let loading = false;

// Initialize the login form
document.addEventListener('DOMContentLoaded', function() {
    setupEventListeners();
});

function setupEventListeners() {
    const loginForm = document.getElementById('loginForm');
    const alertClose = document.getElementById('alertClose');

    // Form submission
    loginForm.addEventListener('submit', handleSubmit);

    // Alert close button
    alertClose.addEventListener('click', hideAlert);

    // Real-time validation
    const emailInput = document.getElementById('email');
    const passwordInput = document.getElementById('password');

    emailInput.addEventListener('blur', function() {
        validateEmail(this.value);
    });

    passwordInput.addEventListener('input', function() {
        if (this.value.length > 0) {
            hideAlert();
        }
    });
}

async function handleSubmit(e) {
    e.preventDefault();
    
    const email = document.getElementById('email').value.trim();
    const password = document.getElementById('password').value.trim();
    
    // Basic validation
    if (!email || !password) {
        showAlert('error', 'Please fill in all fields');
        return;
    }

    if (!isValidEmail(email)) {
        showAlert('error', 'Please enter a valid email address');
        return;
    }

    setLoading(true);
    hideAlert();

    try {
        // Simulate API call
        await new Promise(resolve => setTimeout(resolve, 1500));
        
        // Simulate login logic
        const success = await performLogin(email, password);
        
        if (success) {
            showAlert('success', 'Login successful! Redirecting...');
            
            // Redirect after success message
            setTimeout(() => {
                window.location.href = 'dashboard-react-converted.html';
            }, 2000);
        } else {
            showAlert('error', 'Invalid email or password. Please try again.');
        }
        
    } catch (error) {
        showAlert('error', 'Login failed. Please try again.');
    } finally {
        setLoading(false);
    }
}

async function performLogin(email, password) {
    // This would typically make an API call to your backend
    // For demo purposes, we'll simulate a successful login
    
    // Simulate some basic validation
    if (email === 'demo@resumedoctor.ai' && password === 'demo123') {
        // Store token (in real app, this would come from backend)
        localStorage.setItem('access_token', 'demo_token_' + Date.now());
        localStorage.setItem('user_email', email);
        return true;
    }
    
    // For demo, accept any valid email format
    if (isValidEmail(email) && password.length >= 6) {
        localStorage.setItem('access_token', 'demo_token_' + Date.now());
        localStorage.setItem('user_email', email);
        return true;
    }
    
    return false;
}

function validateEmail(email) {
    if (email && !isValidEmail(email)) {
        showAlert('error', 'Please enter a valid email address');
        return false;
    }
    return true;
}

function isValidEmail(email) {
    const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
    return emailRegex.test(email);
}

function showAlert(type, message) {
    const alertBox = document.getElementById('alertBox');
    const alertMessage = document.getElementById('alertMessage');
    
    alertBox.className = `alert ${type}`;
    alertMessage.textContent = message;
    alertBox.classList.remove('hidden');
}

function hideAlert() {
    const alertBox = document.getElementById('alertBox');
    alertBox.classList.add('hidden');
}

function setLoading(isLoading) {
    loading = isLoading;
    const loginButton = document.getElementById('loginButton');
    const emailInput = document.getElementById('email');
    const passwordInput = document.getElementById('password');
    
    if (isLoading) {
        loginButton.disabled = true;
        loginButton.classList.add('loading');
        loginButton.textContent = 'Signing In...';
        emailInput.disabled = true;
        passwordInput.disabled = true;
    } else {
        loginButton.disabled = false;
        loginButton.classList.remove('loading');
        loginButton.textContent = 'Login';
        emailInput.disabled = false;
        passwordInput.disabled = false;
    }
}

// Check if user is already logged in
function checkAuthStatus() {
    const token = localStorage.getItem('access_token');
    if (token) {
        // Redirect to dashboard if already logged in
        window.location.href = 'dashboard-react-converted.html';
    }
}

// Export functions for potential external use
window.LoginApp = {
    handleSubmit,
    performLogin,
    isValidEmail,
    showAlert,
    hideAlert,
    setLoading,
    checkAuthStatus
};

// Check auth status on load
checkAuthStatus();