document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById("repeater-form");
    const submitBtn = document.getElementById("submit-btn");
    const validationError = document.getElementById("validation-error");
    const landmarkInput = document.getElementById('landmark');
    const nodeTypeSelect = document.getElementById('node-type');
    const resultDiv = document.getElementById('result');

    // Validate form on input changes
    function validateForm() {
        const isLandmarkValid = landmarkInput.value.trim() !== '';
        const isNodeTypeValid = nodeTypeSelect.value !== '';

        // Update visual feedback
        landmarkInput.classList.toggle('invalid', !isLandmarkValid);
        nodeTypeSelect.classList.toggle('invalid', !isNodeTypeValid);

        // Enable/disable submit button
        const isFormValid = isLandmarkValid && isNodeTypeValid;
        submitBtn.disabled = !isFormValid;

        return isFormValid;
    }

    // Add event listeners for real-time validation
    landmarkInput.addEventListener('input', validateForm);
    nodeTypeSelect.addEventListener('change', validateForm);

    // Initial validation check
    validateForm();

    // Handle form submission
    form.addEventListener("submit", async (e) => {
        e.preventDefault();

        // Validate before submission
        if (!validateForm()) {
            validationError.style.display = 'block';
            // Scroll to error message
            validationError.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
            return;
        }

        // Hide validation error if showing
        validationError.style.display = 'none';

        const formData = new FormData(form);
        const data = {};

        // Convert FormData to object, handling checkbox properly
        for (let [key, value] of formData.entries()) {
            data[key] = value;
        }

        // Ensure checkbox is included even if unchecked
        if (!data['is-observer']) {
            data['is-observer'] = 'false';
        }

        // Show loading state
        submitBtn.disabled = true;
        submitBtn.textContent = 'Generating...';

        try {
            const res = await fetch(form.action, {
                method: "POST",
                headers: {"Content-Type": "application/json"},
                body: JSON.stringify(data),
            });

            if (res.ok) {
                const result = await res.json();
                displayResult(result);
            } else {
                throw new Error('Failed to generate configuration');
            }
        } catch (error) {
            displayError(error.message);
        } finally {
            submitBtn.disabled = false;
            submitBtn.textContent = 'Generate Configuration';
        }
    });

    function displayResult(data) {
        // Clear previous content
        resultDiv.innerHTML = '';
        resultDiv.className = 'success';

        // Create header
        const header = document.createElement('div');
        header.className = 'result-header';
        const headerTitle = document.createElement('h2');
        headerTitle.textContent = '✓ Configuration Generated';
        header.appendChild(headerTitle);

        // Create content container
        const content = document.createElement('div');
        content.className = 'result-content';

        // Create node name field
        const nameField = createResultField('Node Name:', data.name, 'node-name');
        content.appendChild(nameField);

        // Create public key ID field
        const keyField = createResultField('Public Key ID:', data.public_key_id, 'public-key-id');
        content.appendChild(keyField);

        // Create actions section
        const actions = document.createElement('div');
        actions.className = 'result-actions';
        const generateKeysLink = document.createElement('a');
        generateKeysLink.href = `https://gessaman.com/mc-keygen/?prefix=${data.public_key_id}`;
        generateKeysLink.target = '_blank';
        generateKeysLink.className = 'generate-keys-btn';
        generateKeysLink.textContent = 'Generate Public & Private Keys →';
        actions.appendChild(generateKeysLink);
        content.appendChild(actions);

        // Append everything to result div
        resultDiv.appendChild(header);
        resultDiv.appendChild(content);
        resultDiv.style.display = 'block';
        resultDiv.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }

    function createResultField(labelText, value, id) {
        const field = document.createElement('div');
        field.className = 'result-field';

        const label = document.createElement('label');
        label.textContent = labelText;

        const valueContainer = document.createElement('div');
        valueContainer.className = 'result-value';

        const code = document.createElement('code');
        code.id = id;
        code.textContent = value;

        const copyBtn = document.createElement('button');
        copyBtn.className = 'copy-btn';
        copyBtn.textContent = 'Copy';
        copyBtn.addEventListener('click', () => copyToClipboard(id));

        valueContainer.appendChild(code);
        valueContainer.appendChild(copyBtn);
        field.appendChild(label);
        field.appendChild(valueContainer);

        return field;
    }

    function displayError(message) {
        // Clear previous content
        resultDiv.innerHTML = '';
        resultDiv.className = 'error';

        // Create error header
        const header = document.createElement('div');
        header.className = 'result-header error';
        const headerTitle = document.createElement('h2');
        headerTitle.textContent = '⚠ Error';
        header.appendChild(headerTitle);

        // Create error content
        const content = document.createElement('div');
        content.className = 'result-content';
        const errorMsg = document.createElement('p');
        errorMsg.textContent = message;
        content.appendChild(errorMsg);

        // Append to result div
        resultDiv.appendChild(header);
        resultDiv.appendChild(content);
        resultDiv.style.display = 'block';
        resultDiv.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }

    function copyToClipboard(elementId) {
        const element = document.getElementById(elementId);
        const text = element.textContent;
        navigator.clipboard.writeText(text).then(() => {
            const button = element.nextElementSibling;
            const originalText = button.textContent;
            button.textContent = 'Copied!';
            button.classList.add('copied');
            setTimeout(() => {
                button.textContent = originalText;
                button.classList.remove('copied');
            }, 2000);
        });
    }

    // Handle dynamic maxlength for landmark input based on city selection
    const citySelect = document.getElementById('city');

    // Set initial landmark details based on the default city selection
    updateLandmarkBasedOnCity();

    // Update maxlength when city changes
    citySelect.addEventListener('change', function() {
        updateLandmarkBasedOnCity();
        validateForm(); // Re-validate after city change
    });

    function updateLandmarkBasedOnCity() {
        const selectedCity = citySelect.value;
        const landmarkLengthSpan = document.getElementById('landmark-length');
        // Clear landmark input if city changes
        landmarkInput.value = '';
        // Change maxlength and update the display based on the selected city
        if (selectedCity === '') {
            landmarkInput.maxLength = 14;
            landmarkLengthSpan.textContent = '14';
        } else {
            landmarkInput.maxLength = 7;
            landmarkLengthSpan.textContent = '7';
        }
    }
});
