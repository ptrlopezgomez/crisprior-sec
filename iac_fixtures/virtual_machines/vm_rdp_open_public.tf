# Ejemplo de fixture: VM con NSG que expone el puerto 3389 (RDP) a Internet,
# sin ningún control compensatorio (Bastion Host o VPN).
# Hallazgo esperado: CKV_AZURE_10 (Checkov) - severidad estática HIGH.

resource "azurerm_network_security_group" "rdp_example" {
  name                = "nsg-vm-rdp-example"
  location            = azurerm_resource_group.example.location
  resource_group_name = azurerm_resource_group.example.name

  security_rule {
    name                       = "RDP"
    priority                   = 100
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "3389"
    source_address_prefix      = "0.0.0.0/0"
    destination_address_prefix = "*"
  }
}

resource "azurerm_windows_virtual_machine" "rdp_example" {
  name                = "vm-rdp-example"
  resource_group_name = azurerm_resource_group.example.name
  location            = azurerm_resource_group.example.location
  size                = "Standard_B2s"
  admin_username      = "adminuser"
  admin_password      = "ChangeMe123!"

  network_interface_ids = [azurerm_network_interface.rdp_example.id]
}
