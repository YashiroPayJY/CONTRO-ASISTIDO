import streamlit as st
import pandas as pd
import plotly.express as px
import datetime
import os
import calendar

# Configuración de la página
st.set_page_config(page_title="Control de Ventas & Promotores", layout="wide")

# Archivo local para persistencia de datos (simula una base de datos)
DB_FILE = "base_datos_ventas.json"

# Inicializar datos por defecto si no existen
def cargar_datos():
    if os.path.exists(DB_FILE):
        try:
            df_base = pd.read_json(DB_FILE)
            return {
                "tiendas": df_base.get("tiendas", pd.Series([['Tienda Principal', 'Tienda Norte']])).iloc[0] if not df_base.empty else ['Tienda Principal'],
                "promotores": df_base.get("promotores", pd.Series([[]])).iloc[0] if "promotores" in df_base else [],
                "ventas": df_base.get("ventas", pd.Series([[]])).iloc[0] if "ventas" in df_base else [],
                "meta_valor": float(df_base.get("meta_valor", pd.Series([10000])).iloc[0]) if "meta_valor" in df_base else 10000.0,
                "meta_unidades": int(df_base.get("meta_unidades", pd.Series([100])).iloc[0]) if "meta_unidades" in df_base else 100
            }
        except Exception:
            pass
    return {
        "tiendas": ['Tienda Principal', 'Tienda Norte'],
        "promotores": [],
        "ventas": [],
        "meta_valor": 10000.0,
        "meta_unidades": 100
    }

def guardar_datos(data):
    df = pd.DataFrame([data])
    df.to_json(DB_FILE)

db = cargar_datos()

MARCAS_DISPONIBLES = ["Samsung", "Motorola", "Xiaomi", "Oppo", "Honor", "Tecno", "Infinix", "Realme", "Nubia", "Vivo"]

st.sidebar.title("Menú Principal")
menu = st.sidebar.radio("Ir a:", [
    "Dashboard", 
    "Registro Promotor", 
    "Registrar Venta", 
    "Mis Ventas", 
    "Módulo Admin"
])

st.sidebar.markdown("---")
st.sidebar.info(f"Mes Actual: {datetime.date.today().strftime('%B %Y')}")

# ================= 1. DASHBOARD =================
if menu == "Dashboard":
    st.title("📊 Dashboard de Rendimiento del Mes")
    
    if not db["ventas"]:
        st.warning("Aún no hay ventas registradas en el sistema.")
    
    df_ventas = pd.DataFrame(db["ventas"]) if db["ventas"] else pd.DataFrame(columns=["id", "docAsesor", "nombreAsesor", "tienda", "clienteNombre", "clienteApellido", "marca", "valor", "fecha"])

    tiendas_opciones = ["TODAS"] + list(db["tiendas"])
    tienda_seleccionada = st.selectbox("Filtrar por Tienda:", tiendas_opciones)

    if tienda_seleccionada != "TODAS" and not df_ventas.empty:
        df_filtrado = df_ventas[df_ventas["tienda"] == tienda_seleccionada]
    else:
        df_filtrado = df_ventas

    total_ventas_valor = df_filtrado["valor"].sum() if not df_filtrado.empty else 0.0
    total_unidades = len(df_filtrado)
    
    meta_val = db["meta_valor"]
    meta_uni = db["meta_unidades"]
    
    cumplimiento_val = (total_ventas_valor / meta_val * 100) if meta_val > 0 else 0
    
    hoy = datetime.date.today()
    dia_actual = hoy.day
    _, total_dias_mes = calendar.monthrange(hoy.year, hoy.month)
    
    proyeccion_val = (cumplimiento_val / dia_actual * total_dias_mes) if dia_actual > 0 else 0
    proyeccion_uni = int((total_unidades / dia_actual * total_dias_mes)) if dia_actual > 0 else 0
    unidades_restantes = max(0, meta_uni - total_unidades)

    col1, col2, col3 = st.columns(3)
    col1.metric("Meta del Mes ($)", f"${meta_val:,.2f}")
    col2.metric("Ventas a la Fecha ($)", f"${total_ventas_valor:,.2f}", f"{cumplimiento_val:.1f}% Cumplimiento")
    col3.metric("Proyección de Cumplimiento", f"{proyeccion_val:.1f}%")

    col4, col5, col6 = st.columns(3)
    col4.metric("Unidades Vendidas / Meta", f"{total_unidades} / {meta_uni}")
    col5.metric("Proyección de Unidades", f"{proyeccion_uni} unds")
    col6.metric("Unidades Restantes", f"{unidades_restantes} unds")

    st.markdown("---")

    if not df_filtrado.empty:
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("Share por Marca (Unidades)")
            fig_marca = px.pie(df_filtrado, names="marca", hole=0.4, color_discrete_sequence=px.colors.qualitative.Pastel)
            st.plotly_chart(fig_marca, use_container_width=True)
        with c2:
            st.subheader("Share por Tienda (Unidades)")
            fig_tienda = px.bar(df_filtrado, x="tienda", color="tienda", title="Ventas por Tienda")
            st.plotly_chart(fig_tienda, use_container_width=True)
    else:
        st.info("No hay datos suficientes para mostrar los gráficos con el filtro seleccionado.")

