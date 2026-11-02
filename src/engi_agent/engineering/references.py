"""Present only recognized formal standards; retain raw references in audit data."""
import re

STANDARDS={
    '50010':('《混凝土结构设计标准》','GB/T 50010—2010（2024年版）'),
    '55001':('《工程结构通用规范》','GB 55001—2021'),
    '55008':('《混凝土结构通用规范》','GB 55008—2021'),
    '50009':('《建筑结构荷载规范》','GB 50009—2012'),
}


def professional_references(references):
    result=[]
    for raw in references:
        match=re.match(r'^GB(?:/T)?\s*(50010|55001|55008|50009)(?:[-—]\d{4})?\s*(.*)$',raw.strip())
        if not match:continue
        name,code=STANDARDS[match[1]]
        clauses=re.sub(r'（2024修订）','',match[2]).strip()
        text=name+' '+code+('，条文：'+clauses if clauses else '')
        if text not in result:result.append(text)
    return result
