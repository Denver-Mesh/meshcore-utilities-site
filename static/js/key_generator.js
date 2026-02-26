// noble-ed25519 library reference (loaded dynamically)
let nobleEd25519 = null;

// Load noble-ed25519 library with cascading fallbacks
async function loadNobleEd25519() {
    if (nobleEd25519) return nobleEd25519;

    const sources = [
        'https://cdn.skypack.dev/noble-ed25519',
        'https://unpkg.com/noble-ed25519@latest/esm/index.js',
        'https://cdn.jsdelivr.net/npm/noble-ed25519@latest/esm/index.js',
        './noble-ed25519-offline-simple.js'
    ];

    for (const src of sources) {
        try {
            nobleEd25519 = await import(src);
            console.log(`✓ noble-ed25519 loaded from: ${src}`);
            return nobleEd25519;
        } catch (e) {
            // Silently try next source
        }
    }

    throw new Error('Failed to load Ed25519 library from all sources');
}

// Generate a MeshCore-compatible Ed25519 keypair (RFC 8032 compliant)
async function generateMeshCoreKeypair() {
    await loadNobleEd25519();

    // Step 1: Generate 32-byte random seed
    const seed = crypto.getRandomValues(new Uint8Array(32));

    // Step 2: Hash the seed with SHA-512
    const digest = await crypto.subtle.digest('SHA-512', seed);
    const digestArray = new Uint8Array(digest);

    // Step 3: Clamp the first 32 bytes according to Ed25519 rules
    const clamped = new Uint8Array(digestArray.slice(0, 32));
    clamped[0] &= 248;   // Clear bottom 3 bits
    clamped[31] &= 63;   // Clear top 2 bits
    clamped[31] |= 64;   // Set bit 6

    // Step 4: Generate public key using Point.BASE.multiply (no double clamping)
    let publicKey;
    try {
        // Convert scalar to BigInt for Point.BASE.multiply
        let scalarBigInt = 0n;
        for (let i = 0; i < 32; i++) {
            scalarBigInt += BigInt(clamped[i]) << BigInt(8 * i);
        }
        publicKey = nobleEd25519.Point.BASE.multiply(scalarBigInt);
    } catch (error) {
        // Fallback to getPublicKey if Point.BASE.multiply fails
        try {
            publicKey = await nobleEd25519.getPublicKey(clamped);
        } catch (fallbackError) {
            publicKey = nobleEd25519.getPublicKey(clamped);
        }
    }

    // Convert public key to Uint8Array
    let publicKeyBytes;
    if (publicKey instanceof Uint8Array) {
        publicKeyBytes = publicKey;
    } else if (publicKey.toRawBytes) {
        publicKeyBytes = publicKey.toRawBytes();
    } else if (publicKey.toBytes) {
        publicKeyBytes = publicKey.toBytes();
    } else if (publicKey.x !== undefined && publicKey.y !== undefined) {
        // Point object with x, y coordinates - convert to compressed format
        publicKeyBytes = new Uint8Array(32);
        const y = publicKey.y;
        const x = publicKey.x;
        for (let i = 0; i < 31; i++) {
            publicKeyBytes[i] = Number((y >> BigInt(8 * i)) & 255n);
        }
        publicKeyBytes[31] = Number((x & 1n) << 7);
    } else {
        throw new Error('Unsupported public key format from noble-ed25519');
    }

    // Step 5: Create 64-byte private key: [clamped_scalar][sha512_second_half]
    const meshcorePrivateKey = new Uint8Array(64);
    meshcorePrivateKey.set(clamped, 0);
    meshcorePrivateKey.set(digestArray.slice(32, 64), 32);

    return {
        publicKey: publicKeyBytes,
        privateKey: meshcorePrivateKey
    };
}

// Convert bytes to hex
function toHex(bytes) {
    return Array.from(bytes)
        .map(b => b.toString(16).padStart(2, '0'))
        .join('')
        .toUpperCase();
}

