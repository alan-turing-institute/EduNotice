# EduHub Notification Service

Created and designed by <a href="https://github.com/tomaslaz">Tomas Lazauskas</a>.

## Notes

Existing details (are not updated)

## Setup

Set the required and optional environmental parameters (recommended by modifying the `~/.bash_profile` file).

```bash
# EduDB
export ENS_SQL_SERVER="<<replace me>>"
export ENS_SQL_HOST=$ENS_SQL_SERVER".postgres.database.azure.com"
export ENS_SQL_USERNAME="<<replace me>>"
export ENS_SQL_USER=$ENS_SQL_USERNAME"@"$ENS_SQL_SERVER
export ENS_SQL_PASS="<<replace me>>"
export ENS_SQL_DBNAME="<<replace me>>"
export ENS_SQL_PORT="<<replace me>>"
export ENS_TEST_MODE=False
```

Do not forget either restart the terminal or use the `source` command to effect the changes.