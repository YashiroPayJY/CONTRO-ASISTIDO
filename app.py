import calendar
import datetime
from zoneinfo import ZoneInfo
import pandas as pd
import plotly.express as px
import streamlit as st
from supabase import create_client

st.set_page_config(page_title="Control de Créditos y Ventas", page_icon="📱", layout="wide")

ADMIN_PASS = "hectorpc90"
SYSTEM_PASS = "payjoy2026"

if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

SUPABASE_URL = "https://rijwgapwfqjxvojxqbtx.supabase.co"
SUPABASE_KEY = "sb_publishable_HgFTwscjE-NfZ_RpfDl3fw_yhNypkDQ"

@st.cache_resource
def init_supabase():
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase = init_supabase()

def obtener_tabla(nombre_tabla):
    try:
        response = supabase.table(nombre_tabla).select("*").execute()
        return response.data if response.data else []
    except Exception as e:
        return []

def insertar_fila(nombre_tabla, datos):
    try:
        supabase.table(nombre_tabla).insert(datos).execute()
        return True
    except Exception as e:
        st.error(f"Error al insertar en {nombre_tabla}: {e}")
        return False

def eliminar_fila(nombre_tabla, columna_id, valor_id):
    try:
        supabase.table(nombre_tabla).delete().eq(columna_id, valor_id).execute()
    except Exception as e:
        st.error(f"Error al eliminar en {nombre_tabla}: {e}")

def actualizar_fila(nombre_tabla, columna_id, valor_id, datos_nuevos):
    try:
        supabase.table(nombre_tabla).update(datos_nuevos).eq(columna_id, valor_id).execute()
    except Exception as e:
        st.error(f"Error al actualizar en {nombre_tabla}: {e}")

def cargar_datos():
    responsables_default = [
        {"id": "1", "nombre": "Héctor Pino"},
        {"id": "2", "nombre": "Sebastián Pineda"}
    ]
    resp_data = obtener_tabla("responsables")
    responsables_list = resp_data if resp_data else responsables_default
    
    tiendas_default = [
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
        "409 EXITO UNICENTRO MEDELLIN", "4054 EXITO LLANOGRANDE PALMIRA", "33 EXITO POBLADO", "355 EXITO DIVERPLAZA",
        "9990 EXITO MALL PLAZA NQS", "489 EXITO FONTANAR CHIA", "158 EXITO ZIPAQUIRA", "172 EXITO MAGANGUE",
        "51 EXITO SAN FERNANDO", "41 EXITO BARRANQUILLA", "283 EXITO NUEVO KENNEDY", "275 EXITO BELLO CENTRO",
        "370 EXITO CASTELLANA", "40 EXITO ITAGUI", "514 EXITO MOLINOS", "65 EXITO UNICENTRO ARMENIA",
        "352 EXITO ORIENTAL BUCARAMANGA CV", "363 EXITO BUENA VISTA SANTA MARTA", "64 EXITO TULUA",
        "157 EXITO SAN PEDRO NEIVA", "353 EXITO SAN MATEO CUCUTA CV", "156 EXITO IBAGUE",
        "357 EXITO ALAMEDAS DEL SINU MONTERIA", "4039 EXITO UNICENTRO GIRARDOT", "173 EXITO MOSQUERA",
        "35 EXITO ENVIGADO", "31 EXITO COLOMBIA", "54 EXITO LA FLORA", "4025 EXITO SOACHA",
        "159 EXITO VILLAVICENCIO", "71 EXITO BUCARAMANGA", "47 EXITO METROPOLITANO", "174 EXITO PEREIRA CUBA",
        "362 EXITO BUENA VISTA", "44 EXITO CARTAGENA", "94 EXITO CHAPINERO", "56 EXITO UNICALI",
        "258 EXITO SANTA MARTA CENTRO", "435 EXITO PANAMERICANA POPAYAN", "354 EXITO LAS FLORES VALLEDUPAR CV",
        "45 EXITO APARTADO", "0265 EXITO CAUCASIA", "93 PJK EXITO SUBA", "376 PJK EXITO BOSA",
        "30 PJK EXITO BELLO", "83 PJK EXITO VILLA MAYOR"
    ]
    
    tiendas_data = obtener_tabla("tiendas")
    if tiendas_data:
        tiendas_list = [t["tienda"] for t in tiendas_data]
        for t in tiendas_default:
            if t not in tiendas_list:
                tiendas_list.append(t)
    else:
        tiendas_list = tiendas_default
        for t in tiendas_default:
            insertar_fila("tiendas", {"tienda": t})
    
    ventas_list = obtener_tabla("ventas")
    marcas_list = ["Samsung", "Motorola", "Oppo", "Xiaomi", "Infinix", "Realme", "Tecno", "Vivo", "Honor", "Nubia"]

    meta_data = obtener_tabla("meta")
    meta_val = int(meta_data[0]["meta"]) if meta_data and meta_data[0] and str(meta_data[0].get("meta", "")).isdigit() else 200

    return responsables_list, tiendas_list, ventas_list, marcas_list, meta_val

