import calendar
import datetime
from zoneinfo import ZoneInfo
import pandas as pd
import plotly.express as px
import streamlit as st
from supabase import create_client

st.set_page_config(page_title="Control de Créditos y Ventas", page_icon="📊", layout="wide")

# --- CONEXIÓN A SUPABASE ---
SUPABASE_URL = "https://rijwgapwfqjxvojxqbtx.supabase.co"
SUPABASE_KEY = "sb_publishable_HgFTwscjE-NfZ_RpfDl3fw_yhNypkDQ"

def init_supabase():
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase = init_supabase()

# --- FUNCIONES DE BASE DE DATOS ---
def obtener_tabla(nombre_tabla):
    try:
        response = supabase.table(nombre_tabla).select("*").execute()
        return response.data if response.data else []
    except Exception as e:
        st.error(f"⚠️ Error al cargar la tabla '{nombre_tabla}': {e}")
        return []

def insertar_fila(nombre_tabla, datos):
    try:
        supabase.table(nombre_tabla).insert(datos).execute()
        return True
    except Exception as e:
        st.error(f"❌ Error crítico al insertar en '{nombre_tabla}': {e}")
        return False

def actualizar_fila(nombre_tabla, columna_id, valor_id, datos):
    try:
        supabase.table(nombre_tabla).update(datos).eq(columna_id, str(valor_id)).execute()
        return True
    except Exception as e:
        st.error(f"❌ Error al actualizar en '{nombre_tabla}': {e}")
        return False

def eliminar_fila(nombre_tabla, columna_id, valor_id):
    try:
        supabase.table(nombre_tabla).delete().eq(columna_id, str(valor_id)).execute()
        return True
    except Exception as e:
        st.error(f"❌ Error al eliminar en '{nombre_tabla}': {e}")
        return False

# --- LISTAS INICIALES ---
TIENDAS_INICIALES = [
    "EXITO OCCIDENTE", "EXITO LA HERRADURA TULUA", "281 EXITO FLORESTA", "4052 EXITO NUESTRO BOGOTA",
    "EXITO WOW UNICENTRO", "EXITO CHIPICHAPE", "369 EXITO SAN DIEGO CARTAGENA", "EXITO CAÑAVERAL",
    "EXITO BUGA", "39 ATENDIDO SAN ANTONIO", "384 EXITO LA CEJA", "135 EXITO YOPAL",
    "40 CATALOGO ITAGUI", "75 CATALOGO MAYORCA", "96 CATALOGO FUSAGASUGA", "81 EXITO WOW COUNTRY",
    "4065 EXITO SAN PEDRO DE LOS MILAGRO", "483 EXITO FONTANAR", "266 EXITO VALLEDUPAR CENTRO",
    "67 PJK EXITO BUENAVENTURA", "EXITO SABANETA", "4058 EXITO VALLE DE LILI.", "379 EXITO PITALITO",
    "303 EXITO UNICENTRO BOGOTA", "578 EXITO SOGAMOSO", "28 EXITO DEL ESTE", "53 PJK EXITO SIMON BOLIVAR",
    "302 PJK EXITO CIUDAD TUNAL", "84 EXITO AMERICAS", "63 EXITO PEREIRA", "173 EXITO ECOPLAZA MOSQUERA",
    "320 EXITO CANAVERAL FLORIDA B", "4056 EXITO SUPERCENTRO TULUA", "328 EXITO NEIVA CENTRO",
    "385 EXITO RIOHACHA", "180 EXITO BARRANCABERMEJA", "408 EXITO SAN DIEGO MEDELLIN", "175 EXITO FLORENCIA",
    "409 EXITO UNICENTRO MEDELLIN", "4054 EXITO LLANOGRANDE PALMIRA", "33 EXITO POBLADO",
    "355 EXITO DIVERPLAZA", "9990 EXITO MALL PLAZA NQS", "489 EXITO FONTANAR CHIA", "158 EXITO ZIPAQUIRA",
    "172 EXITO MAGANGUE", "51 EXITO SAN FERNANDO", "41 EXITO BARRANQUILLA", "283 EXITO NUEVO KENNEDY",
    "275 EXITO BELLO CENTRO", "370 EXITO CASTELLANA", "40 EXITO ITAGUI", "514 EXITO MOLINOS",
    "65 EXITO UNICENTRO ARMENIA", "352 EXITO ORIENTAL BUCARAMANGA CV", "363 EXITO BUENA VISTA SANTA MARTA",
    "64 EXITO TULUA", "157 EXITO SAN PEDRO NEIVA", "353 EXITO SANTIAGO CUCUTA CV", "156 EXITO IBAGUE",
    "357 EXITO ALAMEDAS DEL SINU MONTERIA", "4039 EXITO UNICENTRO GIRARDOT", "173 EXITO MOSQUERA",
    "35 EXITO ENVIGADO", "31 EXITO COLOMBIA", "54 EXITO LA FLORA", "4025 EXITO SOACHA",
    "159 EXITO VILLAVICENCIO", "71 EXITO BUCARAMANGA", "47 EXITO METROPOLITANO", "174 EXITO PEREIRA CUBA",
    "362 EXITO BUENA VISTA", "44 EXITO CARTAGENA", "94 EXITO CHAPINERO", "56 EXITO UNICALI",
    "258 EXITO SANTA MARTA CENTRO", "435 EXITO PANAMERICANA POPAYAN", "354 EXITO LAS FLORES VALLEDUPAR CV",
    "45 EXITO APARTADO", "0265 EXITO CAUCASIA", "63 PJK EXITO PEREIRA", "93 PJK EXITO SUBA",
    "51 PJK EXITO SAN FERNANDO", "376 PJK EXITO BOSA", "39 PJK EXITO SAN ANTONIO", "30 PJK EXITO BELLO",
    "83 PJK EXITO VILLA MAYOR"
]

