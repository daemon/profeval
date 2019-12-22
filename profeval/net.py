from collections import OrderedDict
from dataclasses import dataclass
from typing import Sequence
import json
import re

import requests

from profeval.data import SurveyMetadata, Survey


class AuthError(Exception):
    pass


def login(username, password, url='https://cas.uwaterloo.ca/cas/login'):
    session = requests.Session()
    login_data = dict(username=username, password=password, lt='e1s1', _eventId='submit', submit='LOGIN')
    auth_html = session.get(url).content.decode()
    jsess_id = re.search(r'action="/cas/login;jsessionid=(.+?)"', auth_html).group(1).strip()
    response = session.post(f'{url};jsessionid={jsess_id}', data=login_data)
    if response.status_code != 200:
        raise AuthError
    return session


_MATHSOC_EVAL_PATTERN_Q = re.compile(r"<strong>(.+?)</strong>.+?<ol>(.+?)</ol>", re.DOTALL)
_MATHSOC_EVAL_PATTERN_A = re.compile(r"<li>(.+?): (\d+?)</li>")


@dataclass
class MathSocSurveyApi(object):
    session: requests.Session
    base_url: str = 'https://mathsoc.uwaterloo.ca/university/evaluations'

    def fetch_all_survey_metadata(self) -> Sequence[SurveyMetadata]:
        content = self.session.get(self.base_url).content.decode()
        content = re.search(r'var term_survey_map = (.+?);', content).group(1)
        metadata = []
        for _, data_lst in json.loads(content).items():
            metadata.extend(SurveyMetadata(**obj) for obj in data_lst)
        return metadata

    def fetch_survey(self, metadata: SurveyMetadata) -> Survey:
        url = f'{self.base_url}/{metadata.evaluate_id}'
        content = self.session.get(url).content.decode()
        questions = re.findall(_MATHSOC_EVAL_PATTERN_Q, content)
        data_dict = OrderedDict()
        for question_txt, body in questions:
            answers = re.findall(_MATHSOC_EVAL_PATTERN_A, body)
            answers = OrderedDict([(a, int(b)) for a, b in answers])
            data_dict[question_txt] = answers
        return Survey(data_dict, metadata)
