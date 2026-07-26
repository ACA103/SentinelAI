import duckdb
import pandas as pd
from pathlib import Path
from src.utils.config import ConfigManager

class DataStore:
    """
    Data Access Layer (DAL) responsible for persistence operations.
    Wraps DuckDB for analytics and Parquet for file-based data contracts.
    """
    def __init__(self):
        self.config = ConfigManager()
        
        project_root = Path(__file__).parent.parent.parent
        db_rel_path = self.config.get("paths.database", "database/sentinel.duckdb")
        self.db_path = project_root / db_rel_path
        
        # Ensure database directory exists
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = duckdb.connect(str(self.db_path))
        
        # Configure DuckDB resources
        mem_limit = self.config.get("duckdb.memory_limit", "2GB")
        threads = self.config.get("duckdb.threads", 2)
        self.conn.execute(f"PRAGMA memory_limit='{mem_limit}';")
        self.conn.execute(f"PRAGMA threads={threads};")

    def initialize_schema(self):
        """
        Initializes the DuckDB database schema from database/schema.sql.
        This sets up the formal entity tables for the platform.
        """
        project_root = Path(__file__).resolve().parents[3]
        schema_path = project_root / "database" / "schema.sql"
        
        if not schema_path.exists():
            raise FileNotFoundError(f"Schema file not found at {schema_path}")
            
        with open(schema_path, 'r') as f:
            sql_script = f.read()
            
        # Execute the script
        self.conn.execute(sql_script)

    def query(self, sql_query: str) -> pd.DataFrame:
        """Execute a DuckDB SQL query and return a Pandas DataFrame."""
        return self.conn.execute(sql_query).df()

    def register_dataframe(self, name: str, df: pd.DataFrame):
        """Register a Pandas DataFrame as a virtual table in DuckDB."""
        self.conn.register(name, df)

    def write_parquet(self, df: pd.DataFrame, relative_file_path: str):
        """
        Write a DataFrame to a Parquet file.
        Ensures parent directories exist to comply with interface contracts.
        """
        project_root = Path(__file__).parent.parent.parent
        full_path = project_root / relative_file_path
        
        full_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_parquet(str(full_path), engine="pyarrow", index=False)

    def read_parquet(self, relative_file_path: str) -> pd.DataFrame:
        """Read a Parquet file into a Pandas DataFrame."""
        project_root = Path(__file__).parent.parent.parent
        full_path = project_root / relative_file_path
        
        if not full_path.exists():
            raise FileNotFoundError(f"Parquet file not found: {full_path}")
        return pd.read_parquet(str(full_path), engine="pyarrow")

    def close(self):
        """Close the DuckDB connection."""
        self.conn.close()
