import calendar
import datetime
from zoneinfo import ZoneInfo
import pandas as pd
import plotly.express as px
import streamlit as st
from supabase import create_client

st.set_page_config(page_title="Control de Créditos y Ventas", page_icon="📊", layout="wide")

SUPABASE_URL = "https://rijwgapwfqjxvojxqbtx.supabase.co"
SUPABASE_KEY = "sb_publishable_HgFTwscjE-NfZ_RpfDl3fw_yhNypkDQ"

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
        st.error(f"Error al insertar: {e}")
        return False

def actualizar_fila(nombre_tabla, columna_id, valor_id, datos):
    try:
        supabase.table(nombre_tabla).update(datos).eq(columna_id, str(valor_id)).execute()
        return True
    except Exception as e:
        st.error(f"Error al actualizar: {e}")
        return False

def eliminar_fila(nombre_tabla, columna_id, valor_id):
    try:
        supabase.table(nombre_tabla).delete().eq(columna_id, str(valor_id)).execute()
        return True
    except Exception as e:
        st.error(f"Error al eliminar: {e}")
        return False

TIENDAS_INICIALES = [
    "EXITO OCCIDENTE", "EXITO LA HERRADURA TULUA", "281 EXITO FLORESTA", "4052 EXITO NUESTRO BOGOTA",
    "EXITO WOW UNICENTRO", "EXITO CHIPICHAPE", "369 EXITO SAN DIEGO CARTAGENA", "EXITO CAÑAVERAL",
    "EXITO BUGA", "39 ATENDIDO SAN ANTONIO", "384 EXITO LA CEJA", "135 EXITO YOPAL"
]
RESPONSABLES_INICIALES = ["Héctor Pino", "Sebastián Pineda"]
MARCAS_INICIALES = ["Samsung", "Motorola", "Oppo", "Xiaomi", "Infinix", "Realme", "Tecno", "Honor", "Vivo", "Nubia"]

def cargar_listas():
    t_data = obtener_tabla("tiendas")
    tiendas = [t.get("tienda") for t in t_data if t and t.get("tienda")] if t_data else []
    if not tiendas:
        tiendas = TIENDAS_INICIALES
        for t in TIENDAS_INICIALES:
            insertar_fila("tiendas", {"tienda": t})

    r_data = obtener_tabla("responsables")
    responsables = [r.get("nombre") for r in r_data if r and r.get("nombre")] if r_data else []
    if not responsables:
        responsables = RESPONSABLES_INICIALES
        for r in RESPONSABLES_INICIALES:
            insertar_fila("responsables", {"nombre": r})

    m_data = obtener_tabla("marcas")
    marcas = [m.get("marca") for m in m_data if m and m.get("marca")] if m_data else []
    if not marcas:
        marcas = MARCAS_INICIALES
        for m in MARCAS_INICIALES:
            insertar_fila("marcas", {"marca": m})

    meta_data = obtener_tabla("meta")
    meta_val = int(meta_data[0]["meta"]) if meta_data and str(meta_data[0].get("meta", "")).isdigit() else 200

    return tiendas, responsables, marcas, meta_val

tiendas_list, responsables_list, marcas_list, META = cargar_listas()

if "auth_general" not in st.session_state:
    st.session_state.auth_general = False
if "auth_admin" not in st.session_state:
    st.session_state.auth_admin = False
if "auth_auditoria" not in st.session_state:
    st.session_state.auth_auditoria = False

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

