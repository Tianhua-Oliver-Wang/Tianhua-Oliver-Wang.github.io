"""Generate the static multilingual website with Python's standard library.
Edit content/site.json, then run: python3 build.py
"""
import json
import posixpath
from html import escape
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parent
DATA = json.loads((ROOT / 'content/site.json').read_text(encoding='utf-8'))
LOCALES = {'en-US':'', 'zh-CN':'zh-cn', 'zh-HK':'zh-hk'}
LABELS = {'en-US':'English', 'zh-CN':'简体', 'zh-HK':'繁體'}
BASE_URL = 'https://tianhua-oliver-wang.github.io/'
PAGES = ['index.html', 'research.html', 'writing.html', 'cv.html']


def e(value):
    return escape(str(value), quote=True)


def link(value):
    """Allow public web URLs and site-relative paths, not executable schemes."""
    parts = urlsplit(value)
    if parts.scheme and parts.scheme not in ('http', 'https'):
        raise ValueError(f'Unsupported link scheme: {parts.scheme}')
    if value.startswith('//'):
        raise ValueError('Use an explicit HTTPS URL')
    return e(value)


def target(locale, page):
    return posixpath.join(LOCALES[locale], page)


def relative(dest, directory):
    return posixpath.relpath(dest, directory or '.')


def empty(text, note=''):
    return f'<div class="empty"><p class="note">{e(text)}</p>' + (f'<p class="note">{e(note)}</p>' if note else '') + '</div>'


def section(key, heading, body):
    return f'<section id="{key}" aria-labelledby="{key}-title"><h2 id="{key}-title">{e(heading)}</h2>{body}</section>'


def entries(items):
    result = []
    for item in items:
        title = e(item['title'])
        if item.get('url'):
            title = f'<a href="{link(item["url"])}">{title}</a>'
        metadata = ' · '.join(str(item[k]) for k in ['authors', 'date', 'status'] if item.get(k))
        tags = ''.join(f'<span>{e(tag)}</span>' for tag in item.get('tags', []))
        result.append(f'<article class="entry"><h3>{title}</h3><p class="meta">{e(metadata)}</p><p>{e(item.get("summary", ""))}</p><div class="tags">{tags}</div></article>')
    return ''.join(result)


def cv_link(t, prefix):
    path = DATA['profile']['cv_file']
    if not path:
        return empty(t['cv_empty'])
    if not (ROOT / path).is_file():
        raise ValueError('CV file is configured but missing')
    return f'<p><a class="button" href="{link(prefix + path)}">{e(t["cv_download"])}</a></p>'


def contact(t):
    profile = DATA['profile']
    result = f'<p>{e(t["contact_intro"])}</p><p><a href="{link(profile["github"])}">GitHub <span aria-hidden="true">↗</span></a></p>'
    if profile['email']:
        result += f'<p>{e(t["email_label"])}: <a href="mailto:{e(profile["email"])}">{e(profile["email"])}</a></p>'
    else:
        result += f'<p class="note">{e(t["email_pending"])}</p>'
    return result


def body(t, page, prefix):
    nav = t['nav']
    if page == 'index.html':
        title = '<br>'.join(e(line) for line in t['hero'])
        result = f'<div class="hero"><span class="eyebrow">{e(t["eyebrow"])}</span><h1>{title}</h1><p class="lede">{e(t["intro"])}</p><div class="actions"><a class="button" href="research.html">{e(t["research_link"])} <span aria-hidden="true">↗</span></a><a href="cv.html">{e(t["cv_link"])}</a></div></div>'
        about = ''.join(f'<p>{e(p)}</p>' for p in t['about'])
        if t['bio_pending']:
            about += f'<p class="note">{e(t["bio_pending"])}</p>'
        result += section('about', nav[0], about)
        rows = ''
        for i, area in enumerate(t['areas'], 1):
            rows += f'<a class="topic-row" href="research.html#area-{i}"><span class="number">0{i}</span><div><h3>{e(area["title"])}</h3><p>{e(area["summary"])}</p></div><span aria-hidden="true">↗</span></a>'
        result += section('research', nav[1], f'<p class="note">{e(t["research_intro"])}</p>{rows}')
        result += section('publications', nav[2], entries(t['publications']) or empty(t['publications_empty'], t['publications_note']))
        result += section('projects', nav[3], entries(t['projects']) or empty(t['projects_empty'], t['projects_note']))
        result += section('writing', t['writing_page'], f'<p>{e(t["writing_intro"])}</p>' + (entries(t['writing'][:3]) or empty(t['writing_empty'])) + f'<p style="margin-top:16px"><a href="writing.html">{e(t["writing_page"])} <span aria-hidden="true">↗</span></a></p>')
        result += section('cv', t['cv_page'], f'<p>{e(t["cv_intro"])}</p><a href="cv.html">{e(t["cv_link"])} <span aria-hidden="true">↗</span></a>')
        result += section('contact', nav[5], contact(t))
        return result
    heading = t[{'research.html':'research_page','writing.html':'writing_page','cv.html':'cv_page'}[page]]
    intro = t[{'research.html':'detail_intro','writing.html':'writing_intro','cv.html':'cv_intro'}[page]]
    result = f'<div class="subhero"><h1>{e(heading)}</h1><p class="lede">{e(intro)}</p></div>'
    if page == 'research.html':
        result += f'<p class="note">{e(t["research_note"])}</p>'
        for i, area in enumerate(t['areas'], 1):
            tags = ''.join(f'<span>{e(tag)}</span>' for tag in area['topics'])
            result += f'<section class="research-item" id="area-{i}" aria-labelledby="area-{i}-title"><span class="number">0{i}</span><h2 id="area-{i}-title">{e(area["title"])}</h2><p>{e(area["summary"])}</p><div class="question"><span class="eyebrow">{e(t["question_label"])}</span><p>{e(area["question"])}</p></div><div class="tags" role="group" aria-label="{e(t["topics_label"])}">{tags}</div></section>'
    elif page == 'writing.html':
        result += section('notes', t['writing_page'], entries(t['writing']) or empty(t['writing_empty']))
    else:
        result += cv_link(t, prefix)
        for i, (label, text) in enumerate(zip(t['cv_sections'], t['cv_pending'])):
            result += section(f'cv-{i}', label, empty(text))
        result += section('contact', nav[5], contact(t))
    return result


