"""Validate all frozen runs and make a condition-masked review packet.

Keeps outputs, reference arithmetic and label mapping local. No semantic grade.
"""
import argparse
import csv
from decimal import Decimal
import hashlib
import io
import json
from pathlib import Path
import random
import re
import subprocess
import sys


def reference(case):
    """Separate Decimal calculation, not a call to the evidence implementation."""
    spec=json.loads(case['materials']['.kpdm/task.json'])['table']
    rows=list(csv.DictReader(io.StringIO(case['materials'][spec['path']])))
    def median(values):
        values=sorted(values);n=len(values)
        return values[n//2] if n%2 else (values[n//2-1]+values[n//2])/2
    result={}
    for group in sorted({r[spec['group']] for r in rows}):
        selected=[r for r in rows if r[spec['group']]==group]
        by={}
        for r in selected:
            key=(r[spec['pair']],r[spec['condition']]);assert key not in by;by[key]=r
        pairs=sorted({k[0] for k in by if (k[0],spec['baseline']) in by and (k[0],spec['treatment']) in by})
        result[group]={}
        for metric in spec['metrics']:
            before=[Decimal(by[p,spec['baseline']][metric]) for p in pairs]
            after=[Decimal(by[p,spec['treatment']][metric]) for p in pairs]
            changes=[100*(a-b)/b for a,b in zip(after,before) if b]
            fmt=lambda n:str(n.quantize(Decimal('.001'))) if n is not None else None
            b,a=median(before),median(after)
            result[group][metric]={'n_pairs':len(pairs),'baseline_median':fmt(b),'treatment_median':fmt(a),
                'paired_changes_pct':{p:fmt(100*(y-x)/x) if x else None for p,x,y in zip(pairs,before,after)},
                'median_paired_change_pct':fmt(median(changes)) if changes else None,
                'ratio_of_group_medians_pct':fmt(100*(a-b)/b) if b else None}
    return result


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('run',type=Path)
    parser.add_argument('--old-bundle',type=Path,required=True)
    parser.add_argument('--new-bundle',type=Path,required=True)
    args=parser.parse_args();base=args.run.resolve(strict=True)
    protocol=json.loads((base/'protocol.json').read_text())
    raw=(base/'frozen-cases.json').read_bytes();assert hashlib.sha256(raw).hexdigest()==protocol['tasks_sha256']
    tasks={r['id']:r for r in json.loads(raw)}
    reference_data={k:reference(v) for k,v in tasks.items()}
    (base/'reference-decimal.json').write_text(json.dumps(reference_data,indent=2),encoding='utf-8')
    rows=[]
    for block in protocol['schedule']:
        for arm in block['arms']:
            name=f"{block['task']}-r{block['rep']}-{arm}";d=base/name
            summary=json.loads((d/'summary.json').read_text(encoding='utf-8'))
            incoming=json.loads((d/'input.json').read_text(encoding='utf-8'))
            assert incoming['prompt']==tasks[block['task']]['prompt']
            expected_files=dict(tasks[block['task']]['materials'])
            expected_files['.kpdm/config.json']=json.dumps({'schema_version':1,'evidence':arm!='lean'})
            assert incoming['materials']==expected_files
            assert summary['provided_files_sha256']=={n:hashlib.sha256(v.encode()).hexdigest() for n,v in expected_files.items()}
            for n,h in summary['provided_files_sha256'].items():assert hashlib.sha256((d/'project'/n).read_bytes()).hexdigest()==h
            assert not [p for p in (d/'project').rglob('*') if p.is_file() and p.relative_to(d/'project').as_posix() not in expected_files]
            events=[json.loads(s) for s in (d/'events.jsonl').read_text(encoding='utf-8').splitlines()]
            inventory=events[0]['condition_inventory'];assert inventory['enabled']==(arm!='off')
            turns=[e for e in events if e.get('method')=='turn/completed'];assert len(turns)==1 and turns[0]['params']['turn']['status']=='completed'
            runs=[e['params']['run'] for e in events if e.get('method')=='hook/completed']
            contexts=[entry['text'] for r in runs if r.get('statusMessage')=='KnowTether: UserPromptSubmit' for entry in r['entries'] if entry['kind']=='context']
            if arm=='off':
                assert not runs and not inventory['active_knowtether_skills']
            else:
                assert len(runs)==3 and all(r['status']=='completed' for r in runs)
                bundle=args.old_bundle if arm=='old' else args.new_bundle
                code="import sys,json;sys.path.insert(0,sys.argv[1]);from pathlib import Path;from kpdm_hooks.hooks import handle;print(json.dumps(handle(json.loads(sys.stdin.read()),Path(sys.argv[2]),'UserPromptSubmit',plugin=True)))"
                event={'hook_event_name':'UserPromptSubmit','prompt':incoming['prompt']}
                expected=json.loads(subprocess.check_output([sys.executable,'-I','-B','-c',code,str(bundle.resolve()),str((d/'project').resolve())],input=json.dumps(event),text=True,encoding='utf-8'))['hookSpecificOutput']['additionalContext']
                assert contexts==[expected],name
                assert ('PROJECT_EVIDENCE' in expected)==(arm=='new')
                if arm=='new':assert '"status":"ready"' in expected
            answer=(d/'output.md').read_text(encoding='utf-8');assert answer
            row=dict(summary,output_sha256=hashlib.sha256(answer.encode()).hexdigest())
            rows.append(row)
    assert len(rows)==protocol['planned_valid_outputs']==16
    retained=json.loads((base/'retained-initial.json').read_text())
    assert hashlib.sha256((base/retained['case']/'output.md').read_bytes()).hexdigest()==retained['output_sha256']
    order=list(rows);random.Random(606122).shuffle(order)
    packets=[];mapping={}
    for i,r in enumerate(order,1):
        label=f'M{i:02d}';mapping[label]=r['case']
        packets.append({'id':label,'task':r['task'],'criteria':tasks[r['task']]['criteria'],
                        'answer':re.sub(re.escape(str((base/r['case']/'project').resolve()).replace('\\','/'))+'/', '',
                                        (base/r['case']/'output.md').read_text(encoding='utf-8').replace('\\','/'))})
    for name,value in [('validated-results.json',rows),('private-mapping.json',mapping),('masked-review.json',packets)]:
        (base/name).write_text(json.dumps(value,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'validated':len(rows),'exact_context':True,'initial_answer_retained':True,'masked_review':'pending'}))


if __name__=='__main__':main()
