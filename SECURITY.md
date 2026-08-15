# Security Policy

The SkyBound engineering team takes the security of the Flight Management System and user data seriously.

---

## Supported Versions

Security fixes and patches are actively applied to the following release tracks:

| Version | Supported          | Status      |
| ------- | ------------------ | ----------- |
| 1.0.x   | :white_check_mark: | Active      |
| < 1.0   | :x:                | Unsupported |

---

## Reporting a Vulnerability

If you discover a security vulnerability or suspect a potential security flaw in this project:

1. **Do not create a public issue.** Please avoid disclosing potential vulnerabilities publicly.
2. **Contact the maintainers:** Email security details and reproduction steps to `security@skybound.aero` or open a private advisory on GitHub.
3. **Include details:**
   - Detailed description of the vulnerability.
   - Steps to reproduce the issue.
   - Affected system components (Django WSGI engine, standalone HTTP server, SQLite storage, etc.).
   - Proof of Concept (PoC) scripts or HTTP payloads if applicable.

---

## Response Timeline

- **Initial Acknowledgement:** Within 48 hours of initial report.
- **Triage & Assessment:** Within 5 business days.
- **Fix & Disclosure:** Coordinated release and advisory publication following confirmation of fix.

---

## Security Best Practices for Deployment

- **Secret Keys:** Never commit production `.env` files or secret keys to source control.
- **Debug Mode:** Always set `DEBUG=False` in production environments.
- **Database Safety:** Ensure appropriate file permissions on the `db.sqlite3` database file.
- **Transport Security:** Run behind a TLS/HTTPS reverse proxy (e.g., Nginx, Caddy, Cloudflare) for production deployments.
