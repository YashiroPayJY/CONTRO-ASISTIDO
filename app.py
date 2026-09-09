import calendar
import datetime
from zoneinfo import ZoneInfo
import pandas as pd
import plotly.express as px
import streamlit as st
from supabase import create_client

st.set_page_config(page_title="Control de Ventas - Supabase", page_icon="📱", layout="wide")
ADMIN_PASS = "admin123"

# --- CONEXIÓN DIRECTA A SUPABASE ---
SUPABASE_URL = "https://rijwgapwfqjxvojxqbtx.supabase.co"
SUPABASE_KEY = "sb_publishable_HgFTwscjE-NfZ_RpfDl3fw_yhNypkDQ"

@st.cache_resource
def init_supabase():
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase = init_supabase()

# --- FUNCIONES DE BASE DE DATOS ---
def obtener_tabla(nombre_tabla):
    try:
        response = supabase.table(nombre_tabla).select("*").execute()
        return response.data if response.data else []
    except Exception as e:
        return []

def insertar_fila(nombre_tabla, datos):
    try:
        supabase.table(nombre_tabla).insert(datos).execute()
    except Exception as e:
        st.error(f"Error al insertar en {nombre_tabla}: {e}")

def eliminar_fila(nombre_tabla, columna_id, valor_id):
    try:
        supabase.table(nombre_tabla).delete().eq(columna_id, valor_id).execute()
    except Exception as e:
        st.error(f"Error al eliminar en {nombre_tabla}: {e}")

# --- CARGAR DATOS CON RESPALDO SEGURO ---
def cargar_datos():
    asesores_list = obtener_tabla("asesores")
    
    tiendas_default = ["Éxito Calle 80", "Falabella Centro", "Alkosto 170"]
    tiendas_data = obtener_tabla("tiendas")
    tiendas_list = [t["tienda"] for t in tiendas_data] if tiendas_data else tiendas_default
    
    ventas_list = obtener_tabla("ventas")
    
    marcas_default = ["Samsung", "Motorola", "Oppo", "Infinix", "Vivo", "Xiaomi", "Honor", "Tecno", "Realme"]
    marcas_data = obtener_tabla("marcas")
    marcas_list = [m["marca"] for m in marcas_data] if marcas_data else marcas_default

    meta_data = obtener_tabla("meta")
    meta_val = int(meta_data[0]["meta"]) if meta_data and meta_data[0] and str(meta_data[0].get("meta", "")).isdigit() else 200

    return asesores_list, tiendas_list, ventas_list, marcas_list, meta_val

def guardar_meta_db(nueva_meta):
    try:
        supabase.table("meta").delete().neq("meta", -1).execute()
        supabase.table("meta").insert({"meta": nueva_meta}).execute()
    except Exception as e:
        st.error(f"Error al actualizar la meta: {e}")

asesores, tiendas, ventas, MARCAS, META = cargar_datos()

# --- MENÚ LATERAL ---
st.title("Sistema de Control de Ventas")
st.markdown("---")

menu = st.sidebar.selectbox(
    "Menú Principal",
    [
        "Registrar Venta",
        "Consultar Mis Ventas",
        "Registro de Asesor",
        "Dashboard",
        "Administración"
    ]
)

