from db_sync.models import TableSync

TABLES: list[TableSync] = [
    TableSync(
        name="Empresas",
        query=(
            "SELECT CodigoEmpresa, Empresa "
            "FROM Empresas "
        ),
    ),
]
