# infrastructure.sh

Creates the infrastructre for EduHub Notification Service on Azure.

## Requirements

Python packages:

- EduNotice

## Setup

Set the required and optional environmental parameters (recommended by modifying the `~/.bash_profile` file).

```bash
export ENS_SUBSCRIPTION_ID="<<replace me>>"
export ENS_SQL_WHITELISTED_IP="<<replace me>>" # an ip address that you would like to whitelist
```

Do not forget either restart the terminal or use the `source` command to effect the changes.

## Usage

```bash

./infrastructure {environment}

positional arguments:
  {environment} - PROD or TEST

```