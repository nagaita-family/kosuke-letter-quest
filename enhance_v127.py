"""Promote the verified v12.6 first-person road experience from GREEN FOREST to all ten worlds."""
from pathlib import Path

p=Path("game.js")
js=p.read_text()

old='// This prototype is intentionally restricted to GREEN FOREST.\nconst forestView=()=>stageIndex===0;'
new='// v12.7: the verified first-person road experience is shared by all ten worlds.\nconst forestView=()=>true;'
assert js.count(old)==1, ("v12.7 promotion mismatch", js.count(old))
js=js.replace(old,new)
p.write_text(js)

print("v12.7 all-world first-person promotion applied")