if menu == "Dashboard":
    if not st.session_state.auth_general:
        st.header("Módulo Protegido")
        pass_input = st.text_input("Ingrese la contraseña general", type="password")
        if st.button("Acceder"):
            if pass_input == "payjoy2026":
                st.session_state.auth_general = True
                st.rerun()
            else:
                st.error("Contraseña incorrecta.")
    else:
        st.header("📊 Dashboard General y Analítica")
        if st.sidebar.button("Cerrar Sesión"):
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

            # Día de la semana con más ventas
            if not df_mes.empty:
                dias_esp = {0: "Lunes", 1: "Martes", 2: "Miércoles", 3: "Jueves", 4: "Viernes", 5: "Sábado", 6: "Domingo"}
                df_mes["dia_semana"] = df_mes["_dt"].dt.dayofweek.map(dias_esp)
                top_dia = df_mes["dia_semana"].mode()[0] if not df_mes["dia_semana"].mode().empty else "N/A"
            else:
                top_dia = "N/A"

            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Meta del Mes", str(META))
            m2.metric("Créditos a la Fecha", str(total_mes))
            m3.metric("Faltantes para Meta", str(faltantes))
            m4.metric("% Cumplimiento", f"{pct_cumplimiento}%")

            st.progress(min(total_mes / META, 1.0) if META > 0 else 1.0)
            
            m5, m6, m7, m8 = st.columns(4)
            m5.metric("Proyección Unidades", str(proyeccion_unidades))
            m6.metric("Tienda que Más Vende", top_tienda)
            m7.metric("Marca que Más Vende", top_marca)
            m8.metric("Día que Más se Vende", top_dia)

            st.markdown("---")
            st.subheader("📈 Analítica y Gráficos del Mes")

            if not df_mes.empty:
                g1, g2 = st.columns(2)
                with g1:
                    st.markdown("##### 🏆 Ventas por Marca")
                    df_marcas = df_mes["marca_equipo"].value_counts().reset_index()
                    df_marcas.columns = ["Marca", "Cantidad"]
                    fig_marca = px.bar(df_marcas, x="Marca", y="Cantidad", text="Cantidad", color="Marca", template="plotly_white")
                    st.plotly_chart(fig_marca, use_container_width=True)

                with g2:
                    st.markdown("##### 📅 Ventas por Día de la Semana")
                    orden_dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
                    df_dias = df_mes["dia_semana"].value_counts().reindex(orden_dias, fill_value=0).reset_index()
                    df_dias.columns = ["Día", "Cantidad"]
                    fig_dias = px.line(df_dias, x="Día", y="Cantidad", markers=True, template="plotly_white")
                    st.plotly_chart(fig_dias, use_container_width=True)

                g3, g4 = st.columns(2)
                with g3:
                    st.markdown("##### 🏬 Top Tiendas con Más Ventas")
                    df_tiendas = df_mes["tienda"].value_counts().head(5).reset_index()
                    df_tiendas.columns = ["Tienda", "Cantidad"]
                    fig_tiendas = px.pie(df_tiendas, names="Tienda", values="Cantidad", hole=0.4, template="plotly_white")
                    st.plotly_chart(fig_tiendas, use_container_width=True)

                with g4:
                    st.markdown("##### 🏅 Top 5 Mejores Promotores")
                    df_promotores = df_mes["nombre_promotor"].value_counts().head(5).reset_index()
                    df_promotores.columns = ["Promotor", "Cantidad"]
                    fig_prom = px.bar(df_promotores, x="Promotor", y="Cantidad", text="Cantidad", color="Promotor", template="plotly_white")
                    st.plotly_chart(fig_prom, use_container_width=True)
            else:
                st.info("No hay suficientes datos este mes para mostrar gráficos analíticos.")
        else:
            st.info("No hay créditos registrados en el mes actual.")

elif menu == "Registrar Crédito / Venta":
    st.header("Registrar Nuevo Crédito")
    with st.form("f_registro", clear_on_submit=True):
        responsable = st.selectbox("Responsable de Venta", responsables_list)
        tienda = st.selectbox("Tienda", tiendas_list)
        nombre_cliente = st.text_input("Nombre del Cliente").strip()
        telefono_cliente = st.text_input("Teléfono del Cliente").strip()
        nombre_promotor = st.text_input("Nombre del Promotor").strip().title()
        documento_promotor = st.text_input("Documento del Promotor").strip()
        marca_equipo = st.selectbox("Marca del Equipo", marcas_list)
        modelo_equipo = st.text_input("Modelo del Equipo").strip()
        imei_equipo = st.text_input("IMEI del Equipo").strip()
        tag_credito = st.text_input("Tag del Crédito").strip()
        
        if st.form_submit_button("Guardar Crédito", type="primary"):
            if not documento_promotor or not imei_equipo or not tag_credito:
                st.warning("Complete los campos obligatorios.")
            else:
                id_credito = datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")
                fecha_actual = str(datetime.datetime.now(ZoneInfo("America/Bogota")).date())
                nuevo_reg = {
                    "id_credito": id_credito, "fecha": fecha_actual, "responsable": responsable,
                    "tienda": tienda, "nombre_cliente": nombre_cliente, "telefono_cliente": telefono_cliente,
                    "nombre_promotor": nombre_promotor, "documento_promotor": documento_promotor,
                    "marca_equipo": marca_equipo, "modelo_equipo": modelo_equipo, "imei": imei_equipo, "tag": tag_credito
                }
                if insertar_fila("creditos", nuevo_reg):
                    st.success("¡Crédito registrado con éxito!")
                    st.rerun()

elif menu == "Mis Ventas (Promotor)":
    st.header("Consultar Mis Ventas (Promotor)")
    doc_con = st.text_input("Número de Documento del Promotor").strip()
    if doc_con:
        creditos_act = obtener_tabla("creditos")
        if creditos_act:
            df_c = pd.DataFrame(creditos_act).fillna("")
            df_prom = df_c[df_c["documento_promotor"].astype(str).str.strip() == doc_con]
            if not df_prom.empty:
                st.success(f"Total Créditos: {len(df_prom)}")
                st.dataframe(df_prom, use_container_width=True)
            else:
                st.warning("No se encontraron registros.")