def guardar_meta_db(nueva_meta):
    try:
        supabase.table("meta").delete().neq("meta", -1).execute()
        supabase.table("meta").insert({"meta": nueva_meta}).execute()
    except Exception as e:
        st.error(f"Error al actualizar la meta: {e}")

responsables, tiendas, ventas, MARCAS, META = cargar_datos()

st.sidebar.title("📱 Navegación")
st.sidebar.markdown("---")

menu = st.sidebar.selectbox(
    "Seleccione el Módulo",
    [
        "Dashboard",
        "Registrar Venta / Crédito",
        "Mis Ventas (Promotor)",
        "Reportes",
        "Administración"
    ]
)

if menu != "Mis Ventas (Promotor)":
    if not st.session_state.autenticado:
        st.title("🔒 Acceso Restringido")
        st.info("Por favor, ingrese la contraseña del sistema para continuar.")
        
        ingreso_pass = st.text_input("Contraseña", type="password")
        if st.button("Ingresar", type="primary"):
            if ingreso_pass == SYSTEM_PASS:
                st.session_state.autenticado = True
                st.success("¡Acceso concedido!")
                st.rerun()
            else:
                st.error("Contraseña incorrecta.")
        st.stop()
    else:
        if st.sidebar.button("Cerrar Sesión General"):
            st.session_state.autenticado = False
            st.rerun()

if menu == "Dashboard":
    st.header("📊 Dashboard General de Ventas y Créditos")
    
    ventas_db = obtener_tabla("ventas")
    if ventas_db:
        df_v = pd.DataFrame(ventas_db)
        df_v["_dt"] = pd.to_datetime(df_v["fecha"], errors="coerce")
        df_v["cantidad"] = 1 
        
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
        top_marca = df_mes.groupby("marca")["cantidad"].sum().idxmax() if not df_mes.empty else "N/A"

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Meta del Mes", str(META))
        m2.metric("Ventas a la Fecha", str(ventas_mes))
        m3.metric("Faltante para Meta", str(unidades_faltantes))
        m4.metric("% Cumplimiento", f"{pct_cumplimiento}%")

        st.progress(min(ventas_mes / META, 1.0) if META > 0 else 1.0)
        
        m5, m6, m7, m8 = st.columns(4)
        m5.metric("Proyección Unidades", str(proyeccion_unidades))
        m6.metric("Proyección Cumplimiento", f"{proyeccion_pct}%")
        m7.metric("Tienda que más aporta", top_tienda)
        m8.metric("Marca más vendida", top_marca)

        st.markdown("---")

        if not df_mes.empty:
            g1, g2 = st.columns(2)
            with g1:
                st.subheader("Ventas por Tienda")
                df_t_chart = df_mes.groupby("tienda")["cantidad"].sum().reset_index()
                st.plotly_chart(px.bar(df_t_chart, x="tienda", y="cantidad", color="tienda"), use_container_width=True)
            
            with g2:
                st.subheader("Ventas por Marca de Celular")
                df_m_chart = df_mes.groupby("marca")["cantidad"].sum().reset_index()
                st.plotly_chart(px.pie(df_m_chart, names="marca", values="cantidad", hole=0.4), use_container_width=True)
    else:
        st.info("No hay créditos o ventas registradas para generar el dashboard este mes.")

