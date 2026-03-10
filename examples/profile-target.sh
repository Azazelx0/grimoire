#!/bin/bash
# GRIMOIRE — CUPP-Style Target Profiling Example
# Generates a personalized wordlist from target information.

grimoire --profile "name=John last=Smith nick=Johnny dob=15/06/1990 partner=Jane pet=Rex company=Acme" \
  --output john-profile.txt

echo "Profile wordlist saved to john-profile.txt"
echo ""

# You can also run interactively:
# grimoire
# → Select [2] Profile Target
# → Answer the questions
