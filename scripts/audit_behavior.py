"""Replay synthetic collaboration examples against the actual advisory checker."""
import json
from pathlib import Path
import sys
import tempfile

REPO=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(REPO))
from kpdm_hooks.engine import knowledge_prompt
from kpdm_hooks.hooks import handle


def audit():
    cases=json.loads((REPO/'examples/behavior-audit.json').read_text(encoding='utf-8'))['cases']
    records=[]
    with tempfile.TemporaryDirectory(prefix='knowtether-behavior-audit-') as temp:
        root=Path(temp)
        for case in cases:
            assert knowledge_prompt(case['text']), case['id']
            response=handle({'hook_event_name':'Stop','session_id':'synthetic-audit',
                             'last_assistant_message':case['text']},root,'Stop',plugin=True)
            records.append({'id':case['id'],'concern':case['concern'],'response':response})
        assert not list(root.iterdir()), 'Advisory checker must not write project files'
    expected={'citation-control':'CITATION_PLACEHOLDER','absolute-control':'ABSOLUTE_CLAIM',
              'status-control':'STATUS_LANGUAGE','style-control':'LANGUAGE_PATTERN'}
    for record in records:
        if record['id'] in expected:
            assert expected[record['id']] in record['response']['systemMessage'], record
    return {'method':'actual Stop handler; plugin mode; synthetic final-message fixtures',
            'limitation':'Not a model behavior or semantic quality evaluation. Silence is not a pass.',
            'project_files_written':False,'records':records}

if __name__=='__main__':
    print(json.dumps(audit(),ensure_ascii=True,indent=2))
