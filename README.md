# 📊 Provision Cartera USA (en desarrollo)

Este proyecto es una aplicación interactiva desarrollada con **Streamlit**, que permite visualizar y analizar la **provisión de cartera** de clientes en EE. UU. a partir de una base de datos en Excel.  
Actualmente, el proyecto se encuentra **en fase de desarrollo**, con funcionalidades básicas implementadas para el cálculo, visualización y comparación de provisiones entre diferentes meses.

---

## 🚀 Funcionalidades actuales

✅ **Carga de datos** desde un archivo Excel (`Data/Base Provision.xlsx`).  
✅ **Filtrado automático** para los años **2024** y **2025**.  
✅ **Cálculo de provisiones** según rangos de días y condiciones específicas:
- 91–180 días: 20 % (2024) / 3 % (2025)  
- 181–270 días: 50 %  
- 271–360 días: 50 % (2024) / 100 % (2025)  
- > 360 días: 100 %  

✅ **Cálculo del total de provisión** por cliente y por mes.  
✅ **Comparación de meses** (actual vs. anterior) con métricas automáticas.  
✅ **Visualización interactiva**:
- **Tabla detallada** del último mes.  
- **Gráfico de barras apiladas** con la distribución de provisión por rango.  
- **Gráfico de líneas** mostrando la evolución mensual de la provisión total.  

---

## 🧩 Tecnologías utilizadas

- [Streamlit](https://streamlit.io/)
- [Pandas](https://pandas.pydata.org/)
- [Plotly Express](https://plotly.com/python/plotly-express/)
- Python 3.10+

---

## ⚙️ Cómo ejecutar el proyecto

1. Clonar este repositorio:
   ```bash
   git clone https://github.com/tu-usuario/provision-cartera-usa.git
   cd provision-cartera-usa
Crear y activar un entorno virtual (opcional pero recomendado):

python -m venv .venv
source .venv/bin/activate   # En macOS/Linux
.venv\Scripts\activate      # En Windows


Instalar las dependencias:

pip install -r requirements.txt


Ejecutar la aplicación:

streamlit run app.py


Abrir el enlace local que aparecerá en la terminal (por ejemplo http://localhost:8501).

📁 Estructura del proyecto
provision-cartera-usa/
│
├── Data/
│   └── Base Provision.xlsx         # Archivo con los datos fuente
│
├── app.py                          # Código principal de Streamlit
├── requirements.txt                # Dependencias del proyecto
└── README.md                       # Este archivo

🧠 Próximos pasos

♠ Cambiar el color de la tabla para que se vea acorde en la pagina
♠ Manejo de datos adicionales dentro de la tabla
♠ pendiente aprobacion y mas cambios en verificacion.

📅 Estado actual

Versión: 0.5 (en desarrollo)
Última actualización: noviembre 2025

🧑‍💻 Autor

Desarrollado por [Nicolas Cabral]
📧 [nickabral@gmail.com]
