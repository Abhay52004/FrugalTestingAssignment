/**
 * Resilient Closed and Open Shadow DOM Piercing Strategy
 * 
 * 1. Global Interception Hook: Must be injected at document_start (before any scripts run)
 *    to intercept Element.prototype.attachShadow and capture references to closed shadow roots.
 * 2. Pathfinding Engine: Traverses DOM trees recursively, checking standard children,
 *    open shadow roots, and intercepted closed shadow roots.
 */

(function() {
    // WeakMap to securely store references to closed shadow roots mapped to their host elements
    const closedShadowRoots = new WeakMap();

    // 1. Hook into attachShadow to trap closed shadow roots
    const nativeAttachShadow = Element.prototype.attachShadow;
    Element.prototype.attachShadow = function(init) {
        const shadowRoot = nativeAttachShadow.call(this, init);
        if (init && init.mode === 'closed') {
            // Keep a secret reference to the closed shadow root
            closedShadowRoots.set(this, shadowRoot);
        }
        return shadowRoot;
    };

    // Make the registry accessible globally for testing and automation runners
    window.__closedShadowRootsRegistry = closedShadowRoots;

    /**
     * Resilient pathfinding function to locate target elements within deeply nested DOMs
     * (including open/closed shadow roots and dynamically obfuscated host classnames).
     * 
     * @param {Node} root - The starting node (e.g. document or element)
     * @param {Function} predicate - A matcher function: element => boolean
     * @returns {Element|null} - The found element or null
     */
    window.findDeepElement = function(root, predicate) {
        if (!root) return null;

        // If the current element matches the predicate, return it
        if (root.nodeType === Node.ELEMENT_NODE && predicate(root)) {
            return root;
        }

        // 1. Search regular children
        let child = root.firstChild;
        while (child) {
            const found = window.findDeepElement(child, predicate);
            if (found) return found;
            child = child.nextSibling;
        }

        // 2. Search Shadow DOM (if host is an Element)
        if (root.nodeType === Node.ELEMENT_NODE) {
            // Check for open shadow root
            let shadowRoot = root.shadowRoot;

            // If null, check our registry for a closed shadow root
            if (!shadowRoot) {
                shadowRoot = closedShadowRoots.get(root);
            }

            if (shadowRoot) {
                const found = window.findDeepElement(shadowRoot, predicate);
                if (found) return found;
            }
        }

        return null;
    };

    /**
     * Example Usage targeting the specific obfuscated and closed structure:
     * 
     * <enterprise-portal id="root-gateway">
     *   #shadow-root (open)
     *     <payment-terminal class="obfuscated_v4_x89a">
     *       #shadow-root (closed)
     *         <security-sandbox id="iframe-sandbox-wrapper">
     *           #shadow-root (open)
     *             <button class="trigger-finalize" data-qa-state="unlocked-token">Authorize Ledger Funds</button>
     */
    window.locateAuthorizeButton = function() {
        const rootGateway = document.getElementById("root-gateway");
        if (!rootGateway) return null;

        return window.findDeepElement(rootGateway, (element) => {
            // Match criteria based on invariant attributes rather than dynamic classes:
            // - tag name matches 'button'
            // - contains class 'trigger-finalize'
            // - data-qa-state attribute is 'unlocked-token' (or any token state)
            return element.tagName.toLowerCase() === 'button' && 
                   element.classList.contains('trigger-finalize') && 
                   element.getAttribute('data-qa-state') === 'unlocked-token';
        });
    };
})();
