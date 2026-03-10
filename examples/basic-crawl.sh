#!/bin/bash
# GRIMOIRE — Basic Web Crawl Example
# Crawls a target URL and extracts words into a plaintext wordlist.

grimoire --url https://example.com \
  --depth 2 \
  --min-length 5 \
  --emails \
  --meta \
  --output wordlist.txt

echo "Wordlist saved to wordlist.txt"
