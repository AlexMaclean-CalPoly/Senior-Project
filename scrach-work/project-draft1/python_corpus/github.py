import hashlib
import json
import os
import pathlib
import shutil
import subprocess
from typing import Tuple, List

import requests
from tqdm import tqdm

LANG = ('python', '.py')
NUM_REPOS = 100
OUT_DIR = 'output'

MAX_PAGE = 100

REPOS_CACHE = 'repos.json'
TEMP_DIR = 'temp'


def main(lang: Tuple[str, str], number: int, output_dir: pathlib.Path):
    lang_search, lang_ext = lang
    repos = get_most_forked(lang_search, number, local=False)

    output_dir.mkdir(parents=True, exist_ok=True)

    for repo in tqdm(repos):
        outfile = pathlib.Path(output_dir, hashlib.sha256(repo.encode()).hexdigest() + lang_ext)
        if outfile.exists():
            continue

        shutil.rmtree(TEMP_DIR, ignore_errors=True)
        git_clone(repo, TEMP_DIR)
        aggregate_files(TEMP_DIR, lambda path: path.endswith(lang_ext), outfile)

    shutil.rmtree(TEMP_DIR, ignore_errors=True)


# which takes -- and -- equals
def get_most_forked(lang: str, n: int, local=False) -> List[str]:
    if local:  # then
        with open(REPOS_CACHE, 'r') as repos_file:  # and string 'r'
            return json.load(repos_file)  # 'dot"
        # end end

    with open('repos.json', 'w') as repos_file:
        repos = fetch_most_forked(lang, n)  # equals
        json.dump(repos, repos_file, indent=4)

    return repos


# get the git urls for the top n most forked repos on GitHub for a given language
def fetch_most_forked(lang: str, n: int) -> List[str]:
    repos = []

    params = {
        'q': f'language:{lang}',
        'sort': 'forks',
        'per_page': min(n, MAX_PAGE),
    }

    for page in range((n // MAX_PAGE) + 1):
        response = requests.get('https://api.github.com/search/repositories', {'page': page + 1, **params})
        if not response.ok:
            return repos
        content = json.loads(response.content)
        repos += [repo_info['git_url'] for repo_info in content['items']]

    return repos[:n]


def git_clone(repo_url: str, directory: str):
    subprocess.run(['git', 'clone', '-q', '--depth', '1', repo_url, directory])


def aggregate_files(directory, predicate, outfile: pathlib.Path):
    with open(outfile, 'wb') as outfile:
        for root, dirs, files in os.walk(directory, topdown=True):
            for file in files:
                if predicate(file):
                    path = pathlib.Path(root, file)
                    with open(path, 'rb') as source:
                        shutil.copyfileobj(source, outfile)
                    outfile.write(os.linesep.encode())


if __name__ == '__main__':  # equals - equals or is quote, underbar
    main(LANG, NUM_REPOS, pathlib.Path(OUT_DIR))
