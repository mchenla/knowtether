"""Build fixed real-work packets from previously published measurement records.

No invented company observations. ASCII data avoids the earlier shell-encoding
artifact equally in all conditions. Rubrics are not included in model input.
"""
import csv
import io
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    output = ROOT/'examples/mechanism-work'
    output.mkdir(exist_ok=True)
    tasks=[]
    for kind, filename, list_key in [('work-report','adaptive-0.5.0-results.json','records'),
                                      ('practical-chapter','paired-0.4.1-results.json','results')]:
        data=json.loads((ROOT/'examples'/filename).read_text(encoding='utf-8'))
        rows=[r for r in data[list_key] if r.get('arm')!='old']
        stream=io.StringIO(newline='')
        fields=['task','rep','arm','seconds','input_tokens','cached_input_tokens','long_dash_ranges']
        writer=csv.DictWriter(stream,fieldnames=fields,lineterminator='\n');writer.writeheader()
        quality=[]
        for r in sorted(rows,key=lambda r:r['case']):
            usage=r['token_usage']['total']
            writer.writerow(dict(task=r['task'],rep=r['repetition'],arm='new' if r['plugin_enabled'] else 'off',
                                 seconds=r['elapsed_seconds'],input_tokens=usage['inputTokens'],
                                 cached_input_tokens=usage['cachedInputTokens'],long_dash_ranges=r.get('raw_numeric_long_dash_count',0)))
            statuses=[c['grade'] for c in r['criteria_review']] if 'criteria_review' in r else r['masked_review']['statuses']
            codes={'met':'M','满足':'M','部分满足':'P','partial':'P','failed':'F'}
            quality.append({'case':r['case'],'criteria':''.join(codes[s] for s in statuses)})
        version='0.5.0' if kind=='work-report' else '0.4.1'
        context={'source':'https://github.com/mchenla/knowtether/blob/v'+version+'/examples/'+filename,
                 'observations':'Actual previously published Codex runs; fixed gpt-6.1-sol medium, web disabled; two opposite-order repeats per task; all valid completed runs retained.',
                 'quality_review':quality, 'grade_codes':{'M':'met','P':'partially met','F':'failed'},
                 'quality_scope':'Condition-label-masked development AI review, not independent human or reader validation. Different task rubrics are not a common quality scale. All numbers refer to that historical plugin version, not the current runtime.',
                 'measurement':'seconds = full wall time including host/tools/hooks/model; input_tokens = cumulative input including cache; cached_input_tokens is a subset, not monetary cost. Long-dash counts describe one narrow formatting convention, not content quality.',
                 'selection':'0.5.0 old-version arm excluded, retaining off/new pairs.' if kind=='work-report' else 'One quota failure retained in original report; only missing final pair resumed with same model/order after ordinary window recovery. CSV contains the 24 valid final runs, not the failed attempt.',
                 'constraints':'No real target readers, organizational ROI, generic factual accuracy rate or stable treatment effect was measured.'}
        context['criterion_order'] = {
            'light':['three concrete actions','no overprocessing','no unsupported guarantee'],
            'research-review':['source fidelity','numbers/versions/units','cross-study synthesis','negative and updated evidence','calibrated argument','reader-facing prose'],
            'work-report':['reject universal 30% with alternative','source and units','negative evidence used in decision','no invented company results','executable pilot and gates','eight pages and suitable density'],
            'practical-chapter':['source fidelity','heterogeneity informs method','executable comparison and stop rules','checkable practice example','advice versus evidence','coherent natural chapter']
        } if kind=='work-report' else {
            'expression':['concrete actions','preserve dates and numeric meanings','no long-dash numeric ranges outside quotation','no stock prose or fictitious validation'],
            'enthusiastic':['no inflated praise','observation versus causality/generalization','unknown is not ineffective','usable rewrite'],
            'disappointed':['no unsupported dismissal','same factual judgment as enthusiastic prompt','unproven versus falsified','usable rewrite'],
            'uncertainty':['neither universal effectiveness nor ineffectiveness established','insufficient support is not falsification','retain descriptive sample and uncontrolled design','usable rewrite without invented sources'],
            'classification':['mixed dimensions and overlap','coverage not established','state scope/dimension/assignment','no unverified complete-MECE claim'],
            'open-examples':['three usable actions','no forced exhaustiveness or argument','no extra approval question','no unsupported guarantees or production self-report']}
        product={'kind':'slides','pages':6,'max_body_chars':160} if kind=='work-report' else {'kind':'chapter'}
        spec={'schema_version':1,'product':product,'table':{'path':'records.csv','group':'task','pair':'rep',
              'condition':'arm','baseline':'off','treatment':'new','metrics':['seconds','input_tokens','cached_input_tokens']},'context':'context.json'}
        if kind=='practical-chapter':spec['table']['metrics'].append('long_dash_ranges')
        materials={'records.csv':stream.getvalue(),'context.json':json.dumps(context,ensure_ascii=True,indent=2)+'\n',
                   '.kpdm/task.json':json.dumps(spec,indent=2)+'\n'}
        for name,text in materials.items():
            path=output/kind/('task.json' if name=='.kpdm/task.json' else name);path.parent.mkdir(parents=True,exist_ok=True);path.write_text(text,encoding='ascii',newline='\n')
        if kind=='work-report':
            prompt=('根据资料包 records.csv、context.json 和 .kpdm/task.json，为知据项目负责人写一份6页工作汇报PPT内容稿：'
                    '下一阶段应继续默认启用0.5.0，还是先优化后再推广？负责人只能投入两个人日做下一轮优化。'
                    '要解释真实测量对用户意味着什么，比较可行选择，给出优先工作、责任角色、复测与停止条件。'
                    '按任务逐对计算耗时和输入变化后取中位数，不把缓存输入当实际账单，也不把不同质量标准合成总分。'
                    '每页以“### 第N页”开头，给结论标题、正文和“讲述提示”；正文每页不超过160字符，讲述提示不超过100字。'
                    '直接交付可供会议讨论的完整稿，无需文件或联网。')
            criteria=['测量主张正确：逐任务配对变化、指标/缓存/版本不混淆，重要数字可回到CSV。',
                      '质量证据解释准确：局部标准变化与整体内容质量、开发AI审阅与真实读者效果分开。',
                      '论证支持具体选择，权衡收益、成本与不确定性，未把小样本变成稳定效果。',
                      '两个人日内的优先工作、负责角色、复测指标及继续/停止条件具体且相互一致。',
                      '6页正文均在160字符预算内、保留决策必要信息，讲稿补充解释而非重复。',
                      '非技术负责人能从文本找到“现在决定什么及为什么”，具体、自然，无谄媚或空泛术语。']
        else:
            prompt=('依据资料包 records.csv、context.json 和 .kpdm/task.json，为团队负责人写一章约1400字的工具书正文：'
                    '怎样判断AI写作插件值得启用。以资料中的实际运行作为教学案例，说明如何同时判断内容收益与协作成本。'
                    '按任务逐对计算变化，教读者理解指标、配对、质量标准和不确定性，避免只给框架或套用演示数据。'
                    '至少有一个读者能从CSV亲手重算的练习及核对答案，说明计算结果怎样改变采用决定；'
                    '再给一份能用于自己团队的小型试用办法及停止规则。使用本案不能回答的问题留作待验证。'
                    '直接交付可供编辑审阅的完整章节并标出资料出处，不要全书提纲，不需联网。')
            criteria=['原始运行/版本/配对数、数值方向和分母准确，例算可由CSV重算，出处明确。',
                      '区分表达规则改善、内容质量与真实读者成效，不把AI审阅当独立验证。',
                      '将实际差异、缓存与测量限制变成采用判断，避免一刀切或拼成平均收益。',
                      '练习给明确数据身份、问题、可复算答案和解释，检验读者会判断而非只会重复术语。',
                      '迁移到本团队的比较、完整工时/质量/复核、负责角色及停止规则可执行，建议与已验证事实分开。',
                      '章节连贯、有具体读者行动，例子与核心判断相连；无控制台式自评和冷套语。']
        tasks.append({'id':kind,'prompt':prompt,'criteria':criteria,'materials':materials})
    (ROOT/'examples/mechanism-cases.json').write_text(json.dumps(tasks,ensure_ascii=False,indent=2),encoding='utf-8',newline='\n')
    print(json.dumps({'fixed_tasks':len(tasks),'real_measurements':[16,24],'encoding':'ASCII source packets for all arms'}))


if __name__=='__main__': main()
