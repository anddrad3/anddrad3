"""Refresh GHStats; publish only complete, valid cards. No personal token needed."""
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.parse import urlencode
import json
import xml.etree.ElementTree as ET

USER = "anddrad3"
URL = "https://ghstats.dev/api/card?" + urlencode({
    "username": USER, "theme": "tokyonight", "show_icons": "true",
    "border_radius": "10", "custom_title": "Matheus Andrade | GitHub",
    "hide": "streak,week,trend,avg,active_day,grade,hours",
})

def validate_svg(data, name):
    if len(data) > 250_000:
        raise ValueError(f"{name}: unexpected size")
    root = ET.fromstring(data)
    if root.tag != "{http://www.w3.org/2000/svg}svg":
        raise ValueError(f"{name}: not an SVG")
    text = " ".join(root.itertext()).lower()
    for message in ["something went wrong", "could not fetch", "rate limit", "bad credentials", "user not found", "error fetching"]:
        if message in text:
            raise ValueError(f"{name}: provider error; previous cards preserved")
    for node in root.iter():
        if node.tag.rsplit("}", 1)[-1] in {"script", "foreignObject"}:
            raise ValueError(f"{name}: unexpected active content")
        if any(key.lower().startswith("on") for key in node.attrib):
            raise ValueError(f"{name}: unexpected event handler")
    if not any(node.tag.endswith("}text") for node in root.iter()):
        raise ValueError(f"{name}: empty card")

if __name__ == "__main__":
    folder = Path("profile")
    folder.mkdir(exist_ok=True)
    with urlopen(Request(URL, headers={"User-Agent": "anddrad3-profile-cards"}), timeout=45) as response:
        stats = response.read(250_001)
    validate_svg(stats, "stats")
    for name in ("top-langs", "streak"):
        validate_svg((folder / f"{name}.svg").read_bytes(), name)
    (folder / "stats.svg").write_bytes(stats)
    print(json.dumps({"user": USER, "cards": 3, "validated": True}))
