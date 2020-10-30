# EduHub Activity Notification Service

Created and designed by <a href="https://github.com/tomaslaz">Tomas Lazauskas</a>.

[![Build Status](https://travis-ci.com/tomaslaz/EduNotice.svg?branch=main)](https://travis-ci.org/tomaslaz/EduNotice)

## Notes

Existing details (are not updated)

## Installation

- [EduCrawler](https://github.com/tomaslaz/EduCrawler) Python package

```bash
pip install git+https://github.com/tomaslaz/EduCrawler.git
```

- [EduNotice](https://github.com/tomaslaz/EduNotice) Python package

```bash
pip install git+https://github.com/tomaslaz/EduNotice.git
```

## Requirements

- [EduCrawler](https://github.com/tomaslaz/EduCrawler) Python package

In addition to Python packages listed in `requirements.txt` and EduCrawler,

- SendGrid service
    - Generate API KEY (
        Recommended settings
            Restricted Access
                Allow only `Mail Send` Full Access
    - Export the API key value as `ENS_EMAIL_API` environmental parameter as shown in the `Setup` section.


## Setup

Make sure that the [EduCrawler](https://github.com/tomaslaz/EduCrawler) Python package is installed and configured.

Set the required and optional environmental parameters (recommended by appending/modifying the `~/.bash_profile` file).

```bash
# EduNotice
export ENS_VERBOSE_LEVEL=2 # optional (choices: 0-4, 0 - min, 4 - max, default: 2)
export ENS_SQL_SERVER="<<replace me>>"
export ENS_SQL_HOST=$ENS_SQL_SERVER".postgres.database.azure.com"
export ENS_SQL_USERNAME="<<replace me>>"
export ENS_SQL_USER=$ENS_SQL_USERNAME"@"$ENS_SQL_SERVER
export ENS_SQL_PASS="<<replace me>>"
export ENS_SQL_DBNAME="<<replace me>>"
export ENS_SQL_PORT="<<replace me>>"
# Optional (Testing)
export ENS_TEST_MODE=False
# Email sending
export ENS_EMAIL_API="<<replace me>>"
export ENS_FROM_EMAIL="<<replace me>>"
export ENS_SUMMARY_RECIPIENTS="<<replace me>>"
```

Do not forget either restart the terminal or use the `source` command to effect the changes.

## Getting help
If you found a bug or need support, please submit an issue [here](https://github.com/tomaslaz/EduNotice/issues/new).

## How to contribute
We welcome contributions! If you are willing to propose new features or have bug fixes to contribute, please submit a pull request [here](https://github.com/tomaslaz/EduNotice/pulls).