import datetime
import os

# --- Autenticación de usuarios autorizados ---
cajeros_autorizados = {
    "Alvaro": "alvaro1234",
    "Juan": "juansito",
    "Julia": "qwertyuiop"
}

def login():
    usuario = input("Ingresa tu nombre de usuario: ").strip()
    contraseña = input("Ingresa tu contraseña: ").strip()
    if usuario not in cajeros_autorizados or cajeros_autorizados[usuario] != contraseña:
        print("NO ESTÁS AUTORIZADO")
        return None
    print(f"Bienvenido, {usuario}!")
    return usuario

# --- Módulos para tienda ---
class Inventario:
    def __init__(self):
        # Producto: [precio, cantidad]
        self.productos = {
            "refresco": [20.0, 25],
            "cocacola": [18.0, 40],
            "pepsi": [17.0, 30],
            "agua": [13.0, 50],
            "galletas": [12.5, 25],
            "papas": [15.0, 35],
            "pan": [28.0, 20],
            "leche": [25.0, 18],
            "cerveza": [21.0, 38],
            "jugo": [14.5, 22],
            "chocolate": [16.0, 15],
            "chicles": [9.0, 28],
            "salchichas": [33.0, 12],
            "queso": [45.0, 8],
            "cafe": [19.0, 20],
            "servilletas": [18.5, 21]
        }

    def mostrar(self):
        print("\n--- Inventario ---")
        for producto, datos in sorted(self.productos.items()):
            precio, cantidad = datos
            nombre = producto.replace('_', ' ').title()
            print(f"{nombre}: ${precio:.2f} ({cantidad} disponibles)")

    def consultar_precio(self, producto):
        if producto in self.productos:
            return self.productos[producto][0]
        return None

    def actualizar_stock(self, producto, cantidad):
        if producto in self.productos and self.productos[producto][1] >= cantidad:
            self.productos[producto][1] -= cantidad
            return True
        return False

    def agregar_producto(self, producto, precio, cantidad):
        producto_key = producto.strip().lower().replace(' ', '_')
        if producto_key not in self.productos:
            self.productos[producto_key] = [float(precio), int(cantidad)]
        else:
            self.productos[producto_key][1] += int(cantidad)

