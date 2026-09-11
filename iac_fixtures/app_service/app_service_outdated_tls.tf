# Ejemplo de fixture: App Service con versión mínima de TLS obsoleta (1.1),
# restringido mediante Access Restrictions a una única IP corporativa
# (control compensatorio).
# Hallazgo esperado: CKV_AZURE_15 (Checkov) - severidad estática MEDIUM,
# severidad contextual esperada: LOW.

resource "azurerm_linux_web_app" "outdated_tls_example" {
  name                = "app-outdated-tls-example"
  resource_group_name = azurerm_resource_group.example.name
  location            = azurerm_resource_group.example.location
  service_plan_id     = azurerm_service_plan.example.id

  https_only = true

  site_config {
    minimum_tls_version = "1.1"

    ip_restriction {
      ip_address = "203.0.113.10/32"
      action     = "Allow"
      priority   = 100
      name       = "corporate-office"
    }
  }
}
