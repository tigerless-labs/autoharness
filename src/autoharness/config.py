"""全部旋钮的唯一家 + 两份契约数据的指针（architecture §config 单点）。

标定值（节奏 / 成熟阈值 / 容量）是占位，经验标定走 experiments/；测试只断言关系
（两层俱在、>0），不锁绝对值。
"""
from pathlib import Path

from autoharness.lib import layer

REFLECT_EVERY_N = 10  # ponytail: 占位，待 experiments/ 标定；触发节奏 == REF 喂窗大小

STAGE_MAX_BODY_BYTES = 100_000  # ponytail: 占位，SKILL.md body 上限；stage_skill 入参即时反馈用

# 成熟阈值（毕业出缓刑的分母门槛）/ 容量上限，两层各设、独立可调。global 爆炸半径大 → 更保守（容量更小）。
MATURITY_THRESHOLD = {layer.GLOBAL: 50, layer.PROJECT: 20}  # ponytail: 占位，待标定
CAPACITY = {layer.GLOBAL: 20, layer.PROJECT: 50}  # ponytail: 占位，待标定

_LIB = Path(__file__).parent / "lib"
REDACTION_RULES = _LIB / "redaction_rules.toml"  # secret/PII 规则集，CAP egress + LED 单一来源
FORMAT_SPEC = _LIB / "format_spec.md"            # #416 authoring + lint 单一来源
