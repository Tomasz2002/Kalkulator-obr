import glob, re

files = (
    glob.glob('*.py')
    + glob.glob('src/*.py')
    + glob.glob('src/calculators/*.py')
    + glob.glob('templates/*.html')
    + glob.glob('static/*.css')
    + glob.glob('static/*.js')
)

comments = []
for fpath in files:
    with open(fpath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    for lno, line in enumerate(lines, 1):
        s = line.strip()
        if fpath.endswith('.py'):
            if s.startswith('#') or '"""' in line or "'''" in line:
                comments.append((fpath, lno, line))
        elif fpath.endswith('.html'):
            if '<!--' in line or '-->' in line:
                comments.append((fpath, lno, line))
        elif fpath.endswith('.css'):
            if '/*' in line or '*/' in line:
                comments.append((fpath, lno, line))
        elif fpath.endswith('.js'):
            if '/*' in line or '*/' in line:
                comments.append((fpath, lno, line))
            clean = re.sub(r'https?://[^\s"\']+', '', line)
            clean = re.sub(r'"[^"]*"', '', clean)
            clean = re.sub(r"'[^']*'", '', clean)
            clean = re.sub(r'`[^`]*`', '', clean)
            if '//' in clean:
                comments.append((fpath, lno, line))

if comments:
    print('WARNING! Real comments found:')
    for c in comments:
        print(f'{c[0]}:{c[1]} -> {c[2].strip()}')
else:
    print('VERIFIED: ZERO comments found in all HTML, CSS, JS, and Python files!')
