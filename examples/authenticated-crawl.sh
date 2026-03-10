#!/bin/bash
# GRIMOIRE — Authenticated Crawl Example
# Uses form-based login to crawl a protected site.

grimoire --url https://intranet.example.com \
  --login-url https://intranet.example.com/login \
  --login-user admin \
  --login-pass secret123 \
  --depth 3 \
  --min-length 6 \
  --emails \
  --meta \
  --js \
  --proxy socks5://127.0.0.1:9050 \
  --random-ua \
  --delay 1000 \
  --output authenticated-words.txt

echo "Authenticated crawl complete."
