#!/bin/bash
# GRIMOIRE — Mutation Pipeline Example
# Full mutation with Hashcat rule file.

grimoire --url https://target.com \
  --depth 2 \
  --mutate \
  --leet \
  --case \
  --append-numbers \
  --rule-file examples/mutation-example.rule \
  --format hashcat \
  --output mutated-rules.hc

echo "Hashcat rules saved to mutated-rules.hc"
