#!/bin/bash
# GRIMOIRE — Dictionary Improvement Example
# Enhances an existing wordlist with mutations.

grimoire --improve existing-passwords.txt \
  --leet \
  --case \
  --append-numbers \
  --output improved-passwords.txt

echo "Improved wordlist saved to improved-passwords.txt"
