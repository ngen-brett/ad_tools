# AD Tools

This repository provides Python command-line utilities for querying Active Directory group memberships and members using LDAP.

## Features

- Retrieve both **direct** and **nested** group memberships for a given user.
- List **direct** user members of a specified AD group.
- Configurable connection settings via a `.env` file.
- Supports LDAPS with optional certificate verification bypass.
- Flexible bind identity options: full DN, UPN (`username@domain`), or `DOMAIN\user`.

## Prerequisites

- Python 3.7+
- Install dependencies:
  ```bash
  pip install ldap3 python-dotenv
  ```

## Files

- `ad_utils.py`: Common helper functions for connecting and searching AD.
- `get_user_groups.py`: Lists direct and nested groups for a user.
- `get_group_members.py`: Lists direct user members of a group.
- `.env.example`: Sample configuration file.

## Configuration (`.env`)

Copy the example file to `.env` and adjust values:

```dotenv
# Base DN for all searches, e.g. "DC=example,DC=local"
BASE_DN=DC=example,DC=local

# Either DOMAIN (used for DC discovery) or direct LDAP_SERVER URL
DOMAIN=example.local
# LDAP_SERVER=ldap://ldap.example.local:389

# Bind identity options (only one is required):
# 1. Full Distinguished Name of the bind user
#BIND_USER_DN=CN=Service Account,CN=Users,DC=example,DC=local

# 2. User Principal Name (UPN)
#BIND_USER_UPN=service.account@example.local

# 3. Construct DN using username and suffix
BIND_USER_DN_SUFFIX=CN=Users,DC=example,DC=local

# Optional: ignore LDAPS certificate validation
# Set LDAP_SERVER to ldaps://... to use LDAPS
# (certificate errors will be bypassed)

# Example for LDAPS ignoring certs:
# LDAP_SERVER=ldaps://ldap.example.local:636
```

## Usage

1. Configure `.env`.
2. Run user groups:
   ```bash
   ./get_user_groups.py <username>
   ```
3. Run group members:
   ```bash
   ./get_group_members.py "Group Name"
   ```

## License

MIT License
