import io
p = r'c:\Users\DHARSHINI C\OneDrive\Desktop\COVID-19\static\js\analytics-charts.js'
s = io.open(p, encoding='utf-8').read()
old = "backgroundColor: [NAVY, TEAL, SAGE, '#c5d8c9', RUST, '#b98a2f', '#5b9897', '#1c3a5e'],"
new = "backgroundColor: [NAVY, PINK, PINK_DEEP, NAVY_3, SLATE, MUTED, CREAM_2, '#B23A64'],"
assert old in s, 'OLD NOT FOUND'
s = s.replace(old, new)
s = s.replace("borderColor: '#ffffff',", "borderColor: '#F7F0E6',")
io.open(p, 'w', encoding='utf-8').write(s)
print('analytics-charts.js fixed')
