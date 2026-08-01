from enum import Enum


class RiskLevel(str, Enum):
    UNKNOWN = "UNKNOWN"
    SAFE = "SAFE"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"

    @property
    def _severity(self) -> int:
        return {"UNKNOWN": 0, "SAFE": 1, "LOW": 2, "MEDIUM": 3, "HIGH": 4}[self.value]

    def __lt__(self, other: "RiskLevel") -> bool:
        if not isinstance(other, RiskLevel):
            return NotImplemented
        return self._severity < other._severity

    def __le__(self, other: "RiskLevel") -> bool:
        if not isinstance(other, RiskLevel):
            return NotImplemented
        return self._severity <= other._severity

    def __gt__(self, other: "RiskLevel") -> bool:
        if not isinstance(other, RiskLevel):
            return NotImplemented
        return self._severity > other._severity

    def __ge__(self, other: "RiskLevel") -> bool:
        if not isinstance(other, RiskLevel):
            return NotImplemented
        return self._severity >= other._severity
