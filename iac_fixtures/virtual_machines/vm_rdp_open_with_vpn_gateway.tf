# Ejemplo de fixture: mismo puerto RDP (3389) abierto a Internet que
# vm_rdp_open_public.tf, pero con un VPN Gateway presente en el mismo
# directorio como control compensatorio.
# Hallazgo esperado: CKV_AZURE_10 (Checkov) - severidad estática HIGH.
# Severidad contextual esperada: reducida frente a vm_rdp_open_public.tf,
# ya que has_compensating_controls=true (el motor detecta el VPN Gateway).

resource "azurerm_network_security_group" "vpn_example" {
  name                = "nsg-vm-vpn-example"
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

resource "azurerm_windows_virtual_machine" "vpn_example" {
  name                = "vm-rdp-vpn-example"
  resource_group_name = azurerm_resource_group.example.name
  location            = azurerm_resource_group.example.location
  size                = "Standard_B2s"
  admin_username      = "adminuser"
  admin_password      = "ChangeMe123!"

  network_interface_ids = [azurerm_network_interface.vpn_example.id]
}

resource "azurerm_vpn_gateway" "example" {
  name                = "vpn-gateway-example"
  location            = azurerm_resource_group.example.location
  resource_group_name = azurerm_resource_group.example.name
  virtual_hub_id      = azurerm_virtual_hub.example.id
}