# --- 1. REGISTRAR VENTA ---
if menu == "Registrar Venta":
    st.header("Registrar Nueva Venta")
    
    if not asesores:
        st.warning("⚠️ No hay asesores registrados en el sistema. Por favor registre al menos un asesor en el menú 'Registro de Asesor' antes de continuar.")
    else:
        with st.form("f_registro_venta", clear_on_submit=True):
            st.subheader("👨‍💼 Asesor que Realiza la Venta")
            asesor_opciones = {f"{a['nombre']} (Cédula: {a['cedula']}) - Trabaja en: {a['marca_trabaja']}": a for a in asesores}
            asesor_sel_str = st.selectbox("Seleccione o busque el Asesor", list(asesor_opciones.keys()))
            asesor_seleccionado = asesor_opciones[asesor_sel_str]
            
            st.markdown("---")
            st.subheader("👤 Datos del Cliente")
            nombre_cliente = st.text_input("Nombre del Cliente").strip()
            contacto_cliente = st.text_input("Teléfono o Contacto del Cliente").strip()
            
            st.markdown("---")
            st.subheader("📱 Datos del Equipo y Venta")
            # Selector con buscador integrado para tiendas y marcas
            tienda_sel = st.selectbox("Seleccione o busque la Tienda", tiendas)
            marca_vendida = st.selectbox("Seleccione o busque la Marca Vendida", MARCAS)
            modelo_equipo = st.text_input("Modelo del Equipo (Ej: Galaxy A54, Redmi Note 12)").strip()
            fecha_v = st.date_input("Fecha de la Venta", value=datetime.datetime.now(ZoneInfo("America/Bogota")).date())
            cantidad_v = st.number_input("Cantidad de Unidades", min_value=1, step=1, value=1)
            
            if st.form_submit_button("Guardar Venta", type="primary"):
                if not nombre_cliente or not modelo_equipo:
                    st.warning("Por favor complete al menos el nombre del cliente y el modelo del equipo.")
                else:
                    id_venta = datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")
                    nueva_venta = {
                        "id_venta": id_venta,
                        "fecha": str(fecha_v),
                        "cedula": str(asesor_seleccionado["cedula"]),
                        "nombre_asesor": asesor_seleccionado["nombre"],
                        "marca_trabaja": asesor_seleccionado["marca_trabaja"],
                        "tienda": tienda_sel,
                        "marca_vendida": marca_vendida,
                        "modelo_equipo": modelo_equipo,
                        "nombre_cliente": nombre_cliente,
                        "contacto_cliente": contacto_cliente,
                        "cantidad": int(cantidad_v)
                    }
                    insertar_fila("ventas", nueva_venta)
                    st.success("¡Venta registrada con éxito de forma permanente!")
                    st.rerun()

# --- 2. CONSULTAR MIS VENTAS ---
elif menu == "Consultar Mis Ventas":
    st.header("Consultar Mis Ventas del Mes")
    
    ced_consulta = st.text_input("Ingrese su Documento (Cédula) de Asesor").strip()
    
    if ced_consulta:
        as_info = next((a for a in asesores if str(a.get("cedula")).strip() == ced_consulta), None)
        if as_info:
            st.info(f"Asesor: **{as_info['nombre']}**")
            
            ventas_actualizadas = obtener_tabla("ventas")
            if ventas_actualizadas:
                df_v = pd.DataFrame(ventas_actualizadas)
                df_v["_dt"] = pd.to_datetime(df_v["fecha"], errors="coerce")
                
                df_as_ventas = df_v[df_v["cedula"].astype(str).str.strip() == ced_consulta]
                
                if not df_as_ventas.empty:
                    ahora = datetime.datetime.now(ZoneInfo("America/Bogota"))
                    mes_sel = st.selectbox(
                        "Seleccionar Mes", 
                        range(1, 13), 
                        index=ahora.month - 1, 
                        format_func=lambda x: calendar.month_name[x]
                    )
                    
                    df_mes = df_as_ventas[df_as_ventas["_dt"].dt.month == mes_sel]
                    
                    total_mes = int(df_mes["cantidad"].sum()) if not df_mes.empty else 0
                    st.metric("Total Unidades Vendidas en el Mes", str(total_mes))
                    
                    cols_mostrar = [c for c in ["fecha", "tienda", "marca_vendida", "modelo_equipo", "nombre_cliente", "cantidad"] if c in df_mes.columns]
                    st.dataframe(df_mes[cols_mostrar], use_container_width=True)
                else:
                    st.warning("No tiene ventas registradas.")
            else:
                st.warning("No hay registro de ventas en el sistema.")
        else:
            st.error("Cédula no encontrada en el sistema.")

