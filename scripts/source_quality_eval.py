"""Three-arm frozen source-quality pilot using the released, route-fixed0.6.0.

One already normally trusted isolated HOME. No credential copying or trust edits.
Only config flag switching is temporary; all articles/attempts are retained.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import random
import subprocess

from live_codex_eval import run_case
from paired_codex_eval import switch_config
from integration_eval import runtime_paths

RUNTIME='4b6b8809392ae44c61bdfa44e7e53dff5690ed0c'


def schedule(tasks):
    rng=random.Random(610018);blocks=[]
    for task in tasks:
        first=['off','lean','full'];rng.shuffle(first)
        blocks.extend([{'task':task['id'],'rep':1,'arms':first},
                       {'task':task['id'],'rep':2,'arms':list(reversed(first))}])
    rng.shuffle(blocks)
    # Neutral directories prevent citation paths exposing conditions in review.
    ids=list(range(1,25));rng.shuffle(ids)
    for block in blocks:
        block['runs']=[{'arm':arm,'id':f'S{ids.pop():03d}'} for arm in block.pop('arms')]
    return blocks


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for k in ['home','bundle','output']:p.add_argument('--'+k,type=Path,required=True)
    p.add_argument('--codex',required=True);p.add_argument('--resume',action='store_true')
    a=p.parse_args();home=a.home.resolve(strict=True);bundle=a.bundle.resolve(strict=True);base=a.output.resolve()
    if home==(Path.home()/'.codex').resolve() or base.exists()!=a.resume:p.error('Use an isolated trusted home and fresh output, or explicit --resume')
    repo=Path(__file__).resolve().parents[1]
    # Runtime must match the actual released Git blobs, not this working tree.
    for name in runtime_paths(repo,RUNTIME):assert (bundle/name).read_bytes()==subprocess.check_output(['git','show',RUNTIME+':'+name],cwd=repo),name
    raw=(repo/'examples/source-quality-cases.json').read_bytes();tasks=json.loads(raw);plan=schedule(tasks)
    protocol={'runtime_commit':RUNTIME,'version':'0.6.0','tasks_sha256':hashlib.sha256(raw).hexdigest(),
              'model':'gpt-6.1-sol','effort':'medium','web_search':'disabled','seed':610018,
              'design':'2 genres x complete/challenged packet x3 arms x2 reversed-order repetitions=24 outputs; serial fresh readonly projects',
              'arms':{'off':'whole plugin disabled','lean':'route-fixed0.6.0, evidence:false','full':'same0.6.0, explicit manifest arithmetic enabled'},
              'scope':'actual public historical data plus deliberate evaluation perturbations; not observations of new company defects',
              'review':'neutral directories, randomized IDs and path-sanitized full text; development AI, no independent human or strict blind claim',
              'primary':'specific issues identified, corrected/scoped and reflected in decision/exercise; clean false findings; six frozen content criteria, no total quality score',
              'secondary':'wall/host/hook/tool durations, actual injected characters, cumulative/last input and cache, source reads and delivered product',
              'schedule':plan,'planned_outputs':24}
    base.mkdir(parents=True,exist_ok=a.resume)
    if a.resume:
        assert json.loads((base/'protocol.json').read_text())==protocol
        assert (base/'frozen-cases.json').read_bytes()==raw
    else:
        (base/'protocol.json').write_text(json.dumps(protocol,indent=2),encoding='utf-8');(base/'frozen-cases.json').write_bytes(raw)
    config=home/'config.toml';original=config.read_text(encoding='utf-8')
    env=dict(os.environ,CODEX_HOME=str(home),PYTHONUTF8='1',KNOWTETHER_CONTROLLED_EVAL='1')
    results=[]
    try:
        for block in plan:
            task=next(t for t in tasks if t['id']==block['task'])
            for item in block['runs']:
                arm=item['arm'];config.write_text(switch_config(original,arm!='off'),encoding='utf-8',newline='\n')
                case={'id':item['id'],'prompt':task['prompt'],'web_search':'disabled','materials':dict(task['materials'])}
                case['materials']['.kpdm/config.json']=json.dumps({'schema_version':1,'evidence':arm=='full'})
                folder=base/item['id'];saved=folder/'summary.json'
                if saved.exists():
                    assert a.resume
                    result=json.loads(saved.read_text(encoding='utf-8'))
                    incoming=json.loads((folder/'input.json').read_text(encoding='utf-8'))
                    assert incoming==case and result['model']=='gpt-6.1-sol' and result['plugin_enabled']==(arm!='off')
                    assert result['materials_unchanged'] and not result['project_files']
                    assert (folder/'output.md').read_text(encoding='utf-8')
                    for n,h in result['provided_files_sha256'].items():assert hashlib.sha256((folder/'project'/n).read_bytes()).hexdigest()==h
                else:
                    result=run_case(a.codex,base,case,'gpt-6.1-sol',env=env,enabled=arm!='off')
                result.update(task=task['id'],genre=task['genre'],variant=task['variant'],arm=arm,repetition=block['rep'],runtime_commit=RUNTIME)
                assert result['materials_unchanged'] and not result['project_files']
                (folder/'summary.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
                results.append(result);(base/'progress.json').write_text(json.dumps(results,indent=2),encoding='utf-8')
                print(json.dumps({'completed':item['id'],'n':len(results),'planned':24,'seconds':result['elapsed_seconds'],'hook_ms':result['timing']['hook_milliseconds']}),flush=True)
    finally:config.write_text(original,encoding='utf-8',newline='\n')


if __name__=='__main__':main()
