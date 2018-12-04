from typing import Callable, Dict, List, Optional

CommandList = List[str]

ExecutorMapping = Dict[str, CommandList]

JudgerMapping = Dict[str, CommandList]

CommandMapping = Dict[str, str]

CodeTemplateMapping = Dict[str, str]

VariableMapping = Dict[str, Callable[[], Optional[str]]]
