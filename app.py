import calendar
import datetime
from zoneinfo import ZoneInfo
import pandas as pd
import plotly.express as px
import streamlit as st
from supabase import create_client

st.set_page_config(page_title="Control de Créditos y Ventas", page_icon="📊", layout="wide")

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
        st.error(f"Error al cargar {nombre_tabla}: {e}")
        return []

def insertar_fila(nombre_tabla, datos):
    try:
        supabase.table(nombre_tabla).insert(datos).execute()
        return True
    except Exception as e:
        st.error(f"Error al insertar en {nombre_tabla}: {e}")
        return False

def actualizar_fila(nombre_tabla, columna_id, valor_id, datos):
    try:
        supabase.table(nombre_tabla).update(datos).eq(columna_id, valor_id).execute()
        return True
    except Exception as e:
        st.error(f"Error al actualizar en {nombre_tabla}: {e}")
        return False

def eliminar_fila(nombre_tabla, columna_id, valor_id):
    try:
        supabase.table(nombre_tabla).delete().eq(columna_id, valor_id).execute()
    except Exception as e:
        st.error(f"Error al eliminar en {nombre_tabla}: {e}")

# --- LISTAS INICIALES Y CARGA ---
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

def cargar_datos():
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

    creditos = obtener_tabla("creditos")
    
    meta_data = obtener_tabla("meta")
    meta_val = int(meta_data[0]["meta"]) if meta_data and str(meta_data[0]["meta"]).isdigit() else 200

    return tiendas, responsables, marcas, creditos, meta_val

def guardar_meta_db(nueva_meta):
    try:
        supabase.table("meta").delete().neq("meta", -1).execute()
        supabase.table("meta").insert({"meta": nueva_meta}).execute()
    except Exception as e:
        st.error(f"Error al actualizar la meta: {e}")

tiendas_list, responsables_list, marcas_list, creditos_list, META = cargar_datos()

# --- GESTIÓN DE SESIÓN ---
if "auth_general" not in st.session_state:
    st.session_state.auth_general = False
if "auth_admin" not in st.session_state:
    st.session_state.auth_admin = False

# --- MENÚ LATERAL ---
st.title("📱 Sistema de Control y Créditos")
st.markdown("---")