RESPONSABLES_INICIALES = ["Héctor Pino", "Sebastián Pineda"]
MARCAS_INICIALES = ["Samsung", "Motorola", "Oppo", "Xiaomi", "Infinix", "Realme", "Tecno", "Honor", "Vivo", "Nubia"]

def cargar_listas():
    t_data = obtener_tabla("tiendas")
    tiendas = [t["tienda"] for t in t_data] if t_data else TIENDAS_INICIALES
    if not t_data:
        for t in tiendas:
            insertar_fila("tiendas", {"tienda": t})

    r_data = obtener_tabla("responsables")
    responsables = [r["nombre"] for r in r_data] if r_data else RESPONSABLES_INICIALES
    if not r_data:
        for r in responsables:
            insertar_fila("responsables", {"nombre": r})

    m_data = obtener_tabla("marcas")
    marcas = [m["marca"] for m in m_data] if m_data else MARCAS_INICIALES
    if not m_data:
        for m in marcas:
            insertar_fila("marcas", {"marca": m})

    meta_data = obtener_tabla("meta")
    meta_val = int(meta_data[0]["meta"]) if meta_data and str(meta_data[0]["meta"]).isdigit() else 200

    return tiendas, responsables, marcas, meta_val

tiendas_list, responsables_list, marcas_list, META = cargar_listas()

# --- SESIÓN ---
if "auth_general" not in st.session_state:
    st.session_state.auth_general = False
if "auth_admin" not in st.session_state:
    st.session_state.auth_admin = False
if "auth_auditoria" not in st.session_state:
    st.session_state.auth_auditoria = False

# --- MENÚ LATERAL ---
st.title("📱 Sistema de Control y Créditos")
st.markdown("---")

menu = st.sidebar.selectbox(
    "Menú Principal",
    [
        "Dashboard",
        "Registrar Crédito / Venta",
        "Mis Ventas (Promotor)",
        "Auditoría y Depuración (Admin)",
        "Administración"
    ]
)

