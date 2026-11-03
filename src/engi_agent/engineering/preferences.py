"""Small, local pairwise learner. No engineering formulas or learned surrogates."""
import hashlib
import json
import math
import os
from pathlib import Path
from uuid import uuid4
from pydantic import BaseModel, ConfigDict, Field, field_validator

SCALES = (1000., 1000., 1.)  # mm, mm², dimensionless; fixed across runs
NAMES = ('梁高', '受拉纵筋面积', '控制利用率')


class PreferenceSnapshot(BaseModel):
    model_config = ConfigDict(extra='forbid', allow_inf_nan=False)
    source: str = 'real'
    version: int = Field(default=0,ge=0)
    weights: tuple[float,float,float] = (1/3,1/3,1/3)
    normalization: str = 'h1000-as1000-u1-v1'

    @field_validator('source')
    @classmethod
    def source_valid(cls,v):
        if v not in ('real','simulated'):raise ValueError('评价来源无效')
        return v

    @field_validator('normalization')
    @classmethod
    def normalization_valid(cls,v):
        if v!='h1000-as1000-u1-v1':raise ValueError('归一化版本不兼容')
        return v

    @field_validator('weights')
    @classmethod
    def weights_valid(cls,v):
        if any(x<0 or not math.isfinite(x) for x in v) or not math.isclose(sum(v),1,abs_tol=1e-8):
            raise ValueError('偏好权重必须非负且和为1')
        return v


def verified(revision,span):
    from .design_search import candidate_metrics
    if revision['evaluation']['status']!='pass' or not revision['evaluation']['checks'] or not all(revision['evaluation']['checks'].values()):
        raise ValueError('只能评价通过请求检查的方案')
    m=candidate_metrics(revision,span)
    raw=[m['depth_mm'],m['tension_steel_mm2'],m['governing_utilization']]
    identity=json.dumps([revision['candidate'],revision['parameters']],sort_keys=True)
    return dict(id=hashlib.sha256(identity.encode()).hexdigest(),revision=revision['revision'],
                candidate=revision['candidate'],raw=raw,features=[x/s for x,s in zip(raw,SCALES)])


def pool(state):
    if state.request.task_type!='new_design':return []
    count=state.design_search.get('filter',{}).get('tested',0)
    result={}
    for r in state.revisions[-count:] if count else []:
        if r['evaluation']['status']=='pass':
            item=verified(r,state.request.parameters['span_mm'].value);result[item['id']]=item
    return list(result.values())


def score(item,snapshot):
    return sum(w*x for w,x in zip(snapshot.weights,item['features']))


class PreferenceStore:
    def __init__(self,source='real',directory=None):
        PreferenceSnapshot(source=source)
        self.source=source
        self.path=Path(directory or os.getenv('ENGIAGENT_PREFERENCE_DIR','outputs/preferences'))/(source+'.json')

    def load(self):
        if not self.path.exists():return PreferenceSnapshot(source=self.source),[]
        data=json.loads(self.path.read_text(encoding='utf-8'))
        snap=PreferenceSnapshot.model_validate(data['snapshot'])
        if snap.source!=self.source:raise ValueError('真实与模拟记录不能混用')
        if len(data['records'])!=snap.version or any(r['source']!=self.source or r['version']!=i for i,r in enumerate(data['records'],1)):
            raise ValueError('评价记录版本或来源不一致')
        return snap,data['records']

    def evaluate(self,state,left_id,right_id,chosen_id,expected_version):
        candidates={r['id']:r for r in pool(state)}
        if left_id==right_id or any(k not in candidates for k in (left_id,right_id)) or chosen_id not in (left_id,right_id):
            raise ValueError('必须比较两个不同的已通过候选')
        snap,records=self.load()
        if snap.version!=expected_version:raise ValueError('偏好版本已更新，请重新加载后评价')
        chosen=candidates[chosen_id];other=candidates[right_id if chosen_id==left_id else left_id]
        delta=[b-a for a,b in zip(chosen['features'],other['features'])]
        if not any(abs(d)>1e-12 for d in delta):raise ValueError('这两个方案的三项偏好特征相同')
        z=max(-60,min(60,sum(w*d for w,d in zip(snap.weights,delta))/.25))
        probability=1/(1+math.exp(-z))
        weights=[max(0,w+.25*(1-probability)*d/.25) for w,d in zip(snap.weights,delta)]
        total=sum(weights)
        updated=PreferenceSnapshot(source=self.source,version=snap.version+1,
            weights=tuple(w/total for w in weights) if total else (1/3,1/3,1/3))
        records.append(dict(source=self.source,version=updated.version,left=candidates[left_id],right=candidates[right_id],
                            chosen_id=chosen_id,before=list(snap.weights),after=list(updated.weights)))
        self.path.parent.mkdir(parents=True,exist_ok=True)
        temporary=self.path.with_name(self.path.name+'.'+uuid4().hex+'.tmp')
        with temporary.open('w',encoding='utf-8') as f:
            json.dump(dict(snapshot=updated.model_dump(),records=records),f,ensure_ascii=False,indent=2,allow_nan=False)
            f.flush();os.fsync(f.fileno())
        os.replace(temporary,self.path)
        return updated


def nondominated(items):
    return [a for a in items if not any(all(x<=y for x,y in zip(b['features'],a['features'])) and
            any(x<y for x,y in zip(b['features'],a['features'])) for b in items if b['id']!=a['id'])]
