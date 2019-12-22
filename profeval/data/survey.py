from typing import Dict
from dataclasses import dataclass
import json
import pickle


@dataclass
class SurveyMetadata(object):
    evaluate_id: int
    owner_name: str
    title: str
    term: int
    completed_surveys: int


@dataclass
class Survey(object):
    data: Dict[str, Dict[str, int]]
    metadata: SurveyMetadata

    @property
    def questions(self):
        return list(self.data.keys())

    def pretty_print(self):
        print(json.dumps(self.data, indent=2))
        print(self.metadata)

    def save(self, path):
        with open(path, 'wb') as f:
            pickle.dump(self, f)

    @classmethod
    def load(cls, path):
        with open(path, 'rb') as f:
            return pickle.load(f)
