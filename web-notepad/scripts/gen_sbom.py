import json
import subprocess  # nosec B404
import sys
from datetime import datetime


def generate_simple_sbom():
    # nosec B603: Hardcoded arguments, safe execution
    res = subprocess.run(
        [sys.executable, "-m", "pip", "list", "--format", "json"],
        capture_output=True,
        text=True,
        check=True,
    )
    pkgs = json.loads(res.stdout)

    sbom = {
        "bomFormat": "CycloneDX",
        "specVersion": "1.4",
        "version": 1,
        "metadata": {
            "timestamp": datetime.now().isoformat(),
            "component": {"name": "web-notepad", "type": "application"},
        },
        "components": [
            {
                "type": "library",
                "name": p["name"],
                "version": p["version"],
                "purl": f"pkg:pypi/{p['name']}@{p['version']}",
            }
            for p in pkgs
        ],
    }

    with open("sbom.json", "w", encoding="utf-8") as f:
        json.dump(sbom, f, indent=2, ensure_ascii=False)
    print(f"✅ SBOM created: {len(pkgs)} packages")


if __name__ == "__main__":
    generate_simple_sbom()