# --- 3. REGISTRO DE ASESOR ---
elif menu == "Registro de Asesor":
    st.header("Auto-Registro de Asesores")
    
    with st.form("f_reg_asesor", clear_on_submit=True):
        cedula_nueva = st.text_input("Número de Documento (Cédula)").strip()
        nombre_nuevo = st.text_input("Nombre Completo").strip().title()
        marca_trabaja = st.selectbox("Seleccione o busque la Marca para la que Trabaja", MARCAS)
        
        if st.form_submit_button("Registrarme", type="primary"):
            if not cedula_nueva or not nombre_nuevo:
                st.warning("Debe completar todos los campos.")
            elif any(str(a.get("cedula")).strip() == cedula_nueva for a in asesores):
                st.error("Esta cédula ya se encuentra registrada.")
            else:
                nuevo_asesor = {
                    "cedula": str(cedula_nueva),
                    "nombre": nombre_nuevo,
                    "marca_trabaja": marca_trabaja
                }
                insertar_fila("asesores", nuevo_asesor)
                st.success("Registro guardado permanentemente. Ya puede registrar sus ventas.")
                st.rerun()

# --- 4. DASHBOARD ---
elif menu == "Dashboard":
    st.header("Dashboard General de Ventas")
    
    ventas_db = obtener_tabla("ventas")
    if ventas_db:
        df_v = pd.DataFrame(ventas_db)
        df_v["_dt"] = pd.to_datetime(df_v["fecha"], errors="coerce")
        df_v["cantidad"] = df_v["cantidad"].astype(int)
        
        ahora = datetime.datetime.now(ZoneInfo("America/Bogota"))
        dias_en_mes = calendar.monthrange(ahora.year, ahora.month)[1]
        
        df_mes = df_v[(df_v["_dt"].dt.month == ahora.month) & (df_v["_dt"].dt.year == ahora.year)]
        ventas_mes = int(df_mes["cantidad"].sum()) if not df_mes.empty else 0
        
        pct_cumplimiento = min(round((ventas_mes / META) * 100, 2), 100.0) if META > 0 else 0.0
        promedio_diario = (ventas_mes / ahora.day) if ahora.day > 0 else 0
        proyeccion_unidades = int(promedio_diario * dias_en_mes)
        proyeccion_pct = round((proyeccion_unidades / META) * 100, 2) if META > 0 else 0.0
        unidades_faltantes = max(META - ventas_mes, 0)
        
        top_tienda = df_mes.groupby("tienda")["cantidad"].sum().idxmax() if not df_mes.empty else "N/A"

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Meta del Mes", str(META))
        m2.metric("Ventas a la Fecha", str(ventas_mes))
        m3.metric("Faltante para Meta", str(unidades_faltantes))
        m4.metric("% Cumplimiento", f"{pct_cumplimiento}%")

        st.progress(min(ventas_mes / META, 1.0) if META > 0 else 1.0)
        
        m5, m6, m7 = st.columns(3)
        m5.metric("Proyección Unidades", str(proyeccion_unidades))
        m6.metric("Proyección Cumplimiento", f"{proyeccion_pct}%")
        m7.metric("Tienda Líder", top_tienda)

        st.markdown("---")

        if not df_mes.empty:
            g1, g2 = st.columns(2)
            with g1:
                st.subheader("Ventas por Tienda")
                df_t_chart = df_mes.groupby("tienda")["cantidad"].sum().reset_index()
                st.plotly_chart(px.bar(df_t_chart, x="tienda", y="cantidad", color="tienda"), use_container_width=True)
            
            with g2:
                st.subheader("Ventas por Marca Vendida")
                df_m_chart = df_mes.groupby("marca_vendida")["cantidad"].sum().reset_index()
                st.plotly_chart(px.pie(df_m_chart, names="marca_vendida", values="cantidad", hole=0.4), use_container_width=True)
            
            st.subheader("Desempeño por Asesor")
            df_as_chart = df_mes.groupby(["cedula", "nombre_asesor", "marca_trabaja"])["cantidad"].sum().reset_index()
            st.dataframe(df_as_chart, use_container_width=True)
    else:
        st.info("No hay ventas registradas para generar el dashboard.")

