"""Validate every planned run, then create a path-sanitized condition-masked review.

Does not grade content or silently rewrite any original output.
"""
import argparse
import hashlib
import json
from pathlib import Path
import random
import re
import subprocess
import sys


def sanitize_answer(answer, project):
    native=str(project.resolve())
    for prefix in {native+'\\',native+'/',native.replace('\\','/')+'/'}:
        answer=answer.replace(prefix,'')
    return answer


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('run',type=Path);p.add_argument('--bundle',type=Path,required=True)
    a=p.parse_args();base=a.run.resolve(strict=True);bundle=a.bundle.resolve(strict=True)
    protocol=json.loads((base/'protocol.json').read_text())
    raw=(base/'frozen-cases.json').read_bytes();assert hashlib.sha256(raw).hexdigest()==protocol['tasks_sha256']
    tasks={t['id']:t for t in json.loads(raw)};rows=[]
    for block in protocol['schedule']:
        task=tasks[block['task']]
        for run in block['runs']:
            folder=base/run['id'];r=json.loads((folder/'summary.json').read_text(encoding='utf-8'))
            incoming=json.loads((folder/'input.json').read_text(encoding='utf-8'));arm=run['arm']
            expected=dict(task['materials']);expected['.kpdm/config.json']=json.dumps({'schema_version':1,'evidence':arm=='full'})
            assert incoming=={'id':run['id'],'prompt':task['prompt'],'web_search':'disabled','materials':expected}
            assert r['runtime_commit']==protocol['runtime_commit'] and r['arm']==arm
            assert r['model']==protocol['model'] and r['effort']=='medium' and r['materials_unchanged'] and not r['project_files']
            for name,content in expected.items():assert (folder/'project'/name).read_bytes()==content.encode('utf-8')
            assert not [f for f in (folder/'project').rglob('*') if f.is_file() and f.relative_to(folder/'project').as_posix() not in expected]
            events=[json.loads(line) for line in (folder/'events.jsonl').read_text(encoding='utf-8').splitlines()]
            inv=events[0]['condition_inventory'];assert inv['enabled']==(arm!='off')
            turns=[e for e in events if e.get('method')=='turn/completed'];assert len(turns)==1 and turns[0]['params']['turn']['status']=='completed'
            hooks=[e['params']['run'] for e in events if e.get('method')=='hook/completed']
            if arm=='off':assert not hooks and not inv['active_knowtether_skills']
            else:
                assert len(hooks)==3 and all(h['status']=='completed' for h in hooks)
                code="import sys,json;sys.path.insert(0,sys.argv[1]);from pathlib import Path;from kpdm_hooks.hooks import handle;print(json.dumps(handle(json.loads(sys.stdin.read()),Path(sys.argv[2]),'UserPromptSubmit',plugin=True)))"
                wanted=json.loads(subprocess.check_output([sys.executable,'-I','-B','-c',code,str(bundle),str(folder/'project')],input=json.dumps({'hook_event_name':'UserPromptSubmit','prompt':task['prompt']}),text=True,encoding='utf-8'))['hookSpecificOutput']['additionalContext']
                contexts=[entry['text'] for h in hooks if h.get('eventName')=='userPromptSubmit' for entry in h['entries'] if entry['kind']=='context']
                assert contexts==[wanted] and '"tier": "focused"' in wanted
                assert ('PROJECT_EVIDENCE' in wanted)==(arm=='full')
                if arm=='full':assert '"status":"ready"' in wanted
                assert r['context_characters']==sum(len(e['text']) for h in hooks for e in h['entries'] if e['kind']=='context')
            answer=(folder/'output.md').read_text(encoding='utf-8');assert answer
            r['output_sha256']=hashlib.sha256(answer.encode()).hexdigest()
            usage=[e['params']['tokenUsage'] for e in events if e.get('method')=='thread/tokenUsage/updated' and e['params'].get('tokenUsage',{}).get('total',{}).get('inputTokens',0)>0]
            r['first_observed_request_usage']=usage[0]['last'] if usage else None
            tools=[e['params']['item'] for e in events if e.get('method')=='item/completed' and e['params']['item']['type']=='commandExecution']
            text='\n'.join(str(t.get('command','')) for t in tools).replace('\\','/')
            assert not re.search(r'source-quality-(?:reference|cases)\.json|gold_issues|frozen-cases\.json|protocol\.json',text),'gold access'
            r['source_read_command_counts']={n:sum(n in str(t.get('command','')) for t in tools) for n in ['records.csv','context.json','brief.json','sources.json','reader-checks.csv','SKILL.md']}
            r['hook_context_sha256']=[hashlib.sha256(e['text'].encode()).hexdigest() for h in hooks for e in h['entries'] if e['kind']=='context']
            rows.append(r)
    assert len(rows)==protocol['planned_outputs']
    shuffled=list(rows);random.Random(610122).shuffle(shuffled);packet=[];mapping={}
    for i,r in enumerate(shuffled,1):
        label=f'R{i:02d}';mapping[label]=r['case'];task=tasks[r['task']]
        answer=(base/r['case']/'output.md').read_text(encoding='utf-8')
        sanitized=sanitize_answer(answer,base/r['case']/'project')
        assert not re.search(r'C:[/\\]Users[/\\]|AppData[/\\]|kt061-source-quality|[/\\]S\d{3}[/\\]',sanitized)
        packet.append({'id':label,'genre':r['genre'],'variant':r['variant'],'gold_issues':task['gold_issues'],
                       'criteria':task['criteria'],'answer':sanitized,'original_sha256':r['output_sha256']})
    for name,data in [('validated-results.json',rows),('private-mapping.json',mapping),('masked-review.json',packet)]:
        (base/name).write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8',newline='\n')
    print(json.dumps({'validated':len(rows),'actual_focused_context':True,'unchanged_materials':True,'masked_review':'pending','path_labels_removed_before_reading':True}))


if __name__=='__main__':main()
