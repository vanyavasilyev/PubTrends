# GEO Datasets Visualization

This is a repository for a small app that creates webpage for the visualization of tf-idf representations of GEO datasets linked to selected PubMed publications.

## Usage

- create a python environment
- `pip install -r requirements.txt`
- `python src/main.py`

## Configuration

The configuration file should be provided in json format. It may include:
- `host` - host of the flask application
- `port` - its port
- `pmids_path`- path to file with PMIDs
- `datasets_saved_path` - path to file to store parsed dataset for a certain list of PMIDs
- `logs_path` - path to a logging file.

Even so, `configs/app_config.json` works well.

## Points to improve

While the task is relatively small, it would take more time to make it perfectly. As the task is a step of application, I decided to list obvious things which might be done better.

- **Documentation**: even if I tried to let functions' names describe what they do clearly and employed typings, it is still better to add documentation.
- **Web page**: The page is not convenient enough.
- **Refactoring**: there are many things to refactor, i.e. the `create_app` function, it is not crucial for such a small application though.