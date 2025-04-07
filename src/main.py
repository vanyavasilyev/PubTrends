import argparse
import logging

from flask import Flask, current_app, request, render_template

from config import AppConfig, read_config
from services import GEODatasetFetcher, PointBuilder


def _parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-c", "--config", help="path to config file", default="configs/app_config.json"
    )
    return parser.parse_args()


def create_app(config: AppConfig):
    app = Flask(
        __name__,
    )
    app.logger.addHandler(logging.FileHandler(config.logs_path))
    app.logger.setLevel(5)
    fetcher = GEODatasetFetcher(app.logger)
    point_builder = PointBuilder(app.logger)

    with open(config.pmids_path, "r") as f:
        pmids = [int(s) for s in f.read().split()]
    pubid_to_geo_ids, geo_id_to_dataset = fetcher.get_datasets(
        pmids, config.datasets_saved_path
    )

    @app.route("/")
    def root():
        return render_template("index.html", pmids=pmids)

    @app.route("/api/get_points", methods=["GET"])
    def get_points():
        pmids = request.args.get("pmids")
        pub_ids = [int(s) for s in pmids.split(",")]
        points = point_builder.build_points(
            pub_ids, geo_id_to_dataset, pubid_to_geo_ids
        )
        return points

    return app


if __name__ == "__main__":
    args = _parse_args()
    config = read_config(args.config)
    app = create_app(config)
    app.run(host=config.host, port=config.port)
