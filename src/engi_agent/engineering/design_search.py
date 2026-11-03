"""Bounded candidate generation and transparent filtering; no engineering formulas.

Only absent section dimensions, authorized diameters and reinforcement counts are
varied. Every proposal must go through the normal design and independent checks.
"""
from __future__ import annotations

import heapq
import math


def search_domain(parameters):
    p = parameters
    h = p.get('beam_depth_mm') or math.ceil(p['span_mm']/12/25)*25
    b = p.get('beam_width_mm') or math.ceil(.5*h/25)*25
    domain = {}
    for key, initial, increment in [('beam_width_mm', b, 200), ('beam_depth_mm', h, 300)]:
        bound = 'max_width_mm' if key == 'beam_width_mm' else 'max_depth_mm'
        fixed = p.get(key) is not None
        upper = p.get(bound, initial+increment)
        if key == 'beam_depth_mm' and not fixed:
            upper = min(upper, p['span_mm']/5)  # existing ordinary-beam model boundary
        start = initial if fixed else min(initial, math.floor(upper/25)*25)
        domain[key] = dict(fixed=fixed, initial_mm=start, maximum_mm=initial if fixed else upper,
                           step_mm=25, bound_source='用户上限' if bound in p else '程序有限搜索范围')
    return domain


def domain_text(domain):
    return '；'.join(('梁宽' if k == 'beam_width_mm' else '梁高') +
        (f'固定 {v["initial_mm"]:g} mm' if v['fixed'] else
         f'{v["initial_mm"]:g}–{v["maximum_mm"]:g} mm，步长25 mm（{v["bound_source"]}）')
        for k, v in domain.items()) + '。程序范围是搜索预算边界，不是规范限值；仅向初选以上搜索，不保证全局最优。'


