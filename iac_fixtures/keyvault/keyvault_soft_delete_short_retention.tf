# Ejemplo de fixture: Key Vault con retención de soft-delete en el mínimo
# permitido (7 días) y acceso restringido a una subred aislada (control
# compensatorio).
# Hallazgo esperado: CKV_AZURE_42 (Checkov) - severidad estática MEDIUM,
# severidad contextual esperada: LOW.

resource "azurerm_key_vault" "isolated_example" {
  name                       = "kv-isolated-example"
  location                   = azurerm_resource_group.example.location
  resource_group_name        = azurerm_resource_group.example.name
  tenant_id                  = data.azurerm_client_config.current.tenant_id
  sku_name                   = "standard"
  purge_protection_enabled   = true
  soft_delete_retention_days = 7

  public_network_access_enabled = false

  network_acls {
    default_action             = "Deny"
    bypass                     = "None"
    virtual_network_subnet_ids = [azurerm_subnet.isolated.id]
  }
}