def render(locale, page):
    t = DATA['locales'][locale]
    directory = LOCALES[locale]
    prefix = '../' if directory else './'
    title = t['home'] if page == 'index.html' else t[{'research.html':'research_page','writing.html':'writing_page','cv.html':'cv_page'}[page]]
    alternatives = ''.join(f'<link rel="alternate" hreflang="{loc}" href="{BASE_URL + target(loc,page)}">' for loc in LOCALES)
    alternatives += f'<link rel="alternate" hreflang="x-default" href="{BASE_URL + target("en-US",page)}">'
    switches = ''.join(f'<a href="{relative(target(loc,page), directory)}?lang={loc}" lang="{loc}" hreflang="{loc}"{(" aria-current=\"true\"" if loc == locale else "")}>{label}</a>' for loc,label in LABELS.items())
    menu = [(t['nav'][0],'index.html#about'),(t['nav'][1],'research.html'),(t['nav'][2],'index.html#publications'),(t['nav'][3],'index.html#projects'),(t['writing_page'],'writing.html'),(t['nav'][4],'cv.html'),(t['nav'][5],'index.html#contact')]
    navigation = ''.join(f'<a href="{href}"{(" aria-current=\"page\"" if href == page else "")}>{e(label)}</a>' for label,href in menu)
    return f'''<!doctype html>
<html lang="{t['lang']}" data-page="{page}" data-base="{prefix}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(t['name'])} | {e(title)}</title>
<meta name="description" content="{e(t['description'])}">
<link rel="canonical" href="{BASE_URL + target(locale,page)}">
{alternatives}
<script src="{prefix}assets/language.js"></script>
<script src="{prefix}assets/theme.js"></script>
<link rel="stylesheet" href="{prefix}assets/style.css">
<script defer src="{prefix}assets/name-alignment.js"></script>
</head>
<body>
<a class="skip" href="#main">{e(t['skip'])}</a>
<div class="shell">
<header class="topbar"><a class="brand" href="index.html"><span class="english-name">{e(t['name'])}</span><span class="chinese-name" lang="{'zh-HK' if locale == 'zh-HK' else 'zh-CN'}">{e(t['chinese_name'])}</span></a><div class="header-tools"><nav class="languages" aria-label="{e(t['language'])}">{switches}</nav><button class="theme-toggle" type="button" hidden data-theme-toggle data-dark-label="{e(t['theme_dark_label'])}" data-light-label="{e(t['theme_light_label'])}" aria-label="{e(t['theme_dark_label'])}" aria-pressed="false"><svg class="icon-moon" viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="M20.5 13.1A8.5 8.5 0 0 1 10.9 3.5 8.5 8.5 0 1 0 20.5 13.1Z"/></svg><svg class="icon-sun" viewBox="0 0 24 24" aria-hidden="true" focusable="false"><circle cx="12" cy="12" r="4"/><path d="M12 2v2m0 16v2M2 12h2m16 0h2M4.93 4.93l1.42 1.42m11.3 11.3 1.42 1.42m0-14.14-1.42 1.42m-11.3 11.3-1.42 1.42"/></svg></button></div></header>
<div class="page-grid">
<aside class="sidebar"><nav aria-label="{e(t['navigation_label'])}">{navigation}</nav><div class="profile"><span class="eyebrow">{e(t['profile_label'])}</span><p>{e(t['profile_text'])}</p><a href="{link(DATA['profile']['github'])}">GitHub <span aria-hidden="true">↗</span></a></div></aside>
<main id="main">{body(t,page,prefix)}</main>
</div>
<footer><span>{e(t['name'])}</span><span>{e(t['footer'])}</span></footer>
</div>
</body>
</html>
'''


if __name__ == '__main__':
    keys = set(DATA['locales']['en-US'])
    for locale in LOCALES:
        if set(DATA['locales'][locale]) != keys:
            raise ValueError(f'Translation keys do not match for {locale}')
        for page in PAGES:
            path = ROOT / target(locale, page)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(render(locale, page), encoding='utf-8')
    print(f'Generated {len(LOCALES) * len(PAGES)} static pages.')
