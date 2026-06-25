# Configuración

Esta guía explica cómo manejar la configuración local y las API keys de **MeXiCOSINT**.

---

## Archivo de configuración

MeXiCOSINT puede usar un archivo local para guardar API keys y otros valores de configuración.

Ubicación recomendada:

```text
~/.mx_osint_config.json

Este archivo debe existir solamente en tu computadora.

No debe subirse a GitHub.

Permisos recomendados

Para proteger el archivo:

chmod 600 ~/.mx_osint_config.json
Ejemplo de configuración

Ejemplo básico:

{
  "abstractapi_key": "TU_ABSTRACTAPI_KEY",
  "numverify_key": "TU_NUMVERIFY_KEY",
  "shodan_key": "TU_SHODAN_KEY",
  "ipinfo_key": "TU_IPINFO_KEY",
  "ip2location_key": "TU_IP2LOCATION_KEY",
  "opencage_key": "TU_OPENCAGE_KEY"
}

Reemplaza cada valor con tu propia API key.

APIs opcionales

MeXiCOSINT puede funcionar parcialmente sin algunas API keys.

Servicio	Función
AbstractAPI	Validación y enriquecimiento de números
NumVerify	Validación secundaria
Shodan	Búsqueda opcional relacionada con servicios expuestos
IPInfo	Datos relacionados con IP
IP2Location	Datos relacionados con IP
OpenCage	Geocodificación y mapas
No subir claves a GitHub

Antes de subir cambios, revisa que no hayas agregado tus claves por accidente.

Archivos que no deben subirse:

.env
*.env
.mx_osint_config.json
config.json
secrets.json
keys.json
Revisión rápida antes de hacer commit

Desde terminal puedes revisar si hay claves visibles usando:

grep -Ri "api_key\|apikey\|token\|secret\|password" .

Si aparece una clave real, elimínala antes de subir cambios.

Buenas prácticas
Usa claves personales solamente en tu entorno local.
No hardcodees API keys dentro del código.
No publiques capturas donde se vean claves.
Rota una API key si la subiste accidentalmente.
Mantén .gitignore actualizado.
