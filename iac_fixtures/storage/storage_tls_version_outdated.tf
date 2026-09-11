# Ejemplo de fixture: Storage Account que permite TLS 1.0 (versión obsoleta),
# pero sin acceso público (solo accesible desde dentro de la VNet).
# Hallazgo esperado: CKV_AZURE_44 (Checkov) - severidad estática MEDIUM,
# severidad contextual esperada: LOW (mitigado por el aislamiento de red).

resource "azurerm_storage_account" "tls_example" {
  name                     = "stexampletls"
  resource_group_name      = azurerm_resource_group.example.name
  location                 = azurerm_resource_group.example.location
  account_tier             = "Standard"
  account_replication_type = "LRS"

  public_network_access_enabled = false
  min_tls_version                = "TLS1_0"

  network_rules {
    default_action             = "Deny"
    virtual_network_subnet_ids = [azurerm_subnet.isolated.id]
  }
}
