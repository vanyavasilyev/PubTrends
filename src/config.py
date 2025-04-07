import dataclasses
import json
import os
import typing as tp


@dataclasses.dataclass
class AppConfig:
    host: str = "127.0.0.1"
    port: int = 5000
    pmids_path: str = "./data/PMIDs_list.txt"
    datasets_saved_path: tp.Optional[str] = None
    logs_path: str = "app.log"


def read_config(config_path: str):
    if not os.path.exists:
        return AppConfig()
    with open(config_path, "r") as f:
        config_dict = json.load(f)
    return AppConfig(**config_dict)