// Key generation with prefix matching
async function generateKeyForPrefix(prefix) {
    const targetPrefix = prefix.toUpperCase();

    let attempts = 0;
    const startTime = Date.now();

    // Pre-load the library
    await loadNobleEd25519();

    while (true) {
        attempts++;

        try {
            const keypair = await generateMeshCoreKeypair();
            const publicKeyHex = toHex(keypair.publicKey);

            // Check if it matches the target prefix
            if (publicKeyHex.startsWith(targetPrefix)) {
                const elapsedTime = ((Date.now() - startTime) / 1000).toFixed(2);
                return {
                    publicKey: publicKeyHex,
                    privateKey: toHex(keypair.privateKey),
                    attempts: attempts,
                    timeSeconds: elapsedTime
                };
            }

            // Update progress every 100 attempts
            if (attempts % 100 === 0) {
                const elapsed = (Date.now() - startTime) / 1000;
                const rate = Math.floor(attempts / elapsed);
                updateKeygenProgress(attempts, rate);
            }
        } catch (error) {
            console.error('Key generation error:', error);
            continue;
        }
    }
}

function updateKeygenProgress(attempts, rate) {
    const progressEl = document.getElementById('keygen-progress');
    if (progressEl) {
        progressEl.textContent = `Attempts: ${attempts. toLocaleString()} | Speed: ${rate.toLocaleString()}/sec`;
    }
}

// Show keygen modal
function showKeygenModal(hexId) {
    const modal = document. getElementById('hex-modal');
    const modalBody = document.getElementById('hex-modal-body');

    modalBody.innerHTML = `
        <div class="hex-info-card">
            <div class="hex-info-header">
                <span class="hex-id-badge hex-free-badge">${hexId}</span>
                <span class="hex-state-badge hex-state-available">Available</span>
            </div>
            <h2 class="hex-info-title">Generate Private Key</h2>
            <p class="hex-keygen-description">
                Generate a MeshCore-compatible Ed25519 keypair with this ID prefix.
            </p>
            <div class="hex-info-contact" id="button-container">
                <button id="generate-key-btn" class="hex-contact-btn">🔑 Generate Key</button>
            </div>
            <div id="keygen-status" style="margin-top: 12px; display: none;">
                <p id="keygen-progress"></p>
            </div>
            <div id="keygen-result" style="display: none; margin-top: 12px;">
                <div class="hex-keygen-results">
                    <div class="hex-key-section">
                        <div class="hex-key-header">
                            <span class="hex-info-label">🔑 Public Key</span>
                            <button onclick="copyToClipboard(event, 'public-key-output')" class="copy-btn-inline">📋 Copy</button>
                        </div>
                        <div id="public-key-output" class="key-output-condensed" onclick="toggleKeyExpansion('public-key-output')" title="Click to expand/collapse"></div>
                    </div>
                    <div class="hex-key-section">
                        <div class="hex-key-header">
                            <span class="hex-info-label">🔐 Private Key</span>
                            <button onclick="copyToClipboard(event, 'private-key-output')" class="copy-btn-inline">📋 Copy</button>
                        </div>
                        <div id="private-key-output" class="key-output-condensed" onclick="toggleKeyExpansion('private-key-output')" title="Click to expand/collapse"></div>
                    </div>
                </div>
                <div class="hex-key-stats-inline">
                    <span id="keygen-stats"></span>
                </div>
            </div>
            <div class="hex-keygen-footer">
                <span class="hex-keygen-credit">Based on <a href="https://github.com/agessaman/meshcore-web-keygen" target="_blank">github.com/agessaman/meshcore-web-keygen</a></span>
            </div>
        </div>
    `;

    modal.style.display = 'block';

    // Attach event listener to generate button
    document.getElementById('generate-key-btn').addEventListener('click', async () => {
        const btn = document.getElementById('generate-key-btn');
        btn.disabled = true;
        btn.textContent = '⏳ Generating...';

        document.getElementById('keygen-status').style.display = 'block';

        try {
            const result = await generateKeyForPrefix(hexId);

            // Show results
            document.getElementById('keygen-status').style.display = 'none';
            document.getElementById('keygen-result').style.display = 'block';

            const pubKeyEl = document.getElementById('public-key-output');
            pubKeyEl.dataset.fullKey = result.publicKey;
            pubKeyEl.textContent = result.publicKey.substring(0, 8) + '...' + result.publicKey.substring(result.publicKey.length - 8);

            const privKeyEl = document.getElementById('private-key-output');
            privKeyEl.dataset.fullKey = result.privateKey;
            privKeyEl.textContent = result.privateKey.substring(0, 8) + '...' + result.privateKey.substring(result.privateKey.length - 8);

            document.getElementById('keygen-stats').textContent =
                `✓ Generated in ${result.timeSeconds}s (${result.attempts.toLocaleString()} attempts)`;

            // Add download button next to generate button
            const buttonContainer = document.getElementById('button-container');
            buttonContainer.innerHTML = `
                <button id="generate-key-btn" class="hex-contact-btn">🔑 Generate Key</button>
                <button onclick="downloadKeyJSON('${hexId}')" class="hex-contact-btn">💾 Download</button>
            `;

            // Re-attach event listener to new generate button
            document.getElementById('generate-key-btn').addEventListener('click', async () => {
                const btn = document.getElementById('generate-key-btn');
                btn.disabled = true;
                btn.textContent = '⏳ Generating...';

                document.getElementById('keygen-status').style.display = 'block';

                try {
                    const result = await generateKeyForPrefix(hexId);

                    // Show results
                    document.getElementById('keygen-status').style.display = 'none';
                    document.getElementById('keygen-result').style.display = 'block';

                    const pubKeyEl2 = document.getElementById('public-key-output');
                    pubKeyEl2.dataset.fullKey = result.publicKey;
                    pubKeyEl2.textContent = result.publicKey.substring(0, 8) + '...' + result.publicKey.substring(result.publicKey.length - 8);

                    const privKeyEl2 = document.getElementById('private-key-output');
                    privKeyEl2.dataset.fullKey = result.privateKey;
                    privKeyEl2.textContent = result.privateKey.substring(0, 8) + '...' + result.privateKey.substring(result.privateKey.length - 8);

                    document.getElementById('keygen-stats').textContent =
                        `✓ Generated in ${result.timeSeconds}s (${result.attempts.toLocaleString()} attempts)`;

                    // Re-enable generate button
                    btn.disabled = false;
                    btn.textContent = '🔑 Generate Key';

                    // Store for download
                    window.generatedKey = result;
                } catch (error) {
                    alert('Error generating key: ' + error.message);
                    btn.disabled = false;
                    btn.textContent = '🔑 Generate Key';
                    document.getElementById('keygen-status').style.display = 'none';
                }
            });

            // Store for download
            window.generatedKey = result;
        } catch (error) {
            alert('Error generating key: ' + error.message);
            btn.disabled = false;
            btn.textContent = '🔑 Generate Key';
            document.getElementById('keygen-status').style.display = 'none';
        }
    });
}

