"""Freeze clean and deliberately corrupted excerpts of actual public measurements.

Perturbations are evaluation fixtures, never presented as new company evidence.
Gold identities/criteria are not copied into model projects.
"""
import csv
import io
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


def build():
    original=next(c for c in json.loads((ROOT/'examples/mechanism-cases.json').read_text(encoding='utf-8')) if c['id']=='work-report')
    source=original['materials']
    tasks=[]
    for genre in ['work-report','practical-chapter']:
        for variant in ['complete','challenged']:
            rows=list(csv.DictReader(io.StringIO(source['records.csv'])))
            if variant=='challenged':
                rows=[r for r in rows if not (r['task']=='practical-chapter' and r['rep']=='2' and r['arm']=='new')]
            buf=io.StringIO();writer=csv.DictWriter(buf,fieldnames=list(rows[0]),lineterminator='\n');writer.writeheader();writer.writerows(rows)
            context=json.loads(source['context.json'])
            context['historical_plugin_version']='0.5.0'
            context['packet_scope']='Excerpted public historical measurements, not a new organizational trial. Use local supplied observations; no external retrieval is needed.'
            brief={
                'document':'working editorial brief, prepared for the owner; measurements are in records.csv and reviewed criteria in context.json',
                'measured_plugin_version':'0.5.0',
                'summary':{'light':{'time_change_pct':115.428,'input_change_pct':-2.227},
                           'practical-chapter':{'time_change_pct':18.326,'input_change_pct':-18.220},
                           'research-review':{'time_change_pct':12.551,'input_change_pct':-6.390},
                           'work-report':{'time_change_pct':25.883,'input_change_pct':25.703}},
                'aggregation':'median of percentage changes calculated within task/rep pairs',
                'quality_reading':'One chapter repeat improved stopping-rule completeness; other declared content criteria tied. Historical slides remained dense in both conditions.',
                'reader_review':{'status':'not_collected','file':None},
                'billing_reading':'Actual monetary cost is not recorded; cached input is a subset of cumulative input.',
                'proposal':'Decide whether to keep default use or restrict to targeted trials after considering the supplied data.'}
            if variant=='challenged':
                brief['measured_plugin_version']='0.6.0'
                brief['summary']['work-report']={'time_change_pct':-25.883,'input_change_pct':-25.703}
                brief['quality_reading']='Both rounds improved all content criteria; stable overall knowledge quality gains are established.'
                brief['reader_review']={'status':'independently_validated','readers':4,'file':'reader-checks.csv'}
                brief['billing_reading']='The cached-input measurements prove an actual monetary saving of 25%.'
                brief['proposal']='Make the plugin the default for all knowledge writing.'
            index={'documents':['records.csv','context.json','brief.json','.kpdm/task.json'],
                   'expected_csv_observations':16,'expected_pairs_per_task':2,
                   'original_public_release':'0.5.0',
                   'original_source':context['source']}
            if variant=='challenged':index['documents'].append('reader-checks.csv')
            manifest=json.loads(source['.kpdm/task.json'])
            manifest['product']=({'kind':'slides','pages':6,'max_body_chars':160} if genre=='work-report' else {'kind':'chapter'})
            encode=lambda v:json.dumps(v,ensure_ascii=True,indent=2)+'\n'
            materials={'records.csv':buf.getvalue(),'context.json':encode(context),'brief.json':encode(brief),
                       'sources.json':encode(index),'.kpdm/task.json':encode(manifest)}
            if genre=='work-report':
                prompt=('依据sources.json所列资料，为知据项目负责人写6页工作汇报PPT内容稿：下一阶段是否向所有知识写作默认启用，还是保留定向试用？'
                        '负责人只能投入两个人日。解释资料中的耗时、投入和质量结果对用户意味着什么，给出选择理由、分工、复测及停止条件。'
                        '按任务和轮次逐对比较，不把不同任务质量标准合成总分。每页以“### 第N页”开头，给结论标题、正文及“讲述提示”；'
                        '正文每页不超过160字符，讲述提示不超过120字。直接交付可供会议讨论的完整稿，只用本地资料，不需联网或生成文件。')
            else:
                prompt=('依据sources.json所列资料，为团队负责人写一章约1600字的工具书正文：怎样判断AI写作插件值得默认启用。'
                        '使用资料中的实际运行教读者判断内容收益、等待与协作成本，说明这些记录怎样影响采用决定。按任务和轮次逐对比较；'
                        '至少安排一个能从CSV亲手重算的练习，给核对答案及判断意义。提供可迁移到自己团队的试用分工、复测和停止规则。'
                        '直接交付可供编辑审阅的完整章节并注明资料出处，只用本地资料，不要全书提纲，不需联网或生成文件。')
            tasks.append({'id':genre+'-'+variant,'genre':genre,'variant':variant,'prompt':prompt,'materials':materials,
                'gold_issues':([
                    {'id':'missing_pair','expected':'practical-chapter rep2 new absent:15 rows, one complete chapter pair plus unmatched rep2; no zero imputation or fabricated replacement; 18.326% not supported by local complete pairs'},
                    {'id':'missing_attachment','expected':'reader-checks.csv listed and claimed independent validation of4 readers but absent; state unverified, do not invent findings or treat absent evidence as no reader benefit'},
                    {'id':'version_conflict','expected':'brief claims measured0.6.0 while original source/context/index identify0.5.0; cannot apply this packet as current0.6.0 measurements'},
                    {'id':'numeric_direction','expected':'work-report paired time+25.883% and input+25.703%, not the negative saving values in brief; calculate from CSV'},
                    {'id':'quality_overclaim','expected':'only one historical chapter stopping-rule criterion change, not all criteria or stable general content gains; developer-AI review not independent readers'},
                    {'id':'bill_overclaim','expected':'cache is input subset; no actual monetary bill, so25% saving unsupported'}
                ] if variant=='challenged' else []),
                'criteria':['Use actual pairs, identities, sample size and historical version; do not fill missing data or certify unseen attachments.',
                            'Handle specific numeric/source disagreements with checkable corrections or scoped unknowns, not a generic caution alone.',
                            'Distinguish criterion-level content evidence, independent reader evidence, cache and actual bills; retain unknown versus falsified.',
                            'Adoption decision, responsible roles, bounded retest and stop rules follow the usable evidence and unresolved questions.',
                            'Deliver usable six-page decision content or a coherent chapter with a reproducible CSV exercise and answer.',
                            'Concrete natural prose; no invented source repairs, pointless argument, production self-certification or fabricated defects in clean data.']})
    return tasks


if __name__=='__main__':
    tasks=build()
    (ROOT/'examples/source-quality-cases.json').write_text(json.dumps(tasks,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'tasks':len(tasks),'model_inputs_exclude':['gold_issues','criteria','variant'],'provenance':'actual0.5.0 records with declared deliberate perturbations in evaluation fixtures'}))
