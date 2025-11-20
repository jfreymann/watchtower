# Security Policy

Watchtower is designed with a strong security posture, but no system is perfect.
We take security issues seriously and appreciate responsible disclosure.


### 🔐 Supported Versions

| Version | Supported |
|--------|-----------|
| main   | ✔ Fully supported |
| tags   | ✔ Supported for 6 months after release |

Older or unmaintained branches may not receive security patches.

---

### 📣 Reporting a Vulnerability

If you believe you’ve discovered a security vulnerability in Watchtower, please **DO NOT open a public GitHub issue**.

Instead, email:

**📨 jfreymann@gmail.com**

Your report should include:

- Description of the issue
- Steps to reproduce
- Impact assessment
- Version or commit of Watchtower
- Suggested remediation (if available)

We will acknowledge receipt within **72 hours** and aim to provide a fix or mitigation within **7 days**, depending on severity.

---

### 🛡 Disclosure Policy

We follow responsible disclosure practices:

- You give us reasonable time to investigate and patch
- We coordinate a disclosure timeline with you
- You may publicly discuss the issue once patched
- Severe issues may require longer timelines

---

### ✔ Safe Harbor

Good-faith security research **will not** be met with legal action.

This includes:

- Attacks against your own Watchtower deployments
- Local or network-based testing
- Fuzzing, scanning, penetration testing
- Reverse engineering for research

NOT allowed:

- Attacking installations you don’t own
- Using vulnerabilities for harmful or unauthorized purposes

---

### 🔧 Security Features in Watchtower

- TLS-required communication
- Token-based authentication for agents
- Admin API keys
- IP-fenced admin surfaces
- systemd sandboxing
- SQLite protected with strict filesystem permissions
- No root processes
- Minimal exposed surface (`/login`, `/healthz`)

---

### ❤️ Thanks

We deeply appreciate security researchers and contributors who help improve the safety of the project.
