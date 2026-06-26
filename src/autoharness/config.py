"""全部旋钮的唯一家 + 两份契约数据的指针（architecture §config 单点）。

标定值（节奏 / 成熟阈值 / 容量）是占位，经验标定走 experiments/；测试只断言关系
（两层俱在、>0），不锁绝对值。可经 AUTOHARNESS_* env 覆盖——给 e2e runbook 调小旋钮用
（短会话内跑出毕业 / 容量竞争），缺省回占位。
"""
import os
from pathlib import Path

from autoharness.lib import layer


def _int_env(name, default):
    try:
        return int(os.environ[name])
    except (KeyError, ValueError):
        return default


REFLECT_EVERY_N = _int_env("AUTOHARNESS_REFLECT_EVERY_N", 10)  # 触发节奏 == REF 喂窗大小

STAGE_MAX_BODY_BYTES = 100_000  # ponytail: 占位，SKILL.md body 上限；stage_skill 入参即时反馈用

# 成熟阈值（毕业出缓刑的分母门槛）/ 容量上限，两层各设、独立可调。global 爆炸半径大 → 更保守（容量更小）。
MATURITY_THRESHOLD = {layer.GLOBAL: _int_env("AUTOHARNESS_MATURITY_GLOBAL", 50),
                      layer.PROJECT: _int_env("AUTOHARNESS_MATURITY_PROJECT", 20)}
CAPACITY = {layer.GLOBAL: _int_env("AUTOHARNESS_CAPACITY_GLOBAL", 20),
            layer.PROJECT: _int_env("AUTOHARNESS_CAPACITY_PROJECT", 50)}

_LIB = Path(__file__).parent / "lib"
REDACTION_RULES = _LIB / "redaction_rules.toml"  # secret/PII 规则集，CAP egress + LED 单一来源
FORMAT_SPEC = _LIB / "format_spec.md"            # #416 authoring + lint 单一来源

CHILD_SESSION_ENV = "CLAUDE_CODE_CHILD_SESSION"  # 平台递归 guard 信号：spawn 置、CAP hook 读（单一来源）

REFLECTOR_AGENT = "autoharness:reflector"  # spawn 的 --agent 引用（plugin 命名空间，Phase 0 解析待实测）
CLAUDE_BIN = "claude"                       # spawn 的子会话可执行；PATH 解析，测试可覆盖
RUN_ID_ENV = "AUTOHARNESS_RUN_ID"           # spawn 经环境把 intent 队列 run_id 注入子会话（stage_skill 读）
PROJECT_ROOT_ENV = "AUTOHARNESS_PROJECT_ROOT"  # 同上：repo 根（队列落盘位）
