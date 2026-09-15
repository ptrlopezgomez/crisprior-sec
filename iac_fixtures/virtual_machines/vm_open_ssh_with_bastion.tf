# Ejemplo de fixture: mismo puerto SSH (22) abierto a Internet que
# vm_open_ssh_public.tf, pero esta vez con un Bastion Host presente en el
# mismo directorio como control compensatorio.
# Hallazgo esperado: CKV_AZURE_9 (Checkov) - severidad estática HIGH.
# Severidad contextual esperada: reducida frente a vm_open_ssh_public.tf,
# ya que has_compensating_controls=true (el motor detecta el Bastion Host).

resource "azurerm_network_security_group" "bastion_example" {
  name                = "nsg-vm-bastion-example"
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

resource "azurerm_linux_virtual_machine" "bastion_example" {
  name                = "vm-bastion-example"
  resource_group_name = azurerm_resource_group.example.name
  location            = azurerm_resource_group.example.location
  size                = "Standard_B1s"
  admin_username      = "adminuser"

  network_interface_ids = [azurerm_network_interface.bastion_example.id]
}

resource "azurerm_bastion_host" "example" {
  name                = "bastion-example"
  location            = azurerm_resource_group.example.location
  resource_group_name = azurerm_resource_group.example.name

  ip_configuration {
    name                 = "configuration"
    subnet_id            = azurerm_subnet.bastion.id
    public_ip_address_id = azurerm_public_ip.bastion.id
  }
}
