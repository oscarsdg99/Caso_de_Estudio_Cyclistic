"""
Cyclistic Bike-Share Analysis
Análisis de diferencias entre miembros anuales y ciclistas casuales
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# ============================================================================
# FUNCIÓN PARA FORMATEO DE NÚMEROS EN FORMATO LATINOAMERICANO
# ============================================================================

def format_number(num):
    """
    Formatea números al estilo latinoamericano:
    - Punto (.) como separador de miles
    - Coma (,) como separador decimal
    Ejemplo: 100,000.5 -> "100.000,5"
    """
    if pd.isna(num):
        return "0"
    
    if isinstance(num, (int, np.integer)):
        # Para enteros: usar punto como separador de miles
        return f"{int(num):,}".replace(',', '.')
    else:
        # Para decimales: punto para miles, coma para decimales
        # Primero formateamos con estilo US, luego intercambiamos
        formatted = f"{float(num):,.1f}".replace(',', 'TEMP').replace('.', ',').replace('TEMP', '.')
        return formatted

# ============================================================================
# CONFIGURACIÓN DE COLORES Y ESTILO
# ============================================================================

# Paleta de colores consistente para todo el análisis
COLORS = {
    'casual': '#FF6B6B',    # Rojo coral para usuarios casuales
    'member': '#4ECDC4'     # Turquesa para miembros anuales
}

# Etiquetas en español
LABELS = {
    'casual': 'Usuarios Casuales',
    'member': 'Miembros'
}

# Estilo general
plt.style.use('seaborn-v0_8-whitegrid')
sns.set_palette("husl")
plt.rcParams['font.size'] = 14  
plt.rcParams['axes.titlesize'] = 18 
plt.rcParams['axes.titleweight'] = 'bold'
plt.rcParams['axes.labelsize'] = 14  # Tamaño de etiquetas de ejes
plt.rcParams['xtick.labelsize'] = 13  # Tamaño de números en eje X
plt.rcParams['ytick.labelsize'] = 13  # Tamaño de números en eje Y
plt.rcParams['legend.fontsize'] = 13  # Tamaño de leyenda

# Configurar formato de números en ejes (punto para miles)
from matplotlib.ticker import FuncFormatter

def format_axis_latin(x, pos):
    """Formatea números en ejes al estilo latinoamericano"""
    if x >= 1000:
        return f'{int(x):,}'.replace(',', '.')
    else:
        return f'{int(x)}'

# Crear el formateador para usar en gráficos
latin_formatter = FuncFormatter(format_axis_latin)

# ============================================================================
# 1. CARGAR Y EXPLORAR DATOS
# ============================================================================

print("=" * 80)
print("ANÁLISIS DE CYCLISTIC BIKE-SHARE")
print("=" * 80)
print("\n1. Cargando datos...")

# Cargar el archivo
df = pd.read_csv('cyclistic_final_clean_data.csv')

# Convertir columnas de fecha
df['started_at'] = pd.to_datetime(df['started_at'])
df['ended_at'] = pd.to_datetime(df['ended_at'])

# Extraer información temporal adicional
df['hour'] = df['started_at'].dt.hour
df['month'] = df['started_at'].dt.month
df['month_name'] = df['started_at'].dt.month_name()
df['date'] = df['started_at'].dt.date

# Convertir ride_length a minutos
if df['ride_length'].dtype == 'object':
    df['ride_length_minutes'] = pd.to_timedelta(df['ride_length']).dt.total_seconds() / 60
else:
    df['ride_length_minutes'] = df['ride_length'] / 60

print(f"\nDatos cargados exitosamente!")
print(f"Total de viajes: {format_number(len(df))}")
print(f"Período: {df['started_at'].min().date()} a {df['started_at'].max().date()}")
print(f"\nPrimeras filas:")
print(df.head())

print(f"\nInformación del dataset:")
print(df.info())

# ============================================================================
# 2. ANÁLISIS DESCRIPTIVO POR TIPO DE USUARIO
# ============================================================================

print("\n" + "=" * 80)
print("2. ANÁLISIS DESCRIPTIVO POR TIPO DE USUARIO")
print("=" * 80)

user_counts = df['member_casual'].value_counts()
user_percentages = df['member_casual'].value_counts(normalize=True) * 100

print("\n📊 Distribución de usuarios:")
for user_type in user_counts.index:
    print(f"  {user_type}: {format_number(user_counts[user_type])} viajes ({user_percentages[user_type]:.1f}%)".replace('.', ',', 1))

print("\n⏱️  Estadísticas de duración de viajes (en minutos):")
print(df.groupby('member_casual')['ride_length_minutes'].describe())

# ============================================================================
# 3. ANÁLISIS POR DÍA DE LA SEMANA
# ============================================================================

print("\n" + "=" * 80)
print("3. ANÁLISIS POR DÍA DE LA SEMANA")
print("=" * 80)

day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
day_order_es = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']

# Mapeo de días en inglés a español
day_translation = {
    'Monday': 'Lunes',
    'Tuesday': 'Martes', 
    'Wednesday': 'Miércoles',
    'Thursday': 'Jueves',
    'Friday': 'Viernes',
    'Saturday': 'Sábado',
    'Sunday': 'Domingo'
}

trips_by_day = df.groupby(['day_of_week', 'member_casual']).size().unstack(fill_value=0)

print("\n📅 Viajes por día de la semana:")
print(trips_by_day)

avg_duration_by_day = df.groupby(['day_of_week', 'member_casual'])['ride_length_minutes'].mean().unstack()

print("\n⏱️  Duración promedio (minutos) por día:")
print(avg_duration_by_day.round(2))

# ============================================================================
# 4. ANÁLISIS POR HORA DEL DÍA
# ============================================================================

print("\n" + "=" * 80)
print("4. ANÁLISIS POR HORA DEL DÍA")
print("=" * 80)

trips_by_hour = df.groupby(['hour', 'member_casual']).size().unstack(fill_value=0)

print("\n🕐 Horas pico por tipo de usuario:")
for user_type in ['casual', 'member']:
    if user_type in trips_by_hour.columns:
        peak_hour = trips_by_hour[user_type].idxmax()
        peak_count = trips_by_hour[user_type].max()
        print(f"  {user_type}: Hora {peak_hour}:00 ({format_number(peak_count)} viajes)")

# ============================================================================
# 5. ANÁLISIS POR MES
# ============================================================================

print("\n" + "=" * 80)
print("5. ANÁLISIS POR MES")
print("=" * 80)

trips_by_month = df.groupby(['month', 'member_casual']).size().unstack(fill_value=0)

print("\n📆 Viajes por mes:")
print(trips_by_month)

# ============================================================================
# 6. ANÁLISIS DE ESTACIONES MÁS POPULARES
# ============================================================================

print("\n" + "=" * 80)
print("6. ESTACIONES MÁS POPULARES")
print("=" * 80)

print("\n🚲 Top 5 estaciones de inicio - CASUAL:")
casual_top_start = df[df['member_casual'] == 'casual']['start_station_name'].value_counts().head(5)
for i, (station, count) in enumerate(casual_top_start.items(), 1):
    print(f"  {i}. {station}: {format_number(count)} viajes")

print("\n🚲 Top 5 estaciones de inicio - MEMBER:")
member_top_start = df[df['member_casual'] == 'member']['start_station_name'].value_counts().head(5)
for i, (station, count) in enumerate(member_top_start.items(), 1):
    print(f"  {i}. {station}: {format_number(count)} viajes")

# ============================================================================
# 7. CREAR VISUALIZACIONES INDIVIDUALES
# ============================================================================

print("\n" + "=" * 80)
print("7. GENERANDO VISUALIZACIONES...")
print("=" * 80)

# Preparar datos para ordenar días de la semana
day_mapping = {day: i for i, day in enumerate(day_order)}

# ----- GRÁFICO 1: Distribución de usuarios -----
print("   Generando: 01_distribucion_usuarios.png")
fig, ax = plt.subplots(figsize=(12, 8))

# Preparar datos para el pie chart
labels_list = [LABELS[user_type] for user_type in user_counts.index]
colors_list = [COLORS[user_type] for user_type in user_counts.index]
sizes = user_counts.values
percentages = user_percentages.values

# Función para formatear porcentajes con coma decimal
def format_pct(pct):
    return f'{pct:.1f}%'.replace('.', ',')

# Crear el pie chart con etiquetas desplazadas
wedges, texts, autotexts = ax.pie(sizes, labels=labels_list, colors=colors_list, 
                                    autopct=lambda pct: format_pct(pct),
                                    startangle=90,
                                    textprops={'fontsize': 16, 'weight': 'bold'},
                                    wedgeprops={'edgecolor': 'white', 'linewidth': 2},
                                    labeldistance=1.15)  # Alejamos las etiquetas del centro

# Mejorar el formato de los porcentajes
for autotext in autotexts:
    autotext.set_color('white')
    autotext.set_fontsize(18)
    autotext.set_weight('bold')

# Añadir el conteo de viajes en la leyenda - posición abajo
legend_labels = [f'{labels_list[i]}: {format_number(sizes[i])} viajes' for i in range(len(labels_list))]
ax.legend(legend_labels, loc='upper center', bbox_to_anchor=(0.5, -0.05), 
          fontsize=14, frameon=True, shadow=True, ncol=2)

ax.set_title('Distribución de Tipos de Usuario', pad=20, fontsize=20, fontweight='bold')

plt.tight_layout()
plt.savefig('01_distribucion_usuarios.png', dpi=300, bbox_inches='tight')
plt.close()

# ----- GRÁFICO 2: Duración promedio de viajes -----
print("   Generando: 02_duracion_promedio.png")
fig, ax = plt.subplots(figsize=(10, 6))
avg_duration = df.groupby('member_casual')['ride_length_minutes'].mean()
colors_list = [COLORS[user_type] for user_type in avg_duration.index]
labels_list = [LABELS[user_type] for user_type in avg_duration.index]
bars = ax.bar(labels_list, avg_duration.values, color=colors_list, edgecolor='black', linewidth=1.5)
ax.set_title('Duración Promedio de Viajes por Tipo de Usuario', pad=20, fontsize=18)
ax.set_xlabel('Tipo de Usuario', fontsize=15)
ax.set_ylabel('Duración Promedio (minutos)', fontsize=15)
ax.tick_params(axis='x', labelsize=14)
ax.tick_params(axis='y', labelsize=13)
for bar, value in zip(bars, avg_duration.values):
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2., height,
            f'{format_number(value)} min',
            ha='center', va='bottom', fontweight='bold', fontsize=14)
plt.tight_layout()
plt.savefig('02_duracion_promedio.png', dpi=300, bbox_inches='tight')
plt.close()

# ----- GRÁFICO 3: Viajes por día de la semana -----
print("   Generando: 03_viajes_por_dia.png")
fig, ax = plt.subplots(figsize=(12, 6))
trips_by_day_plot = df.groupby(['day_of_week', 'member_casual']).size().unstack()
if trips_by_day_plot.index.dtype == 'object':
    trips_by_day_plot['sort_key'] = trips_by_day_plot.index.map(day_mapping)
    trips_by_day_plot = trips_by_day_plot.sort_values('sort_key').drop('sort_key', axis=1)

# Traducir los índices a español
trips_by_day_plot.index = trips_by_day_plot.index.map(day_translation)

x = np.arange(len(trips_by_day_plot.index))
width = 0.35
bars1 = ax.bar(x - width/2, trips_by_day_plot['casual'], width, 
               label='Usuarios Casuales', color=COLORS['casual'], edgecolor='black', linewidth=1)
bars2 = ax.bar(x + width/2, trips_by_day_plot['member'], width,
               label='Miembros', color=COLORS['member'], edgecolor='black', linewidth=1)

ax.set_title('Número de Viajes por Día de la Semana', pad=20, fontsize=18)
ax.set_xlabel('Día de la Semana', fontsize=15)
ax.set_ylabel('Número de Viajes', fontsize=15)
ax.set_xticks(x)
ax.set_xticklabels(trips_by_day_plot.index, rotation=45, ha='right', fontsize=13)
ax.tick_params(axis='y', labelsize=13)
ax.yaxis.set_major_formatter(latin_formatter)  # Formato latinoamericano en eje Y
ax.legend(fontsize=14, frameon=True, shadow=True)
ax.grid(axis='y', alpha=0.3)
plt.tight_layout()
plt.savefig('03_viajes_por_dia.png', dpi=300, bbox_inches='tight')
plt.close()

# ----- GRÁFICO 4: Duración promedio por día -----
print("   Generando: 04_duracion_por_dia.png")
fig, ax = plt.subplots(figsize=(12, 6))
avg_duration_day = df.groupby(['day_of_week', 'member_casual'])['ride_length_minutes'].mean().unstack()
if avg_duration_day.index.dtype == 'object':
    avg_duration_day['sort_key'] = avg_duration_day.index.map(day_mapping)
    avg_duration_day = avg_duration_day.sort_values('sort_key').drop('sort_key', axis=1)

# Traducir los índices a español
avg_duration_day.index = avg_duration_day.index.map(day_translation)

ax.plot(avg_duration_day.index, avg_duration_day['casual'], 
        marker='o', linewidth=3, markersize=10, 
        label='Usuarios Casuales', color=COLORS['casual'])
ax.plot(avg_duration_day.index, avg_duration_day['member'], 
        marker='s', linewidth=3, markersize=10,
        label='Miembros', color=COLORS['member'])

ax.set_title('Duración Promedio de Viajes por Día de la Semana', pad=20, fontsize=18)
ax.set_xlabel('Día de la Semana', fontsize=15)
ax.set_ylabel('Duración Promedio (minutos)', fontsize=15)
plt.xticks(rotation=45, ha='right', fontsize=13)
ax.tick_params(axis='y', labelsize=13)
ax.legend(fontsize=14, frameon=True, shadow=True)
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('04_duracion_por_dia.png', dpi=300, bbox_inches='tight')
plt.close()

# ----- GRÁFICO 5: Viajes por hora del día -----
print("   Generando: 05_viajes_por_hora.png")
fig, ax = plt.subplots(figsize=(14, 6))
ax.plot(trips_by_hour.index, trips_by_hour['casual'], 
        marker='o', linewidth=3, markersize=8,
        label='Usuarios Casuales', color=COLORS['casual'])
ax.plot(trips_by_hour.index, trips_by_hour['member'], 
        marker='s', linewidth=3, markersize=8,
        label='Miembros', color=COLORS['member'])

ax.set_title('Número de Viajes por Hora del Día', pad=20, fontsize=18)
ax.set_xlabel('Hora del Día', fontsize=15)
ax.set_ylabel('Número de Viajes', fontsize=15)
ax.set_xticks(range(0, 24))
ax.tick_params(axis='both', labelsize=13)
ax.yaxis.set_major_formatter(latin_formatter)  # Formato latinoamericano en eje Y
ax.legend(fontsize=14, frameon=True, shadow=True)
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('05_viajes_por_hora.png', dpi=300, bbox_inches='tight')
plt.close()

# ----- GRÁFICO 6: Distribución de duración de viajes -----
print("   Generando: 06_distribucion_duracion.png")
fig, ax = plt.subplots(figsize=(12, 6))
df_filtered = df[df['ride_length_minutes'] <= 60]
casual_data = df_filtered[df_filtered['member_casual'] == 'casual']['ride_length_minutes']
member_data = df_filtered[df_filtered['member_casual'] == 'member']['ride_length_minutes']

ax.hist(casual_data, bins=30, alpha=0.7, label='Usuarios Casuales', 
        color=COLORS['casual'], edgecolor='black', linewidth=0.5)
ax.hist(member_data, bins=30, alpha=0.7, label='Miembros', 
        color=COLORS['member'], edgecolor='black', linewidth=0.5)

ax.set_title('Distribución de Duración de Viajes (≤60 minutos)', pad=20, fontsize=18)
ax.set_xlabel('Duración (minutos)', fontsize=15)
ax.set_ylabel('Frecuencia', fontsize=15)
ax.tick_params(axis='both', labelsize=13)
ax.legend(fontsize=14, frameon=True, shadow=True)
ax.grid(axis='y', alpha=0.3)
plt.tight_layout()
plt.savefig('06_distribucion_duracion.png', dpi=300, bbox_inches='tight')
plt.close()

# ----- GRÁFICO 7: Viajes por mes -----
print("   Generando: 07_viajes_por_mes.png")
fig, ax = plt.subplots(figsize=(12, 6))
x = np.arange(len(trips_by_month.index))
width = 0.35
bars1 = ax.bar(x - width/2, trips_by_month['casual'], width,
               label='Usuarios Casuales', color=COLORS['casual'], edgecolor='black', linewidth=1)
bars2 = ax.bar(x + width/2, trips_by_month['member'], width,
               label='Miembros', color=COLORS['member'], edgecolor='black', linewidth=1)

ax.set_title('Número de Viajes por Mes', pad=20, fontsize=18)
ax.set_xlabel('Mes', fontsize=15)
ax.set_ylabel('Número de Viajes', fontsize=15)
ax.set_xticks(x)
ax.set_xticklabels(trips_by_month.index, fontsize=13)
ax.tick_params(axis='y', labelsize=13)
ax.yaxis.set_major_formatter(latin_formatter)  # Formato latinoamericano en eje Y
ax.legend(fontsize=14, frameon=True, shadow=True)
ax.grid(axis='y', alpha=0.3)
plt.tight_layout()
plt.savefig('07_viajes_por_mes.png', dpi=300, bbox_inches='tight')
plt.close()

# ----- GRÁFICO 8: Distribución porcentual por día -----
print("   Generando: 08_distribucion_porcentual_dia.png")
fig, ax = plt.subplots(figsize=(12, 6))
trips_pct = trips_by_day_plot.div(trips_by_day_plot.sum(axis=0), axis=1) * 100

x = np.arange(len(trips_pct.index))
width = 0.35
bars1 = ax.bar(x - width/2, trips_pct['casual'], width,
               label='Usuarios Casuales', color=COLORS['casual'], edgecolor='black', linewidth=1)
bars2 = ax.bar(x + width/2, trips_pct['member'], width,
               label='Miembros', color=COLORS['member'], edgecolor='black', linewidth=1)

ax.set_title('Distribución Porcentual de Viajes por Día de la Semana', pad=20, fontsize=18)
ax.set_xlabel('Día de la Semana', fontsize=15)
ax.set_ylabel('Porcentaje del Total de Viajes (%)', fontsize=15)
ax.set_xticks(x)
ax.set_xticklabels(trips_pct.index, rotation=45, ha='right', fontsize=13)
ax.tick_params(axis='y', labelsize=13)
ax.legend(fontsize=14, frameon=True, shadow=True)
ax.grid(axis='y', alpha=0.3)
plt.tight_layout()
plt.savefig('08_distribucion_porcentual_dia.png', dpi=300, bbox_inches='tight')
plt.close()

# ----- GRÁFICO 9: Comparación de métricas clave -----
print("   Generando: 09_metricas_clave.png")
fig, ax = plt.subplots(figsize=(10, 6))
avg_duration_metric = df.groupby('member_casual')['ride_length_minutes'].mean()
avg_trips_per_day = df.groupby(['member_casual', 'date']).size().groupby('member_casual').mean()

x = np.arange(2)
width = 0.35

# Normalizar para visualización (usando escalas diferentes)
duration_normalized = avg_duration_metric / avg_duration_metric.max() * 100
trips_normalized = avg_trips_per_day / avg_trips_per_day.max() * 100

bars1 = ax.bar(x - width/2, duration_normalized.values, width,
               label='Duración Promedio (normalizado)', 
               color=[COLORS['casual'], COLORS['member']], 
               edgecolor='black', linewidth=1, alpha=0.7)
bars2 = ax.bar(x + width/2, trips_normalized.values, width,
               label='Viajes Promedio/Día (normalizado)',
               color=[COLORS['casual'], COLORS['member']], 
               edgecolor='black', linewidth=1, alpha=0.4, hatch='//')

ax.set_title('Comparación de Métricas Clave (valores normalizados)', pad=20, fontsize=18)
ax.set_ylabel('Valor Normalizado (100 = máximo)', fontsize=15)
ax.set_xticks(x)
ax.set_xticklabels(['Usuarios Casuales', 'Miembros'], fontsize=14)
ax.tick_params(axis='y', labelsize=13)
ax.legend(fontsize=12, frameon=True, shadow=True)
ax.grid(axis='y', alpha=0.3)

# Añadir valores reales como texto
for i, (dur, trip) in enumerate(zip(avg_duration_metric.values, avg_trips_per_day.values)):
    ax.text(i - width/2, duration_normalized.values[i] + 2,
            f'{format_number(dur)} min', ha='center', fontsize=12, fontweight='bold')
    ax.text(i + width/2, trips_normalized.values[i] + 2,
            f'{format_number(int(trip))} viajes', ha='center', fontsize=12, fontweight='bold')

plt.tight_layout()
plt.savefig('09_metricas_clave.png', dpi=300, bbox_inches='tight')
plt.close()

# ----- GRÁFICO 10: Comparación fin de semana vs días laborales -----
print("   Generando: 10_weekend_vs_weekday.png")
fig, ax = plt.subplots(figsize=(10, 6))

# Calcular proporciones
casual_weekend = df[(df['member_casual'] == 'casual') & 
                     (df['day_of_week'].isin(['Saturday', 'Sunday']))].shape[0]
casual_weekday = df[(df['member_casual'] == 'casual') & 
                     (~df['day_of_week'].isin(['Saturday', 'Sunday']))].shape[0]

member_weekend = df[(df['member_casual'] == 'member') & 
                     (df['day_of_week'].isin(['Saturday', 'Sunday']))].shape[0]
member_weekday = df[(df['member_casual'] == 'member') & 
                     (~df['day_of_week'].isin(['Saturday', 'Sunday']))].shape[0]

categories = ['Usuarios Casuales', 'Miembros']
weekend_data = [casual_weekend, member_weekend]
weekday_data = [casual_weekday, member_weekday]

x = np.arange(len(categories))
width = 0.35

bars1 = ax.bar(x - width/2, weekday_data, width, label='Días laborales',
               color=[COLORS['casual'], COLORS['member']], 
               edgecolor='black', linewidth=1, alpha=0.7)
bars2 = ax.bar(x + width/2, weekend_data, width, label='Fin de semana',
               color=[COLORS['casual'], COLORS['member']], 
               edgecolor='black', linewidth=1, alpha=0.4, hatch='///')

ax.set_title('Viajes: Días Laborales vs Fin de Semana', pad=20, fontsize=18)
ax.set_ylabel('Número de Viajes', fontsize=15)
ax.set_xticks(x)
ax.set_xticklabels(categories, fontsize=14)
ax.tick_params(axis='y', labelsize=13)
ax.yaxis.set_major_formatter(latin_formatter)  # Formato latinoamericano en eje Y
ax.legend(fontsize=14, frameon=True, shadow=True)
ax.grid(axis='y', alpha=0.3)

# Añadir porcentajes
for i, (wd, we) in enumerate(zip(weekday_data, weekend_data)):
    total = wd + we
    wd_pct = (wd / total) * 100
    we_pct = (we / total) * 100
    ax.text(i - width/2, wd + wd*0.02, f'{wd_pct:.1f}%'.replace('.', ','), 
            ha='center', fontsize=12, fontweight='bold')
    ax.text(i + width/2, we + we*0.02, f'{we_pct:.1f}%'.replace('.', ','),
            ha='center', fontsize=12, fontweight='bold')

plt.tight_layout()
plt.savefig('10_weekend_vs_weekday.png', dpi=300, bbox_inches='tight')
plt.close()

print("\n✅ Todas las visualizaciones han sido generadas exitosamente!")
print("\nArchivos creados:")
print("   • 01_distribucion_usuarios.png")
print("   • 02_duracion_promedio.png")
print("   • 03_viajes_por_dia.png")
print("   • 04_duracion_por_dia.png")
print("   • 05_viajes_por_hora.png")
print("   • 06_distribucion_duracion.png")
print("   • 07_viajes_por_mes.png")
print("   • 08_distribucion_porcentual_dia.png")
print("   • 09_metricas_clave.png")
print("   • 10_weekend_vs_weekday.png")

# ============================================================================
# 8. INSIGHTS Y HALLAZGOS CLAVE
# ============================================================================

print("\n" + "=" * 80)
print("8. HALLAZGOS CLAVE")
print("=" * 80)

casual_avg_duration = df[df['member_casual'] == 'casual']['ride_length_minutes'].mean()
member_avg_duration = df[df['member_casual'] == 'member']['ride_length_minutes'].mean()
duration_diff = ((casual_avg_duration - member_avg_duration) / member_avg_duration) * 100

casual_peak_day = trips_by_day['casual'].idxmax()
member_peak_day = trips_by_day['member'].idxmax()

casual_weekend_pct = (casual_weekend / (casual_weekend + casual_weekday)) * 100
member_weekend_pct = (member_weekend / (member_weekend + member_weekday)) * 100

print("\n🔍 INSIGHTS PRINCIPALES:\n")

print("1. DURACIÓN DE VIAJES:")
print(f"   • Usuarios casuales: {format_number(casual_avg_duration)} minutos promedio")
print(f"   • Miembros anuales: {format_number(member_avg_duration)} minutos promedio")
print(f"   • Los usuarios casuales viajan {format_number(int(duration_diff))}% más tiempo que los miembros\n")

print("2. PATRONES DE USO SEMANAL:")
print(f"   • Día más popular - Casuales: {casual_peak_day}")
print(f"   • Día más popular - Miembros: {member_peak_day}")
print(f"   • Uso en fin de semana - Casuales: {casual_weekend_pct:.1f}%".replace('.', ','))
print(f"   • Uso en fin de semana - Miembros: {member_weekend_pct:.1f}%\n".replace('.', ','))

print("3. DIFERENCIAS CLAVE:")
print(f"   • Los casuales usan más las bicicletas en fines de semana (ocio/recreación)")
print(f"   • Los miembros muestran uso más distribuido durante la semana (commuting/trabajo)")
print(f"   • Los casuales hacen viajes más largos pero menos frecuentes")
print(f"   • Los miembros hacen viajes más cortos pero más consistentes")

print("\n" + "=" * 80)
print("🎨 PALETA DE COLORES UTILIZADA:")
print(f"   • Usuarios Casuales: {COLORS['casual']} (Rojo coral)")
print(f"   • Miembros: {COLORS['member']} (Turquesa)")
print("=" * 80)

print("\n" + "=" * 80)
print("ANÁLISIS COMPLETADO")
print("=" * 80)
