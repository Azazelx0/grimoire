#!/bin/bash
# GRIMOIRE — Alecto DB Search Example
# Search the bundled default credentials database.

# Search by vendor
grimoire --alecto "cisco"

echo "---"

# Search another vendor
grimoire --alecto "netgear"
