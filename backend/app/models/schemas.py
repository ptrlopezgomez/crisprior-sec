from enum import Enum
from pydantic import BaseModel, Field


class Severity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AzureResourceType(str, Enum):
    VIRTUAL_MACHINE = "azurerm_virtual_machine"
    STORAGE_ACCOUNT = "azurerm_storage_account"
    KEY_VAULT = "azurerm_key_vault"
    APP_SERVICE = "azurerm_app_service"


class StaticFinding(BaseModel):
    """Hallazgo crudo devuelto por un analizador estático (Checkov / tfsec)."""

    check_id: str
    resource_type: str
    resource_name: str
    file_path: str
    line_range: tuple[int, int]
    static_severity: Severity
    source_tool: str = Field(description="checkov | tfsec")
    description: str


class ResourceContext(BaseModel):
    """Contexto operacional extraído del grafo de red del recurso."""

    resource_name: str
    publicly_exposed: bool
    network_isolated: bool
    has_compensating_controls: bool


class PrioritizedFinding(BaseModel):
    """Hallazgo reevaluado con score contextual y explicación generada por el LLM."""

    finding: StaticFinding
    context: ResourceContext
    contextual_score: float = Field(ge=0, le=100)
    contextual_severity: Severity
    explanation: str
