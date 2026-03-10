#!/bin/bash
# GRIMOIRE — Download Wordlists Example
# Download curated wordlist categories.

grimoire --download names
grimoire --download passwords
grimoire --download science

echo "Wordlists downloaded to ~/.grimoire/dictionaries/"
