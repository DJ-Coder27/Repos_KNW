from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class Metric:
    device_name: str
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    status: str
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())