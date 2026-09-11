# Ejemplo de fixture: Key Vault con acceso de red público habilitado
# y sin reglas de firewall (bypass = "AzureServices" + default Allow).
# Hallazgo esperado: CKV_AZURE_109 (Checkov) - severidad estática HIGH.

resource "azurerm_key_vault" "public_example" {
  name                     = "kv-public-example"
  location                 = azurerm_resource_group.example.location
  resource_group_name      = azurerm_resource_group.example.name
  tenant_id                = data.azurerm_client_config.current.tenant_id
  sku_name                 = "standard"
  purge_protection_enabled = true

  public_network_access_enabled = true

  network_acls {
    default_action = "Allow"
    bypass         = "AzureServices"
  }
}
