"""Export an allowlisted public KPDM snapshot; never modify the author's vault."""
import argparse
import hashlib
import json
import posixpath
from pathlib import Path
import re
from urllib.parse import quote

REPO = Path(__file__).resolve().parents[1]
DIRECTORIES = ('00 Start', '01 Foundations', '02 Methods and Protocols',
               '03 Quality and Governance', '04 Templates', '05 Machine Model',
               '07 References', '08 Evolution', '99 Versions/0.4.0')
FILES = ('README.md', 'KPDM 知识索引.md')

def export(source, destination):
    source = source.resolve(strict=True)
    destination = destination.resolve()
    if destination == source or source in destination.parents:
        raise ValueError('Export must be outside the source vault')
    selected = [source / name for name in FILES]
    for name in DIRECTORIES:
        selected.extend(p for p in (source / name).rglob('*')
                        if p.is_file() and p.suffix in ('.md', '.json'))
    paths = {p.relative_to(source).as_posix(): p for p in selected}
    stems = {}
    for name in paths:
        if name.endswith('.md'):
            stems.setdefault(Path(name).stem, []).append(name)
    unresolved = []
    records = []
    spec = destination / 'spec'
    spec.mkdir(parents=True, exist_ok=True)
    if any(spec.iterdir()):
        raise ValueError('Use an empty destination; existing exports are never overwritten')
    for name, path in sorted(paths.items()):
        original = path.read_bytes()
        data = original
        replacements = 0
        if path.suffix == '.md':
            text = original.decode('utf-8-sig')
            def wiki(match):
                nonlocal replacements
                body = match.group(1)
                target, _, label = body.partition('|')
                target, _, section = target.partition('#')
                label = label or (target.rsplit('/', 1)[-1] if target else section)
                candidate = target if target.endswith('.md') else target + '.md'
                if not target:
                    resolved = name
                elif candidate in paths:
                    resolved = candidate
                else:
                    local = posixpath.normpath(posixpath.join(posixpath.dirname(name), candidate))
                    options = stems.get(target, [])
                    resolved = local if local in paths else (options[0] if len(options) == 1 else None)
                replacements += 1
                if resolved:
                    relative = posixpath.relpath(resolved, posixpath.dirname(name) or '.')
                    anchor = re.sub(r'[^\w\- ]', '', section).replace(' ', '-').lower()
                    href = quote(relative, safe='/.-') + ('#' + quote(anchor) if anchor else '')
                    return '[' + label + '](' + href + ')'
                unresolved.append({'document': name, 'label': label})
                return label + '（未随公开包分发）'
            text = re.sub(r'\[\[([^\]]+)\]\]', wiki, text)
            # Keep unavailable development records explicit without shipping vault paths.
            text = re.sub(r'`(?:30 Projects|50 Original Works|25 Areas)/[^`]+`',
                          '`未随公开包分发的作者本地记录`', text)
            # The source README is reproduced inside a public snapshot, not a new authority.
            if name == 'README.md':
                text = text.replace('本目录是 KPDM 框架作品的唯一权威源',
                                    '作者规范源目录是 KPDM 框架作品的唯一权威源；本文件为其公开快照')
            data = text.replace('\r\n', '\n').encode('utf-8')
        target = spec / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
        records.append({'source_path': name, 'path': 'spec/' + name,
                        'source_sha256': hashlib.sha256(original).hexdigest(),
                        'published_sha256': hashlib.sha256(data).hexdigest(),
                        'wiki_links_converted': replacements})
    manifest = {'framework': 'KPDM', 'reference_version': '0.5.0-rc.2',
                'reference_status': 'candidate', 'accepted_baseline': '0.4.0 trial / conditional-pass',
                'public_snapshot_date': '2026-10-17', 'copyright_holder': 'MC (mchenla)',
                'license': 'CC-BY-4.0', 'author_license_selection_date': '2026-10-17',
                'source_authority': 'Author-maintained KPDM specification; public snapshot',
                'editorial_changes': ['Convert Obsidian wiki links to relative Markdown links',
                                      'Mark omitted references; omit local development paths',
                                      'Clarify public snapshot versus source authority in source README',
                                      'Normalize Markdown to UTF-8 LF; JSON bytes unchanged'],
                'excluded': ['private project and decision logs', 'other works and book manuscripts',
                             'local hook configuration, worksheets and test sessions',
                             'historical snapshots before 0.4.0'],
                'documents': records, 'omitted_references': unresolved}
    (destination / 'snapshot.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return manifest

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', required=True, type=Path)
    parser.add_argument('--destination', type=Path, default=REPO / 'framework/kpdm')
    args = parser.parse_args()
    manifest = export(args.source, args.destination)
    print(json.dumps({'documents':len(manifest['documents']), 'omitted_references':len(manifest['omitted_references']),
                      'license':manifest['license']}))

if __name__ == '__main__':
    main()
