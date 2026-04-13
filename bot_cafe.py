import pandas as pd
import pywhatkit as kit
import time
from datetime import datetime

# =============== CONFIGURACIÓN ===============
ruta_csv = r'archivo csv'

def crear_mensaje(nombre, kilo, tostion, molienda, total, pedido_id):
    return f"""Hola {nombre} (◕‿◕),
Tu pedido #{pedido_id} de {kilo} kilos con tostión {tostion} y molienda {molienda} está listo ✅
Debes pagar un total de ${total},
Gracias por confiar en nosotros ☕ LA HUMANCIA ☺️ ✧ദ്ദി(˵•̀ ᴗ•̀˵)✧"""

print(f"🚀 Iniciando envío AUTOMÁTICO - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# Leer CSV
df = pd.read_csv(ruta_csv)

# Crear columna de control si no existe
if 'mensaje_enviado' not in df.columns:
    df['mensaje_enviado'] = 'no'

# Limpieza de datos
df['teléfono'] = df['teléfono'].astype(str).str.strip().str.replace('.0', '', regex=False)
df['total'] = pd.to_numeric(df['total'], errors='coerce')
df['terminado'] = df['terminado'].astype(str).str.strip().str.lower()
df['entregado'] = df['entregado'].astype(str).str.strip().str.lower()
df['mensaje_enviado'] = df['mensaje_enviado'].astype(str).str.lower()
df['tostion'] = df['tostion'].astype(str).str.strip().replace(['nan', ''], 'no especificada')
df['molienda'] = df['molienda'].astype(str).str.strip().replace(['nan', ''], 'no especificada')

# Filtrar pedidos listos (usando ID como clave principal)
para_enviar = df[
    (df['terminado'] == 'si') &
    (df['entregado'] != 'si') &
    (df['mensaje_enviado'] != 'si') &
    (df['teléfono'].str.strip() != '') &
    (df['teléfono'] != 'nan') &
    (df['total'].notna()) &
    (df['total'] > 0)
].copy()

if para_enviar.empty:
    print("✅ No hay pedidos nuevos para notificar.")
else:
    print(f"📨 Se encontraron {len(para_enviar)} pedidos nuevos listos para notificar.\n")
    
    enviados_hoy = set()  # Evita enviar más de 1 mensaje por número en la misma ejecución

    for idx, row in para_enviar.iterrows():
        telefono = "+57" + str(row['teléfono']).strip()
        
        # Evitar spam al mismo número en una sola ejecución
        if telefono in enviados_hoy:
            print(f"⏭️ Saltado (ya notificado en esta ejecución): {row['nombre']} - ID {row['ID']}")
            continue

        try:
            mensaje = crear_mensaje(
                row['nombre'],
                row['kilo'],
                row['tostion'],
                row['molienda'],
                int(row['total']),
                int(row['ID'])          # ←←← Usamos el ID aquí
            )
            
            print(f"➤ Enviando Pedido ID {row['ID']} a {row['nombre']} ({telefono}) ... ", end="")
            
            kit.sendwhatmsg_instantly(
                telefono, 
                mensaje, 
                wait_time=12,
                tab_close=True,
                close_time=3
            )
            
            # Marcar como enviado usando el índice (por ID)
            df.at[idx, 'mensaje_enviado'] = 'si'
            enviados_hoy.add(telefono)
            
            print("✅ ENVIADO")
            time.sleep(4)
            
        except Exception as e:
            print(f"❌ Error con ID {row['ID']}: {e}")

    # Guardar cambios en el CSV
    df.to_csv(ruta_csv, index=False)
    print(f"\n💾 CSV actualizado - {len(para_enviar)} pedidos marcados como notificados.")

print("\n🎉 Proceso completado.")