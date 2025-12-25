

from datetime import datetime

from typing import Dict, Any, Optional

from pydantic import BaseModel

class Message(BaseModel):
    '''
    消息类
    '''
    content: str
    role: str
    timestamp: datetime

    metadata:Optional[Dict[str, Any]]

    def __init__(self,content: str, role: str, **kwargs):
        self.content = content
        self.role = role

        self.timestamp = kwargs.get('timestamp', datetime.now())

        self.metadata = kwargs.get('metadata', {})

    
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
        