# --- 5. ADMINISTRACIÓN ---
elif menu == "Administración":
    st.header("Panel de Administración")
    
    pass_admin = st.text_input("Contraseña de Administrador", type="password")
    
    if pass_admin == ADMIN_PASS:
        st.success("Acceso autorizado.")
        tab1, tab2, tab3, tab4 = st.tabs(["Tiendas", "Asesores", "Eliminar Venta", "Meta Mensual"])
        
        with tab1:
            st.subheader("Crear Tienda")
            nueva_tienda = st.text_input("Nombre de la Nueva Tienda").strip().title()
            if st.button("Agregar Tienda"):
                if not nueva_tienda:
                    st.warning("Ingrese un nombre.")
                elif nueva_tienda in tiendas:
                    st.warning("La tienda ya existe.")
                else:
                    insertar_fila("tiendas", {"tienda": nueva_tienda})
                    st.success("Tienda creada exitosamente.")
                    st.rerun()

            st.markdown("---")
            st.subheader("Eliminar Tienda")
            if tiendas:
                tienda_borrar = st.selectbox("Seleccione o busque la Tienda a Eliminar", tiendas)
                if st.button("Eliminar Tienda", type="primary"):
                    eliminar_fila("tiendas", "tienda", tienda_borrar)
                    st.success("Tienda eliminada.")
                    st.rerun()

        with tab2:
            st.subheader("Asesores Registrados")
            asesores_act = obtener_tabla("asesores")
            if asesores_act:
                st.dataframe(pd.DataFrame(asesores_act), use_container_width=True)
                
                as_borrar_ced = st.selectbox(
                    "Seleccione o busque Asesor a Eliminar", 
                    [str(a["cedula"]) + " - " + str(a["nombre"]) for a in asesores_act]
                )
                if st.button("Eliminar Asesor", type="primary"):
                    ced_target = as_borrar_ced.split(" - ")[0]
                    eliminar_fila("asesores", "cedula", ced_target)
                    st.success("Asesor eliminado de la base de datos.")
                    st.rerun()
            else:
                st.info("Sin asesores registrados.")

        with tab3:
            st.subheader("Eliminar Venta Incorrecta")
            ventas_act = obtener_tabla("ventas")
            if ventas_act:
                df_v_del = pd.DataFrame(ventas_act)
                st.dataframe(df_v_del, use_container_width=True)
                
                ops_ventas = [
                    f"ID: {v.get('id_venta')} | Asesor: {v.get('nombre_asesor')} | Cliente: {v.get('nombre_cliente')} | Equipo: {v.get('modelo_equipo')}" 
                    for v in ventas_act
                ]
                venta_sel = st.selectbox("Seleccione o busque Registro a Eliminar", ops_ventas)
                
                if st.button("Eliminar Venta Seleccionada", type="primary"):
                    id_target = venta_sel.split("ID: ")[1].split(" |")[0]
                    eliminar_fila("ventas", "id_venta", id_target)
                    st.success("Registro de venta eliminado permanentemente.")
                    st.rerun()
            else:
                st.info("No hay ventas registradas para eliminar.")

        with tab4:
            st.subheader("Ajuste Manual de Meta")
            st.write(f"Meta actual: **{META}** unidades")
            nueva_meta = st.number_input("Nueva Meta Mensual", min_value=1, step=1, value=int(META))
            if st.button("Actualizar Meta"):
                guardar_meta_db(nueva_meta)
                st.success("Meta actualizada permanentemente.")
                st.rerun()

    elif pass_admin:
        st.error("Contraseña incorrecta.")
                    
