"""Pure room model for a teaching demo. Revision checks prevent silent overwrite."""
from dataclasses import dataclass, field
from typing import Dict
MAX_CODE = 100000
@dataclass
class Room:
    code: str = "# Добро пожаловать в CodeTogether\nprint('Привет, команда!')\n"
    revision: int = 0
    users: Dict[str,str] = field(default_factory=dict)
    def join(self,client_id,name):
        if not client_id or not isinstance(name,str) or not name.strip(): raise ValueError('invalid participant')
        self.users[client_id]=name.strip()[:32]
        return self.snapshot()
    def leave(self,client_id): self.users.pop(client_id,None)
    def snapshot(self): return {'type':'snapshot','code':self.code,'revision':self.revision,'users':list(self.users.values())}
    def update(self,code,base_revision):
        if not isinstance(code,str): return {'type':'error','message':'code must be text'}
        if len(code)>MAX_CODE: return {'type':'error','message':'document too large'}
        if type(base_revision) is not int: return {'type':'error','message':'revision must be integer'}
        if base_revision != self.revision: return {**self.snapshot(),'type':'conflict'}
        self.code=code;self.revision+=1
        return {'type':'update','code':self.code,'revision':self.revision}
