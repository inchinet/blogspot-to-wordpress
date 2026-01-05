document.getElementById('publishForm').addEventListener('submit', async function (e) {
    e.preventDefault();

    const submitBtn = document.getElementById('submitBtn');
    const statusDiv = document.getElementById('statusMessage');

    // Reset status
    statusDiv.classList.add('hidden');
    statusDiv.classList.remove('success', 'error');
    statusDiv.textContent = '';

    // Loading state
    const originalBtnText = submitBtn.textContent;
    submitBtn.textContent = 'Publishing...';
    submitBtn.disabled = true;

    const data = {
        source_url: document.getElementById('source_url').value,
        wp_url: document.getElementById('wp_url').value,
        username: document.getElementById('username').value,
        password: document.getElementById('password').value
    };

    try {
        const response = await fetch('/publish', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });

        const result = await response.json();

        statusDiv.classList.remove('hidden');

        if (result.success) {
            statusDiv.classList.add('success');
            statusDiv.innerHTML = `Passage is published! <a href="${result.link}" target="_blank" style="color: inherit;">View Post</a>`;
        } else {
            statusDiv.classList.add('error');
            statusDiv.textContent = 'Error: ' + result.message;
        }

    } catch (error) {
        statusDiv.classList.remove('hidden');
        statusDiv.classList.add('error');
        statusDiv.textContent = 'Network or Server Error: ' + error.message;
    } finally {
        submitBtn.textContent = originalBtnText;
        submitBtn.disabled = false;
    }
});
