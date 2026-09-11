# Ejemplo de fixture: Storage Account con acceso público habilitado y SIN
# ninguna restricción de red ni control compensatorio.
# Hallazgo esperado: CKV_AZURE_35 (Checkov) - severidad estática HIGH,
# severidad contextual esperada: CRITICAL (exposición real, sin mitigación).

resource "azurerm_storage_account" "public_example" {
  name                     = "stexamplepublic"
  resource_group_name      = azurerm_resource_group.example.name
  location                 = azurerm_resource_group.example.location
  account_tier             = "Standard"
  account_replication_type = "LRS"

  public_network_access_enabled = true

  network_rules {
    default_action = "Allow"
  }
}
