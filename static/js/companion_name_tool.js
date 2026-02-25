document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById("companion-form");
    const submitBtn = document.getElementById("submit-btn");
    const validationError = document.getElementById("validation-error");
    const handleInput = document.getElementById('handle');
    const emojiInput = document.getElementById('emoji');
    const resultDiv = document.getElementById('result');

    // Suffix strategy elements
    const strategyRadios = document.querySelectorAll('input[name="suffix_strategy"]');
    const suffixStrategy = document.getElementById('suffix-strategy');
    const numberInput = document.getElementById('number-input');
    const roleTypeSelect = document.getElementById('role-type-select');
    const suffixNumberInput = document.getElementById('suffix-number');

    // Handle suffix strategy changes
    strategyRadios.forEach(radio => {
        radio.addEventListener('change', function() {
            suffixStrategy.style.display = 'none';
            numberInput.style.display = 'none';
            roleTypeSelect.value = '';
            suffixNumberInput.value = '';

            if (this.value === 'role') {
                suffixStrategy.style.display = 'block';
            } else if (this.value === 'number') {
                numberInput.style.display = 'block';
            }
            // 'publickey' has no additional input needed

            validateForm();
        });
    });

    // Validate form on input changes
    function validateForm() {
        const isHandleValid = handleInput.value.trim() !== '';
        const selectedStrategy = document.querySelector('input[name="suffix_strategy"]:checked');
        let isStrategyValid = !!selectedStrategy;

        if (isStrategyValid && selectedStrategy.value === 'role') {
            isStrategyValid = roleTypeSelect.value !== '';
        } else if (isStrategyValid && selectedStrategy.value === 'number') {
            isStrategyValid = suffixNumberInput.value !== '';
        }

        // Check that if number strategy is selected, the number is between 1 and 99
        const numberInput = document.getElementById('suffix-number');
        if (numberInput.offsetParent !== null) { // Check if visible
            const value = parseInt(numberInput.value);
            if (isNaN(value) || value < 1 || value > 99) {
                e.preventDefault();alert('Please enter a number between 1 and 99');
            }
        }

        // Update visual feedback
        handleInput.classList.toggle('invalid', !isHandleValid);

        // Enable/disable submit button
        const isFormValid = isHandleValid && isStrategyValid;
        submitBtn.disabled = !isFormValid;

        return isFormValid;
    }

    // Add event listeners for real-time validation
    handleInput.addEventListener('input', validateForm);
    roleTypeSelect.addEventListener('change', validateForm);
    suffixNumberInput.addEventListener('input', validateForm);
    suffixNumberInput.addEventListener('input', function(e) {
        if (this.value > 99) {
            this.value = 99;
        }
        if (this.value < 1 && this.value !== '') {
            this.value = 1;
        }
    });

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

        // Create generate keys button
        const generateKeysLink = document.createElement('a');
        generateKeysLink.href = `https://gessaman.com/mc-keygen/?prefix=${data.public_key_id}`;
        generateKeysLink.target = '_blank';
        generateKeysLink.className = 'generate-keys-btn';
        generateKeysLink.textContent = 'Generate Public & Private Keys →';
        content.appendChild(generateKeysLink);

        // Create explanation field for keys
        const explanationField = document.createElement('div');
        explanationField.className = 'explanation-box';
        explanationField.innerHTML = '<p>Paste your public and private key below to include it in your configuration file.</p><p><strong>NOTE:</strong> These values will remain local and will <strong>NOT</strong> be transmitted or stored.</p>';
        content.appendChild(explanationField);


        // Create public key input field
        const publicKeyField = createKeyInputField('Public Key:', 'public-key-input', 'Paste your public key here');
        content.appendChild(publicKeyField);

        // Create private key input field
        const privateKeyField = createKeyInputField('Private Key:', 'private-key-input', 'Paste your private key here');
        content.appendChild(privateKeyField);

        // Create key update steps
        const keyUpdateSteps = document.createElement('div');
        keyUpdateSteps.className = 'explanation-box';
        function updateKeySteps() {
            keyUpdateSteps.innerHTML = `<p><strong>To update your keys:</strong></p><ol><li>Download your configuration file below and copy it to your phone.</li><li>Open the MeshCore app on your phone and connect your companion device.</li><li>Click the gear icon (⚙️) and scroll down to "Import Config" under "Extra Tools".</li><li>Select the JSON file you downloaded, then check "Name", "Private Identity Key" and "Radio Settings". Make sure all other settings are unchecked.</li><li>Click the check icon (✔️) at the top of the screen to apply the settings.</li></ol><p>This process will update your device's name, public key and private key, effectively giving it a new identity on the mesh.</p>`;
        }
        content.appendChild(keyUpdateSteps);

        // Create actions section
        const actions = document.createElement('div');
        actions.className = 'result-actions';

        const downloadBtn = document.createElement('button');
        downloadBtn.type = 'button';
        downloadBtn.className = 'download-btn';
        downloadBtn.textContent = '⬇ Download Configuration';
        downloadBtn.addEventListener('click', () => {
            const publicKey = document.getElementById('public-key-input').value;
            const privateKey = document.getElementById('private-key-input').value;
            downloadJSON(data.import_json, data.import_json_file_name, publicKey, privateKey);
        });

        actions.appendChild(downloadBtn);
        content.appendChild(actions);

        // Append everything to result div
        resultDiv.appendChild(header);
        resultDiv.appendChild(content);
        resultDiv.style.display = 'block';
        resultDiv.scrollIntoView({ behavior: 'smooth', block: 'nearest' });

        // Trigger private key steps update
        updateKeySteps();
        document.getElementById('private-key-input').addEventListener('input', updateKeySteps);
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

    function createKeyInputField(labelText, id, placeholder) {
        const field = document.createElement('div');
        field.className = 'result-field';

        const label = document.createElement('label');
        label.textContent = labelText;

        const input = document.createElement('textarea');
        input.id = id;
        input.className = 'key-input';
        input.placeholder = placeholder;

        field.appendChild(label);
        field.appendChild(input);

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

    function downloadJSON(importJson, fileName, publicKey, privateKey) {
        // Create a copy of import_json to avoid modifying the original
        const jsonData = JSON.parse(JSON.stringify(importJson));

        // Add keys if provided
        if (publicKey.trim()) {
            jsonData.public_key = publicKey.trim();
        }
        if (privateKey.trim()) {
            jsonData.private_key = privateKey.trim();
        }

        const jsonString = JSON.stringify(jsonData, null, 2);
        const blob = new Blob([jsonString], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `${fileName}.json`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(url);
    }
});