# --- 1. DASHBOARD ---
if menu == "Dashboard":
    if not st.session_state.auth_general:
        st.header("🔒 Módulo Protegido")
        pass_input = st.text_input("Ingrese la contraseña general", type="password", key="pass_gen")
        if st.button("Acceder", key="btn_acc_gen"):
            if pass_input == "payjoy2026":
                st.session_state.auth_general = True
                st.rerun()
            else:
                st.error("Contraseña incorrecta.")
    else:
        st.header("📊 Dashboard General de Créditos")
        if st.sidebar.button("Cerrar Sesión General"):
            st.session_state.auth_general = False
            st.rerun()

        creditos_db = obtener_tabla("creditos")
        if creditos_db:
            df_c = pd.DataFrame(creditos_db).fillna("")
            df_c["_dt"] = pd.to_datetime(df_c["fecha"], errors="coerce")
            
            ahora = datetime.datetime.now(ZoneInfo("America/Bogota"))
            dias_en_mes = calendar.monthrange(ahora.year, ahora.month)[1]
            
            df_mes = df_c[(df_c["_dt"].dt.month == ahora.month) & (df_c["_dt"].dt.year == ahora.year)]
            total_mes = len(df_mes) if not df_mes.empty else 0
            
            pct_cumplimiento = min(round((total_mes / META) * 100, 2), 100.0) if META > 0 else 0.0
            promedio_diario = (total_mes / ahora.day) if ahora.day > 0 else 0
            proyeccion_unidades = int(promedio_diario * dias_en_mes)
            proyeccion_pct = round((proyeccion_unidades / META) * 100, 2) if META > 0 else 0.0
            faltantes = max(META - total_mes, 0)
            
            top_marca = df_mes["marca_equipo"].mode()[0] if not df_mes.empty and "marca_equipo" in df_mes.columns and not df_mes["marca_equipo"].mode().empty else "N/A"
            top_tienda = df_mes["tienda"].mode()[0] if not df_mes.empty and "tienda" in df_mes.columns and not df_mes["tienda"].mode().empty else "N/A"

            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Meta del Mes", str(META))
            m2.metric("Créditos a la Fecha", str(total_mes))
            m3.metric("Faltantes para Meta", str(faltantes))
            m4.metric("% Cumplimiento", f"{pct_cumplimiento}%")

            st.progress(min(total_mes / META, 1.0) if META > 0 else 1.0)
            
            m5, m6, m7, m8 = st.columns(4)
            m5.metric("Proyección Unidades", str(proyeccion_unidades))
            m6.metric("Proyección %", f"{proyeccion_pct}%")
            m7.metric("Marca Líder", top_marca)
            m8.metric("Tienda Líder", top_tienda)
        else:
            st.info("No hay créditos registrados en el mes actual.")

# --- 2. REGISTRAR CRÉDITO ---
elif menu == "Registrar Crédito / Venta":
    mantener_sesion = st.sidebar.checkbox("Mantener sesión abierta para registrar", value=True)
    permitir_registro = st.session_state.auth_general or mantener_sesion
    
    if not permitir_registro:
        st.header("🔒 Módulo Protegido - Registrar Venta")
        pass_input_reg = st.text_input("Ingrese la contraseña general", type="password", key="pass_reg")
        if st.button("Acceder", key="btn_acc_reg"):
            if pass_input_reg == "payjoy2026":
                st.session_state.auth_general = True
                st.rerun()
            else:
                st.error("Contraseña incorrecta.")
    else:
        st.header("📝 Registrar Nuevo Crédito")
        with st.form("f_registro_credito", clear_on_submit=True):
            responsable = st.selectbox("Responsable", responsables_list)
            tienda = st.selectbox("Tienda", tiendas_list)
            
            col1, col2 = st.columns(2)
            with col1:
                nombre_cliente = st.text_input("Nombre del Cliente").strip()
                documento_cliente = st.text_input("Documento del Cliente").strip()
                telefono_cliente = st.text_input("Teléfono del Cliente").strip()
            with col2:
                nombre_promotor = st.text_input("Nombre del Promotor").strip().title()
                documento_promotor = st.text_input("Documento del Promotor").strip()
                marca_equipo = st.selectbox("Marca del Equipo", marcas_list)
                modelo_equipo = st.text_input("Modelo del Equipo").strip()
                
            imei_equipo = st.text_input("IMEI del Equipo").strip()
            tag_credito = st.text_input("Tag del Crédito").strip()
            
            enviado = st.form_submit_button("Guardar Crédito", type="primary")
            
            if enviado:
                if not documento_cliente or not documento_promotor or not imei_equipo or not tag_credito or not modelo_equipo:
                    st.warning("Por favor complete los campos obligatorios.")
                else:
                    id_credito = datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")
                    fecha_actual = str(datetime.datetime.now(ZoneInfo("America/Bogota")).date())
                    
                    nuevo_registro = {
                        "id_credito": id_credito,
                        "fecha": fecha_actual,
                        "responsable": responsable,
                        "tienda": tienda,
                        "nombre_cliente": nombre_cliente,
                        "documento_cliente": documento_cliente,
                        "telefono_cliente": telefono_cliente,
                        "nombre_promotor": nombre_promotor,
                        "documento_promotor": documento_promotor,
                        "marca_equipo": marca_equipo,
                        "modelo_equipo": modelo_equipo,
                        "imei": imei_equipo,
                        "tag": tag_credito
                    }
                    
                    if insertar_fila("creditos", nuevo_registro):
                        st.success("¡Crédito registrado con éxito y guardado en Supabase!")
                        st.rerun()

