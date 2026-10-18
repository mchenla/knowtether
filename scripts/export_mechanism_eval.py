"""Export allowlisted pilot results after the per-draft review has been frozen.

No auth, thread identifiers, host transcripts or private project paths exported.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import statistics


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('run',type=Path)
    args=parser.parse_args();base=args.run.resolve(strict=True)
    repo=Path(__file__).resolve().parents[1]
    raw=(base/'masked-review-frozen.json').read_bytes()
    digest=hashlib.sha256(raw).hexdigest()
    assert digest==(base/'masked-review-frozen.sha256').read_text().strip()
    review=json.loads(raw);mapping=json.loads((base/'private-mapping.json').read_text())
    reviewed={mapping[r['id']]:r for r in review['rows']}
    runs=json.loads((base/'validated-results.json').read_text())
    rows=[];answers=[]
    for r in runs:
        name=r['case'];answer=(base/name/'output.md').read_text(encoding='utf-8')
        assert hashlib.sha256(answer.encode()).hexdigest()==r['output_sha256']
        public=re.sub(re.escape(str((base/name/'project').resolve()).replace('\\','/'))+'/', '',answer.replace('\\','/'))
        assert not re.search(r'C:/Users/|AppData/|kt060-results/',public)
        answers.append({'case':name,'original_sha256':r['output_sha256'],
                        'published_sha256':hashlib.sha256(public.encode()).hexdigest(),'answer':public})
        keys=['case','task','arm','repetition','model','effort','plugin_version','plugin_enabled',
              'elapsed_seconds','timing','context_characters','output_characters','hook_events',
              'reading_pack_complete','provided_files_sha256','materials_unchanged','project_files','output_sha256']
        row={k:r[k] for k in keys}
        row.update(token_usage=r['token_usage'],tool_count=len(r['tool_items']),
                   review_id=reviewed[name]['id'],criteria_review=reviewed[name]['criteria_review'],
                   chinese_characters=len(re.findall(r'[\u4e00-\u9fff]',answer)))
        if name=='work-report-r1-off':row['timing_possible_setup_overlap']=True
        rows.append(row)
    groups=[]
    for task in ['work-report','practical-chapter']:
        for arm in ['off','old','lean','new']:
            selected=[r for r in rows if r['task']==task and r['arm']==arm]
            med=statistics.median
            groups.append({'task':task,'arm':arm,'n':len(selected),
                'wall_seconds_median':med(r['elapsed_seconds'] for r in selected),
                'hook_milliseconds_median':med(r['timing']['hook_milliseconds'] for r in selected),
                'context_characters_median':med(r['context_characters'] for r in selected),
                'input_tokens_median':med(r['token_usage']['total']['inputTokens'] for r in selected),
                'cached_input_tokens_median':med(r['token_usage']['total']['cachedInputTokens'] for r in selected)})
    value={'software_runtime_commit':'0ec2d108c34396badaccc3cfb79fea84fb0b7470',
           'runtime_scope':'pre-release pilot before the final source-path routing and ordinary-code Stop fixes; not an effect test of those fixes',
           'protocol':json.loads((base/'protocol.json').read_text()),
           'frozen_cases':'mechanism-pilot-0.6.0.json',
           'review':{k:v for k,v in review.items() if k!='rows'},'review_frozen_sha256':digest,
           'independent_decimal_reference':json.loads((base/'reference-decimal.json').read_text()),
           'incidents':[
               'Initial off answer retained byte-for-byte; Windows provided-path accounting repaired without regenerating text.',
               'One resume process failed before model initialization/output; subsequent normal resume completed the frozen schedule.',
               'A normally reviewed hook setup CLI turn may have overlapped first off timing; report the timing sensitivity separately.',
               'Before reading answers, generator found to impute unmeasured work-report long_dash_ranges as zero. Six report drafts repeat it. Do not credit these as observed formatting evidence. Time/input and compiler-declared metrics unaffected. Corrected future examples omit the column.',
               'Citation paths leaked condition names during initial development review; not a strict blind or independent review.',
               'Both task prompts contained a .kpdm source path and a complete-draft phrase; old broad route regex selected full reading. Normative context is the same across old/lean here. Fixed after pilot, without rewriting results.'
           ],'group_medians':groups,'records':rows,
           'limitations':['two repeats per genre; local own-project materials',
                          'no real readers, independent domain review or general quality effect established',
                          'manual source/manifest preparation and human review time excluded',
                          'cumulative input includes cache and repeated tool turns; not monetary cost',
                          'no model semantic checker or automatic second revision pass']}
    for name,data in [('mechanism-0.6.0-results.json',value),('mechanism-0.6.0-answers.json',
        {'redaction':'Only local project absolute path prefixes in citations removed. Original and published answer hashes both retained; no prose editing.','records':answers})]:
        (repo/'examples'/name).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'exported':len(rows),'review_frozen_sha256':digest,'private_paths':False}))


if __name__=='__main__':main()