elif menu == "Registrar Venta / Crédito":
    st.header("📝 Registrar Nuevo Crédito / Venta")
    
    if not responsables:
        st.warning("⚠️ No hay responsables registrados. Por favor ingrese al módulo de Administración para agregar uno.")
    else:
        with st.form("f_registro_credito", clear_on_submit=True):
            st.subheader("1. Gestión del Proceso")
            resp_opciones = {r["nombre"]: r for r in responsables}
            responsable_sel = st.selectbox("Responsable del Proceso de Crédito", list(resp_opciones.keys()))
            tienda_sel = st.selectbox("Seleccione o busque la Tienda (Éxito)", tiendas)
            
            st.markdown("---")
            st.subheader("2. Datos del Equipo")
            marca_sel = st.selectbox("Marca del Celular", MARCAS)
            modelo_dig = st.text_input("Modelo del Equipo (Ej: Galaxy A54, Redmi Note 12)").strip()
            email_telefono = st.text_input("Email (Correo del Teléfono)").strip()
            tag_dispositivo = st.text_input("Tag del Dispositivo / Crédito").strip()
            
            st.markdown("---")
            st.subheader("3. Datos del Cliente y Promotor")
            nombre_cliente = st.text_input("Nombre del Cliente").strip()
            cedula_cliente = st.text_input("Cédula del Cliente").strip()
            
            nombre_promotor = st.text_input("Nombre del Promotor").strip()
            documento_promotor = st.text_input("Documento (Cédula) del Promotor").strip()
            
            fecha_v = st.date_input("Fecha de la Venta", value=datetime.datetime.now(ZoneInfo("America/Bogota")).date())
            
            if st.form_submit_button("Guardar Crédito", type="primary"):
                if not modelo_dig or not nombre_cliente or not cedula_cliente or not documento_promotor or not email_telefono or not tag_dispositivo:
                    st.warning("Por favor complete todos los campos obligatorios.")
                else:
                    id_venta = datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")
                    nueva_venta = {
                        "id_venta": id_venta,
                        "responsable": responsable_sel,
                        "tienda": tienda_sel,
                        "marca": marca_sel,
                        "modelo": modelo_dig,
                        "email_telefono": email_telefono,
                        "tag_dispositivo": tag_dispositivo,
                        "nombre_cliente": nombre_cliente,
                        "cedula_cliente": cedula_cliente,
                        "nombre_promotor": nombre_promotor,
                        "documento_promotor": documento_promotor,
                        "fecha": str(fecha_v)
                    }
                    if insertar_fila("ventas", nueva_venta):
                        st.success("¡Crédito y venta registrados con éxito!")
                        st.rerun()

elif menu == "Mis Ventas (Promotor)":
    st.header("🔍 Consultar Mis Ventas (Promotor)")
    
    doc_promotor_busq = st.text_input("Ingrese su Número de Documento (Promotor)").strip()
    
    if doc_promotor_busq:
        ventas_db = obtener_tabla("ventas")
        if ventas_db:
            df_v = pd.DataFrame(ventas_db)
            df_as_ventas = df_v[df_v["documento_promotor"].astype(str).str.strip() == doc_promotor_busq]
            
            if not df_as_ventas.empty:
                nombre_encontrado = df_as_ventas.iloc[0].get("nombre_promotor", "Promotor")
                st.success(f"Promotor: **{nombre_encontrado}** | Total créditos: **{len(df_as_ventas)}**")
                
                df_as_ventas["_dt"] = pd.to_datetime(df_as_ventas["fecha"], errors="coerce")
                ahora = datetime.datetime.now(ZoneInfo("America/Bogota"))
                mes_sel = st.selectbox(
                    "Seleccionar Mes", 
                    range(1, 13), 
                    index=ahora.month - 1, 
                    format_func=lambda x: calendar.month_name[x]
                )
                
                df_mes_promotor = df_as_ventas[df_as_ventas["_dt"].dt.month == mes_sel]
                st.metric("Créditos en el mes seleccionado", len(df_mes_promotor))
                
                cols_mostrar = ["fecha", "tienda", "marca", "modelo", "email_telefono", "tag_dispositivo", "nombre_cliente", "responsable"]
                cols_finales = [c for c in cols_mostrar if c in df_mes_promotor.columns]
                st.dataframe(df_mes_promotor[cols_finales], use_container_width=True)
            else:
                st.warning("No se encontraron créditos registrados con este número de documento.")
        else:
            st.info("No hay registros en el sistema.")

elif menu == "Reportes":
    st.header("📈 Generación de Reportes de Ventas")
    
    ventas_db = obtener_tabla("ventas")
    if ventas_db:
        df_rep = pd.DataFrame(ventas_db)
        df_rep["_dt"] = pd.to_datetime(df_rep["fecha"], errors="coerce")
        
        st.subheader("Filtros de Búsqueda")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            resp_list_filtro = ["TODOS"] + list(df_rep["responsable"].dropna().unique())
            filtro_resp = st.selectbox("Filtrar por Responsable", resp_list_filtro)
        
        with col2:
            tienda_list_filtro = ["TODAS"] + list(df_rep["tienda"].dropna().unique())
            filtro_tienda = st.selectbox("Filtrar por Tienda", tienda_list_filtro)
            
        with col3:
            doc_prom_filtro = st.text_input("Filtrar por Documento de Promotor (Opcional)").strip()

        df_filtrado = df_rep.copy()
        if filtro_resp != "TODOS":
            df_filtrado = df_filtrado[df_filtrado["responsable"] == filtro_resp]
        if filtro_tienda != "TODAS":
            df_filtrado = df_filtrado[df_filtrado["tienda"] == filtro_tienda]
        if doc_prom_filtro:
            df_filtrado = df_filtrado[df_filtrado["documento_promotor"].astype(str).str.strip() == doc_prom_filtro]
            
        st.markdown(f"**Registros encontrados:** {len(df_filtrado)}")
        st.dataframe(df_filtrado, use_container_width=True)
        
        csv_data = df_filtrado.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Descargar Reporte en CSV",
            data=csv_data,
            file_name="reporte_creditos_ventas.csv",
            mime="text/csv"
        )
    else:
        st.info("No hay datos disponibles para generar reportes.")