# --- 3. MIS VENTAS (PROMOTOR) ---
elif menu == "Mis Ventas (Promotor)":
    st.header("🔍 Consultar Mis Ventas (Promotor)")
    doc_promotor_consulta = st.text_input("Número de Documento del Promotor").strip()
    
    if doc_promotor_consulta:
        creditos_act = obtener_tabla("creditos")
        if creditos_act:
            df_c = pd.DataFrame(creditos_act).fillna("")
            df_prom = df_c[df_c["documento_promotor"].astype(str).str.strip() == doc_promotor_consulta]
            
            if not df_prom.empty:
                nombre_p = df_prom["nombre_promotor"].iloc[0]
                st.success(f"Promotor: **{nombre_p}** | Total Créditos: **{len(df_prom)}**")
                cols_most = ["fecha", "tienda", "responsable", "nombre_cliente", "marca_equipo", "modelo_equipo", "imei", "tag"]
                st.dataframe(df_prom[[c for c in cols_most if c in df_prom.columns]], use_container_width=True)
            else:
                st.warning("No se encontraron créditos registrados con este número.")
        else:
            st.info("No hay registros.")

# --- 4. MÓDULO PROTEGIDO: AUDITORÍA Y DEPURACIÓN ---
elif menu == "Auditoría y Depuración (Admin)":
    if not st.session_state.auth_auditoria:
        st.header("🔒 Módulo Protegido - Auditoría de Ventas")
        pass_auditoria = st.text_input("Ingrese la clave de acceso", type="password", key="pass_audit")
        if st.button("Acceder a Auditoría", key="btn_acc_audit"):
            if pass_auditoria == "payjoy2026":
                st.session_state.auth_auditoria = True
                st.rerun()
            else:
                st.error("Contraseña incorrecta.")
    else:
        st.header("📋 Auditoría de Ventas a la Fecha")
        if st.sidebar.button("Cerrar Sesión Auditoría"):
            st.session_state.auth_auditoria = False
            st.rerun()
            
        creditos_auditoria = obtener_tabla("creditos")
        st.write(f"Estado de conexión: Se leyeron **{len(creditos_auditoria)}** registros directamente desde Supabase.")
        
        if creditos_auditoria:
            df_audit = pd.DataFrame(creditos_auditoria).fillna("")
            st.dataframe(df_audit, use_container_width=True)
            
            st.markdown("---")
            st.subheader("🗑️ Eliminar Venta por ID")
            ops_audit = [str(c.get('id_credito')) for c in creditos_auditoria if c.get('id_credito')]
            
            if ops_audit:
                id_elim_audit = st.selectbox("Seleccione el ID del crédito que desea eliminar", ops_audit, key="sel_audit_del")
                if st.button("Eliminar esta Venta Definitivamente", type="primary"):
                    if eliminar_fila("creditos", "id_credito", id_elim_audit):
                        st.success("¡Venta eliminada correctamente!")
                        st.rerun()
        else:
            st.info("La tabla 'creditos' en Supabase está actualmente vacía.")

