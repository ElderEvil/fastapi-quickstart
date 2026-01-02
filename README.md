# FastAPI Quickstart

🚀 **FastAPI Quickstart** is a package designed to streamline FastAPI development. It includes database management with **SQLModel**, **Alembic migrations**, and a powerful **CLI** for automating common tasks.

## 📌 Features
- **Pre-configured FastAPI setup** with SQLModel
- **Async database support** for PostgreSQL & SQLite
- **Built-in CRUD base** for repository-style development
- **Alembic migration CLI** for managing database migrations
- **CLI commands** for scaffolding models, migrations, and more
- **Fully configurable via environment variables**

---

## ⚡ Installation

### 1️⃣ **Install the package**
```bash
uv pip install fastapi-quickstart
```

### 2️⃣ **Install optional database dependencies**
```bash
# For SQLite support
uv add fastapi-quickstart[sqlite]

# For PostgreSQL (asyncpg) support
uv add fastapi-quickstart[postgres]
```

---

## 🚀 Quickstart Guide

### 1️⃣ **Initialize a new FastAPI project with uv**
```bash
uv init myproject
cd myproject
```

### 2️⃣ **Configure your database**
Rename `.env.example.postgres` or `.env.example.sqlite` to `.env`, then update it with your database credentials.

Example `.env` file for **PostgreSQL**:
```
DB_TYPE=postgres
DB_USER=myuser
DB_PASSWORD=mypassword
DB_HOST=localhost
DB_NAME=mydatabase
POOL_SIZE=20
MAX_OVERFLOW=64
DB_ECHO=True
```

### 3️⃣ **Run database migrations**
```bash
fastapi-quickstart migrate init
fastapi-quickstart migrate revision "Initial migration"
fastapi-quickstart migrate upgrade
```

### 4️⃣ **Start your FastAPI app**
```bash
fastapi dev path/to/main.py
```

---

## 🛠 Database Configuration

FastAPI Quickstart **automatically detects your database type** based on the `.env` file and configures the connection accordingly.

**Supported Databases:**
- ✅ PostgreSQL (`postgresql+asyncpg://...`)
- ✅ SQLite (`sqlite+aiosqlite://...`)

### Dynamic Connection Strings
The `ASYNC_DATABASE_URI` is automatically generated based on `.env` settings:
```python
from fastapi_quickstart.core.config import settings
print(settings.ASYNC_DATABASE_URI)  # Outputs the full database URL
```

---

## 🔄 Migrations (Alembic)

### **Initialize Alembic**
```bash
fastapi-quickstart migrate init
```

### **Create a new migration**
```bash
fastapi-quickstart migrate revision "Added users table"
```

### **Apply migrations**
```bash
fastapi-quickstart migrate upgrade
```

### **Rollback last migration**
```bash
fastapi-quickstart migrate downgrade
```

---

## 🔧 CLI Usage

The FastAPI Quickstart CLI provides an easy way to manage your project.

### **List available commands**
```bash
fastapi-quickstart --help
```

### **Available Commands:**
| Command | Description |
|---------|-------------|
| `init` | Create a new FastAPI project |
| `migrate init` | Initialize Alembic migrations |
| `migrate revision "message"` | Generate a new migration script |
| `migrate upgrade` | Apply all pending migrations |
| `migrate downgrade` | Revert last migration |

---

## ✅ Testing

### **Run tests with `pytest`**
```bash
pytest tests/
```

### **Check code style/format with `ruff`**
```bash
ruff check .
ruff format
```

---

## 🤝 Contributing

Contributions are welcome! Feel free to **open an issue or pull request**.

### **Development Setup**
```bash
git clone https://github.com/ElderEvil/fastapi-quickstart.git
cd fastapi-quickstart
uv sync -e .[dev]
```

### **Run tests**
```bash
pytest
```

---

## 📜 License
MIT License © 2025 FastAPI Quickstart

---

## 🌟 Support
If you like this project, please ⭐️ it on GitHub!

