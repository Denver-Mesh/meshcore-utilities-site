document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById("contacts-form");
    const submitBtn = document.getElementById("submit-btn");

    // Handle form submission
    form.addEventListener("submit", async (e) => {
        e.preventDefault();

        const formData = new FormData(form);
        const data = {};

        // Convert FormData to object, handling checkbox properly
        for (let [key, value] of formData.entries()) {
            data[key] = value;
        }

        // Show loading state
        submitBtn.disabled = true;
        submitBtn.textContent = 'Preparing...';

        try {
            await fetch(form.action, {
                method: "POST",
                headers: {"Content-Type": "application/json"},
                body: JSON.stringify(data),
            })
                .then(response => response.json())
                .then(data => {
                    // Convert JSON to string
                    const jsonString = JSON.stringify(data, null, 2);

                    // Create a blob with the JSON data
                    const blob = new Blob([jsonString], {type: 'application/json'});

                    // Create a temporary download link
                    const url = URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = 'colorado_meshcore_contacts.json';

                    // Trigger download
                    document.body.appendChild(a);
                    a.click();

                    // Cleanup
                    document.body.removeChild(a);
                    URL.revokeObjectURL(url);
                })
                .catch(error => console.error('Error:', error))
                .finally(() => {
                    submitBtn.disabled = false;
                    submitBtn.textContent = 'Download Contacts Pack';
                })
        } catch (error) {
            console.log(error.message);
        }
    });
});
