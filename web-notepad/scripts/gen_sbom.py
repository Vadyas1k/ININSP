#!/usr/bin/env python3
"""Простая генерация SBOM без внешних зависимостей"""
import json
import subprocess
from datetime import datetime
import sys


def generate_simple_sbom():
    # nosec B404,B603,B607 — используется sys.executable, команда жёстко задана, ввод не обрабатывается
    res = subprocess.run(
        [sys.executable, "-m", "pip", "list", "--format", "json"],
        capture_output=True,
        text=True,
        check=True,
    )
    packages = json.loads(res.stdout)

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
                "name": pkg["name"],
                "version": pkg["version"],
                "purl": f"pkg:pypi/{pkg['name']}@{pkg['version']}",
            }
            for pkg in packages
        ],
    }

    with open("sbom.json", "w", encoding="utf-8") as f:
        json.dump(sbom, f, indent=2, ensure_ascii=False)

    print(f"✅ SBOM создан: sbom.json ({len(packages)} пакетов)")


if __name__ == "__main__":
    generate_simple_sbom()
