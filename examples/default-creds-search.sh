#!/bin/bash
# GRIMOIRE — Default Credentials Search Example
# Search the dynamic default credentials database.

# Search by vendor
grimoire --default-creds "cisco"

echo "---"

# Search another vendor
grimoire --default-creds "netgear"