function toggleKeyExpansion(elementId) {
    const element = document.getElementById(elementId);
    const fullKey = element.dataset.fullKey;

    if (element.classList.contains('expanded')) {
        // Collapse to condensed view
        element.textContent = fullKey.substring(0, 8) + '...' + fullKey.substring(fullKey.length - 8);
        element.classList.remove('expanded');
    } else {
        // Expand to full view
        element.textContent = fullKey;
        element.classList.add('expanded');
    }
}

function copyToClipboard(event, elementId) {
    const element = document.getElementById(elementId);
    const textToCopy = element.dataset.fullKey || element.textContent;
    const btn = event.target;

    // Try modern clipboard API first, fall back to textarea method
    if (navigator.clipboard && window.isSecureContext) {
        navigator.clipboard.writeText(textToCopy).then(() => {
            showCopyFeedback();
        }).catch(() => {
            fallbackCopy(textToCopy);
        });
    } else {
        fallbackCopy(textToCopy);
    }

    function fallbackCopy(text) {
        const textarea = document.createElement('textarea');
        textarea.value = text;
        textarea.style.position = 'fixed';
        textarea.style.left = '-9999px';
        document.body.appendChild(textarea);
        textarea.select();
        try {
            document.execCommand('copy');
            showCopyFeedback();
        } catch (err) {
            console.error('Failed to copy:', err);
            alert('Failed to copy to clipboard');
        }
        document.body.removeChild(textarea);
    }

    function showCopyFeedback() {
        const originalText = btn.textContent;
        btn.textContent = '✓ Copied!';
        setTimeout(() => {
            btn.textContent = originalText;
        }, 2000);
    }
}

function downloadKeyJSON(prefix) {
    if (!window.generatedKey) return;

    const data = {
        public_key: window.generatedKey.publicKey,
        private_key: window.generatedKey. privateKey,
        generated_at: new Date().toISOString(),
        prefix: prefix
    };

    const json = JSON.stringify(data, null, 2);
    const blob = new Blob([json], { type: 'application/json' });
    const url = URL. createObjectURL(blob);

    const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, -5);
    const filename = `meshcore_${prefix}_${timestamp}.json`;

    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.click();

    URL.revokeObjectURL(url);
}
