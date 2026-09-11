# Ejemplo de fixture: App Service público, con HTTPS forzado pero con
# autenticación integrada (Easy Auth) deshabilitada.
# Hallazgo esperado: CKV_AZURE_13 (Checkov) - severidad estática HIGH.

resource "azurerm_linux_web_app" "no_auth_example" {
  name                = "app-no-auth-example"
  resource_group_name = azurerm_resource_group.example.name
  location            = azurerm_resource_group.example.location
  service_plan_id     = azurerm_service_plan.example.id

  https_only = true

  auth_settings {
    enabled = false
  }

  site_config {}
}
