#!/usr/bin/env python3
"""Build static social-preview pages for active notices. Run in GitHub Actions or locally.
No edits to the existing public UI or spreadsheet.
"""
import json,os,re,urllib.request,html,pathlib,datetime
API=os.environ.get('EVENT_API_URL','https://script.google.com/macros/s/AKfycbzq4EDX6gfB20LN0F071kj2ysbCUX-PETlIlzF7y0dbwIW7WBO23m7vy6xTlB189g4wuQ/exec')
BASE='https://nckageshwori1.github.io/members/'
req=urllib.request.Request(API,data=json.dumps({'action':'publicHome'}).encode(),headers={'Content-Type':'text/plain;charset=utf-8'},method='POST')
with urllib.request.urlopen(req,timeout=45) as res: data=json.load(res)
if not data.get('ok') or not isinstance(data.get('notices'),list): raise RuntimeError('Public notices API returned invalid data; refusing to overwrite pages')
root=pathlib.Path('events');root.mkdir(exist_ok=True)
seen=set()
for n in data['notices']:
    id=str(n.get('ID','')).strip()
    if not id or not re.fullmatch(r'[a-zA-Z0-9_-]{1,100}',id): continue
    seen.add(id)
    title=str(n.get('शीर्षक') or 'कार्यक्रम सूचना').strip()[:180]
    description=' • '.join(str(n.get(k,'')).strip() for k in ('मिति','समय','स्थान') if n.get(k))
    description=(description+' — '+str(n.get('विवरण') or '')).strip(' —')[:280]
    image=str(n.get('ImageURL') or '')
    if not image.startswith('https://'): image=''
    from urllib.parse import quote
    target=BASE+'event.html?id='+quote(id,safe='')
    canonical=BASE+'events/'+quote(id,safe='')+'/index.html'
    tags=f'''<meta property="og:type" content="article"><meta property="og:site_name" content="नेपाली कांग्रेस वडा नं. १"><meta property="og:title" content="{html.escape(title,quote=True)}"><meta property="og:description" content="{html.escape(description,quote=True)}"><meta property="og:url" content="{html.escape(canonical,quote=True)}"><meta name="twitter:card" content="summary_large_image">'''
    if image: tags+=f'<meta property="og:image" content="{html.escape(image,quote=True)}"><meta name="twitter:image" content="{html.escape(image,quote=True)}">'
    page=f'''<!doctype html><html lang="ne"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{html.escape(title)}</title><meta name="description" content="{html.escape(description,quote=True)}">{tags}<link rel="canonical" href="{html.escape(target,quote=True)}"><meta http-equiv="refresh" content="0;url={html.escape(target,quote=True)}"></head><body><p>कार्यक्रम विवरण खोलिँदैछ... <a href="{html.escape(target,quote=True)}">{html.escape(title)}</a></p><script>location.replace({json.dumps(target,ensure_ascii=False)});</script></body></html>'''
    dest=root/id;dest.mkdir(exist_ok=True);(dest/'index.html').write_text(page,encoding='utf-8')
# Do not delete old event previews; old links remain valid, with event.html displaying unavailable if deleted.
print('Generated previews:',len(seen))
