import csv
from datetime import datetime, timedelta

# BASE DE DATOS (CSV)
ARCHIVO_CSV = "empleados.csv"
ARCHIVO_SOLICITUDES = "solicitudes.csv"


def cargar_empleados():
    empleados = {}
    try:
        with open(ARCHIVO_CSV, newline="", encoding="utf-8") as archivo:
            lector = csv.DictReader(archivo)
            for fila in lector:
                legajo = int(fila["legajo"])
                empleados[legajo] = {
                    "nombre": fila["nombre"],
                    "apellido": fila["apellido"],
                    "dias_disponibles": int(fila["dias_disponibles"]),
                    "dias_tomados": int(fila["dias_tomados"])
                }
    except FileNotFoundError:
        print("[ERROR] No se encontró el archivo empleados.csv")
    return empleados


def guardar_solicitud(legajo, nombre, apellido, dias, fecha_inicio):
    # Calcular la fecha de fin sumando los días al inicio
    fecha_dt = datetime.strptime(fecha_inicio, "%d/%m/%Y")
    fecha_fin = fecha_dt + timedelta(days=dias - 1)
    fecha_fin_str = fecha_fin.strftime("%d/%m/%Y")

    # Marca de tiempo del momento en que se registra
    timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    encabezados = ["legajo", "nombre", "apellido",
                "dias_solicitados", "fecha_inicio",
                "fecha_fin", "estado", "timestamp"]

    # Verificar si el archivo ya existe para no repetir encabezados
    try:
        with open(ARCHIVO_SOLICITUDES, "r", encoding="utf-8"):
            archivo_existe = True
    except FileNotFoundError:
        archivo_existe = False

    with open(ARCHIVO_SOLICITUDES, "a", newline="", encoding="utf-8") as archivo:
        escritor = csv.DictWriter(archivo, fieldnames=encabezados)
        if not archivo_existe:
            escritor.writeheader()
        escritor.writerow({
            "legajo": legajo,
            "nombre": nombre,
            "apellido": apellido,
            "dias_solicitados": dias,
            "fecha_inicio": fecha_inicio,
            "fecha_fin": fecha_fin_str,
            "estado": "Pendiente",
            "timestamp": timestamp
        })


def actualizar_saldo(legajo, dias_tomados_nuevos):
    filas = []
    with open(ARCHIVO_CSV, newline="", encoding="utf-8") as archivo:
        lector = csv.DictReader(archivo)
        encabezados = lector.fieldnames
        for fila in lector:
            if int(fila["legajo"]) == legajo:
                fila["dias_disponibles"] = str(
                    int(fila["dias_disponibles"]) - dias_tomados_nuevos
                )
                fila["dias_tomados"] = str(
                    int(fila["dias_tomados"]) + dias_tomados_nuevos
                )
            filas.append(fila)

    with open(ARCHIVO_CSV, "w", newline="", encoding="utf-8") as archivo:
        escritor = csv.DictWriter(archivo, fieldnames=encabezados)
        escritor.writeheader()
        escritor.writerows(filas)


estado_actual = "INICIO"

sesion = {
    "legajo": None,
    "empleado": None,
    "dias_solicitados": None,
    "fecha_inicio": None
}

def reiniciar_sesion():
    """Limpia los datos de sesión para empezar de nuevo."""
    global estado_actual, sesion
    estado_actual = "PEDIR_LEGAJO"
    sesion = {
        "legajo": None,
        "empleado": None,
        "dias_solicitados": None,
        "fecha_inicio": None
    }

# VALIDACIONES (Camino Infeliz / Robustez)
def validar_entero_positivo(texto):
    try:
        numero = int(texto.strip())
        if numero > 0:
            return True, numero
        else:
            return False, None
    except ValueError:
        return False, None


def validar_fecha(texto):
    try:
        fecha = datetime.strptime(texto.strip(), "%d/%m/%Y")
        if fecha.date() < datetime.today().date():
            return False, None  # No se puede pedir vacaciones en el pasado
        return True, texto.strip()
    except ValueError:
        return False, None


