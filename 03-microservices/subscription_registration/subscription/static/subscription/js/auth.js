async function submitAddressForm(formData) {
    console.log('Sending API request with data:', formData);
    try {
        let response = await fetch('http://192.168.1.5:7000/api/v1/addresses/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData),
            credentials: 'include',
        });
        console.log('API response status:', response.status);
        if (response.status === 401) {
            console.log('Attempting token refresh');
            const refreshResponse = await fetch('http://192.168.1.5:7000/api/v1/token/refresh/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                credentials: 'include',
            });
            console.log('Refresh response status:', refreshResponse.status);
            if (refreshResponse.ok) {
                response = await fetch('http://192.168.1.5:7000/api/v1/addresses/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(formData),
                    credentials: 'include',
                });
                console.log('Retry API response status:', response.status);
            } else {
                console.error('Token refresh failed:', await refreshResponse.json());
                window.location.href = '/subscription/login/';
                return false;
            }
        }
        const data = await response.json();
        if (response.ok) {
            console.log('Address created:', data);
            return true;
        } else {
            console.error('API error:', data);
            return false;
        }
    } catch (error) {
        console.error('Fetch error:', error);
        return false;
    }
}

document.addEventListener('DOMContentLoaded', () => {
    console.log('auth.js loaded');
    const form = document.getElementById('subscription-form');
    if (form) {
        console.log('Form found');
        form.addEventListener('submit', async (e) => {
            console.log('Submit event triggered');
            e.preventDefault();
            const formData = {
                name: document.getElementById('id_name').value,
                address: document.getElementById('id_address').value,
                postalcode: document.getElementById('id_postalcode').value,
                city: document.getElementById('id_city').value,
                country: document.getElementById('id_country').value,
                email: document.getElementById('id_email').value,
            };
            console.log('Form data:', formData);
            const success = await submitAddressForm(formData);
            if (success) {
                window.location.href = '/success/';
            } else {
                alert('Failed to submit address. Please try again or log in.');
            }
        });
    } else {
        console.error('Form with id="subscription-form" not found');
    }
});