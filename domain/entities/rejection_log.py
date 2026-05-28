"""Domain entity: RejectionLog - Rich Domain Model.

Responsabilidades:
- Registrar rechazo de datasets/filas por gateway BPMN
- Mantener trazabilidad de motivos de rechazo
- Vincular con reglas de negocio específicas (RF-XXX, RB-XXX)
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any, Optional


@dataclass
class RejectionLog:
    """Registro de rechazo en el pipeline BPMN.

    Attributes:
        id: Identificador único del log
        dataset_id: ID del dataset rechazado
        motivo: Descripción del motivo de rechazo
        gateway_bpmn: Gateway BPMN que rechazó (1-4)
        regla_negocio: Código de regla de negocio (RF-XXX, RB-XXX)
        fecha: Timestamp del rechazo
        detalles: Información adicional del rechazo
    """

    id: str
    dataset_id: str
    motivo: str
    gateway_bpmn: int
    regla_negocio: str = ""
    fecha: datetime = field(default_factory=datetime.utcnow)
    detalles: Dict[str, Any] = field(default_factory=dict)
    row_index: Optional[int] = None  # Para rechazos a nivel de fila

    def to_dict(self) -> Dict[str, Any]:
        """Serializa el log a diccionario."""
        return {
            "id": self.id,
            "dataset_id": self.dataset_id,
            "motivo": self.motivo,
            "gateway_bpmn": self.gateway_bpmn,
            "regla_negocio": self.regla_negocio,
            "fecha": self.fecha.isoformat(),
            "detalles": self.detalles,
            "row_index": self.row_index,
        }

    def mensaje_descriptivo(self) -> str:
        """Genera mensaje descriptivo del rechazo para reportes."""
        gateway_desc = {
            1: "Extracción incompleta",
            2: "Formato inválido",
            3: "Transformación fallida",
            4: "Calidad insuficiente",
        }
        return (
            f"[Gateway {self.gateway_bpmn}: {gateway_desc.get(self.gateway_bpmn, 'Desconocido')}] "
            f"{self.motivo} (Regla: {self.regla_negocio})"
        )
