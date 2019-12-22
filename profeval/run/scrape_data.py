import argparse
import getpass
import os
import pathlib
import time

from tqdm import tqdm

from profeval.net import login, MathSocSurveyApi, AuthError


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--username', '-u', type=str, required=True)
    parser.add_argument('--delay', '-d', type=float, default=1, help='Delay in seconds.')
    parser.add_argument('--output-path', '-o', required=True, type=pathlib.Path)
    args = parser.parse_args()

    password = getpass.getpass()
    try:
        session = login(args.username, password)
    except AuthError:
        print('Error logging in.')
        return
    api = MathSocSurveyApi(session)
    metadata_lst = api.fetch_all_survey_metadata()
    os.makedirs(args.output_path, exist_ok=True)
    for metadata in tqdm(metadata_lst):
        save_path = args.output_path / f'{metadata.evaluate_id}.pkl'
        if save_path.exists():
            continue
        api.fetch_survey(metadata).save(save_path)
        time.sleep(args.delay)


if __name__ == '__main__':
    main()
