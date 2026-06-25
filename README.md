![MeXiCOSINT Banner](mexsint.png)

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![OSINT](https://img.shields.io/badge/OSINT-Mexico-red.svg)

## Tabla de Contenidos
- [Instalación](#instalación)
- [Uso](#uso)
- [Módulos](#módulos)
- [Dependencias](#dependencias)
- [Nota](#nota)

# MeXiCOSINT

Herramienta de OSINT para numeros telefonicos Mexicanos.

## Instalacion

git clone https://github.com/KiMiGuel/MeXiCOSINT.git

cd MeXiCOSINT

python3 -m venv venv

source venv/bin/activate

pip install -r requirements.txt

## Ejecutar con launcher

Después de instalar las dependencias, puedes ejecutar MeXiCOSINT con:

```bash
bash bin/mexicosint

## Uso

python3 bash bin/mexicosint

## Modulos

- local_parser.py - Validacion y parsing de numeros mexicanos
- quienhabla.py - Integracion con QuienHabla.mx
- ift_sns.py - Procesamiento de datos IFT/SNS

## Dependencias

requests, beautifulsoup4, phonenumbers, python-dotenv, lxml

## Nota

No subas tu .env al repositorio.