class CandidateSearch:
    def __init__(self, parameters, diameters, preference=None):
        self.base = parameters.copy()
        self.domain = search_domain(parameters)
        self.diameters = list(dict.fromkeys([parameters['bar_diameter_mm'], *diameters]))
        self.queue = []
        self.seen = set()
        self.sequence = 0
        self.preference=preference
        self.anchors={}
        self.anchor_keys={}
        self.selection_trace=[]
        self.guided_steps=0

    def observe(self,revision):
        if self.preference and revision['evaluation']['status']=='pass':
            from .preferences import verified
            item=verified(revision,self.base['span_mm'])
            self.anchors[item['id']]=(item,revision)

    def preference_neighbours(self):
        from .preferences import score
        item,revision=min(self.anchors.values(),key=lambda pair:score(pair[0],self.preference))
        p={**revision['parameters'],**{k:v for k,v in revision['candidate'].items() if k in self.base or k in self.domain}}
        n=revision['candidate']['bar_count']
        variants=[({},n+1),({},max(2,n-1))]
        for k,delta in [('beam_width_mm',25),('beam_depth_mm',25)]:
            variants.extend([({k:p[k]+delta},2),({k:p[k]-delta},2)])
        variants.extend([({'bar_diameter_mm':d},2) for d in self.diameters])
        for changes,count in variants:
            candidate={**self.base,**{k:p[k] for k in self.domain},'bar_diameter_mm':p['bar_diameter_mm'],**changes}
            key=self.key(candidate,count)
            self.add(candidate,count,'已通过修订'+str(revision['revision'])+'的偏好邻域；新候选仍需完整验算',3)
            if any(self.key(entry[2],entry[3])==key for entry in self.queue):
                self.anchor_keys[key]=item

    def initial(self):
        return {**self.base, **{k: v['initial_mm'] for k, v in self.domain.items()}}

    def key(self, p, count):
        return (p['beam_width_mm'], p['beam_depth_mm'], p['bar_diameter_mm'], count)

    def add(self, p, count, reason, priority):
        for k, limit in self.domain.items():
            if limit['fixed'] and p[k] != limit['initial_mm']:
                return
            if not limit['initial_mm'] <= p[k] <= limit['maximum_mm']:
                return
        key = self.key(p, count)
        if key in self.seen:
            return
        self.seen.add(key)
        self.sequence += 1
        heapq.heappush(self.queue, (priority, self.sequence, p.copy(), count, reason))

    def propose(self, state, p, minimum_count):
        c = state.candidate
        count = c.get('bar_count', minimum_count)
        failed = [k for k, v in state.evaluation.checks.items() if not v]
        detail = state.tool_results.get('evaluation.detailing_check')
        reasons = detail.outputs.get('reasons', []) if detail else []
        labels = {'flexure':'抗弯','shear':'抗剪','detailing':'构造','crack':'裂缝','deflection':'挠度'}
        prefix = ('未通过：' + '、'.join(labels.get(k,k) for k in failed)) if failed else '继续比较已授权的不同方案'
        if reasons:prefix += '（'+'；'.join(reasons)+'）'
        if not c:
            failures = [e for r in state.tool_results.values() for e in r.errors if r.status == 'failed']
            prefix = '设计未形成候选：'+'；'.join(failures)
        layout = any('净距不足' in r for r in reasons)
        passed = state.evaluation.status == 'pass'

        def offer(changes, n, reason, priority):
            self.add({**p, **changes}, n, prefix+'；'+reason+'；重新设计并复核全部项目', priority)

        if layout:
            # Calculate the geometric width needed for the current layer; the
            # detailing tool independently verifies this proposal afterwards.
            required = 2*(p['cover_mm']+p['stirrup_diameter_mm'])
            required += count*p['bar_diameter_mm']+(count-1)*max(25, p['bar_diameter_mm'], 4*p['aggregate_size_mm']/3)
            if any('上部钢筋净距' in r for r in reasons):
                required = max(required, 2*(p['cover_mm']+p['stirrup_diameter_mm'])+
                    p['top_bar_count']*p['top_bar_diameter_mm']+
                    (p['top_bar_count']-1)*max(30, 1.5*p['top_bar_diameter_mm']))
            width = max(p['beam_width_mm']+25, math.ceil(required/25)*25)
            offer({'beam_width_mm': width}, minimum_count, f'净距不足，梁宽调整为{width:g}mm', 0)
        if not c or 'deflection' in failed or 'flexure' in failed or 'shear' in failed or 'crack' in failed or layout:
            h = min(p['beam_depth_mm']+50, math.floor(self.domain['beam_depth_mm']['maximum_mm']/25)*25)
            priority = 4 if failed == ['crack'] else 1
            offer({'beam_depth_mm': h}, 2, f'尝试增加梁高至{h:g}mm，重新确定配筋', priority)
        # A detailing failure can depend on diameter even when spacing is fine
        # (e.g. transverse reinforcement in the anchorage region). Always offer
        # authorized alternatives for detailing failures as well, without
        # changing the existing flexure/serviceability repair priorities.
        for d in self.diameters if passed or 'detailing' in failed or not c else []:
            if d != p['bar_diameter_mm']:
                priority = 0 if 'detailing' in failed and not layout else 2 if passed or layout else 4
                offer({'bar_diameter_mm': d}, 2, f'尝试已允许的直径{d}mm，按新直径重新计算根数', priority)
        # More steel cannot fix insufficient spacing, anchors, cover or side bars.
        if c and not layout and (passed or ('detailing' not in failed and failed)):
            offer({}, count+1, f'纵筋至少{count+1}根', 2 if failed == ['crack'] else 3)
        if passed:
            for key in self.domain:
                delta = 25 if key == 'beam_width_mm' else 50
                value = min(p[key]+delta, math.floor(self.domain[key]['maximum_mm']/25)*25)
                offer({key: value}, 2, f'比较不同截面：{key}={value:g}mm', 3)
        if self.preference and self.anchors:self.preference_neighbours()
        if self.queue:
            mode='rule';anchor=None
            if self.preference and self.anchors:
                from .preferences import score
                self.guided_steps+=1
                options=[(i,e,self.anchor_keys[self.key(e[2],e[3])]) for i,e in enumerate(self.queue) if self.key(e[2],e[3]) in self.anchor_keys]
                if options and self.guided_steps%4!=0:
                    i,entry,anchor=min(options,key=lambda x:(score(x[2],self.preference),x[1][0],x[1][1]))
                    self.queue.pop(i);heapq.heapify(self.queue);mode='preference_neighbour'
                else:entry=heapq.heappop(self.queue);mode='rule_exploration'
            else:entry=heapq.heappop(self.queue)
            _, _, params, n, reason = entry
            self.selection_trace.append(dict(mode=mode,parameters=params.copy(),minimum_bar_count=n,
                anchor_revision=anchor['revision'] if anchor else None,
                verified_anchor_features=anchor['features'] if anchor else None,
                anchor_score=score(anchor,self.preference) if anchor else None))
            return params, n, reason
        return None


