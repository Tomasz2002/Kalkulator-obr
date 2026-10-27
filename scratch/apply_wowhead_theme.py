with open("static/style.css", "r", encoding="utf-8") as f:
    css = f.read()

replacements = [
    ("#0f1015", "#12100e"),
    ("#161720", "#1c1916"),
    ("#1c1d28", "#241f1a"),
    ("#12131b", "#161310"),
    ("#11121c", "#181512"),
    ("#2f3244", "#3a332c"),
    ("#c69b3a", "#c9a227"),
    ("#e2e4ea", "#e8e0d4"),
    ("#9499ad", "#9c8f7d"),
    ("#4a4f68", "#5a4f3f"),
    ("#3c4056", "#5a4f3f"),
    ("#171824", "#1d1813"),
    ("#232638", "#2c251e"),
    ("#23273c", "#2c251e"),
    ("#252837", "#3a2f16"),
    ("#0b0c10", "#0c0a08"),
    ("#777788", "#5a4f3f"),
    ('rgba(10, 10, 18, 0.96)', '#0c0a08'),
    ('rgba(255, 255, 255, 0.04)', 'rgba(201, 162, 39, 0.06)'),
    ('rgba(255, 255, 255, 0.03)', 'rgba(201, 162, 39, 0.04)'),
    ('"Outfit", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif', '"Segoe UI", system-ui, -apple-system, BlinkMacSystemFont, "Outfit", sans-serif'),
]

new_css = css
for old, new in replacements:
    new_css = new_css.replace(old, new)

# Check for any comments
import re
assert "/*" not in new_css and "*/" not in new_css, "Comment found!"

with open("static/style.css", "w", encoding="utf-8") as f:
    f.write(new_css)

print("Updated style.css to Wowhead/OctoWoW warm umber/gold color scheme!")
