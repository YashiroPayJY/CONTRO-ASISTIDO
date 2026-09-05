import streamlit as st
import pandas as pd
import plotly.express as px
import datetime
import os
import calendar

# Configuración de la página
st.set_page_config(page_title="Control de Ventas por Unidades - Tienda", layout="wide")

# Archivo local para persistencia de datos
DB_FILE = "base_datos_ventas_unidades.json"

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
    "385 EXITO RIOHACHA", "180 EXITO BARRANCABERMEJA", "408 EXITO SAN DIEGO MEDELLIN",
    "175 EXITO FLORENCIA", "409 EXITO UNICENTRO MEDELLIN", "4054 EXITO LLANOGRANDE PALMIRA",
    "33 EXITO POBLADO", "355 EXITO DIVERPLAZA", "9990 EXITO MALL PLAZA NQS", "489 EXITO FONTANAR CHIA",
    "158 EXITO ZIPAQUIRA", "172 EXITO MAGANGUE", "51 EXITO SAN FERNANDO", "41 EXITO BARRANQUILLA",
    "283 EXITO NUEVO KENNEDY", "275 EXITO BELLO CENTRO", "370 EXITO CASTELLANA", "40 EXITO ITAGUI",
    "514 EXITO MOLINOS", "65 EXITO UNICENTRO ARMENIA", "352 EXITO ORIENTAL BUCARAMANGA CV",
    "363 EXITO BUENA VISTA SANTA MARTA", "64 EXITO TULUA", "157 EXITO SAN PEDRO NEIVA",
    "353 EXITO SAN MATEO CUCUTA CV", "156 EXITO IBAGUE", "357 EXITO ALAMEDAS DEL SINU MONTERIA",
    "4039 EXITO UNICENTRO GIRARDOT", "173 EXITO MOSQUERA", "35 EXITO ENVIGADO",
    "31 EXITO COLOMBIA", "54 EXITO LA FLORA", "4025 EXITO SOACHA", "159 EXITO VILLAVICENCIO",
    "71 EXITO BUCARAMANGA", "47 EXITO METROPOLITANO", "302 EXITO CIUDAD TUNAL",
    "174 EXITO PEREIRA CUBA", "75 EXITO MAYORCA", "362 EXITO BUENA VISTA", "44 EXITO CARTAGENA",
    "94 EXITO CHAPINERO", "56 EXITO UNICALI", "258 EXITO SANTA MARTA CENTRO",
    "435 EXITO PANAMERICANA POPAYAN", "354 EXITO LAS FLORES VALLEDUPAR CV", "45 EXITO APARTADO",
    "0265 EXITO CAUCASIA", "63 PJK EXITO PEREIRA", "93 PJK EXITO SUBA", "376 PJK EXITO BOSA",
    "39 PJK EXITO SAN ANTONIO", "30 PJK EXITO BELLO", "83 PJK EXITO VILLA MAYOR"
]

# Inicializar datos por defecto y asegurar que se carguen todas las tiendas
def cargar_datos():
    tiendas_actuales = TIENDAS_INICIALES
    promotores_val = []
    ventas_val = []
    meta_val = 100

    if os.path.exists(DB_FILE):
        try:
            df_base = pd.read_json(DB_FILE)
            if not df_base.empty:
                if "tiendas" in df_base and len(df_base["tiendas"].iloc[0]) > 0:
                    tiendas_guardadas = list(df_base["tiendas"].iloc[0])
                    tiendas_actuales = sorted(list(set(tiendas_guardadas + TIENDAS_INICIALES)))
                if "promotores" in df_base:
                    promotores_val = list(df_base["promotores"].iloc[0])
                if "ventas" in df_base:
                    ventas_val = list(df_base["ventas"].iloc[0])
                if "meta_unidades" in df_base:
                    meta_val = int(df_base["meta_unidades"].iloc[0])
        except Exception:
            pass

    return {
        "tiendas": tiendas_actuales,
        "promotores": promotores_val,
        "ventas": ventas_val,
        "meta_unidades": meta_val
    }

def guardar_datos(data):
    df = pd.DataFrame([data])
    df.to_json(DB_FILE)

db = cargar_datos()

MARCAS_DISPONIBLES = ["Samsung", "Motorola", "Xiaomi", "Oppo", "Honor", "Tecno", "Infinix", "Realme", "Nubia", "Vivo"]
RESPONSABLES_DISPONIBLES = ["HECTOR PINO", "SEBASTIAN PINEDA"]

