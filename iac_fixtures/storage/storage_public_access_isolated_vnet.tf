# Ejemplo de fixture: Storage Account con acceso publico habilitado,
# pero restringido a una VNet aislada sin salida a Internet (control compensatorio).
# Hallazgo esperado: CKV_AZURE_35 (Checkov) - severidad estática HIGH,
# severidad contextual esperada: MEDIUM (por el aislamiento de red).

resource "azurerm_storage_account" "example" {
  name                     = "stexampleisolated"
  resource_group_name      = azurerm_resource_group.example.name
  location                 = azurerm_resource_group.example.location
  account_tier             = "Standard"
  account_replication_type = "LRS"

  public_network_access_enabled = true

  network_rules {
    default_action = "Deny"
    virtual_network_subnet_ids = [azurerm_subnet.isolated.id]
  }
}