# LÓGICA DEL CHATBOT (Procesar cada mensaje del usuario)
def procesar_mensaje(mensaje, empleados):
    global estado_actual, sesion
    mensaje = mensaje.strip()


    # ESTADO: INICIO → espera /start
    if estado_actual == "INICIO":
        if mensaje.lower() == "/start":
            estado_actual = "PEDIR_LEGAJO"
            return (
                "👋 ¡Bienvenido al sistema de Gestión de Vacaciones!\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                "Por favor, ingresá tu número de legajo para continuar:"
            )
        else:
            return "ℹ️< Para iniciar, escribí el comando: /start"

    # ESTADO: PEDIR_LEGAJO → valida legajo y consulta CSV
    # Gateway 1: ¿Existe el legajo?
    elif estado_actual == "PEDIR_LEGAJO":
        es_valido, legajo = validar_entero_positivo(mensaje)

        # Camino Infeliz: formato incorrecto
        if not es_valido:
            return (
                "⚠️ El legajo debe ser un número entero positivo.\n"
                "Ejemplo: 1001\n"
                "Por favor, ingresalo nuevamente:"
            )

        # Gateway 1 - Camino No: legajo no existe en la base de datos
        if legajo not in empleados:
            return (
                f"✖️ El legajo {legajo} no se encuentra registrado.\n"
                "Verificá el número e intentá nuevamente:"
            )

        # Gateway 1 - Camino Sí: legajo válido
        sesion["legajo"] = legajo
        sesion["empleado"] = empleados[legajo]
        emp = sesion["empleado"]
        estado_actual = "PEDIR_DIAS"

        return (
            f"✅ Identidad verificada.\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"👤 Empleado : {emp['nombre']} {emp['apellido']}\n"
            f"📅 Saldo disponible: {emp['dias_disponibles']} días\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"¿Cuántos días de vacaciones querés solicitar?"
        )

    # ESTADO: PEDIR_DIAS → valida cantidad y compara con saldo
    # Gateway 2: ¿Días solicitados ≤ saldo disponible?
    elif estado_actual == "PEDIR_DIAS":
        es_valido, dias = validar_entero_positivo(mensaje)

        # Camino Infeliz: formato incorrecto
        if not es_valido:
            return (
                "⚠️ La cantidad de días debe ser un número entero positivo.\n"
                "Ejemplo: 5\n"
                "Por favor, ingresala nuevamente:"
            )

        saldo = sesion["empleado"]["dias_disponibles"]

        # Gateway 2 - Camino No: saldo insuficiente → FIN del proceso
        # Envía Alerta: Saldo Insuficiente y llega a un Evento de Fin, no hay bucle de reintento.
        if dias > saldo:
            estado_actual = "FIN"
            emp = sesion["empleado"]
            return (
                f"❌ SOLICITUD RECHAZADA: Saldo Insuficiente\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"Solicitaste {dias} días pero tu saldo disponible\n"
                f"es de {emp['dias_disponibles']} días.\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"El proceso ha finalizado.\n"
                f"Para iniciar una nueva solicitud, escribí /start"
            )

        # Gateway 2 - Camino Sí: saldo suficiente
        sesion["dias_solicitados"] = dias
        estado_actual = "PEDIR_FECHA"

        return (
            f"✅ Cantidad de días válida: {dias} día(s).\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"¿Cuál es la fecha de inicio de tus vacaciones?\n"
            f"Formato requerido: DD/MM/AAAA\n"
            f"Ejemplo: 15/01/2027"
        )


    # ESTADO: PEDIR_FECHA → valida la fecha de inicio
    elif estado_actual == "PEDIR_FECHA":
        es_valida, fecha = validar_fecha(mensaje)

        # Camino Infeliz: formato incorrecto o fecha pasada
        if not es_valida:
            return (
                "⚠️ Fecha inválida. Asegurate de:\n"
                "  • Usar el formato DD/MM/AAAA\n"
                "  • Que la fecha no sea del pasado\n"
                "Por favor, ingresala nuevamente:"
            )

        sesion["fecha_inicio"] = fecha
        estado_actual = "CONFIRMACION"

        emp = sesion["empleado"]
        dias = sesion["dias_solicitados"]

        # Calcular fecha de fin para mostrar en el resumen
        fecha_dt = datetime.strptime(fecha, "%d/%m/%Y")
        fecha_fin = (fecha_dt + timedelta(days=dias - 1)).strftime("%d/%m/%Y")

        return (
            f"📋 RESUMEN DE TU SOLICITUD\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"👤 Empleado    : {emp['nombre']} {emp['apellido']}\n"
            f"🔢 Legajo      : {sesion['legajo']}\n"
            f"📅 Desde       : {fecha}\n"
            f"📅 Hasta       : {fecha_fin}\n"
            f"🗓️ Días solicitados: {dias}\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"¿Confirmás la solicitud?\n"
            f"  SI → Escribí 'si'\n"
            f"  NO → Escribí 'no' para cancelar"
        )

    # ESTADO: CONFIRMACION → registra o cancela
    elif estado_actual == "CONFIRMACION":
        if mensaje.lower() in ["si", "sí", "s"]:
            guardar_solicitud(
                sesion["legajo"],
                sesion["empleado"]["nombre"],
                sesion["empleado"]["apellido"],
                sesion["dias_solicitados"],
                sesion["fecha_inicio"]
            )
            actualizar_saldo(sesion["legajo"], sesion["dias_solicitados"])

            emp = sesion["empleado"]
            dias = sesion["dias_solicitados"]
            saldo_restante = emp["dias_disponibles"] - dias

            estado_actual = "FIN"
            return (
                f"✅ ¡SOLICITUD REGISTRADA CON ÉXITO!\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"Tu solicitud fue enviada con estado: PENDIENTE\n"
                f"Recibirás la aprobación de tu jefe a la brevedad.\n"
                f"Días restantes luego de esta solicitud: {saldo_restante}\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"Gracias, {emp['nombre']}. ¡Que disfrutes tus vacaciones! 🌴\n"
                f"Para hacer otra consulta, escribí /start"
            )

        elif mensaje.lower() in ["no", "n"]:
            estado_actual = "FIN"
            return (
                "✖️ Solicitud cancelada.\n"
                "Tus días disponibles no fueron modificados.\n"
                "Para iniciar una nueva solicitud, escribí /start"
            )
        else:
            return (
                "⚠️ Respuesta no reconocida.\n"
                "Por favor escribí 'si' para confirmar o 'no' para cancelar:"
            )

    # ESTADO: FIN → el proceso terminó
    elif estado_actual == "FIN":
        if mensaje.lower() == "/start":
            reiniciar_sesion()
            return (
                "🔄 Nueva solicitud iniciada.\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                "Por favor, ingresá tu número de legajo:"
            )
        else:
            return (
                "ℹ️ El proceso ha finalizado.\n"
                "Para iniciar una nueva solicitud, escribí /start"
            )


# BUCLE PRINCIPAL (Simulador de consola)
def main():
    print("=" * 50)
    print("  SISTEMA DE GESTIÓN DE VACACIONES")
    print("  Simulador de Chatbot - UTN TUPaD")
    print("=" * 50)
    print("  (Escribí 'salir' para cerrar el programa)")
    print("=" * 50)
    print()

    empleados = cargar_empleados()
    if not empleados:
        print("[ERROR CRÍTICO] No se pudo cargar la base de datos. Verificá el archivo empleados.csv")
        return

    print("🤖 Bot: Para iniciar, escribí /start\n")

    while True:
        try:
            entrada = input("👤 Vos: ").strip()
        except KeyboardInterrupt:
            print("\n\n[Sistema] Programa cerrado.")
            break

        if entrada.lower() == "salir":
            print("🤖 Bot: ¡Hasta luego!")
            break

        if not entrada:
            continue

        respuesta = procesar_mensaje(entrada, empleados)
        print(f"\n🤖 Bot: {respuesta}\n")


if __name__ == "__main__":
    main()
