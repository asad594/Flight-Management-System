# Contributing to SkyBound Flight Management System

Thank you for your interest in contributing to the SkyBound Flight Management System! We welcome code contributions, documentation improvements, issue reports, and design pattern refinements.

---

## 1. Code of Conduct

All contributors and maintainers are expected to uphold a respectful, inclusive, and collaborative environment.

---

## 2. Development Setup

### Prerequisites
- **Python 3.8+** (Python 3.10+ recommended)
- **Git**
- **SQLite3**

### Getting Started

1. **Clone the repository:**
   ```bash
   git clone https://github.com/asad594/Flight-Management-System.git
   cd Flight-Management-System
   ```

2. **Create and activate a virtual environment:**
   ```bash
   # Windows (PowerShell)
   python -m venv venv
   .\venv\Scripts\Activate.ps1

   # macOS / Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Configure environment settings:**
   ```bash
   cp .env.example .env
   ```

4. **Initialize demo data:**
   ```bash
   python seed_data.py
   ```

5. **Run the application:**
   - **Pure-Python Engine:**
     ```bash
     python server.py
     ```
   - **Django WSGI Engine:**
     ```bash
     python manage.py runserver
     ```

---

## 3. Running Tests

Always ensure all unit tests pass before submitting changes:

```bash
# Run tests with Django test runner
python manage.py test

# Or run tests using pytest
pytest
```

---

## 4. Coding Standards

- **PEP 8 Compliance**: Follow PEP 8 style rules for Python code formatting.
- **Type Annotations**: Include type hints (`typing`) on domain models, factory methods, and public functions.
- **Docstrings**: Provide PEP 257 compliant docstrings explaining function inputs, outputs, and design pattern roles.
- **Design Pattern Integrity**: When modifying core features, adhere to the architectural design patterns:
  - **Singleton**: `core/singleton.py`
  - **Strategy**: `core/strategies.py`
  - **Observer**: `core/observers.py`
  - **Factory**: `core/factories.py`

---

## 5. Branching & Commit Conventions

### Branch Naming
- `feature/<feature-name>` for new features
- `fix/<bug-name>` for bug fixes
- `docs/<topic>` for documentation improvements
- `refactor/<topic>` for code restructuring

### Commit Message Format
We follow the **Conventional Commits** specification:

```
<type>(<scope>): <short summary>

[optional body]
```

**Types:**
- `feat`: A new feature
- `fix`: A bug fix
- `docs`: Documentation updates
- `style`: Formatting, missing semicolons, etc. (no code logic change)
- `refactor`: Refactoring production code without changing behavior
- `test`: Adding or correcting tests
- `chore`: Build processes, tooling configs, or auxiliary tools
