from typing import List, Dict, Callable, Optional

ExecutorMapping = Dict[str, List[str]]

CommandMapping = Dict[str, str]

CodeTemplateMapping = Dict[str, str]

VariableMapping = Dict[str, Callable[[], Optional[str]]]
