# Ejemplo de fixture: App Service sin HTTPS forzado.
# Hallazgo esperado: CKV_AZURE_14 (Checkov) - severidad estática HIGH.

resource "azurerm_linux_web_app" "example" {
  name                = "app-example"
  resource_group_name = azurerm_resource_group.example.name
  location            = azurerm_resource_group.example.location
  service_plan_id     = azurerm_service_plan.example.id

  https_only = false

  site_config {}
}
