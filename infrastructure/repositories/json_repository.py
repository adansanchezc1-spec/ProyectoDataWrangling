"""Infrastructure: JsonRepository - Repository Pattern Implementation.

Persiste entidades en JSON con operaciones CRUD atómicas.
Implementa el contrato IDataRepository para independencia del almacenamiento.
"""
import json
from pathlib import Path
from typing import Any, Optional, Iterable, List

from domain.interfaces import IDataRepository
from domain.exceptions import RepositorioException


class JsonRepository(IDataRepository):
    """Repositorio que persiste entidades en archivos JSON.

    Características:
    - Almacenamiento atómico con archivo temporal
    - Una entidad = Un archivo JSON
    - Implements IDataRepository
    """

    def __init__(self, storage_dir: str) -> None:
        """Inicializa el repositorio.

        Args:
            storage_dir: Directorio donde se guardarán los JSONs
        """
        self.storage_dir = Path(storage_dir)
        try:
            self.storage_dir.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            raise RepositorioException(
                f"Failed to create storage directory: {storage_dir}",
                context={"error": str(e)},
            )

    def _path_for_id(self, entity_id: str) -> Path:
        """Calcula la ruta para una entidad por ID.

        Args:
            entity_id: ID de la entidad

        Returns:
            Path al archivo JSON
        """
        return self.storage_dir / f"{entity_id}.json"

    def save(self, entity: Any) -> None:
        """Guarda una entidad con escritura atómica.

        Usa escritura temporal seguida de rename para evitar corrupción
        si el proceso se interrumpe.

        Args:
            entity: Entidad con método to_dict()

        Raises:
            RepositorioException: Si hay error en persistencia
        """
        try:
            path = self._path_for_id(entity.id)
            tmp_path = path.with_suffix(".json.tmp")

            # Escribe en temporal
            with tmp_path.open("w", encoding="utf-8") as f:
                json.dump(entity.to_dict(), f, ensure_ascii=False, indent=2)

            # Rename atómico
            tmp_path.replace(path)

        except (OSError, IOError, AttributeError) as e:
            raise RepositorioException(
                f"Failed to save entity {entity.id}",
                context={"error": str(e)},
            )

    def get_by_id(self, entity_id: str) -> Optional[Any]:
        """Recupera una entidad por ID.

        Args:
            entity_id: ID de la entidad

        Returns:
            Dict con datos de la entidad, o None si no existe

        Raises:
            RepositorioException: Si hay error en lectura
        """
        try:
            path = self._path_for_id(entity_id)

            if not path.exists():
                return None

            with path.open("r", encoding="utf-8") as f:
                return json.load(f)

        except (OSError, IOError, json.JSONDecodeError) as e:
            raise RepositorioException(
                f"Failed to read entity {entity_id}",
                context={"error": str(e)},
            )

    def list_all(self) -> Iterable[Any]:
        """Lista todas las entidades en el repositorio.

        Yields:
            Dicts con datos de entidades
        """
        try:
            for json_file in sorted(self.storage_dir.glob("*.json")):
                if json_file.name.startswith("."):
                    continue
                try:
                    with json_file.open("r", encoding="utf-8") as f:
                        yield json.load(f)
                except json.JSONDecodeError:
                    # Silenciosamente salta JSONs corruptos
                    pass

        except OSError as e:
            raise RepositorioException(
                "Failed to list entities",
                context={"error": str(e)},
            )

    def update(self, entity: Any) -> None:
        """Actualiza una entidad (en JSON, es lo mismo que save).

        Args:
            entity: Entidad con cambios

        Raises:
            RepositorioException: Si hay error
        """
        self.save(entity)

    def delete(self, entity_id: str) -> None:
        """Elimina una entidad por ID.

        Args:
            entity_id: ID a eliminar

        Raises:
            RepositorioException: Si hay error
        """
        try:
            path = self._path_for_id(entity_id)

            if path.exists():
                path.unlink()

        except OSError as e:
            raise RepositorioException(
                f"Failed to delete entity {entity_id}",
                context={"error": str(e)},
            )
