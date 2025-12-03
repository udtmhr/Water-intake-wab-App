document.addEventListener('DOMContentLoaded', () => {
    const settingsModal = document.getElementById('settings-modal');
    const settingsBtn = document.getElementById('settings-btn');
    const closeBtn = document.querySelector('.close');
    const settingsForm = document.getElementById('settings-form');

    const waterLevel = document.getElementById('water-level');
    const currentIntakeEl = document.getElementById('current-intake');
    const dailyGoalEl = document.getElementById('daily-goal');
    const progressPercentageEl = document.getElementById('progress-percentage');

    // Modal Logic
    settingsBtn.onclick = async () => {
        settingsModal.style.display = 'block';
        try {
            const response = await fetch('/api/settings');
            if (response.ok) {
                const data = await response.json();
                if (data.height) document.getElementById('height').value = data.height;
                if (data.weight) document.getElementById('weight').value = data.weight;
                if (data.age) document.getElementById('age').value = data.age;
                if (data.gender) document.getElementById('gender').value = data.gender;
                if (data.line_user_id) document.getElementById('line_user_id').value = data.line_user_id;
            }
        } catch (e) {
            console.error("Failed to fetch settings", e);
        }
    };
    closeBtn.onclick = () => settingsModal.style.display = 'none';
    window.onclick = (event) => {
        if (event.target == settingsModal) {
            settingsModal.style.display = 'none';
        }
    };

    // Request Notification Permission
    if (Notification.permission !== 'granted') {
        Notification.requestPermission();
    }

    // Save Settings
    settingsForm.onsubmit = async (e) => {
        e.preventDefault();
        const formData = new FormData(settingsForm);
        const data = Object.fromEntries(formData.entries());

        // Convert types
        data.height = parseFloat(data.height);
        data.weight = parseFloat(data.weight);
        data.age = parseInt(data.age);

        try {
            const response = await fetch('/api/settings', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });
            const result = await response.json();
            if (response.ok) {
                alert('Settings saved! Goal: ' + result.daily_goal + 'ml');
                settingsModal.style.display = 'none';
                updateStatus();
            } else {
                alert('Error: ' + result.error);
            }
        } catch (error) {
            console.error('Error saving settings:', error);
        }
    };

    // Update Status (Polling)
    async function updateStatus() {
        try {
            const response = await fetch('/api/status');
            if (response.status === 401) {
                window.location.href = '/login';
                return;
            }
            const data = await response.json();

            if (data.configured) {
                dailyGoalEl.textContent = data.daily_goal + ' ml';
                currentIntakeEl.textContent = data.current_intake + ' ml';
                progressPercentageEl.textContent = data.percentage + '%';

                // Update water level animation
                waterLevel.style.height = data.percentage + '%';

                // Check for alert
                if (data.alert) {
                    sendNotification("Time to drink water!");
                }
            } else {
                // Prompt for settings if not configured
                // settingsModal.style.display = 'block'; // Optional: auto-open
            }
        } catch (error) {
            console.error('Error fetching status:', error);
        }
    }

    function sendNotification(message) {
        if (Notification.permission === 'granted') {
            new Notification("Water Intake Tracker", { body: message });
        }
    }

    // Poll every 5 seconds
    setInterval(updateStatus, 5000);
    updateStatus(); // Initial call
});
