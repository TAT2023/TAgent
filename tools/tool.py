
from abc import ABC, abstractmethod

from typing import Any, Dict, List

from pydantic import BaseModel

class ToolParameter(BaseModel):
    """
    工具参数
    """
    name: str
    description: str
    type: str
    required: bool = True
    default: Any = None


class Tool(ABC):
    """
    工具抽象基类
    """

    def __init__(self,name:str,description:str):
        self.name=name
        self.description=description


    @abstractmethod
    def run(self,parameters:Dict[str,Any])->str:
        """
        执行工具的核心方法
        parameters: Dict[str,Any] 工具参数字典
        返回: str 工具执行结果
        """
        pass


    @abstractmethod
    def get_parameters(self)->List[ToolParameter]:
        """
        获取工具参数定义
        返回: Dict[str,ToolParameter] 工具参数字典
        """
        pass

    

    def to_dict(self)->Dict[str,Any]:
        """
        将工具信息转换为字典格式
        返回: Dict[str,Any] 工具信息字典
        """
        return {
            "name":self.name,
            "description":self.description,
            "parameters":[param.model_dump() for param in self.get_parameters()]
        }