# Inicializar estado de sesión para administrador si no existe
if "admin_autenticado" not in st.session_state:
    st.session_state["admin_autenticado"] = False

st.sidebar.title("Menú Principal")
menu = st.sidebar.radio("Ir a:", [
    "Dashboard (Admin)", 
    "Registro Promotor (Admin)", 
    "Registrar Venta (Admin)", 
    "Mis Ventas (Libre)", 
    "Módulo Admin"
])

st.sidebar.markdown("---")
st.sidebar.info(f"Mes Actual: {datetime.date.today().strftime('%B %Y')}")

# Botón en la barra lateral para cerrar sesión manualmente en cualquier momento
if st.session_state["admin_autenticado"]:
    if st.sidebar.button("🔒 Cerrar Sesión de Admin"):
        st.session_state["admin_autenticado"] = False
        st.rerun()

# ================= 1. DASHBOARD (PROTEGIDO) =================
if menu == "Dashboard (Admin)":
    st.title("📊 Dashboard de Progreso por Unidades")
    st.markdown("⚠️ *Sección protegida con contraseña de administrador.*")
    
    if not st.session_state["admin_autenticado"]:
        pass_dash = st.text_input("Ingrese la Contraseña de Administrador", type="password", key="pass_dashboard")
        if pass_dash == "admin123":
            st.session_state["admin_autenticado"] = True
            st.rerun()
        elif pass_dash != "":
            st.error("Contraseña incorrecta.")
            
    if st.session_state["admin_autenticado"]:
        st.success("Sesión activa de administrador.")
        st.markdown("---")
        
        if not db["ventas"]:
            st.warning("Aún no hay ventas registradas en el sistema.")
        
        df_ventas = pd.DataFrame(db["ventas"]) if db["ventas"] else pd.DataFrame(columns=["id", "fecha", "responsable", "clienteNombre", "clienteDoc", "cartag", "marca", "modelo", "imei", "promotorNombre", "docPromotor", "telPromotor", "tienda"])

        tiendas_opciones = ["TODAS"] + list(db["tiendas"])
        tienda_seleccionada = st.selectbox("Filtrar por Tienda:", tiendas_opciones)

        if tienda_seleccionada != "TODAS" and not df_ventas.empty:
            df_filtrado = df_ventas[df_ventas["tienda"] == tienda_seleccionada]
        else:
            df_filtrado = df_ventas

        total_unidades = len(df_filtrado)
        meta_uni = db["meta_unidades"]
        
        cumplimiento_uni = (total_unidades / meta_uni * 100) if meta_uni > 0 else 0
        
        hoy = datetime.date.today()
        dia_actual = hoy.day
        _, total_dias_mes = calendar.monthrange(hoy.year, hoy.month)
        
        proyeccion_uni = int((total_unidades / dia_actual * total_dias_mes)) if dia_actual > 0 else 0
        unidades_restantes = max(0, meta_uni - total_unidades)

        col1, col2, col3 = st.columns(3)
        col1.metric("Meta de Unidades del Mes", f"{meta_uni} unds")
        col2.metric("Ventas a la Fecha (Unidades)", f"{total_unidades} unds", f"{cumplimiento_uni:.1f}% Cumplimiento")
        col3.metric("Proyección de Unidades", f"{proyeccion_uni} unds")

        col4, col5 = st.columns(2)
        col4.metric("Progreso Actual", f"{total_unidades} / {meta_uni}")
        col5.metric("Unidades Restantes para la Meta", f"{unidades_restantes} unds")

        st.markdown("---")

        if not df_filtrado.empty:
            c1, c2 = st.columns(2)
            with c1:
                st.subheader("Share por Marca (Unidades)")
                fig_marca = px.pie(df_filtrado, names="marca", hole=0.4, color_discrete_sequence=px.colors.qualitative.Pastel)
                st.plotly_chart(fig_marca, use_container_width=True)
            with c2:
                st.subheader("Share por Tienda (Unidades)")
                fig_tienda = px.bar(df_filtrado, x="tienda", color="tienda", title="Unidades Vendidas por Tienda")
                st.plotly_chart(fig_tienda, use_container_width=True)
        else:
            st.info("No hay datos suficientes para mostrar los gráficos con el filtro seleccionado.")

