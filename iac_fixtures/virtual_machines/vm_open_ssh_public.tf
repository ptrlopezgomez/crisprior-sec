# Ejemplo de fixture: VM con NSG que expone el puerto 22 (SSH) a Internet.
# Hallazgo esperado: CKV_AZURE_9 (Checkov) - severidad estática HIGH.

resource "azurerm_network_security_group" "example" {
  name                = "nsg-vm-example"
  location            = azurerm_resource_group.example.location
  resource_group_name = azurerm_resource_group.example.name

  security_rule {
    name                       = "SSH"
    priority                   = 100
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "22"
    source_address_prefix      = "0.0.0.0/0"
    destination_address_prefix = "*"
  }
}

resource "azurerm_linux_virtual_machine" "example" {
  name                = "vm-example"
  resource_group_name = azurerm_resource_group.example.name
  location            = azurerm_resource_group.example.location
  size                = "Standard_B1s"
  admin_username      = "adminuser"

  network_interface_ids = [azurerm_network_interface.example.id]
}
