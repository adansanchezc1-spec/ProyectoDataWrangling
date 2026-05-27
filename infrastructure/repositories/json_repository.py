"""Infrastructure: JsonRepository skeleton implementing atomic JSON storage"""
import json
from pathlib import Path
from typing import Any, Optional


class JsonRepository:
    def __init__(self, storage_dir: str):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)

    def _path_for_id(self, id: str) -> Path:
        return self.storage_dir / f"{id}.json"

    def save(self, entity: Any) -> None:
        p = self._path_for_id(entity.id)
        tmp = p.with_suffix('.json.tmp')
        with tmp.open('w', encoding='utf-8') as f:
            json.dump(entity.to_dict(), f, ensure_ascii=False)
        tmp.replace(p)

    def get_by_id(self, id: str) -> Optional[Any]:
        p = self._path_for_id(id)
        if not p.exists():
            return None
        with p.open('r', encoding='utf-8') as f:
            return json.load(f)

    def list_all(self):
        for p in self.storage_dir.glob('*.json'):
            with p.open('r', encoding='utf-8') as f:
                yield json.load(f)

    def update(self, entity: Any) -> None:
        self.save(entity)

    def delete(self, id: str) -> None:
        p = self._path_for_id(id)
        if p.exists():
            p.unlink()
