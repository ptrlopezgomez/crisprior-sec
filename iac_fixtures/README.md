# Fixtures de Terraform para el protocolo de validación (HU-08)

Este directorio contiene los 50 archivos Terraform de prueba usados en el
Capítulo 6 (Validación y Diseño Experimental) para medir la reducción de la
fatiga por alertas frente al baseline de Checkov y tfsec.

## Convención

- `virtual_machines/` — VMs con fallas conocidas (puertos abiertos, discos sin cifrar, etc.)
- `storage/` — Storage Accounts (acceso público, TLS deshabilitado, sin cifrado)
- `keyvault/` — Key Vaults (políticas de acceso laxas, purge protection deshabilitada)
- `app_service/` — App Services (HTTPS no forzado, autenticación deshabilitada)

Cada archivo `.tf` debe ir acompañado de un `.expected.json` con el hallazgo
esperado (severidad estática y severidad contextual "gold standard" asignada
por el panel de expertos DevSecOps), para poder calcular el coeficiente de
Spearman y el F1-Score del clasificador.

Nombrado sugerido: `<servicio>_<escenario>.tf`, p. ej. `vm_open_ssh_public.tf`.
