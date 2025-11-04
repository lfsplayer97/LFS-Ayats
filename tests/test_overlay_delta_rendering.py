import json
import subprocess
from pathlib import Path


def test_overlay_delta_rendering():
  harness = Path(__file__).with_name("overlay_delta_harness.js")
  result = subprocess.run(["node", str(harness)], check=True, capture_output=True, text=True)
  payload = json.loads(result.stdout.strip())

  assert payload["positive"] == "+1:10.000"
  assert payload["negative"].startswith("-")
  assert payload["negative"].endswith("45.000")
  assert payload["seconds"] == "+10.000"