# ================= 2. REGISTRO PROMOTOR (PROTEGIDO) =================
elif menu == "Registro Promotor (Admin)":
    st.title("📝 Registro de Promotores y Asesores")
    st.markdown("⚠️ *Sección protegida con contraseña de administrador.*")
    
    if not st.session_state["admin_autenticado"]:
        pass_promotor = st.text_input("Ingrese la Contraseña de Administrador", type="password", key="pass_reg_promotor")
        if pass_promotor == "admin123":
            st.session_state["admin_autenticado"] = True
            st.rerun()
        elif pass_promotor != "":
            st.error("Contraseña incorrecta.")
            
    if st.session_state["admin_autenticado"]:
        st.success("Sesión activa de administrador.")
        st.markdown("---")
        
        with st.form("form_promotor", clear_on_submit=True):
            nombre = st.text_input("Nombre Completo")
            doc = st.text_input("Número de Documento")
            marca = st.selectbox("Marca Representada", MARCAS_DISPONIBLES)
            tienda = st.selectbox("Tienda Asignada", db["tiendas"])
            
            submitted = st.form_submit_button("Registrarse")
            if submitted:
                if not nombre or not doc:
                    st.error("Por favor completa todos los campos.")
                elif any(p["doc"] == doc for p in db["promotores"]):
                    st.error("Ya existe un promotor registrado con este número de documento.")
                else:
                    db["promotores"].append({
                        "nombre": nombre,
                        "doc": doc,
                        "marca": marca,
                        "tienda": tienda
                    })
                    guardar_datos(db)
                    st.success("¡Promotor registrado con éxito!")

# ================= 3. REGISTRAR VENTA (PROTEGIDO Y ORDENADO) =================
elif menu == "Registrar Venta (Admin)":
    st.title("🛒 Módulo de Registro de Ventas Detallado")
    st.markdown("⚠️ *Sección protegida con contraseña de administrador.*")
    
    if not st.session_state["admin_autenticado"]:
        pass_venta = st.text_input("Ingrese la Contraseña de Administrador", type="password", key="pass_reg_venta")
        if pass_venta == "admin123":
            st.session_state["admin_autenticado"] = True
            st.rerun()
        elif pass_venta != "":
            st.error("Contraseña incorrecta.")
            
    if st.session_state["admin_autenticado"]:
        st.success("Sesión activa. Puedes registrar todas las ventas que necesites sin volver a ingresar contraseña.")
        st.markdown("---")
        
        with st.form("form_venta", clear_on_submit=True):
            fecha_venta = st.date_input("Fecha:", datetime.date.today())
            responsable = st.selectbox("Responsable:", RESPONSABLES_DISPONIBLES)
            cliente_nombre = st.text_input("Nombre del cliente:")
            cliente_doc = st.text_input("Documento del cliente:")
            cartag = st.text_input("Cartag:")
            marca = st.selectbox("Marca:", MARCAS_DISPONIBLES)
            modelo = st.text_input("Modelo:")
            imei = st.text_input("IMEI:")
            promotor_nombre = st.text_input("Nombre del promotor:")
            doc_promotor = st.text_input("Documento del promotor:")
            tel_promotor = st.text_input("Teléfono del promotor:")
            tienda = st.selectbox("Tienda:", db["tiendas"])
            
            btn_venta = st.form_submit_button("Registrar Venta")
            
            if btn_venta:
                if not cliente_nombre or not cliente_doc or not imei or not doc_promotor or not modelo or not promotor_nombre:
                    st.error("Por favor completa todos los campos requeridos.")
                else:
                    nueva_venta = {
                        "id": int(datetime.datetime.now().timestamp() * 1000),
                        "fecha": str(fecha_venta),
                        "responsable": responsable,
                        "clienteNombre": cliente_nombre,
                        "clienteDoc": cliente_doc,
                        "cartag": cartag,
                        "marca": marca,
                        "modelo": modelo,
                        "imei": imei,
                        "promotorNombre": promotor_nombre,
                        "docPromotor": doc_promotor,
                        "telPromotor": tel_promotor,
                        "tienda": tienda
                    }
                    db["ventas"].append(nueva_venta)
                    guardar_datos(db)
                    st.success("¡Venta detallada registrada con éxito y campos limpios!")
                    st.rerun()

