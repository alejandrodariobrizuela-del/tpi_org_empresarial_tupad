# Chatbot de Gestión de Solicitud de Vacaciones

Trabajo Práctico Integrador — Cátedra **Organización Empresarial**
Tecnicatura Universitaria en Programación a Distancia (UTN)

Simulador en Python de un chatbot institucional que automatiza el proceso administrativo de solicitud de vacaciones, siguiendo el modelo de procesos **BPMN 2.0** diseñado para este TPI.

---

## 📋 Descripción del proyecto

Este bot reemplaza el proceso manual actual (envío de mails entre el empleado, RR.HH. y el jefe) por un flujo automatizado donde el empleado:

1. Valida su identidad con su número de legajo.
2. Consulta su saldo de días disponibles en tiempo real.
3. Solicita una cantidad de días y una fecha de inicio.
4. Recibe confirmación inmediata, quedando la solicitud registrada con estado **Pendiente**.

El bot está implementado como **simulador de consola**, replicando la lógica que tendría desplegado sobre la API de **Telegram** (ver justificación en el apartado Enlances en Selección de Stack).

---

## 🗂️ Estructura del repositorio

```
chatbot-vacaciones-tpi/
├── src/
│   └── chatbot_vacaciones.py      # Código fuente del bot
├── data/
│   └── empleados.csv              # Base de datos simulada de empleados
|
├── .gitignore
└── README.md
```

> **Nota:** el archivo `solicitudes.csv` no forma parte del repositorio. Se genera automáticamente la primera vez que se confirma una solicitud y queda excluido mediante `.gitignore`.

---

## ⚙️ Requisitos

- [Python 3.10](https://www.python.org/downloads/) o superior
- No requiere librerías externas (usa únicamente `csv` y `datetime`, ambas de la biblioteca estándar)

---

## 🚀 Cómo desplegarlo y ejecutarlo

### 1. Clonar el repositorio

```bash
git clone https://github.com/alejandrodariobrizuela-del/tpi_org_empresarial_tupad
cd tpi_org_empresarial_tupad
```

### 2. Verificar que Python esté instalado

```bash
python --version
```

### 3. Ejecutar el bot

El archivo `chatbot_vacaciones.py` espera encontrar `empleados.csv` en su **misma carpeta de trabajo**, así que hay que ejecutarlo desde `src/` o copiar el CSV junto al script:

```bash
cd src
cp ../data/empleados.csv .
python chatbot.py
```

### 4. Usar el bot

```
Bot: Para iniciar, escribí /start

Vos: /start
Bot: Ingresá tu número de legajo:

Vos: 1001
Bot: Identidad verificada. Juan García — Saldo: 15 días.
...
```

Ver el detalle completo de comandos y mensajes de error en `docs/manual_de_usuario.docx`.

---

## 🧠 Lógica del sistema

| Componente | Implementación |
|---|---|
| Persistencia | Archivos CSV (`empleados.csv`, `solicitudes.csv`) |
| Máquina de Estados | Variable `estado_actual` (`INICIO`, `PEDIR_LEGAJO`, `PEDIR_DIAS`, `PEDIR_FECHA`, `CONFIRMACION`, `FIN`) |
| Validaciones | Funciones `validar_entero_positivo()` y `validar_fecha()` |
| Gateway 1 — ¿Existe legajo? | Bucle de reintento ante legajo inválido o inexistente |
| Gateway 2 — ¿Días ≤ Saldo? | Finaliza el proceso si el saldo es insuficiente (sin reintento) |

El detalle completo de cada variable está documentado en el apartado de Enlaces mas abajo, en Diccionario de datos.

---

## 👤 Autores

Alejandro Darío Brizuela y Lautaro Gorge — TUPaD, UTN — 2026

---

## 🔗 Enlaces

- [Manual de Usuario](https://drive.google.com/file/d/1T672YvXflrnDuZdENjLC4qAstUIQLzqU/view?usp=sharing)
- [Selección de Stack](https://drive.google.com/file/d/1c0F9aY1dy_vyeVZiWP3XDoxZa_XKaLzM/view?usp=sharing)
- [Diccionario de Datos](https://drive.google.com/file/d/1nqbHhAVV-3odGIgzW2hb9rr2DWOYkevg/view?usp=sharing)
- [Pruebas de estrés](https://drive.google.com/file/d/1ihPKd4QE-VCtYGgSQXrOp-AZWnMGpsQV/view?usp=sharing)