"""Bounded task routing, not semantic certainty or an authorization boundary."""
import re

LIGHT_GUIDANCE = (
    "[KnowTether LIGHT] 简单知识任务轻量处理：直接完成当前委托，不额外打开Skill或整套规范。"
    "判断随材料而非用户期待；必要异议给理由和改法，不为反对而争辩。保留原意、限定与未知，"
    "缺少依据不等于已证伪，不编来源或把模拟说成真实。用读者熟悉的词和具体动作，"
    "避免冷硬套语、自造术语、机械对仗和不合文体的标题列表；必要专业表达和直接引文保留。"
    "中文数字区间如1 - 2天；分类先定总体和维度、查重叠遗漏；开放举例不强行MECE。自然修订不等于技术水印移除。"
    "这是适配摘要，本次未读KPDM原文；复杂研究、出版或完整框架任务再按需读规范。"
)


def route(prompt):
    text = prompt if isinstance(prompt, str) else ''
    complex_cues = (r'研究综述|文献综述|学术报告|论文|出版|书籍|工具书|章节|专著|'
                    r'汇报|决策|政策|PPT|幻灯|演示文稿|研究报告|完整报告|论证|系统性|因果|'
                    r'research review|literature|publication|chapter|book|decision|slide|causal')
    long_request = bool(re.search(r'(?:[1-9]\d{3,}|[2-9]\d{2})\s*(?:字|words)', text, re.I))
    tier = 'focused' if len(text) > 1600 or long_request or re.search(complex_cues, text, re.I) else 'light'
    # A source path such as .kpdm/task.json followed by "完整稿" is not a
    # request for the full framework. Require an adjacent workflow request.
    intent = re.sub(r'\.?kpdm[/\\][\w./\\-]+', '', text, flags=re.I)
    if re.search(r'完整(?:的)?\s*KPDM|KPDM\s*(?:完整(?:流程|规范|工作流|框架|处理)|全套)|(?:full|complete)\s+KPDM', intent, re.I):
        tier = 'full'
    modules = ['grounds', 'judgment']
    if re.search(r'文风|表达|改写|润色|冷|术语|语言|style|rewrite', text, re.I):
        modules.append('expression')
    if re.search(r'书籍|工具书|章节|book|chapter', text, re.I):
        modules.append('book')
    elif re.search(r'报告|汇报|PPT|幻灯|report|slide|decision', text, re.I):
        modules.append('report')
    return {'tier': tier, 'modules': modules}


def prompt_context(prompt, *, compact=False):
    plan = route(prompt)
    if plan['tier'] == 'light':
        return LIGHT_GUIDANCE
    from .reading import reading_context
    return reading_context(profile=plan, compact=compact and plan['tier']=='focused')
