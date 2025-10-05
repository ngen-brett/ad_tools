#!/usr/bin/env python3
import sys
from ad_utils import get_connection, search

def get_user_groups(username):
    """
    Lists a user’s direct and nested (indirect) group memberships.
    Direct groups are those in the user’s memberOf attribute.
    Nested groups are parent groups of the direct groups.
    """
    conn = get_connection()

    # Retrieve the user entry
    user_filter = f"(&(objectClass=user)(sAMAccountName={username}))"
    entries = search(conn, user_filter, ['displayName', 'memberOf'])
    if not entries:
        print(f"User '{username}' not found.")
        sys.exit(1)
    user = entries[0]

    direct_dns = user.memberOf or []
    direct_groups = {}
    nested_groups = {}

    # Helper to extract CN from a DN
    def extract_cn(dn):
        cn_part = dn.split(',')[0]
        return cn_part[3:] if cn_part.lower().startswith('cn=') else cn_part

    # Mark direct groups
    for dn in direct_dns:
        grp = extract_cn(dn)
        direct_groups[dn] = grp

    # Recursive discovery of nested groups
    visited = set(direct_dns)

    def recurse(group_dns):
        for dn in group_dns:
            # Find parent groups of this group
            entries = search(conn, f"(distinguishedName={dn})", ['memberOf'])
            if not entries or not entries[0].memberOf:
                continue
            for parent_dn in entries[0].memberOf:
                if parent_dn in visited:
                    continue
                visited.add(parent_dn)
                grp = extract_cn(parent_dn)
                nested_groups[parent_dn] = grp
                recurse([parent_dn])

    recurse(direct_dns)

    # Output results
    print(f"Group memberships for {username} ({user.displayName.value if user.displayName else 'No display name'}):")
    print("-" * 60)

    print(f"Direct memberships ({len(direct_groups)}):")
    for dn, grp in sorted(direct_groups.items(), key=lambda x: x[1].lower()):
        print(f"  • {grp}")
        print(f"    DN:  {dn}")

    print(f"\nNested memberships ({len(nested_groups)}):")
    for dn, grp in sorted(nested_groups.items(), key=lambda x: x[1].lower()):
        print(f"  • {grp}")
        print(f"    DN:  {dn}")

    print(f"\nTotal unique groups: {len(direct_groups) + len(nested_groups)}")

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: get_user_groups.py <username>")
        sys.exit(1)
    get_user_groups(sys.argv[1])

