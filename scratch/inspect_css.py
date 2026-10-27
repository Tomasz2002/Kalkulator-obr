with open("static/style.css", "r", encoding="utf-8") as f:
    css = f.read()

import re
selectors = re.findall(r"([^{}]+)\{", css)
clean_sel = [s.strip() for s in selectors if not s.strip().startswith("@")]
print("Total rule blocks:", len(clean_sel))
for s in clean_sel[:25]:
    print(" ", s)
