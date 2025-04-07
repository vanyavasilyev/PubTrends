import dataclasses
import typing as tp


@dataclasses.dataclass
class DataPoint:
    x: float
    y: float
    pmids: tp.List[int]
    geo_id: int
