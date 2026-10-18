"""Frozen light old/new/off benchmark and complex new/off writing comparison.

Requires a prepared isolated home and two local marketplace fixtures. Uses its
existing login normally; never copies credentials or grants trust. Serially
changes only that home's marketplace source/plugin flag and restores config.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import random
import re
import subprocess

from live_codex_eval import run_case
from paired_codex_eval import switch_config


def market_source(text, source):
    pattern = r'(?ms)(^\[marketplaces\.knowtether\][ \t]*\n)(.*?)(?=^\[|\Z)'
    def replace(match):
        body, count = re.subn(r'(?m)^source[ \t]*=.*$', lambda _: "source = '" + str(source) + "'", match[2])
        if count != 1:
            raise ValueError('Expected one isolated local marketplace source')
        return match[1] + body
    value, count = re.subn(pattern, replace, text)
    if count != 1:
        raise ValueError('Expected isolated knowtether marketplace')
    return value


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--home', type=Path, required=True)
    parser.add_argument('--old-market', type=Path, required=True)
    parser.add_argument('--new-market', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--codex', required=True)
    args = parser.parse_args()
    home = args.home.resolve(strict=True)
    base = args.output.resolve()
    if base.exists() or home == (Path.home()/'.codex').resolve():
        parser.error('Use an isolated home and a new output directory')
    repo = Path(__file__).resolve().parents[1]
    raw = (repo/'examples/complex-work-cases.json').read_bytes()
    tasks = json.loads(raw)
    source = (repo/'examples/knowledge-work-sources.md').read_text(encoding='utf-8')
    schedule=[]
    rng=random.Random(20261018)
    for task in tasks:
        if task['id']=='light':
            first=['off','old','new'];rng.shuffle(first)
            for rep, order in enumerate((first,list(reversed(first))),1):
                schedule.append({'task':task['id'],'rep':rep,'arms':order})
        else:
            first=rng.choice([['new','off'],['off','new']])
            schedule += [{'task':task['id'],'rep':1,'arms':first},
                         {'task':task['id'],'rep':2,'arms':list(reversed(first))}]
    rng.shuffle(schedule)
    base.mkdir(parents=True)
    protocol={'model':'gpt-6.1-sol','effort':'medium','web_search':'disabled','seed':20261018,
              'tasks_sha256':hashlib.sha256(raw).hexdigest(),'source_sha256':hashlib.sha256(source.encode()).hexdigest(),
              'schedule':schedule,'planned_valid_outputs':18,
              'review':'frozen task criteria; condition-label-masked development-AI review, no independent human claim',
              'primary':'source support, synthesis, calibrated conclusions, usable decisions/methods; punctuation excluded from quality ranking',
              'secondary':'wall time, cumulative and cached input, actual context, tool calls, fulfillment, overprocessing',
              'scope':'real published research in a fixed excerpt packet, not autonomous full literature search or actual audience validation'}
    (base/'protocol.json').write_text(json.dumps(protocol,indent=2),encoding='utf-8')
    (base/'frozen-tasks.json').write_bytes(raw)
    (base/'sources.md').write_text(source,encoding='utf-8',newline='\n')
    config=home/'config.toml';original=config.read_text(encoding='utf-8')
    env=dict(os.environ,CODEX_HOME=str(home),PYTHONUTF8='1',KNOWTETHER_CONTROLLED_EVAL='1')
    results=[]
    try:
        for block in schedule:
            task=next(t for t in tasks if t['id']==block['task'])
            for arm in block['arms']:
                market=(args.old_market if arm=='old' else args.new_market).resolve(strict=True)
                config.write_text(market_source(original,market),encoding='utf-8',newline='\n')
                setup=subprocess.run([args.codex,'plugin','add','knowtether@knowtether','--json'],env=env,
                                     text=True,encoding='utf-8',capture_output=True,timeout=180)
                if setup.returncode:
                    raise RuntimeError(setup.stderr)
                version=json.loads(setup.stdout)['version']
                assert version==('0.4.1' if arm=='old' else '0.5.0')
                current=config.read_text(encoding='utf-8')
                config.write_text(switch_config(current,arm!='off'),encoding='utf-8',newline='\n')
                case=dict(task,id=f"{task['id']}-r{block['rep']}-{arm}",web_search='disabled')
                if task['id']!='light':
                    case['materials']={'sources.md':source}
                result=run_case(args.codex,base,case,'gpt-6.1-sol',env=env,enabled=arm!='off')
                result.update(arm=arm,task=task['id'],repetition=block['rep'],plugin_version=version)
                assert result['materials_unchanged']
                (base/case['id']/'summary.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
                results.append(result)
                (base/'progress.json').write_text(json.dumps(results,indent=2),encoding='utf-8')
                print(json.dumps({'completed':case['id'],'seconds':result['elapsed_seconds'],
                                  'context':result['context_characters'],'tools':len(result['tool_items'])}),flush=True)
    finally:
        config.write_text(original,encoding='utf-8',newline='\n')
    print(json.dumps({'completed':len(results)}),flush=True)


if __name__=='__main__':
    main()