elif menu == "Auditoría y Depuración (Admin)":
    if not st.session_state.auth_auditoria:
        pass_a = st.text_input("Contraseña de Auditoría", type="password")
        if st.button("Acceder"):
            if pass_a == "payjoy2026":
                st.session_state.auth_auditoria = True
                st.rerun()
            else:
                st.error("Contraseña incorrecta.")
    else:
        st.header("📋 Auditoría, Modificación y Depuración")
        if st.sidebar.button("Cerrar Sesión"):
            st.session_state.auth_auditoria = False
            st.rerun()
            
        creditos_aud = obtener_tabla("creditos")
        if creditos_aud:
            df_a = pd.DataFrame(creditos_aud).fillna("")
            st.dataframe(df_a, use_container_width=True)
            
            st.markdown("---")
            ops = [str(c.get('id_credito')) for c in creditos_aud if c.get('id_credito')]
            if ops:
                id_sel = st.selectbox("Seleccione el ID del Crédito a Gestionar", ops)
                
                credito_obj = next((c for c in creditos_aud if str(c.get("id_credito")) == str(id_sel)), None)
                
                if credito_obj:
                    col_m1, col_m2 = st.columns(2)
                    with col_m1:
                        st.markdown("##### ✏️ Modificar Registro")
                        n_cli = st.text_input("Nombre Cliente", value=str(credito_obj.get("nombre_cliente", "")))
                        t_cli = st.text_input("Teléfono Cliente", value=str(credito_obj.get("telefono_cliente", "")))
                        n_prom = st.text_input("Nombre Promotor", value=str(credito_obj.get("nombre_promotor", "")))
                        d_prom = st.text_input("Documento Promotor", value=str(credito_obj.get("documento_promotor", "")))
                        n_mod = st.text_input("Modelo Equipo", value=str(credito_obj.get("modelo_equipo", "")))
                        n_imei = st.text_input("IMEI", value=str(credito_obj.get("imei", "")))
                        n_tag = st.text_input("Tag", value=str(credito_obj.get("tag", "")))
                        
                        if st.button("Guardar Cambios"):
                            datos_act = {
                                "nombre_cliente": n_cli, "telefono_cliente": t_cli,
                                "nombre_promotor": n_prom, "documento_promotor": d_prom,
                                "modelo_equipo": n_mod, "imei": n_imei, "tag": n_tag
                            }
                            if actualizar_fila("creditos", "id_credito", id_sel, datos_act):
                                st.success("¡Crédito actualizado con éxito!")
                                st.rerun()
                                
                    with col_m2:
                        st.markdown("##### 🗑️ Eliminar Registro")
                        st.markdown("<br><br>", unsafe_allow_html=True)
                        if st.button("Eliminar esta Venta Definitivamente", type="primary"):
                            if eliminar_fila("creditos", "id_credito", id_sel):
                                st.success("Venta eliminada correctamente.")
                                st.rerun()

elif menu == "Administración":
    if not st.session_state.auth_admin:
        pass_ad = st.text_input("Contraseña de Administrador", type="password")
        if st.button("Acceder Admin"):
            if pass_ad == "hectorp2026":
                st.session_state.auth_admin = True
                st.rerun()
            else:
                st.error("Contraseña incorrecta.")
    else:
        st.header("Panel de Administración")
        if st.sidebar.button("Cerrar Sesión Admin"):
            st.session_state.auth_admin = False
            st.rerun()
            
        t1, t2 = st.tabs(["Gestión Responsables", "Gestión Tiendas"])
        
        with t1:
            n_r = st.text_input("Nuevo Responsable").strip().title()
            if st.button("Agregar Responsable"):
                if n_r and insertar_fila("responsables", {"nombre": n_r}):
                    st.success("Agregado.")
                    st.rerun()
            r_list = [r.get("nombre") for r in obtener_tabla("responsables") if r.get("nombre")] or responsables_list
            if r_list:
                del_r = st.selectbox("Eliminar Responsable", r_list, key="del_r")
                if st.button("Borrar Responsable", type="primary"):
                    if eliminar_fila("responsables", "nombre", del_r):
                        st.success("Eliminado.")
                        st.rerun()

        with t2:
            n_t = st.text_input("Nueva Tienda").strip().upper()
            if st.button("Agregar Tienda"):
                if n_t and insertar_fila("tiendas", {"tienda": n_t}):
                    st.success("Agregada.")
                    st.rerun()
            t_list = [t.get("tienda") for t in obtener_tabla("tiendas") if t.get("tienda")] or tiendas_list
            if t_list:
                del_t = st.selectbox("Eliminar Tienda", t_list, key="del_t")
                if st.button("Borrar Tienda", type="primary"):
                    if eliminar_fila("tiendas", "tienda", del_t):
                        st.success("Eliminada.")
                        st.rerun()
        