def candidate_metrics(revision, span_mm):
    c, tools = revision['candidate'], revision['tools']
    outputs = lambda name: tools['evaluation.'+name]['outputs']
    f, s, w, d = map(outputs, ['flexural_check','shear_check','crack_check','deflection_check'])
    utilization = max(f['utilization'], s['demand_kn']/s['capacity_kn'],
                      s['demand_kn']/s['section_limit_kn'],
                      w['crack_width_mm']/w['limit_mm'], d['deflection_mm']/d['limit_mm'])
    return dict(concrete_m3=c['beam_width_mm']*c['beam_depth_mm']*span_mm/1e9,
                tension_steel_mm2=c['As_mm2'], depth_mm=c['beam_depth_mm'],
                governing_utilization=utilization)


def shortlist(revisions, span_mm, limit):
    passing = [r for r in revisions if r['evaluation']['status'] == 'pass']
    unique = {}
    for r in passing:
        c = r['candidate']
        identity = tuple(c[k] for k in ('beam_width_mm','beam_depth_mm','bar_diameter_mm',
                        'bar_count','stirrup_diameter_mm','stirrup_legs','stirrup_spacing_mm'))
        if identity not in unique:
            unique[identity] = dict(revision=r['revision'], candidate=c.copy(),
                checks=r['evaluation']['checks'].copy(), metrics=candidate_metrics(r, span_mm))
    pool = list(unique.values())
    def dominates(a, b):
        x, y = list(a['metrics'].values()), list(b['metrics'].values())
        return all(i <= j+1e-9 for i, j in zip(x, y)) and any(i < j-1e-9 for i, j in zip(x, y))
    front = [a for a in pool if not any(dominates(b, a) for b in pool if a is not b)]
    selected = []
    if front:
        lows = {k:min(a['metrics'][k] for a in front) for k in front[0]['metrics']}
        # Equal relative weight for volume and tension-steel area; not a price model.
        score = lambda a: (a['metrics']['concrete_m3']/lows['concrete_m3']+
                           a['metrics']['tension_steel_mm2']/lows['tension_steel_mm2'],
                           a['metrics']['depth_mm'], a['metrics']['governing_utilization'], a['revision'])
        selected = [min(front, key=score)]
        selected[0]['selection_reason'] = '已验算候选中，混凝土体积与受拉纵筋面积的等权相对指标最小'
        for field, label in [('governing_utilization','验算裕量较大'),('depth_mm','梁高较小')]:
            if len(selected) >= limit:
                break
            remaining = [a for a in front if a not in selected]
            if not remaining:
                break
            a = min(remaining, key=lambda a:(a['metrics'][field], score(a)))
            a['selection_reason'] = label+'，保留工程取舍'
            selected.append(a)
    meta = dict(tested=len(revisions), passed=len(passing), unique_passed=len(pool),
                duplicates=len(passing)-len(pool), dominated=len(pool)-len(front),
                pareto_count=len(front), displayed=len(selected),
                rule='先去重，再按混凝土体积、受拉纵筋面积、梁高、控制利用率剔除支配方案；最多保留确认数量。',
                limitation='仅比较实际算过且全部检查通过的候选；纵筋面积不含箍筋、架立筋、腰筋及锚固用量，不代表总用钢量或造价。')
    return selected, meta
