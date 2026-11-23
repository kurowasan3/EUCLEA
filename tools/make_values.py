#!/usr/bin/env python3
"""頻出度の自動判定（EUCLEA）→ content/values.json

    python3 tools/make_values.py [content フォルダ] [--check]

頻出度は「院試・検定や他の分野でも繰り返し使われる考え方を扱う問題ほど高い」という目安（1=低 2=中 3=高）。
EUCLEA では全問に管理表の「解法」列（先頭が主な解法）があるので、主な解法が何問の主な解法になっているか
（＝その考え方が問題集全体で何度出てくるか）と、補助として結びつく分野の広さから決める。

  高（3）：主な解法が 5問以上の主な解法で、かつ 2分野以上で使われる
  低（1）：主な解法が 2問以下の主な解法で、1分野でしか使われない
  中（2）：それ以外（中は書き出さない）

管理表の「頻出度」列に値がある問題は、build_app_data.py がそちらを優先する（ここでの判定は使われない）。
問題文が変わると判定は無効になる（h＝問題文の SHA-1 の先頭12桁。build_app_data.py と同じ）。
"""
import hashlib
import json
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HIGH_MAIN, HIGH_FIELDS = 5, 2
LOW_MAIN = 2


def judge(content):
    content = Path(content)
    tdoc = json.loads((content / 'techniques.json').read_text(encoding='utf-8'))
    tname = {}
    for t in tdoc['techniques']:
        for x in [t['id'], t['name'], *t.get('former', [])]:
            tname[x] = t['id']
    probs = []
    for f in sorted((content / 'problems').glob('*.json')):
        if f.name == 'builtin.json':
            continue
        probs += [p for p in json.loads(f.read_text(encoding='utf-8')) if p['quality']['status'] == 'published']
    main_n = defaultdict(int)
    fields = defaultdict(set)
    for p in probs:
        ms = [tname[x] for x in p.get('techniques') or [] if x in tname]
        if not ms:
            continue
        main_n[ms[0]] += 1
        for m in ms:
            fields[m].add(p['field'])
    out = {}
    for p in sorted(probs, key=lambda p: p['id']):
        ms = [tname[x] for x in p.get('techniques') or [] if x in tname]
        if not ms:
            continue
        m = ms[0]
        v = 3 if main_n[m] >= HIGH_MAIN and len(fields[m]) >= HIGH_FIELDS else 1 if main_n[m] <= LOW_MAIN and len(fields[m]) <= 1 else 2
        if v != 2:
            out[p['id']] = {'h': hashlib.sha1(p['statement']['tex'].encode('utf-8')).hexdigest()[:12], 'v': v}
    return out


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    content = Path(args[0]) if args else ROOT / 'content'
    out = judge(content)
    text = json.dumps(out, ensure_ascii=False, indent=0) + '\n'
    path = content / 'values.json'
    if '--check' in sys.argv:
        same = path.exists() and path.read_text(encoding='utf-8') == text
        print('頻出度（content/values.json）：', '今の判定と同じ' if same else '古い → python3 tools/make_values.py')
        sys.exit(0 if same else 1)
    path.write_text(text, encoding='utf-8')
    c = defaultdict(int)
    for v in out.values():
        c[v['v']] += 1
    print(f'頻出度：高 {c[3]}問・低 {c[1]}問（ほかは中） → {path}')


if __name__ == '__main__':
    main()
