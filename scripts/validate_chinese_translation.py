#!/usr/bin/env python3
"""Check the Chinese ARB catalog before Flutter gen-l10n/build."""
import json,re,sys
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
P=ROOT/'lib/l10n/arb'

def icu_structure(text):
    """Validate brace nesting and retain argument/type/selector structure."""
    out=[]
    def block(pos):
        assert text[pos]=='{'
        m=re.match(r'\{\s*([A-Za-z_][A-Za-z_0-9]*)\s*([},])',text[pos:])
        if not m:raise ValueError(f'invalid ICU argument at {pos}')
        arg,sep=m.groups();pos+=len(m.group());out.append(('arg',arg))
        if sep=='}':return pos
        m=re.match(r'\s*(plural|select|selectordinal|number|date|time)\s*',text[pos:])
        if not m:raise ValueError(f'invalid ICU type at {pos}')
        kind=m.group(1);out.append(('type',arg,kind));pos+=len(m.group())
        if kind not in ('plural','select','selectordinal'):
            while pos<len(text) and text[pos]!='}':pos+=1
            if pos>=len(text):raise ValueError('unclosed ICU argument')
            return pos+1
        if pos>=len(text) or text[pos]!=',':raise ValueError('missing selector comma')
        pos+=1
        while True:
            while pos<len(text) and text[pos].isspace():pos+=1
            if pos<len(text) and text[pos]=='}':return pos+1
            off=re.match(r'offset:\s*\d+',text[pos:])
            if off:out.append(('offset',arg,off.group()));pos+=len(off.group());continue
            m=re.match(r'(=\d+|[A-Za-z_][A-Za-z_0-9]*)\s*\{',text[pos:])
            if not m:raise ValueError(f'invalid selector at {pos}')
            selector=m.group(1);out.append(('selector',arg,selector));pos+=len(m.group())
            pos=content(pos,True)
    def content(pos,nested=False):
        while pos<len(text):
            if text[pos]=='{':pos=block(pos)
            elif text[pos]=='}':
                if not nested:raise ValueError('extra closing brace')
                return pos+1
            else:pos+=1
        if nested:raise ValueError('unclosed selector branch')
        return pos
    content(0)
    return Counter(out)

def main():
    en=json.loads((P/'app_en.arb').read_text());zh=json.loads((P/'app_zh_CN.arb').read_text())
    keys={k for k in en if not k.startswith('@')};zkeys={k for k in zh if not k.startswith('@')};errors=[]
    if keys!=zkeys:errors.append(f'key mismatch missing={keys-zkeys} extra={zkeys-keys}')
    translated=0;unchanged=[]
    for key in sorted(keys&zkeys):
        a,b=en[key],zh[key]
        if not isinstance(b,str) or not b.strip():errors.append(key+': empty/non-string');continue
        if re.search(r'[\u3400-\u9fff]',b):translated+=1
        if a==b:unchanged.append(key)
        try:
            if icu_structure(a)!=icu_structure(b):errors.append(key+': ICU arguments/selectors differ')
        except ValueError as exc:errors.append(key+': '+str(exc))
        for url in re.findall(r'https?://[^\s<>"\)]+',a):
            if url not in b:errors.append(key+': source URL changed')
    text=(ROOT/'lib/l10n/supported_locales.dart').read_text()
    if "Locale('zh', 'CN')" not in text or "'zh_CN'" not in text:errors.append('Chinese not enabled in locale list')
    if translated/len(keys)<.70:errors.append('Chinese coverage below 70%')
    summary={'total_keys':len(keys),'chinese_text_keys':translated,'chinese_coverage_percent':round(100*translated/len(keys),2),'unchanged_english_keys':unchanged,'errors':errors,'note':'Static checks only; Flutter compilation and on-device UI still require a compatible build host.'}
    print(json.dumps(summary,ensure_ascii=False,indent=2))
    return bool(errors)
if __name__=='__main__':sys.exit(main())
