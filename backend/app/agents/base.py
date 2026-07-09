"""
agents/base.py — Agent orchestration engine.

Every agent inherits BaseAgent. AgentPipeline chains them.
PipelineContext is the shared blackboard between agents.
"""

import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class AgentStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED  = "failed"


@dataclass
class AgentResult:
    agent_name: str
    status: AgentStatus
    output: Any = None
    error: str = None
    duration_seconds: float = 0.0


@dataclass
class PipelineContext:
    """Shared blackboard — agents read/write data here."""
    data: dict = field(default_factory=dict)
    results: list = field(default_factory=list)

    def set(self, key: str, value: Any): self.data[key] = value
    def get(self, key: str, default: Any = None): return self.data.get(key, default)


class BaseAgent(ABC):
    name: str = "BaseAgent"
    max_retries: int = 0

    @abstractmethod
    def run(self, context: PipelineContext) -> Any:
        raise NotImplementedError

    def execute(self, context: PipelineContext) -> AgentResult:
        start = time.time()
        last_error = None

        for attempt in range(self.max_retries + 1):
            try:
                output = self.run(context)
                duration = round(time.time() - start, 3)
                result = AgentResult(self.name, AgentStatus.SUCCESS, output=output, duration_seconds=duration)
                context.results.append(result)
                context.set(self.name, output)
                return result
            except Exception as e:
                last_error = str(e)
                if attempt < self.max_retries:
                    time.sleep(0.5 * (attempt + 1))

        duration = round(time.time() - start, 3)
        result = AgentResult(self.name, AgentStatus.FAILED, error=last_error, duration_seconds=duration)
        context.results.append(result)
        return result


class AgentPipeline:
    def __init__(self, agents: list, stop_on_failure: bool = False):
        self.agents = agents
        self.stop_on_failure = stop_on_failure

    def run(self, context: PipelineContext) -> PipelineContext:
        for agent in self.agents:
            result = agent.execute(context)
            if result.status == AgentStatus.FAILED and self.stop_on_failure:
                break
        return context
