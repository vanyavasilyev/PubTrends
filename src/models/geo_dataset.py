import dataclasses


@dataclasses.dataclass
class GEODataset:
    uid: int
    accession: str = ""
    title: str = ""
    experiment_type: str = ""
    summary: str = ""
    organizm: str = ""
    overall_design: str = ""
