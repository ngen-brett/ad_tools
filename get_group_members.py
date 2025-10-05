#!/usr/bin/env python3
# get_group_members.py
import sys
from ad_utils import get_connection, search

def get_group_members(group_name):
    """Get all members of a given group"""
    conn = get_connection()
    
    # First, find the group by CN (Common Name)
    group_filter = f"(&(objectClass=group)(cn={group_name}))"
    entries = search(conn, group_filter, ['distinguishedName', 'description'])
    
    if not entries:
        print(f"Group '{group_name}' not found.")
        sys.exit(1)

    group = entries[0]
    group_dn = group.distinguishedName.value
    
    print(f"Members of group: {group_name}")
    if group.description:
        print(f"Description: {group.description.value}")
    print(f"DN: {group_dn}")
    print("-" * 60)

    # Search for users who are members of this group
    member_filter = f"(&(objectClass=user)(memberOf={group_dn}))"
    members = search(conn, member_filter, ['sAMAccountName', 'displayName', 'mail', 'userAccountControl'])
    
    if not members:
        print("No direct user members found for this group.")
        return

    # Process and sort members
    member_list = []
    for member in members:
        username = member.sAMAccountName.value
        display_name = member.displayName.value if member.displayName else "No display name"
        email = member.mail.value if member.mail else "No email"
        
        # Check if account is enabled (userAccountControl bit 2 = disabled)
        uac = int(member.userAccountControl.value) if member.userAccountControl else 0
        is_enabled = not (uac & 2)
        status = "Enabled" if is_enabled else "Disabled"
        
        member_list.append((username, display_name, email, status))

    # Sort by username
    member_list.sort(key=lambda x: x[0].lower())

    print(f"Direct user members ({len(member_list)} users):")
    for username, display_name, email, status in member_list:
        print(f"  • {username} - {display_name}")
        print(f"    Email: {email}")
        print(f"    Status: {status}")
        print()

def main():
    if len(sys.argv) != 2:
        print("Usage: get_group_members.py <group_name>")
        print("Example: get_group_members.py \"Domain Users\"")
        sys.exit(1)
    
    group_name = sys.argv[1]
    get_group_members(group_name)

if __name__ == '__main__':
    main()
