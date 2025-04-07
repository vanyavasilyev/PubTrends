import logging
import typing as tp

import numpy as np
import scipy
from sklearn.decomposition import TruncatedSVD
from sklearn.feature_extraction.text import TfidfVectorizer

from models import DataPoint, GEODataset


class PointBuilder:
    def __init__(self, logger: tp.Optional[logging.Logger] = None):
        if logger is not None:
            self.logger = logger
        else:
            self.logger = logging.Logger("PointBuilder logger")
            self.logger.addHandler(logging.StreamHandler())
            self.logger.addHandler(logging.FileHandler("point_builder.log"))

    def _get_tfidf_vectors(
        self,
        geo_id_to_dataset: tp.Dict[int, tp.Optional[GEODataset]],
        geo_ids: tp.List[int],
    ) -> scipy.sparse._csr.csr_matrix:
        corpus = []
        for geo_id in geo_ids:
            dataset = geo_id_to_dataset[geo_id]
            if dataset is None:
                continue
            corpus.append(
                " ".join(
                    [
                        dataset.title,
                        dataset.experiment_type,
                        dataset.summary,
                        dataset.organizm,
                        dataset.overall_design,
                    ]
                )
            )
        return TfidfVectorizer().fit_transform(corpus)

    def _reduce_dimensions(self, vectors: scipy.sparse._csr.csr_matrix) -> np.ndarray:
        reduced = TruncatedSVD(2).fit_transform(vectors)
        if reduced.shape[1] < 2:
            reduced = np.hstack((reduced, np.zeros((reduced.shape[0], 1))))
        return reduced

    def build_points(
        self,
        pub_ids: tp.List[int],
        geo_id_to_dataset: tp.Dict[int, tp.Optional[GEODataset]],
        pubid_to_geo_ids: tp.Dict[int, tp.List[int]],
    ) -> tp.List[DataPoint]:
        self.logger.info("Started building points")
        geo_id_to_pub_ids = dict()
        for pub_id in pub_ids:
            for geo_id in pubid_to_geo_ids[pub_id]:
                if geo_id not in geo_id_to_pub_ids:
                    geo_id_to_pub_ids[geo_id] = []
                geo_id_to_pub_ids[geo_id].append(pub_id)
        geo_ids = [
            geo_id for geo_id in geo_id_to_pub_ids if geo_id_to_dataset is not None
        ]
        vectors = self._get_tfidf_vectors(geo_id_to_dataset, geo_ids)
        vectors = self._reduce_dimensions(vectors)

        result = []
        for i, geo_id in enumerate(geo_ids):
            result.append(
                DataPoint(
                    vectors[i, 0],
                    vectors[i, 1],
                    geo_id_to_pub_ids[geo_id],
                    geo_id,
                )
            )
        return result
