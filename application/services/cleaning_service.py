"""Application service: CleaningService (skeleton)"""
from typing import List


class CleaningService:
    def __init__(self, cleaners: List = None):
        self.cleaners = cleaners or []

    def register_cleaner(self, cleaner):
        self.cleaners.append(cleaner)

    def run(self, dataset):
        result = dataset
        for cleaner in self.cleaners:
            result = cleaner.clean(result)
        return result
