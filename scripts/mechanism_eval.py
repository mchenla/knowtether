"""Four-arm frozen writing comparison. Requires two normally trusted isolated homes."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import random
import subprocess

from adaptive_work_eval import market_source
from paired_codex_eval import switch_config
from live_codex_eval import run_case


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ['old-home','new-home','old-market','new-market','output']:
        parser.add_argument('--'+name,type=Path,required=True)
    parser.add_argument('--codex',required=True)
    args=parser.parse_args()
    base=args.output.resolve()
    homes={'old':args.old_home.resolve(strict=True),'new':args.new_home.resolve(strict=True)}
    if base.exists() or any(p==(Path.home()/'.codex').resolve() for p in homes.values()) or homes['old']==homes['new']:
        parser.error('Use a new output directory and two distinct isolated homes')
    repo=Path(__file__).resolve().parents[1]
    raw=(repo/'examples/mechanism-cases.json').read_bytes();tasks=json.loads(raw)
    rng=random.Random(606018);schedule=[]
    for task in tasks:
        first=['off','old','lean','new'];rng.shuffle(first)
        schedule.extend([{'task':task['id'],'rep':1,'arms':first},{'task':task['id'],'rep':2,'arms':list(reversed(first))}])
    rng.shuffle(schedule)
    base.mkdir(parents=True)
    protocol={'tasks_sha256':hashlib.sha256(raw).hexdigest(),'model':'gpt-6.1-sol','effort':'medium','web_search':'disabled',
              'arms':{'off':'whole plugin disabled','old':'0.5.0','lean':'0.6.0 fast launcher and compact normative reading, evidence compiler off','new':'0.6.0 including opt-in evidence compiler and product hints'},
              'design':'two task genres x two reversed-order repeats x four arms = 16 valid outputs; serial fresh readonly projects',
              'source_scope':'real previously published plugin measurements, not invented company observations; ASCII source packets identical in all arms',
              'primary':'source/number fidelity, argument, concrete decision/reader exercise usability; no overall quality score',
              'review':'condition-label-masked development AI against frozen six criteria per task; not independent or real reader testing',
              'secondary':'full wall time incl synchronous hooks, hook/tool durations, input/cache, fulfillment and product budget',
              'schedule':schedule,'planned_valid_outputs':16,'seed':606018}
    (base/'protocol.json').write_text(json.dumps(protocol,indent=2),encoding='utf-8')
    (base/'frozen-cases.json').write_bytes(raw)
    original={k:(v/'config.toml').read_text(encoding='utf-8') for k,v in homes.items()}
    results=[]
    try:
        for block in schedule:
            task=next(t for t in tasks if t['id']==block['task'])
            for arm in block['arms']:
                side='old' if arm in ('old','off') else 'new';home=homes[side]
                market=(args.old_market if side=='old' else args.new_market).resolve(strict=True)
                config=home/'config.toml'
                config.write_text(market_source(original[side],market),encoding='utf-8',newline='\n')
                env=dict(os.environ,CODEX_HOME=str(home),PYTHONUTF8='1',KNOWTETHER_CONTROLLED_EVAL='1')
                setup=subprocess.run([args.codex,'plugin','add','knowtether@knowtether','--json'],env=env,text=True,encoding='utf-8',capture_output=True,timeout=180,check=True)
                version=json.loads(setup.stdout)['version'];assert version==('0.5.0' if side=='old' else '0.6.0')
                config.write_text(switch_config(config.read_text(encoding='utf-8'),arm!='off'),encoding='utf-8',newline='\n')
                case=dict(task,id=f"{task['id']}-r{block['rep']}-{arm}",web_search='disabled',materials=dict(task['materials']))
                case['materials']['.kpdm/config.json']=json.dumps({'schema_version':1,'evidence':arm!='lean'})
                result=run_case(args.codex,base,case,'gpt-6.1-sol',env=env,enabled=arm!='off')
                result.update(arm=arm,task=task['id'],repetition=block['rep'],plugin_version=version)
                assert result['materials_unchanged'] and not result['project_files']
                (base/case['id']/'summary.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
                results.append(result);(base/'progress.json').write_text(json.dumps(results,indent=2),encoding='utf-8')
                print(json.dumps({'completed':case['id'],'seconds':result['elapsed_seconds'],'hook_ms':result['timing']['hook_milliseconds'],'tools':len(result['tool_items'])}),flush=True)
    finally:
        for side,home in homes.items():(home/'config.toml').write_text(original[side],encoding='utf-8',newline='\n')
    print(json.dumps({'completed':len(results)}),flush=True)


if __name__=='__main__':main()