elif menu == "Administración":
    st.header("🔐 Módulo de Administración General")
    
    pass_admin = st.text_input("Contraseña de Administrador", type="password")
    
    if pass_admin == ADMIN_PASS:
        st.success("Acceso de administrador autorizado.")
        tab1, tab2, tab3 = st.tabs(["Gestión de Responsables", "Modificar / Eliminar Ventas", "Meta Mensual"])
        
        with tab1:
            st.subheader("Agregar Nuevo Responsable")
            nuevo_resp = st.text_input("Nombre del Responsable").strip().title()
            if st.button("Guardar Responsable"):
                if not nuevo_resp:
                    st.warning("Ingrese un nombre.")
                else:
                    id_resp = datetime.datetime.now().strftime("%f")
                    insertar_fila("responsables", {"id": id_resp, "nombre": nuevo_resp})
                    st.success("Responsable agregado con éxito.")
                    st.rerun()
            
            st.markdown("---")
            st.subheader("Responsables Actuales")
            resp_act = obtener_tabla("responsables")
            if resp_act:
                df_r = pd.DataFrame(resp_act)
                st.dataframe(df_r, use_container_width=True)
                
                resp_borrar = st.selectbox("Seleccione Responsable a Eliminar", [r["nombre"] for r in resp_act])
                if st.button("Eliminar Responsable", type="primary"):
                    try:
                        supabase.table("responsables").delete().eq("nombre", resp_borrar).execute()
                        st.success("Responsable eliminado.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error al eliminar: {e}")
            else:
                st.info("No hay responsables registrados.")

        with tab2:
            st.subheader("Editar o Eliminar Créditos / Ventas Registradas")
            ventas_admin = obtener_tabla("ventas")
            if ventas_admin:
                df_va = pd.DataFrame(ventas_admin)
                st.dataframe(df_va, use_container_width=True)
                
                opciones_v = [
                    f"ID: {v.get('id_venta')} | Cliente: {v.get('nombre_cliente')} | Tag: {v.get('tag_dispositivo')} | Fecha: {v.get('fecha')}" 
                    for v in ventas_admin
                ]
                venta_sel_str = st.selectbox("Seleccione el registro a modificar o eliminar", opciones_v)
                id_seleccionado = venta_sel_str.split("ID: ")[1].split(" |")[0]
                
                venta_actual = next((v for v in ventas_admin if str(v.get("id_venta")) == str(id_seleccionado)), None)
                
                if venta_actual:
                    st.markdown("### Editar Datos del Registro")
                    with st.form("f_editar_venta"):
                        nuevo_cliente = st.text_input("Nombre del Cliente", value=venta_actual.get("nombre_cliente", ""))
                        nueva_cedula = st.text_input("Cédula del Cliente", value=venta_actual.get("cedula_cliente", ""))
                        nuevo_modelo = st.text_input("Modelo del Equipo", value=venta_actual.get("modelo", ""))
                        nuevo_email = st.text_input("Email del Teléfono", value=venta_actual.get("email_telefono", ""))
                        nuevo_tag = st.text_input("Tag del Dispositivo", value=venta_actual.get("tag_dispositivo", ""))
                        nuevo_promotor = st.text_input("Nombre Promotor", value=venta_actual.get("nombre_promotor", ""))
                        nuevo_doc_promotor = st.text_input("Documento Promotor", value=venta_actual.get("documento_promotor", ""))
                        
                        col_btn1, col_btn2 = st.columns(2)
                        with col_btn1:
                            if st.form_submit_button("Actualizar Registro", type="primary"):
                                datos_actualizados = {
                                    "nombre_cliente": nuevo_cliente,
                                    "cedula_cliente": nueva_cedula,
                                    "modelo": nuevo_modelo,
                                    "email_telefono": nuevo_email,
                                    "tag_dispositivo": nuevo_tag,
                                    "nombre_promotor": nuevo_promotor,
                                    "documento_promotor": nuevo_doc_promotor
                                }
                     
