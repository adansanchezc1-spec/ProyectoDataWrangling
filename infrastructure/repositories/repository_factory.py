"""Infrastructure: RepositoryFactory - Factory Method Pattern.

Crea instancias de repositorios según el tipo especificado.
Desacopla la creación de repositorios de su uso.
"""
from typing import Literal

from domain.interfaces import IDataRepository
from domain.exceptions import RepositorioException
from .json_repository import JsonRepository


class RepositoryFactory:
    """Factory para crear repositorios según tipo."""

    @staticmethod
    def create(
        repo_type: Literal["json", "pandas"] = "json",
        **kwargs
    ) -> IDataRepository:
        """Crea un repositorio del tipo especificado.

        Args:
            repo_type: Tipo de repositorio ("json" | "pandas")
            **kwargs: Argumentos específicos para cada repositorio

        Returns:
            Instancia de repositorio que implementa IDataRepository

        Raises:
            RepositorioException: Si tipo no soportado
        """
        if repo_type == "json":
            storage_dir = kwargs.get("storage_dir", "./data/repositories")
            return JsonRepository(storage_dir)

        elif repo_type == "pandas":
            # Para futuro: PandasRepository
            raise NotImplementedError("PandasRepository not yet implemented")

        else:
            raise RepositorioException(
                f"Unknown repository type: {repo_type}",
                context={"repo_type": repo_type},
            )

    @staticmethod
    def create_default() -> IDataRepository:
        """Crea un repositorio con configuración por defecto (JSON).

        Returns:
            JsonRepository en ./data/repositories
        """
        return RepositoryFactory.create("json")
