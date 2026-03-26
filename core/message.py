

from datetime import datetime

from typing import Dict, Any, Optional
from typing import Literal

from pydantic import BaseModel

RoleType = Literal["system", "user", "assistant", "tool"]

class Message(BaseModel):
    '''
    消息类
    '''
    content: str
    role: RoleType
    timestamp: datetime

    metadata:Optional[Dict[str, Any]]

    def __init__(self,content: str, role: RoleType, **kwargs):
        super().__init__(
            content=content,
            role=role,
            timestamp=kwargs.get('timestamp', datetime.now()),
            metadata=kwargs.get('metadata', {})
        )

    
    def to_dict(self) -> Dict[str, Any]:
        '''
        将消息转换为字典格式
        '''
        return {
            'content': self.content,
            'role': self.role,
        }
    
    def __str__(self) -> str:
        return f"[{self.role}]:{self.content}"
        