class TiendaConveniencia:
    def __init__(self, operador):
        self.inventario = Inventario()
        self.ticket_num = 1
        self.operador = operador
        self.transacciones = []  # Lista para almacenar transacciones antes del corte

    def _registro_venta(self, carrito, total, folio):
        ahora = datetime.datetime.now().isoformat(sep=' ', timespec='seconds')
        registro = {
            "folio": folio,
            "fecha": ahora,
            "tipo": "venta",
            "operador": self.operador,
            "items": carrito,
            "total": total
        }
        self.transacciones.append(registro)

    def _registro_servicio(self, servicio, monto, folio):
        ahora = datetime.datetime.now().isoformat(sep=' ', timespec='seconds')
        registro = {
            "folio": folio,
            "fecha": ahora,
            "tipo": "servicio",
            "operador": self.operador,
            "servicio": servicio,
            "monto": monto
        }
        self.transacciones.append(registro)

    def _registro_recarga(self, telefono, monto, folio):
        ahora = datetime.datetime.now().isoformat(sep=' ', timespec='seconds')
        registro = {
            "folio": folio,
            "fecha": ahora,
            "tipo": "recarga",
            "operador": self.operador,
            "telefono": telefono,
            "monto": monto
        }
        self.transacciones.append(registro)

    def _registro_devolucion(self, folio_original, monto, folio_nuevo):
        ahora = datetime.datetime.now().isoformat(sep=' ', timespec='seconds')
        registro = {
            "folio": folio_nuevo,
            "fecha": ahora,
            "tipo": "devolucion",
            "operador": self.operador,
            "folio_original": folio_original,
            "monto": monto
        }
        self.transacciones.append(registro)

    def vender_producto(self):
        carrito = []
        total = 0.0
        print("Ingrese productos al carrito (vacío para terminar):")
        while True:
            prod = input("Producto: ").strip().lower()
            if not prod:
                break
            prod_key = prod.replace(' ', '_')
            if prod_key not in self.inventario.productos:
                print("Producto no disponible.")
                continue
            try:
                cantidad = int(input("Cantidad: "))
                if cantidad <= 0:
                    print("Ingresa una cantidad mayor que cero.")
                    continue
            except ValueError:
                print("Cantidad inválida.")
                continue

            if self.inventario.actualizar_stock(prod_key, cantidad):
                precio = self.inventario.consultar_precio(prod_key)
                subtotal = precio * cantidad
                carrito.append({"producto": prod_key, "cantidad": cantidad, "precio": precio, "subtotal": subtotal})
                total += subtotal
            else:
                print("Stock insuficiente.")

        if carrito:
            print("\n--- TICKET ---")
            for it in carrito:
                nombre = it["producto"].replace('_', ' ').title()
                print(f"{it['cantidad']} x {nombre} @ ${it['precio']:.2f} = ${it['subtotal']:.2f}")
            ahora = datetime.datetime.now().strftime('%d-%m-%Y %H:%M')
            print(f"TOTAL: ${total:.2f}")
            print(f"Folio: {self.ticket_num}   {ahora}")
            # registrar transacción
            self._registro_venta(carrito, total, self.ticket_num)
            self.ticket_num += 1
        else:
            print("No se realizó ninguna venta.")

    def cobrar_servicio(self):
        servicio = input("Servicio (agua, luz, etc.): ").strip()
        try:
            monto = float(input("Monto a pagar: $"))
            print(f"Servicio '{servicio}' cobrado por ${monto:.2f}. Ticket #{self.ticket_num}")
            self._registro_servicio(servicio, monto, self.ticket_num)
            self.ticket_num += 1
        except ValueError:
            print("Monto inválido. Operación cancelada.")

    def recarga_telefono(self):
        telefono = input("Número de celular: ").strip()
        try:
            monto = float(input("Monto recarga: $"))
            print(f"Recarga de ${monto:.2f} realizada a {telefono}. Ticket #{self.ticket_num}")
            self._registro_recarga(telefono, monto, self.ticket_num)
            self.ticket_num += 1
        except ValueError:
            print("Monto inválido. Operación cancelada.")

    def corte_caja(self):
        # Genera un archivo .txt con todas las transacciones registradas
        if not self.transacciones:
            print("No hay transacciones para archivar. Corte vacío.")
            return

        ahora = datetime.datetime.now()
        nombre_archivo = f"corte_{ahora.strftime('%Y%m%d_%H%M%S')}.txt"
        ruta = os.path.join(os.getcwd(), nombre_archivo)
        try:
            with open(ruta, "w", encoding="utf-8") as f:
                f.write(f"Corte de caja - Fecha: {ahora.strftime('%d-%m-%Y %H:%M:%S')}\n")
                f.write(f"Operador: {self.operador}\n")
                f.write("=" * 50 + "\n\n")
                for tr in self.transacciones:
                    f.write(f"FOLIO: {tr.get('folio')} | FECHA: {tr.get('fecha')} | TIPO: {tr.get('tipo').upper()} | OPERADOR: {tr.get('operador')}\n")
                    if tr["tipo"] == "venta":
                        f.write("Items:\n")
                        for it in tr["items"]:
                            nombre = it["producto"].replace('_', ' ').title()
                            f.write(f"  - {it['cantidad']} x {nombre} @ ${it['precio']:.2f} = ${it['subtotal']:.2f}\n")
                        f.write(f"TOTAL VENTA: ${tr['total']:.2f}\n")
                    elif tr["tipo"] == "servicio":
                        f.write(f"  Servicio: {tr['servicio']} | Monto: ${tr['monto']:.2f}\n")
                    elif tr["tipo"] == "recarga":
                        f.write(f"  Recarga a: {tr['telefono']} | Monto: ${tr['monto']:.2f}\n")
                    elif tr["tipo"] == "devolucion":
                        f.write(f"  Devolución por folio: {tr['folio_original']} | Monto DEVOLUCIÓN: ${tr['monto']:.2f}\n")
                    f.write("-" * 50 + "\n")
                f.write("\nFIN DEL CORTE\n")
            print(f"Corte de caja guardado en: {ruta}")
            # opcional: limpiar transacciones después del corte
            self.transacciones.clear()
        except Exception as e:
            print("Error al escribir el archivo de corte:", e)

    def devolucion(self):
        folio = input("Folio del ticket a devolver: ").strip()
        if not folio:
            print("Folio inválido.")
            return
        try:
            monto = float(input("Monto a devolver: $"))
        except ValueError:
            print("Monto inválido. Operación cancelada.")
            return
        # registramos la devolución como transacción (folio nuevo)
        folio_nuevo = self.ticket_num
        print(f"Devolución procesada para el ticket #{folio}. Se generó folio de devolución #{folio_nuevo}")
        self._registro_devolucion(folio, monto, folio_nuevo)
        self.ticket_num += 1

    def menu(self):
        opciones = {
            "1": ("Venta de productos", self.vender_producto),
            "2": ("Cobrar servicios", self.cobrar_servicio),
            "3": ("Recarga telefónica", self.recarga_telefono),
            "4": ("Mostrar inventario", self.inventario.mostrar),
            "5": ("Devolución", self.devolucion),
            "6": ("Cerrar caja y generar corte (txt)", self.corte_caja)
        }
        while True:
            print("\n--- Menú Cajero Profesional ---")
            for k, v in opciones.items():
                print(f"{k}. {v[0]}")
            opcion = input("Selecciona opción: ").strip()
            if opcion in opciones:
                # Si es cerrar caja, ejecutar y salir
                if opcion == "6":
                    opciones[opcion][1]()
                    break
                else:
                    opciones[opcion][1]()
            else:
                print("Opción no válida, intenta de nuevo.")

if __name__ == "__main__":
    usuario = login()
    if usuario:
        TiendaConveniencia(usuario).menu()
