# Ejemplo de fixture: VM aislada de red (sin IP pública, solo en VNet privada)
# pero con disco de datos sin cifrado.
# Hallazgo esperado: CKV_AZURE_2 (Checkov) - severidad estática MEDIUM,
# severidad contextual esperada: LOW (por el aislamiento de red).

resource "azurerm_managed_disk" "data_example" {
  name                 = "disk-data-example"
  location             = azurerm_resource_group.example.location
  resource_group_name  = azurerm_resource_group.example.name
  storage_account_type = "Standard_LRS"
  create_option        = "Empty"
  disk_size_gb         = 128
  encryption_settings {
    enabled = false
  }
}

resource "azurerm_linux_virtual_machine" "isolated_example" {
  name                = "vm-isolated-example"
  resource_group_name = azurerm_resource_group.example.name
  location            = azurerm_resource_group.example.location
  size                = "Standard_B1s"
  admin_username      = "adminuser"

  network_interface_ids = [azurerm_network_interface.isolated_example.id]
}
