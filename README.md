# db-sync

Command-line tool that synchronizes tables from a SQL Server database to a local SQLite file.

## Requirements

- Python 3.10+
- Access to a SQL Server instance

## Setup

1. Clone the repository:

```bash
git clone https://github.com/chemecador/db-sync.git
cd db-sync
```

2. Create a virtual environment and install dependencies:

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # Linux / macOS
pip install .
```

3. Create a `.env` file from the example and fill in your values:

```bash
cp .env.example .env
```

```env
SQLSERVER_HOST=localhost
SQLSERVER_DATABASE=your_database
SQLSERVER_USER=your_user
SQLSERVER_PASSWORD=your_password
SQLITE_OUTPUT_DIR=./output
CLIENT_CODE=your_client_code
```

## Usage

```bash
db-sync
```

The tool will connect to SQL Server, read the configured tables, and write them to `output/<CLIENT_CODE>.db`.

## Adding tables

Edit `src/db_sync/tables.py` to add more tables to sync:

```python
TABLES: list[TableSync] = [
    TableSync(
        name="Empresas",
        query="SELECT CodigoEmpresa, Empresa FROM Empresas",
    ),
    TableSync(
        name="Clientes",
        query="SELECT Id, Nombre FROM Clientes",
    ),
]
```

## Building the executable

1. Install PyInstaller:

```bash
pip install pyinstaller
```

2. Build:

```bash
pyinstaller db-sync.spec
```

The executable will be generated in `dist/db-sync/`. Place the `.env` file next to `db-sync.exe` to run it.
