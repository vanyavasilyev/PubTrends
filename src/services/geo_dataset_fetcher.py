import json
import logging
import os
import pickle
import time
import typing as tp

import requests
from bs4 import BeautifulSoup

from models import GEODataset


class GEODatasetFetcher:
    def __init__(self, logger: tp.Optional[logging.Logger] = None):
        if logger is not None:
            self.logger = logger
        else:
            self.logger = logging.Logger("GEODatasetFetcher logger")
            self.logger.addHandler(logging.StreamHandler())
            self.logger.addHandler(logging.FileHandler("dataset_fetcher.log"))

    _NCBI_URL = "https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc="
    _EUTILS_GEO_SUMMARY = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=gds&retmode=json&id="
    _EUTILS_PUB_LINKS = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/elink.fcgi?dbfrom=pubmed&db=gds&linkname=pubmed_gds&retmode=json&id="

    def _get_content(
        self, url: str, max_attempts: int = 5, wait_time_ms: float = 1000
    ) -> tp.Optional[bytes]:
        attempts = 0
        while attempts < max_attempts:
            response = requests.get(url)
            if response.status_code == 200:
                return response.content
            time.sleep(wait_time_ms / 1000)
            attempts += 1
        self.logger.warning(f"Failed to get content from url {url}")
        return None

    def _get_overall_design(self, accession: str) -> str:
        url = self._NCBI_URL + accession.upper()
        content = self._get_content(url)
        if content is None:
            return ""
        soup = BeautifulSoup(content, features="lxml")
        overall_design_left_tag = soup.find(
            lambda tag: tag.name == "td" and tag.string == "Overall design"
        )
        if not overall_design_left_tag:
            self.logger.warning(f"No overall design data for {accession}")
            return ""
        overall_design_parent_tag = overall_design_left_tag.parent
        if len(overall_design_parent_tag.contents) < 4:
            self.logger.warning(f"Failed to parse overall design data for {accession}")
            return ""
        overall_design_main_tag = overall_design_parent_tag.contents[-2]
        if overall_design_main_tag.name == "td" and overall_design_main_tag.has_attr(
            "style"
        ):
            return overall_design_main_tag.get_text()
        else:
            self.logger.warning(f"Failed to parse overall design data for {accession}")
            return ""

    def _get_dataset_by_id(self, uid: int) -> tp.Optional[GEODataset]:
        url = self._EUTILS_GEO_SUMMARY + str(uid)
        content = self._get_content(url)
        if content is None:
            return None
        data = json.loads(content)
        try:
            result = data["result"][str(uid)]
            if "error" in result:
                return None
            dataset = GEODataset(
                uid=uid,
                accession=result["accession"],
                title=result["title"],
                experiment_type=result["gdstype"],
                summary=result["summary"],
                organizm=result["taxon"],
                overall_design=self._get_overall_design(result["accession"]),
            )
            return dataset
        except KeyError:
            self.logger.warning(f"Failed to parse dataset info for {uid}")
            return None

    def _get_geo_ids_by_pubid(self, pubid: int) -> tp.List[int]:
        url = self._EUTILS_PUB_LINKS + str(pubid)
        content = self._get_content(url)
        if content is None:
            return []
        data = json.loads(content)
        try:
            result = data["linksets"][0]["linksetdbs"][0]["links"]
            return [int(uid) for uid in result]
        except (KeyError, IndexError):
            self.logger.warning(f"Failed to parse linked datasets for {pubid}")
            return []

    def get_datasets(
        self, pubids: tp.List[int], save_path: tp.Optional[str] = None
    ) -> tp.Tuple[tp.Dict[int, tp.List[int]], tp.Dict[int, tp.Optional[GEODataset]]]:
        if save_path is not None:
            if os.path.exists(save_path):
                self.logger.info("Loading previously fetched datasets")
                with open(save_path, "rb") as f:
                    return pickle.load(f)
        self.logger.info("Started fetching GEO datasets")
        pubid_to_geo_ids = dict()
        geo_id_to_dataset = dict()
        for pubid in pubids:
            pubid_to_geo_ids[pubid] = []
            geo_ids = self._get_geo_ids_by_pubid(pubid)
            for geo_id in geo_ids:
                if geo_id not in geo_id_to_dataset:
                    geo_id_to_dataset[geo_id] = self._get_dataset_by_id(geo_id)
                if geo_id_to_dataset[geo_id] is not None:
                    pubid_to_geo_ids[pubid].append(geo_id)
        self.logger.info("Fetched GEO datasets")
        if save_path is not None:
            with open(save_path, "wb") as f:
                pickle.dump((pubid_to_geo_ids, geo_id_to_dataset), f)
        return pubid_to_geo_ids, geo_id_to_dataset
