#!/usr/bin/env python3
"""
unpack-gs.py

Unpacker for grayscale trace format using gs-mapping.json.
"""

import re
import os
import json

TARGET_DIR = "grayscale-traces"
OUTPUT_DIR = "traces"
MAPPING_FILE = "gs-mapping.json"

def extract_mapping(json):
  """
  Takes a JSON object read in from a mappings file and extracts a responses
  mapping object from it.
  """
  responses = {}
  for choice in json:
    rkeys = filter(lambda x: re.match(r"\d+", x), choice.keys())
    #choices[choice["id"]] = { k: choice[k] for k in rkeys }
    for k in rkeys:
      responses[choice[k]] = [choice["id"], k]

  return responses


def unpack(trace, mapping):
  """
  Takes a Grayscale trace JSON object and a response mapping object (see
  extract_mapping above) and returns a JSON string for an equivalent PDM trace.
  """
  history = trace["clickTrackers"]["clickTracker"]["eventHistory"]
  decisions = []
  for event in history:
    if event["eventId"] == "ResponseSelect":
      data = event["eventData"]
      label = data.get("label")
      if label:
        decisions.append(mapping[label])

  return decisions


def main():
  """
  Unpacks each trace from the TARGET_DIR into the OUTPUT_DIR using the mapping
  specified by the given MAPPING_FILE.
  """
  with open(MAPPING_FILE, 'r') as fin:
    mapping = extract_mapping(json.load(fin))
  targets = [
    os.path.join(TARGET_DIR, x)
      for x in os.listdir(TARGET_DIR)
      if x.endswith(".json")
  ]
  for t in targets:
    with open(t, 'r') as fin:
      raw = json.load(fin)
    conv = unpack(raw, mapping)
    ofile = os.path.join(OUTPUT_DIR, os.path.split(t)[1])
    with open(ofile, 'w') as fout:
      json.dump(conv, fout)

if __name__ == "__main__":
  main()
