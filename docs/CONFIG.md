# Guía de configuración

Esta guía explica cómo manejar la configuración local y las API keys de **MeXiCOSINT**.

---

## Archivo de configuración

MeXiCOSINT puede usar un archivo local para guardar API keys y otros valores de configuración.

La ruta recomendada es:

```text
~/.mx_osint_config.json
```

Este archivo debe existir solamente en tu computadora.

No debe subirse a GitHub.

---

## Crear el archivo de configuración

Puedes crear el archivo con:

```bash
nano ~/.mx_osint_config.json
```

Dentro del archivo puedes agregar tus API keys.

Ejemplo:

```json
{
  "abstractapi_key": "TU_ABSTRACTAPI_KEY",
  "numverify_key": "TU_NUMVERIFY_KEY",
  "shodan_key": "TU_SHODAN_KEY",
  "ipinfo_key": "TU_IPINFO_KEY",
  "ip2location_key": "TU_IP2LOCATION_KEY",
  "opencage_key": "TU_OPENCAGE_KEY"
}
```

Reemplaza cada valor con tu propia API key.

---

## Proteger el archivo

Para proteger el archivo de configuración local:

```bash
chmod 600 ~/.mx_osint_config.json
```

Esto limita el acceso al archivo únicamente a tu usuario.

---

## APIs opcionales

MeXiCOSINT puede funcionar parcialmente sin API keys.

Sin embargo, algunas funciones tendrán mejores resultados si se configuran servicios externos.

| Servicio    | Función                                                      |
| ----------- | ------------------------------------------------------------ |
| AbstractAPI | Validación y enriquecimiento de números telefónicos          |
| NumVerify   | Validación secundaria de números telefónicos                 |
| Shodan      | Enriquecimiento opcional relacionado con servicios expuestos |
| IPInfo      | Enriquecimiento de metadatos IP                              |
| IP2Location | Enriquecimiento de metadatos IP                              |
| OpenCage    | Geocodificación y soporte para mapas                         |

---

## Funcionamiento sin API keys

Si no configuras API keys, MeXiCOSINT puede seguir funcionando parcialmente.

Ejemplo:

```text
Sin API keys:
- Validación local
- Parsing básico
- Formato nacional/internacional
- Resultados limitados

Con API keys:
- Enriquecimiento adicional
- Validación secundaria
- Más fuentes de comparación
- Mejor contexto para reportes
```

---

## Archivos que NO deben subirse

No subas archivos que contengan claves, tokens o datos sensibles.

Ejemplos:

```text
.env
*.env
.mx_osint_config.json
config.json
secrets.json
keys.json
tokens.json
credentials.json
```

Si uno de estos archivos aparece en GitHub por accidente, elimina el archivo y rota las claves afectadas.

Porque sí, una API key subida a GitHub se convierte en comida gratis para bots antes de que termines de pestañear. Qué civilización tan brillante.

---

## Revisar antes de hacer commit

Antes de subir cambios, puedes buscar posibles claves dentro del proyecto:

```bash
grep -Ri "api_key\|apikey\|token\|secret\|password\|credential" .
```

Si aparece una clave real, elimínala antes de hacer commit.

También puedes revisar los archivos modificados con:

```bash
git status
```

Y revisar diferencias con:

```bash
git diff
```

---

## Configuración recomendada en `.gitignore`

El archivo `.gitignore` debe incluir entradas para evitar subir secretos por accidente:

```gitignore
.env
*.env
.mx_osint_config.json
config.json
secrets.json
keys.json
tokens.json
credentials.json
*.key
*.pem
```

---

## Estructura recomendada

La configuración sensible debe vivir fuera del repositorio:

```text
/home/usuario/.mx_osint_config.json
```

o:

```text
~/.mx_osint_config.json
```

El repositorio solo debe contener ejemplos, documentación y código.

---

## Ejemplo seguro para documentación

Si quieres mostrar un ejemplo en la documentación, usa valores falsos:

```json
{
  "abstractapi_key": "TU_ABSTRACTAPI_KEY",
  "numverify_key": "TU_NUMVERIFY_KEY"
}
```

Nunca uses claves reales en ejemplos públicos.

---

## Permisos recomendados

Revisa los permisos actuales:

```bash
ls -la ~/.mx_osint_config.json
```

Aplica permisos seguros:

```bash
chmod 600 ~/.mx_osint_config.json
```

Resultado esperado aproximado:

```text
-rw------- 1 usuario usuario ... /home/usuario/.mx_osint_config.json
```

---

## Si subiste una API key por accidente

1. Elimina la clave del repositorio.
2. Haz commit del cambio.
3. Entra al panel del proveedor de la API.
4. Revoca o elimina la API key expuesta.
5. Crea una API key nueva.
6. Actualiza tu archivo local `~/.mx_osint_config.json`.

No basta con borrar la línea del README o del archivo actual. Git guarda historial. Porque Git es útil, pero también es un archivista con tendencias obsesivas.

---

## Variables de entorno

En futuras versiones, MeXiCOSINT también podría usar variables de entorno.

Ejemplo:

```bash
export ABSTRACTAPI_KEY="TU_ABSTRACTAPI_KEY"
```

Pero la forma recomendada para este proyecto es usar:

```text
~/.mx_osint_config.json
```

---

## Buenas prácticas

* Mantén tus API keys fuera del repositorio.
* No compartas capturas donde se vean claves.
* No hardcodees API keys dentro del código.
* Usa permisos `600` para archivos sensibles.
* Rota cualquier clave que haya sido expuesta.
* Usa ejemplos falsos en documentación pública.
* Revisa cambios antes de hacer commit.

---

## Estado

Si el archivo existe y tiene permisos correctos, puedes ejecutar:

```bash
bash bin/mexicosint
```

Y MeXiCOSINT debería poder leer la configuración local según las funciones disponibles en la versión actual.
