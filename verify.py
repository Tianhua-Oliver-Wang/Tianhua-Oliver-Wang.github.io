"""Check all generated static pages without third-party dependencies."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit
import json

ROOT = Path(__file__).resolve().parent

class Page(HTMLParser):
    def __init__(self, path):
        super().__init__()
        self.ids = []
        self.links = []
        self.alternates = []
        self.canonical = []
        self.language_links = []
        self.lang = None
        self.h1s = 0
        self.feed(path.read_text(encoding='utf-8'))
    def handle_starttag(self, tag, attrs):
        d = dict(attrs)
        if 'id' in d:
            self.ids.append(d['id'])
        if tag == 'html':
            self.lang = d.get('lang')
        if tag == 'h1':
            self.h1s += 1
        if tag == 'a':
            self.links.append(d['href'])
            if 'hreflang' in d:
                self.language_links.append(d)
        if tag == 'script' and d.get('src'):
            self.links.append(d['src'])
        if tag == 'link':
            if d.get('rel') == 'alternate':
                self.alternates.append(d)
            if d.get('rel') == 'canonical':
                self.canonical.append(d['href'])
            if d.get('rel') == 'stylesheet':
                self.links.append(d['href'])

pages = {p.resolve():Page(p) for p in ROOT.rglob('*.html')}
assert len(pages) == 12, len(pages)
checked = 0
for path, page in pages.items():
    expected = 'zh-CN' if path.parent.name == 'zh-cn' else 'zh-HK' if path.parent.name == 'zh-hk' else 'en-US'
    assert page.lang == expected, (path, page.lang)
    assert page.h1s == 1, path
    assert len(page.ids) == len(set(page.ids)), path
    assert len(page.canonical) == 1, path
    assert {a['hreflang'] for a in page.alternates} == {'en-US','zh-CN','zh-HK','x-default'}, path
    assert len(page.language_links) == 3, path
    assert sum('aria-current' in a for a in page.language_links) == 1, path
    for a in page.language_links:
        dest = (path.parent / urlsplit(a['href']).path).resolve()
        assert dest.name == path.name, (path,a)
        assert pages[dest].lang == a['hreflang'], (path,a)
    for href in page.links:
        u = urlsplit(href)
        if u.scheme or u.netloc:
            continue
        dest = (path.parent / unquote(u.path)).resolve() if u.path else path
        assert dest.is_relative_to(ROOT), (path, href)
        assert dest.is_file(), (path, href)
        if u.fragment:
            assert dest in pages and unquote(u.fragment) in pages[dest].ids, (path,href)
        checked += 1
content = json.loads((ROOT/'content/site.json').read_text())
keys = content['locales']['en-US'].keys()
assert all(t.keys() == keys for t in content['locales'].values())
print(f'PASS: {len(pages)} pages, {checked} local links, locale parity, language switching, anchors and metadata.')
