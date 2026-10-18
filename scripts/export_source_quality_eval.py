"""Export all24 outputs and allowlisted metrics after per-output review freeze.

Issue handling is reported by specific issue, never merged into a quality score.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import statistics

from summarize_source_quality_eval import sanitize_answer


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('run',type=Path);a=p.parse_args()
    base=a.run.resolve(strict=True);repo=Path(__file__).resolve().parents[1]
    raw=(base/'review-frozen.json').read_bytes();digest=hashlib.sha256(raw).hexdigest()
    assert digest==(base/'review-frozen.sha256').read_text().strip()
    review=json.loads(raw);packet=json.loads((base/'masked-review.json').read_text(encoding='utf-8'))
    assert review['packet_sha256']==hashlib.sha256((base/'masked-review.json').read_bytes()).hexdigest()
    mapping=json.loads((base/'private-mapping.json').read_text());frozen={r['id']:r for r in packet}
    assert set(frozen)=={r['id'] for r in review['records']} and len(frozen)==24
    by={mapping[r['id']]:r for r in review['records']}
    for label,r in [(r['id'],r) for r in review['records']]:
        assert len(r['criteria_review'])==6
        assert all(c['grade'] in ['usable','partial','unmet'] and c['reason'] for c in r['criteria_review'])
        assert {i['id'] for i in r['issue_review']}=={i['id'] for i in frozen[label]['gold_issues']}
        assert all(i['status'] in ['unaddressed','located','handled'] and i['reason'] for i in r['issue_review'])
        assert isinstance(r['false_findings'],list)
    rows=[];answers=[]
    results=json.loads((base/'validated-results.json').read_text(encoding='utf-8'))
    for r in results:
        case=r['case'];answer=(base/case/'output.md').read_text(encoding='utf-8')
        assert hashlib.sha256(answer.encode()).hexdigest()==r['output_sha256']
        public=sanitize_answer(answer,base/case/'project')
        assert not re.search(r'C:[/\\]Users[/\\]|AppData[/\\]|kt061-source-quality',public)
        row={k:r[k] for k in ['case','task','genre','variant','arm','repetition','runtime_commit','model','effort',
            'elapsed_seconds','timing','context_characters','output_characters','hook_events','reading_pack_complete',
            'materials_unchanged','project_files','provided_files_sha256','output_sha256','token_usage',
            'first_observed_request_usage','source_read_command_counts','hook_context_sha256']}
        row.update(tool_count=len(r['tool_items']),review_id=by[case]['id'],
                   criteria_review=by[case]['criteria_review'],issue_review=by[case]['issue_review'],
                   false_findings=by[case]['false_findings'],chinese_characters=len(re.findall(r'[\u4e00-\u9fff]',answer)))
        rows.append(row)
        answers.append({'case':case,'review_id':by[case]['id'],'original_sha256':r['output_sha256'],
                        'published_sha256':hashlib.sha256(public.encode()).hexdigest(),'answer':public})
    groups=[];issue_counts=[];contrasts=[];med=statistics.median
    for task in sorted({r['task'] for r in rows}):
        task_rows=[r for r in rows if r['task']==task]
        for arm in ['off','lean','full']:
            selected=[r for r in task_rows if r['arm']==arm];assert len(selected)==2
            groups.append({'task':task,'arm':arm,'n':len(selected),
                'wall_seconds_median':med(r['elapsed_seconds'] for r in selected),
                'hook_milliseconds_median':med(r['timing']['hook_milliseconds'] for r in selected),
                'tool_milliseconds_median':med(r['timing']['tool_milliseconds'] for r in selected),
                'injected_characters_median':med(r['context_characters'] for r in selected),
                'input_tokens_median':med(r['token_usage']['total']['inputTokens'] for r in selected),
                'cached_input_tokens_median':med(r['token_usage']['total']['cachedInputTokens'] for r in selected),
                'first_observed_input_tokens_median':med(r['first_observed_request_usage']['inputTokens'] for r in selected),
                'tool_count_median':med(r['tool_count'] for r in selected),
                'outputs_with_false_findings':sum(bool(r['false_findings']) for r in selected)})
            for issue in sorted({i['id'] for r in selected for i in r['issue_review']}):
                entries=[i for r in selected for i in r['issue_review'] if i['id']==issue]
                issue_counts.append({'task':task,'arm':arm,'issue':issue,'n':len(entries),
                    **{s:sum(i['status']==s for i in entries) for s in ['unaddressed','located','handled']}})
        for baseline,treatment in [('off','lean'),('off','full'),('lean','full')]:
            before={r['repetition']:r for r in task_rows if r['arm']==baseline}
            after={r['repetition']:r for r in task_rows if r['arm']==treatment}
            changes=[100*(after[k]['elapsed_seconds']/before[k]['elapsed_seconds']-1) for k in sorted(before)]
            inputs=[100*(after[k]['token_usage']['total']['inputTokens']/before[k]['token_usage']['total']['inputTokens']-1) for k in sorted(before)]
            contrasts.append({'task':task,'baseline':baseline,'treatment':treatment,'n_pairs':2,
                'wall_paired_changes_pct':changes,'median_paired_wall_change_pct':med(changes),
                'input_paired_changes_pct':inputs,'median_paired_input_change_pct':med(inputs)})
    data={'runtime_commit':results[0]['runtime_commit'],'runtime_version':'0.6.0',
          'protocol':json.loads((base/'protocol.json').read_text()),'frozen_cases':'source-quality-cases.json',
          'review':{k:v for k,v in review.items() if k!='records'},'review_frozen_sha256':digest,
          'read_counts_scope':'Command mentions of each filename, not proof of full reading or comprehension.',
          'group_medians':groups,'paired_performance_contrasts':contrasts,'issue_counts':issue_counts,
          'limitations':['own-project historical data plus deliberate evaluation perturbations; two repeats per task',
                         'development AI authored fixtures and review; randomized IDs do not establish independent or strict blind evaluation',
                         'no real readers, actual bills, human revision time or population effect established',
                         'multiple co-occurring problems do not identify an independent causal effect for each issue',
                         'wall time includes host/tools/hooks/model; input includes cache and multiple requests; not a bill'],
          'records':rows}
    for name,value in [('source-quality-0.6.0-results.json',data),('source-quality-0.6.0-answers.json',
        {'redaction':'Only exact local project path prefixes in citations removed; original and published hashes retained, prose unchanged.','records':answers})]:
        (repo/'examples'/name).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({'exported':len(rows),'review_frozen_sha256':digest,'private_paths_exported':False}))


if __name__=='__main__':main()
