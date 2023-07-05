#!/usr/bin/python3

from enum import Enum
from pydantic import BaseModel
from typing import List, Dict


class ToolchainStatus(str, Enum):
    NOT_AVAILABLE = 'NOT AVAILABLE'
    OUTDATED = 'OUTDATED'
    AVAILABLE = 'AVAILABLE'


class ToolchainOption(BaseModel):
    name: str = ''
    values: List[str] = []


class ToolchainInfo(BaseModel):
    name: str = 'none'
    status: ToolchainStatus = ToolchainStatus.NOT_AVAILABLE
    build_opts: List[ToolchainOption] = []
    run_opts: List[ToolchainOption] = []
    deploy_opts: List[ToolchainOption] = []


class StatusCode(int, Enum):
    SUCCESS = 0
    ERROR_INTERNAL = -1
    ERROR_INVALID_CONFIG = -2
    ERROR_COMMAND_FAILED = -3


class Result(BaseModel):
    code: StatusCode
    message: str = ''
    info: Dict[str, str] = {}

    def ok(self):
        return (self.code == StatusCode.SUCCESS)
