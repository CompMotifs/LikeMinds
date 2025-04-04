<div style="display: flex; align-items: center;">
  <div>
    <img src="data/logo.png" alt="Logo" width="200">
  </div>
  <div style="margin-left: 20px;">
    <h1 style="margin: 0;">LikeMinds</h1>
    <p style="margin: 0;">People you need to know</p>
  </div>
</div>

LikeMinds is a lightweight web tool that helps researchers on [Bluesky](https://bsky.app) discover potential collaborators or competitors by analysing overlapping likes on posts. It recommends 3 users with similar interests—based on mutual likes—but excludes those you're already following.

## Features

- Enter your Bluesky handle
- Fetch recent liked posts
- Compare likes with other users
- Recommend 3 users with the highest overlap
- Simple web UI to view and follow suggestions

## Usage
- clone repo `git clone git@github.com:CompMotifs/LikeMinds.git`
- build environment `uv sync`
- run `uv run streamlit run src/web/app.py`

## Ideas

- do it as a command line tool
- base it on a conference feed
-





## Project Structure 

```bash
skymatch/
├── CONTRIBUTING.md         # Guidelines on branch strategy, code reviews, and merge process
├── LICENSE                 # License file
├── README.md               # Project overview and setup instructions
├── .gitignore              # Files/directories to ignore (e.g. __pycache__, venv)
├── docs/                   # Documentation and design notes
│   └── branching.md        # Branching strategy and best practices
├── notebooks/              # Jupyter notebooks for experiments and data exploration
├── src/                    # Main source code
│   └── likeminds/
│       ├── __init__.py
│       ├── api/                # Modules for Bluesky API integration
│       │   ├── __init__.py
│       │   └── bluesky_api.py  # Functions to interact with the Bluesky API
│       ├── recommendation/     # Modules for recommendation logic using sklearn-surprise
│       │   ├── __init__.py
│       │   └── recommender.py  # Implementation of collaborative filtering or other techniques
│       │   └── filter.py        # Filtering posts
│       ├── web/                # Web interface using Flask (or another framework)
│       │   ├── __init__.py
│       │   └── app.py          # Web app entry point and route definitions
│       └── config.py           # Configuration settings (e.g. API keys, model parameters)
└── tests/                  # Automated tests for each module
    ├── __init__.py
    ├── test_api.py         # Unit tests for the Bluesky API integration
    ├── test_recommender.py # Tests for the recommendation engine
    └── test_web.py         # Tests for the web interface