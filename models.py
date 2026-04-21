from dataclasses import dataclass
from datetime import datetime

@dataclass
class Metric:
    device_name: str
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    status: str
    timestamp: str = datetime.utcnow().isoformat()