# ================= 2. REGISTRO PROMOTOR =================
elif menu == "Registro Promotor":
    st.title("📝 Registro de Promotores y Asesores")
    
    with st.form("form_promotor"):
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

# ================= 3. REGISTRAR VENTA =================
elif menu == "Registrar Venta":
    st.title("🛒 Módulo de Registro de Ventas")
    
    if not db["promotores"]:
        st.warning("Primero debes registrar al menos un promotor en el sistema.")
    else:
        doc_asesor = st.text_input("Digite su Número de Documento (Asesor):")
        asesor_encontrado = next((p for p in db["promotores"] if p["doc"] == doc_asesor), None)
        
        if doc_asesor:
            if asesor_encontrado:
                st.success(f"Asesor encontrado: **{asesor_encontrado['nombre']}** ({asesor_encontrado['marca']} - Tienda: {asesor_encontrado['tienda']})")
            else:
                st.error("Asesor no encontrado con este documento. Verifique o regístrese primero.")

        with st.form("form_venta"):
            c_nombre = st.text_input("Nombre del Cliente")
            c_apellido = st.text_input("Apellido del Cliente")
            v_marca = st.selectbox("Marca Vendida", MARCAS_DISPONIBLES)
            v_valor = st.number_input("Valor de la Venta ($)", min_value=0.0, step=0.01)
            v_fecha = st.date_input("Fecha de la Venta", datetime.date.today())
            
            btn_venta = st.form_submit_button("Registrar Venta")
            
            if btn_venta:
                if not asesor_encontrado:
                    st.error("No se puede registrar la venta sin un asesor válido.")
                elif not c_nombre or not c_apellido:
                    st.error("Por favor complete los datos del cliente.")
                else:
                    nueva_venta = {
                        "id": int(datetime.datetime.now().timestamp() * 1000),
                        "docAsesor": asesor_encontrado["doc"],
                        "nombreAsesor": asesor_encontrado["nombre"],
                        "tienda": asesor_encontrado["tienda"],
                        "clienteNombre": c_nombre,
                        "clienteApellido": c_apellido,
                        "marca": v_marca,
                        "valor": v_valor,
                        "fecha": str(v_fecha)
                    }
                    db["ventas"].append(nueva_venta)
                    guardar_datos(db)
                    st.success("¡Venta registrada con éxito!")
                    st.rerun()

# ================= 4. MIS VENTAS =================
elif menu == "Mis Ventas":
    st.title("🔍 Consulta de Mis Ventas")
    
    doc_consulta = st.text_input("Ingrese su Número de Documento:")
    
    if doc_consulta:
        ventas_asesor = [v for v in db["ventas"] if v["docAsesor"] == doc_consulta]
        
        if ventas_asesor:
            df_mis_ventas = pd.DataFrame(ventas_asesor)
            st.dataframe(df_mis_ventas[["fecha", "clienteNombre", "clienteApellido", "marca", "tienda", "valor"]])
            
            csv = df_mis_ventas.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Descargar mis ventas en Excel (CSV)",
                data=csv,
                file_name=f"mis_ventas_{doc_consulta}.csv",
                mime="text/csv",
            )
        else:
            st.info("No se encontraron ventas registradas para este documento.")

# ================= 5. MÓDULO ADMIN =================
elif menu == "Módulo Admin":
    st.title("🔐 Módulo de Administración")
    
    password = st.text_input("Contraseña de Administrador", type="password")
    
    if password == "admin123":
        st.success("Acceso concedido.")
        st.markdown("---")
        
        st.subheader("Configuración de Metas del Mes")
        with st.form("form_metas"):
            nueva_meta_val = st.number_input("Meta Financiera Global ($)", value=float(db["meta_valor"]))
            nueva_meta_uni = st.number_input("Meta de Unidades Totales", value=int(db["meta_unidades"]))
            btn_metas = st.form_submit_button("Actualizar Metas")
            if btn_metas:
                db["meta_valor"] = nueva_meta_val
                db["meta_unidades"] = nueva_meta_uni
                guardar_datos(db)
                st.success("¡Metas actualizadas con éxito!")
        
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
                st.error("El nombre de la tienda está vacío o ya existe.")
        
        st.write("Tiendas actuales:", db["tiendas"])
        
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
            
    elif password != "":
        st.error("Contraseña incorrecta.")
  
