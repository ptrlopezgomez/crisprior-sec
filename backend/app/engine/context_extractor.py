"""Extracción de variables de contexto de red desde el AST de Terraform (HU-03)."""

from pathlib import Path
from typing import Any

import hcl2

from app.models.schemas import ResourceContext

ResourceKey = tuple[str, str]
ResourceIndex = dict[ResourceKey, dict[str, Any]]

_PUBLIC_SOURCE_PREFIXES = {"*", "0.0.0.0/0", "internet", "any"}

_APP_SERVICE_TYPES = {
    "azurerm_app_service",
    "azurerm_linux_web_app",
    "azurerm_windows_web_app",
    "azurerm_linux_function_app",
    "azurerm_windows_function_app",
}

# Recursos que, de existir en el mismo directorio, se consideran un control
# compensatorio frente a una regla de red demasiado permisiva (Bastion Host,
# VPN Gateway, Application Gateway/WAF).
_COMPENSATING_CONTROL_TYPES = {
    "azurerm_bastion_host",
    "azurerm_vpn_gateway",
    "azurerm_virtual_network_gateway",
    "azurerm_application_gateway",
}


def _get(body: dict[str, Any], key: str, default: Any = None) -> Any:
    """Desenvuelve el wrapping de listas de un nivel que aplica python-hcl2
    tanto a atributos escalares como a bloques anidados únicos."""
    value = body.get(key)
    if value is None:
        return default
    if isinstance(value, list):
        return value[0] if value else default
    return value


def _load_resources(terraform_dir: Path) -> ResourceIndex:
    """Parsea todos los .tf del directorio y construye un índice (tipo, nombre) -> atributos."""
    resources: ResourceIndex = {}
    for tf_file in sorted(terraform_dir.glob("*.tf")):
        with tf_file.open("r", encoding="utf-8") as fh:
            parsed = hcl2.load(fh)
        for resource_block in parsed.get("resource", []):
            for resource_type, named_bodies in resource_block.items():
                for resource_name, body in named_bodies.items():
                    resources[(resource_type, resource_name)] = body
    return resources


def _has_compensating_network_control(resources: ResourceIndex) -> bool:
    return any(resource_type in _COMPENSATING_CONTROL_TYPES for resource_type, _ in resources)


def _nsg_allows_public_ingress(nsg_body: dict[str, Any]) -> bool:
    for rule in nsg_body.get("security_rule", []) or []:
        direction = str(_get(rule, "direction", "")).lower()
        access = str(_get(rule, "access", "")).lower()
        if direction != "inbound" or access != "allow":
            continue

        sources = []
        single_source = _get(rule, "source_address_prefix")
        if single_source is not None:
            sources.append(single_source)
        sources.extend(_get(rule, "source_address_prefixes", []) or [])

        if any(str(source).strip().lower() in _PUBLIC_SOURCE_PREFIXES for source in sources):
            return True
    return False


def _any_nsg_publicly_exposed(resources: ResourceIndex) -> bool:
    return any(
        _nsg_allows_public_ingress(body)
        for (resource_type, _), body in resources.items()
        if resource_type == "azurerm_network_security_group"
    )


def _network_security_group_context(
    body: dict[str, Any], resources: ResourceIndex
) -> tuple[bool, bool, bool]:
    publicly_exposed = _nsg_allows_public_ingress(body)
    return publicly_exposed, not publicly_exposed, _has_compensating_network_control(resources)


def _storage_account_context(body: dict[str, Any]) -> tuple[bool, bool, bool]:
    public_enabled = bool(_get(body, "public_network_access_enabled", True))
    network_rules = _get(body, "network_rules", {})
    default_action = str(_get(network_rules, "default_action", "Allow")).lower()
    has_vnet_restriction = bool(_get(network_rules, "virtual_network_subnet_ids"))

    network_isolated = default_action == "deny" and has_vnet_restriction
    publicly_exposed = public_enabled and default_action != "deny"
    return publicly_exposed, network_isolated, has_vnet_restriction


def _key_vault_context(body: dict[str, Any]) -> tuple[bool, bool, bool]:
    network_acls = _get(body, "network_acls")
    if not network_acls:
        return False, False, False

    public_enabled = bool(_get(body, "public_network_access_enabled", True))
    default_action = str(_get(network_acls, "default_action", "Deny")).lower()
    has_vnet_restriction = bool(_get(network_acls, "virtual_network_subnet_ids"))

    if public_enabled and default_action == "allow":
        return True, False, has_vnet_restriction
    if not public_enabled and default_action == "deny" and has_vnet_restriction:
        return False, True, has_vnet_restriction
    return False, False, has_vnet_restriction


def _app_service_context(body: dict[str, Any]) -> tuple[bool, bool, bool]:
    site_config = _get(body, "site_config", {})
    has_ip_restriction = bool(site_config.get("ip_restriction"))
    return (not has_ip_restriction), False, has_ip_restriction


def extract_resource_context(
    terraform_dir: Path, resource_type: str, resource_name: str
) -> ResourceContext:
    """Analiza el grafo de recursos para determinar exposición pública,
    aislamiento de red y presencia de controles compensatorios.

    Para tipos con configuración de red explícita (NSG, Storage Account, Key
    Vault, App Service) el contexto se deriva de los atributos del propio
    recurso. Para el resto (VMs, discos, etc., cuya exposición depende de la
    NIC/subred a la que se asocian y que estas fixtures no modelan de forma
    resoluble) se infiere del resto del grafo: si existe algún NSG con una
    regla de ingreso público en el mismo directorio, se asume el mismo
    contexto de red; si no existe ninguno, se asume aislado (por defecto los
    recursos de Azure no son públicos salvo que algo los exponga).
    """
    resources = _load_resources(terraform_dir)
    body = resources.get((resource_type, resource_name))
    if body is None:
        raise ValueError(
            f"Recurso '{resource_type}.{resource_name}' no encontrado en {terraform_dir}"
        )

    if resource_type == "azurerm_network_security_group":
        publicly_exposed, network_isolated, has_controls = _network_security_group_context(
            body, resources
        )
    elif resource_type == "azurerm_storage_account":
        publicly_exposed, network_isolated, has_controls = _storage_account_context(body)
    elif resource_type == "azurerm_key_vault":
        publicly_exposed, network_isolated, has_controls = _key_vault_context(body)
    elif resource_type in _APP_SERVICE_TYPES:
        publicly_exposed, network_isolated, has_controls = _app_service_context(body)
    else:
        publicly_exposed = _any_nsg_publicly_exposed(resources)
        network_isolated = not publicly_exposed
        has_controls = _has_compensating_network_control(resources)

    return ResourceContext(
        resource_name=resource_name,
        publicly_exposed=publicly_exposed,
        network_isolated=network_isolated,
        has_compensating_controls=has_controls,
    )
