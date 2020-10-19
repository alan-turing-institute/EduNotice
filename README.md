# EduHub DB

Created and designed by <a href="https://github.com/tomaslaz">Tomas Lazauskas</a>.

## Setup

Set the required and optional environmental parameters (recommended by modifying the `~/.bash_profile` file).

```bash
# EduDB
export EDB_SQL_SERVER="<<replace me>>"
export EDB_SQL_HOST=$EDB_SQL_SERVER".postgres.database.azure.com"
export EDB_SQL_USERNAME="<<replace me>>"
export EDB_SQL_USER=$EDB_SQL_USERNAME"@"$EDB_SQL_SERVER
export EDB_SQL_PASS="<<replace me>>"
export EDB_SQL_DBNAME="<<replace me>>"
export EDB_SQL_PORT="<<replace me>>"
```

Do not forget either restart the terminal or use the `source` command to effect the changes.