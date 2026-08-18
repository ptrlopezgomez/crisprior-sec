# Ejemplo de fixture: Key Vault sin purge protection habilitada.
# Hallazgo esperado: CKV_AZURE_110 (Checkov) - severidad estática MEDIUM.

resource "azurerm_key_vault" "example" {
  name                     = "kv-example"
  location                 = azurerm_resource_group.example.location
  resource_group_name      = azurerm_resource_group.example.name
  tenant_id                = data.azurerm_client_config.current.tenant_id
  sku_name                 = "standard"
  purge_protection_enabled = false
}