# --- 5. ADMINISTRACIÓN ---
elif menu == "Administración":
    if not st.session_state.auth_admin:
        st.header("🔒 Panel de Administración Protegido")
        pass_admin_input = st.text_input("Contraseña de Administrador", type="password", key="pass_admin")
        if st.button("Acceder como Admin", key="btn_admin"):
            if pass_admin_input == "hectorp2026":
                st.session_state.auth_admin = True
                st.rerun()
            else:
                st.error("Contraseña incorrecta.")
    else:
        st.header("⚙️ Panel de Administración General")
        if st.sidebar.button("Cerrar Sesión Admin"):
            st.session_state.auth_admin = False
            st.rerun()
            
        tab1, tab2, tab3, tab4 = st.tabs([
            "Gestión de Responsables", 
            "Gestión de Tiendas", 
            "Modificar o Eliminar Crédito", 
            "Informe General"
        ])
        
        with tab1:
            st.subheader("Gestión de Responsables")
            nuevo_resp = st.text_input("Nombre del Nuevo Responsable").strip().title()
            if st.button("Agregar Responsable"):
                if nuevo_resp and nuevo_resp not in responsables_list:
                    if insertar_fila("responsables", {"nombre": nuevo_resp}):
                        st.success("Responsable agregado.")
                        st.rerun()
            
            t_resp = obtener_tabla("responsables")
            lista_r = [r["nombre"] for r in t_resp] if t_resp else responsables_list
            if lista_r:
                resp_b = st.selectbox("Seleccionar Responsable a Eliminar", lista_r)
                if st.button("Eliminar Responsable", type="primary"):
                    if eliminar_fila("responsables", "nombre", resp_b):
                        st.success("Responsable eliminado.")
                        st.rerun()

        with tab2:
            st.subheader("Gestión de Tiendas")
            nueva_tienda = st.text_input("Nombre de la Nueva Tienda").strip().upper()
            if st.button("Agregar Tienda"):
                if nueva_tienda and nueva_tienda not in tiendas_list:
                    if insertar_fila("tiendas", {"tienda": nueva_tienda}):
                        st.success("Tienda agregada.")
                        st.rerun()
            
            t_tiendas = obtener_tabla("tiendas")
            lista_t = [t["tienda"] for t in t_tiendas] if t_tiendas else tiendas_list
            if lista_t:
                tienda_b = st.selectbox("Seleccionar Tienda a Eliminar", lista_t)
                if st.button("Eliminar Tienda", type="primary"):
                    if eliminar_fila("tiendas", "tienda", tienda_b):
                        st.success("Tienda eliminada.")
                        st.rerun()

        with tab3:
            st.subheader("Modificar o Eliminar Crédito")
            creditos_act = obtener_tabla("creditos")
            
            if creditos_act:
                df_cred = pd.DataFrame(creditos_act).fillna("")
                st.dataframe(df_cred, use_container_width=True)
                
                ops_c = [str(c.get('id_credito')) for c in creditos_act if c.get('id_credito')]
                if ops_c:
                    id_sel = st.selectbox("Seleccionar ID del Crédito a Gestionar", ops_c)
                    if id_sel:
                        credito_obj = None
                        for c in creditos_act:
                            if str(c.get("id_credito")) == str(id_sel):
                                credito_obj = c
                                break
                                
                        if credito_obj:
                            st.markdown("---")
                            col_m1, col_m2 = st.columns(2)
                            with col_m1:
                                st.markdown("### ✏️ Modificar")
                                n_cli = st.text_input("Nombre Cliente", value=str(credito_obj.get("nombre_cliente", "")))
                                d_cli = st.text_input("Documento Cliente", value=str(credito_obj.get("documento_cliente", "")))
                                t_cli = st.text_input("Teléfono Cliente", value=str(credito_obj.get("telefono_cliente", "")))
                                n_prom = st.text_input("Nombre Promotor", value=str(credito_obj.get("nombre_promotor", "")))
                                d_prom = st.text_input("Documento Promotor", value=str(credito_obj.get("documento_promotor", "")))
                                n_mod = st.text_input("Modelo Equipo", value=str(credito_obj.get("modelo_equipo", "")))
                                n_imei = st.text_input("IMEI", value=str(credito_obj.get("imei", "")))
                                n_tag = st.text_input("Tag", value=str(credito_obj.get("tag", "")))
                                
                                if st.button("Guardar Cambios"):
                                    datos_act = {
                                        "nombre_cliente": n_cli,
                                        "documento_cliente": d_cli,
                                        "telefono_cliente": t_cli,
                                        "nombre_promotor": n_prom,
                                        "documento_promotor": d_prom,
      
