"""Check public snapshot integrity, JSON syntax and contained Markdown file links."""
import hashlib
import json
from pathlib import Path
import re
from urllib.parse import unquote, urlsplit

REPO = Path(__file__).resolve().parents[1]

def check(repo=REPO):
    framework = repo / 'framework/kpdm'
    manifest = json.loads((framework / 'snapshot.json').read_text(encoding='utf-8'))
    assert manifest['license'] == 'CC-BY-4.0'
    assert manifest['reference_version'] == '0.5.0-rc.2' and manifest['reference_status'] == 'candidate'
    assert manifest['accepted_baseline'] == '0.4.0 trial / conditional-pass'
    tracked = set()
    for item in manifest['documents']:
        path = (framework / item['path']).resolve(strict=True)
        assert framework.resolve() in path.parents, item
        assert path not in tracked, item
        tracked.add(path)
        data = path.read_bytes()
        assert hashlib.sha256(data).hexdigest() == item['published_sha256'], str(path)
        if path.suffix == '.json':
            json.loads(data)
            assert item['source_sha256'] == item['published_sha256'], item
        else:
            text = data.decode('utf-8')
            assert '[[' not in text, str(path)
            assert not re.search(r'\b[A-Za-z]:[\\/]|obsidian://|30 Projects/|50 Original Works/|25 Areas/', text), str(path)
    assert tracked == {p.resolve() for p in (framework / 'spec').rglob('*') if p.is_file()}
    consulted = json.loads((repo / 'policy/source-map.json').read_text(encoding='utf-8'))
    sources = {item['source_path']:item for item in manifest['documents']}
    for item in consulted['documents']:
        assert item['sha256'] == sources[item['path']]['source_sha256'], item
        assert (repo / item['public_path']).is_file(), item
    checked_links = 0
    docs = list(framework.rglob('*.md')) + [repo / 'skills/knowtether/SKILL.md']
    for doc in docs:
        for href in re.findall(r'\[[^\]]*\]\(([^)]+)\)', doc.read_text(encoding='utf-8')):
            parsed = urlsplit(href)
            if parsed.scheme or not parsed.path:
                continue
            target = (doc.parent / unquote(parsed.path)).resolve()
            assert target == repo.resolve() or repo.resolve() in target.parents, (str(doc), href)
            assert target.exists(), (str(doc), href)
            checked_links += 1
    assert 'Attribution 4.0 International' in (framework / 'LICENSE').read_text(encoding='utf-8')
    return {'framework_documents': len(tracked), 'local_file_links_checked':checked_links,
            'json_content_unchanged':True, 'license':'CC-BY-4.0'}

if __name__ == '__main__':
    print(json.dumps(check()))