# ================= 4. MIS VENTAS (LIBRE / SIN CONTRASEÑA) =================
elif menu == "Mis Ventas (Libre)":
    st.title("🔍 Consulta de Mis Ventas")
    st.markdown("ℹ️ *Módulo libre para que cada promotor consulte sus ventas con su número de documento.*")
    
    doc_consulta = st.text_input("Ingrese su Número de Documento de Promotor:")
    
    if doc_consulta:
        ventas_asesor = [v for v in db["ventas"] if str(v.get("docPromotor")) == str(doc_consulta)]
        
        if ventas_asesor:
            df_mis_ventas = pd.DataFrame(ventas_asesor)
            st.info(f"Total de unidades vendidas por ti en el mes: **{len(df_mis_ventas)}**")
            st.dataframe(df_mis_ventas[["fecha", "responsable", "clienteNombre", "clienteDoc", "cartag", "marca", "modelo", "imei", "promotorNombre", "tienda"]])
            
            csv = df_mis_ventas.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Descargar mis ventas en Excel (CSV)",
                data=csv,
                file_name=f"mis_ventas_{doc_consulta}.csv",
                mime="text/csv",
            )
        else:
            st.info("No se encontraron ventas registradas para este documento.")

# ================= 5. MÓDULO ADMIN (PROTEGIDO) =================
elif menu == "Módulo Admin":
    st.title("🔐 Módulo de Administración")
    
    if not st.session_state["admin_autenticado"]:
        password = st.text_input("Contraseña de Administrador", type="password")
        if password == "admin123":
            st.session_state["admin_autenticado"] = True
            st.rerun()
        elif password != "":
            st.error("Contraseña incorrecta.")
            
    if st.session_state["admin_autenticado"]:
        st.success("Acceso de administrador activo.")
        st.markdown("---")
        
        st.subheader("Configuración de Meta de Unidades del Mes")
        with st.form("form_metas", clear_on_submit=False):
            nueva_meta_uni = st.number_input("Meta de Unidades Totales del Mes", value=int(db["meta_unidades"]), step=1)
            btn_metas = st.form_submit_button("Actualizar Meta")
            if btn_metas:
                db["meta_unidades"] = int(nueva_meta_uni)
                guardar_datos(db)
                st.success("¡Meta de unidades actualizada con éxito!")
        
        st.markdown("---")
        st.subheader("Gestión de Tiendas")
        
        nueva_tienda = st.text_input("Nombre de la nueva tienda:")
        if st.button("Agregar Tienda"):
            if nueva_tienda and nueva_tienda not in db["tiendas"]:
                db["tiendas"].append(nueva_tienda)
                guardar_datos(db)
                st.success(f"Tienda '{nueva_tienda}' agregada correctamente.")
                st.rerun()
            else:
                st.error("Error: El nombre está vacío o la tienda ya existe.")
        
        st.markdown("#### Eliminar Tienda")
        if db["tiendas"]:
            tienda_a_eliminar = st.selectbox("Seleccione la tienda a eliminar:", db["tiendas"])
            if st.button("Eliminar Tienda Seleccionada"):
                if len(db["tiendas"]) <= 1:
                    st.error("Debe haber al menos una tienda registrada en el sistema.")
                else:
                    db["tiendas"].remove(tienda_a_eliminar)
                    guardar_datos(db)
                    st.success(f"Tienda '{tienda_a_eliminar}' eliminada con éxito.")
                    st.rerun()
        else:
            st.info("No hay tiendas registradas para eliminar.")
        
        st.markdown("---")
        st.subheader("Eliminar Registros Erróneos")
        
        col_1, col_2 = st.columns(2)
        with col_1:
            st.markdown("#### Eliminar Promotor")
            doc_eliminar = st.text_input("Documento del promotor a eliminar:")
            if st.button("Eliminar Asesor"):
                antes = len(db["promotores"])
                db["promotores"] = [p for p in db["promotores"] if p["doc"] != doc_eliminar]
                if len(db["promotores"]) < antes:
                    guardar_datos(db)
                    st.success("Promotor eliminado.")
                    st.rerun()
                else:
                    st.error("No se encontró un promotor con ese documento.")
                    
        with col_2:
            st.markdown("#### Eliminar Venta por ID")
            id_eliminar = st.number_input("ID de la venta:", step=1, format="%d")
            if st.button("Eliminar Venta"):
                antes = len(db["ventas"])
                db["ventas"] = [v for v in db["ventas"] if v["id"] != int(id_eliminar)]
                if len(db["ventas"]) < antes:
                    guardar_datos(db)
                    st.success("Venta eliminada correctamente.")
                    st.rerun()
                else:
                    st.error("No se encontró una venta con ese ID.")
                    
        st.markdown("---")
        st.subheader("Listado General de Ventas Registradas")
        if db["ventas"]:
            st.dataframe(pd.DataFrame(db["ventas"]))
        else:
            st.info("No hay ventas registradas.")
    