menu = st.sidebar.selectbox(
    "Menú Principal",
    [
        "Dashboard",
        "Registrar Crédito / Venta",
        "Mis Ventas (Promotor)",
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
            df_c = pd.DataFrame(creditos_db)
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
            
            top_marca = df_mes["marca_equipo"].mode()[0] if not df_mes.empty and "marca_equipo" in df_mes.columns else "N/A"
            top_tienda = df_mes["tienda"].mode()[0] if not df_mes.empty and "tienda" in df_mes.columns else "N/A"

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

            st.markdown("---")

            if not df_mes.empty:
                g1, g2 = st.columns(2)
                with g1:
                    st.subheader("Créditos por Tienda")
                    df_t_chart = df_mes.groupby("tienda").size().reset_index(name="cantidad")
                    st.plotly_chart(px.bar(df_t_chart, x="tienda", y="cantidad", color="tienda"), use_container_width=True)
                
                with g2:
                    st.subheader("Créditos por Marca de Celular")
                    df_m_chart = df_mes.groupby("marca_equipo").size().reset_index(name="cantidad")
                    st.plotly_chart(px.pie(df_m_chart, names="marca_equipo", values="cantidad", hole=0.4), use_container_width=True)
        else:
            st.info("No hay créditos registrados en el mes actual para mostrar el dashboard.")

# --- 2. REGISTRAR CRÉDITO / VENTA (PROTEGIDO CON PAYJOY2026) ---
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
                
            imei_equipo = st.text_input("IMEI del Equipo").strip()
            tag_credito = st.text_input("Tag del Crédito").strip()
            
            enviado = st.form_submit_button("Guardar Crédito", type="primary")
            
            if enviado:
                if not documento_cliente or not documento_promotor or not imei_equipo or not tag_credito:
                    st.warning("Por favor complete los campos obligatorios (Documentos, IMEI y Tag).")
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
                        "imei": imei_equipo,
                        "tag": tag_credito
                    }
                    
                    if insertar_fila("creditos", nuevo_registro):
                        st.success("¡Crédito registrado con éxito! Los campos han sido limpiados.")
                        st.rerun()

# --- 3. MIS VENTAS (PROMOTOR) - SIN CONTRASEÑA ---
elif menu == "Mis Ventas (Promotor)":
    st.header("🔍 Consultar Mis Ventas (Promotor)")
    st.write("Ingrese su número de documento para consultar los créditos registrados a su nombre.")
    
    doc_promotor_consulta = st.text_input("Número de Documento del Promotor").strip()
    
    if doc_promotor_consulta:
        creditos_act = obtener_tabla("creditos")
        if creditos_act:
            df_c = pd.DataFrame(creditos_act)
            df_prom = df_c[df_c["documento_promotor"].astype(str).str.strip() == doc_promotor_consulta]
            
            if not df_prom.empty:
                nombre_p = df_prom["nombre_promotor"].iloc[0]
                st.success(f"Promotor: **{nombre_p}** | Total Créditos Registrados: **{len(df_prom)}**")
                
                cols_most = ["fecha", "tienda", "responsable", "nombre_cliente", "marca_equipo", "imei", "tag"]
                st.dataframe(df_prom[cols_most], use_container_width=True)
            else:
                st.warning("No se encontraron créditos registrados con este número de documento.")
        else:
            st.info("No hay registros en la base de datos.")

# --- 4. ADMINISTRACIÓN ---
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
            
        tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
            "Responsables", 
            "Tiendas", 
            "Marcas", 
            "Meta Mensual", 
            "Modificar / Eliminar Créditos", 
            "Informe y Filtros"
        ])
        
        with tab1:
            st.subheader("Gestionar Responsables")
            nuevo_resp = st.text_input("Nombre del Nuevo Responsable").strip().title()
            if st.button("Agregar Responsable"):
                if nuevo_resp and nuevo_resp not in responsables_list:
                    insertar_fila("responsables", {"nombre": nuevo_resp})
                    st.success("Responsable agregado.")
                    st.rerun()
                else:
                    st.warning("Nombre inválido o ya existente.")
            
            if responsables_list:
                resp_borrar = st.selectbox("Seleccionar Responsable a Eliminar", responsables_list)
                if st.button("Eliminar Responsable", type="primary"):
                    eliminar_fila("responsables", "nombre", resp_borrar)
                    st.success("Responsable eliminado.")
                    st.rerun()

        with tab2:
            st.subheader("Gestionar Tiendas")
            nueva_tienda = st.text_input("Nombre de la Nueva Tienda").strip().upper()
            if st.button("Agregar Tienda"):
                if nueva_tienda and nueva_tienda not in tiendas_list:
                    insertar_fila("tiendas", {"tienda": nueva_tienda})
                    st.success("Tienda agregada.")
                    st.rerun()
                else:
                    st.warning("Tienda inválida o ya existente.")
            
            if tiendas_list:
                tienda_borrar = st.selectbox("Seleccionar Tienda a Eliminar", tiendas_list)
                if st.button("Eliminar Tienda", type="primary"):
                    eliminar_fila("tiendas", "tienda", tienda_borrar)
                    st.success("Tienda eliminada.")
                    st.rerun()

        with tab3:
            st.subheader("Gestionar Marcas de Celulares")
            nueva_marca = st.text_input("Nombre de la Nueva Marca").strip().capitalize()
            if st.button("Agregar Marca"):
                if nueva_marca and nueva_marca not in marcas_list:
                    insertar_fila("marcas", {"marca": nueva_marca})
                    st.success("Marca agregada.")
                    st.rerun()
                else:
                    st.warning("Marca inválida o ya existente.")
            
            if marcas_list:
                marca_borrar = st.selectbox("Seleccionar Marca a Eliminar", marcas_list)
                if st.button("Eliminar Marca", type="primary"):
                    eliminar_fila("marcas", "marca", marca_borrar)
                    st.success("Marca eliminada.")
                    st.rerun()

        with tab4:
            st.subheader("Ajustar Meta Mensual")
            st.write(f"Meta actual: **{META}** créditos")
            nueva_meta = st.number_input("Nueva Meta del Mes", min_value=1, step=1, value=int(META))
            if st.button("Actualizar Meta"):
                guardar_meta_db(nueva_meta)
                st.success("Meta actualizada con éxito.")
                st.rerun()

        with tab5:
            st.subheader("Modificar o Eliminar Créditos Registrados")
            creditos_act = obtener_tabla("creditos")
            if creditos_act:
                df_cred = pd.DataFrame(creditos_act)
                st.dataframe(df_cred[["id_credito", "fecha", "responsable", "nombre_promotor", "imei", "tag"]], use_container_width=True)
                
                ops_c = [f"ID: {c.get('id_credito')} | Promotor: {c.get('nombre_promotor')} | IMEI: {c.get('imei')}" for c in creditos_act]
                sel_c = st.selectbox("Seleccionar Registro de Crédito", ops_c)
                
                if sel_c:
                    id_sel = sel_c.split("ID: ")[1].split(" |")[0]
                    credito_obj = next((c for c in creditos_act if str(c.get("id_credito")) == id_sel), None)
                    
                    if credito_obj:
                        nuevo_cliente = st.text_input("Nombre Cliente", value=credito_obj.get("nombre_cliente", ""))
                        nuevo_doc_cli = st.text_input("Documento Cliente", value=credito_obj.get("documento_cliente", ""))
                        nuevo_tel = st.text_input("Teléfono Cliente", value=credito_obj.get("telefono_cliente", ""))
                        nuevo_prom = st.text_input("Nombre Promotor", value=credito_obj.get("nombre_promotor", ""))
                        nuevo_doc_prom = st.text_input("Documento Promotor", value=credito_obj.get("documento_promotor", ""))
                        nuevo_imei = st.text_input("IMEI", value=credito_obj.get("imei", ""))
                        nuevo_tag = st.text_input("Tag", value=credito_obj.get("tag", ""))
                        
                        col_e1, col_e2 = st.columns(2)
                        if col_e1.button("Guardar Cambios"):
                            if actualizar_fila("creditos", "id_credito", id_sel, {
                                "nombre_cliente": nuevo_cliente,
                                "documento_cliente": nuevo_doc_cli,
                                "telefono_cliente": nuevo_tel,
                                "nombre_promotor": nuevo_prom,
                                "documento_promotor": nuevo_doc_prom,
                                "imei": nuevo_imei,
                                "tag
