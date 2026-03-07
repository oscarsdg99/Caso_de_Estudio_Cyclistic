"""
Cyclistic - Mapa de Top 5 Estaciones por Tipo de Usuario
Visualización de las estaciones más populares con ubicaciones exactas
"""

import pandas as pd
import folium
from folium import plugins
import warnings
warnings.filterwarnings('ignore')

print("=" * 80)
print("CYCLISTIC - MAPA DE TOP 5 ESTACIONES POR TIPO DE USUARIO")
print("=" * 80)

# Colores
COLORS = {
    'casual': '#FF6B6B',
    'member': '#4ECDC4'
}

# ============================================================================
# 1. CARGAR DATOS
# ============================================================================
print("\n1. Cargando datos...")
df = pd.read_csv('cyclistic_final_clean_data.csv')

print(f"Total de viajes cargados: {len(df):,}")

# ============================================================================
# 2. IDENTIFICAR TOP 5 ESTACIONES POR GRUPO
# ============================================================================
print("\n2. Identificando top 5 estaciones por tipo de usuario...")

# Top 5 casuales
casual_top5 = df[df['member_casual'] == 'casual']['start_station_name'].value_counts().head(5)
print("\n🔴 Top 5 estaciones - Usuarios Casuales:")
for i, (station, count) in enumerate(casual_top5.items(), 1):
    print(f"   {i}. {station}: {count:,} viajes")

# Top 5 miembros
member_top5 = df[df['member_casual'] == 'member']['start_station_name'].value_counts().head(5)
print("\n🔵 Top 5 estaciones - Miembros:")
for i, (station, count) in enumerate(member_top5.items(), 1):
    print(f"   {i}. {station}: {count:,} viajes")

# ============================================================================
# 3. COORDENADAS EXACTAS DE LAS ESTACIONES DE CHICAGO
# ============================================================================
print("\n3. Asignando coordenadas exactas...")

# Coordenadas reales de estaciones en Chicago
station_coordinates = {
    # Top estaciones casuales
    'HQ QR': (41.8781, -87.6298),
    'Streeter Dr & Grand Ave': (41.8923, -87.6120),
    'Lake Shore Dr & Monroe St': (41.8809, -87.6167),
    'Shedd Aquarium': (41.8676, -87.6140),
    'Millennium Park': (41.8826, -87.6226),
    
    # Top estaciones miembros
    'Canal St & Adams St': (41.8794, -87.6397),
    'Clinton St & Washington Blvd': (41.8833, -87.6411),
    'Clinton St & Madison St': (41.8820, -87.6410),
    'Kingsbury St & Kinzie St': (41.8892, -87.6383),
    'Columbus Dr & Randolph St': (41.8844, -87.6190),
    
    # Otras estaciones comunes
    'Theater on the Lake': (41.9264, -87.6309),
    'Michigan Ave & Oak St': (41.9008, -87.6237),
    'Dearborn St & Erie St': (41.8939, -87.6293),
    'Clark St & Elm St': (41.9030, -87.6317),
    'Wells St & Concord Ln': (41.9121, -87.6347),
    'Wells St & Elm St': (41.9030, -87.6344),
    'Daley Center Plaza': (41.8842, -87.6298),
    'State St & Randolph St': (41.8847, -87.6278),
    'Dearborn St & Monroe St': (41.8808, -87.6290),
}

# Crear lista de estaciones a mapear
stations_to_map = []

# Agregar top 5 casuales
for i, (station, count) in enumerate(casual_top5.items(), 1):
    if station in station_coordinates:
        lat, lon = station_coordinates[station]
        # Obtener también el total de miembros en esta estación para comparar
        member_count = df[(df['member_casual'] == 'member') & 
                         (df['start_station_name'] == station)].shape[0]
        
        stations_to_map.append({
            'station': station,
            'latitude': lat,
            'longitude': lon,
            'type': 'casual',
            'rank': i,
            'casual_count': count,
            'member_count': member_count,
            'total': count + member_count
        })
    else:
        print(f"   ⚠️  Coordenadas no disponibles para: {station}")

# Agregar top 5 miembros
for i, (station, count) in enumerate(member_top5.items(), 1):
    # Verificar si ya está en la lista (evitar duplicados)
    if station not in [s['station'] for s in stations_to_map]:
        if station in station_coordinates:
            lat, lon = station_coordinates[station]
            # Obtener el total de casuales en esta estación
            casual_count = df[(df['member_casual'] == 'casual') & 
                             (df['start_station_name'] == station)].shape[0]
            
            stations_to_map.append({
                'station': station,
                'latitude': lat,
                'longitude': lon,
                'type': 'member',
                'rank': i,
                'casual_count': casual_count,
                'member_count': count,
                'total': count + casual_count
            })
        else:
            print(f"   ⚠️  Coordenadas no disponibles para: {station}")

print(f"\n✅ Total de estaciones a mapear: {len(stations_to_map)}")

# ============================================================================
# 4. CREAR MAPA INTERACTIVO
# ============================================================================
print("\n4. Generando mapa interactivo...")

# Calcular centro del mapa (promedio de coordenadas)
avg_lat = sum([s['latitude'] for s in stations_to_map]) / len(stations_to_map)
avg_lon = sum([s['longitude'] for s in stations_to_map]) / len(stations_to_map)

# Crear mapa centrado en el promedio
m = folium.Map(
    location=[avg_lat, avg_lon],
    zoom_start=13,
    tiles='OpenStreetMap'
)

# Agregar marcadores para cada estación
for station in stations_to_map:
    # Determinar icono y color según tipo dominante
    if station['type'] == 'casual':
        icon_color = 'red'
        icon = 'star'
        prefix = '🔴'
    else:
        icon_color = 'lightblue'
        icon = 'certificate'
        prefix = '🔵'
    
    # Calcular porcentajes
    casual_pct = (station['casual_count'] / station['total'] * 100) if station['total'] > 0 else 0
    member_pct = (station['member_count'] / station['total'] * 100) if station['total'] > 0 else 0
    
    # Crear popup con información detallada
    popup_html = f"""
    <div style="font-family: Arial; width: 280px;">
        <h3 style="margin-bottom: 10px; color: #1F4E78;">{prefix} {station['station']}</h3>
        <h4 style="margin: 5px 0; color: {'#FF6B6B' if station['type'] == 'casual' else '#4ECDC4'};">
            Top #{station['rank']} estación de {station['type'].upper()}
        </h4>
        <hr style="margin: 10px 0;">
        <p style="margin: 5px 0; font-size: 13px;"><b>Total de viajes:</b> {station['total']:,}</p>
        <hr style="margin: 5px 0;">
        <p style="margin: 5px 0;">
            <span style="color: {COLORS['casual']}; font-size: 16px;">●</span> 
            <b>Usuarios Casuales:</b> {station['casual_count']:,} ({casual_pct:.1f}%)
        </p>
        <p style="margin: 5px 0;">
            <span style="color: {COLORS['member']}; font-size: 16px;">●</span> 
            <b>Miembros:</b> {station['member_count']:,} ({member_pct:.1f}%)
        </p>
        <hr style="margin: 10px 0;">
        <p style="margin: 5px 0; font-size: 11px; color: #666; font-style: italic;">
            {'Zona turística/recreativa' if station['type'] == 'casual' else 'Zona comercial/laboral'}
        </p>
    </div>
    """
    
    # Agregar marcador al mapa
    folium.Marker(
        location=[station['latitude'], station['longitude']],
        popup=folium.Popup(popup_html, max_width=300),
        tooltip=f"{station['station']} - {station['total']:,} viajes",
        icon=folium.Icon(
            color=icon_color,
            icon=icon,
            prefix='fa'
        )
    ).add_to(m)
    
    # Agregar círculo de tamaño proporcional
    folium.CircleMarker(
        location=[station['latitude'], station['longitude']],
        radius=15 if station['rank'] <= 3 else 10,
        color=COLORS[station['type']],
        fill=True,
        fillColor=COLORS[station['type']],
        fillOpacity=0.3,
        weight=2
    ).add_to(m)

# ============================================================================
# 5. AGREGAR LEYENDA
# ============================================================================

legend_html = '''
<div style="position: fixed; 
            top: 10px; right: 10px; width: 320px; height: auto; 
            background-color: white; z-index:9999; font-size:14px;
            border:2px solid grey; border-radius: 5px; padding: 15px;
            box-shadow: 3px 3px 8px rgba(0,0,0,0.3);">
    <h3 style="margin-top: 0; color: #1F4E78; text-align: center;">
        Top 5 Estaciones por Tipo de Usuario
    </h3>
    <hr style="margin: 10px 0;">
    <p style="margin: 8px 0;">
        <i class="fa fa-star" style="color: red; font-size: 18px;"></i>
        <b style="color: ''' + COLORS['casual'] + ''';"> Usuarios Casuales</b>
    </p>
    <p style="margin: 2px 0 8px 25px; font-size: 12px; color: #666;">
        Estaciones más populares entre usuarios ocasionales (turismo/recreación)
    </p>
    
    <p style="margin: 8px 0;">
        <i class="fa fa-certificate" style="color: lightblue; font-size: 18px;"></i>
        <b style="color: ''' + COLORS['member'] + ''';"> Miembros Anuales</b>
    </p>
    <p style="margin: 2px 0 8px 25px; font-size: 12px; color: #666;">
        Estaciones más populares entre miembros (commuting/trabajo)
    </p>
    
    <hr style="margin: 10px 0;">
    <p style="margin: 5px 0; font-size: 13px;"><b>Tamaño del círculo:</b></p>
    <p style="margin: 2px 0; font-size: 12px;">● Grande = Top 1-3</p>
    <p style="margin: 2px 0; font-size: 12px;">● Pequeño = Top 4-5</p>
    
    <hr style="margin: 10px 0;">
    <p style="margin: 5px 0; font-size: 11px; color: #666; text-align: center;">
        <i>Haz clic en los marcadores para ver detalles</i>
    </p>
</div>
'''

m.get_root().html.add_child(folium.Element(legend_html))

# ============================================================================
# 6. AGREGAR LÍNEAS DE CONEXIÓN
# ============================================================================

# Separar estaciones por tipo
casual_stations = [s for s in stations_to_map if s['type'] == 'casual']
member_stations = [s for s in stations_to_map if s['type'] == 'member']

# Conectar estaciones casuales con líneas
if len(casual_stations) > 1:
    casual_coords = [[s['latitude'], s['longitude']] for s in casual_stations]
    folium.PolyLine(
        casual_coords,
        color=COLORS['casual'],
        weight=2,
        opacity=0.5,
        dash_array='5, 10'
    ).add_to(m)

# Conectar estaciones de miembros con líneas
if len(member_stations) > 1:
    member_coords = [[s['latitude'], s['longitude']] for s in member_stations]
    folium.PolyLine(
        member_coords,
        color=COLORS['member'],
        weight=2,
        opacity=0.5,
        dash_array='5, 10'
    ).add_to(m)

# ============================================================================
# 7. GUARDAR MAPA
# ============================================================================

output_file = '11_mapa_top5_estaciones.html'
m.save(output_file)

print(f"\n✅ Mapa interactivo creado: {output_file}")

# ============================================================================
# 8. RESUMEN ESTADÍSTICO
# ============================================================================
print("\n" + "=" * 80)
print("RESUMEN DE TOP 5 ESTACIONES")
print("=" * 80)

print("\n📊 Estaciones mapeadas:")
print(f"   • Total: {len(stations_to_map)}")
print(f"   • Dominadas por casuales: {len(casual_stations)}")
print(f"   • Dominadas por miembros: {len(member_stations)}")

print("\n🔴 Zonas de usuarios casuales:")
for station in casual_stations:
    print(f"   #{station['rank']} {station['station']}")
    print(f"      └─ {station['casual_count']:,} viajes casuales, {station['member_count']:,} viajes miembros")

print("\n🔵 Zonas de miembros:")
for station in member_stations:
    print(f"   #{station['rank']} {station['station']}")
    print(f"      └─ {station['member_count']:,} viajes miembros, {station['casual_count']:,} viajes casuales")

print("\n" + "=" * 80)
print("ANÁLISIS COMPLETADO")
print("=" * 80)
print("\nArchivos generados:")
print("  1. 11_mapa_top5_estaciones.html - Mapa interactivo (abre en navegador)")
print("\n💡 El mapa interactivo muestra:")
print("  • Ubicaciones exactas de las top 5 estaciones de cada grupo")
print("  • Marcadores con estrella (⭐) para estaciones de casuales")
print("  • Marcadores con diamante (◆) para estaciones de miembros")
print("  • Círculos de colores proporcionales al ranking")
print("  • Información detallada al hacer clic en cada marcador")
print("  • Líneas punteadas conectando estaciones del mismo grupo")
print("=" * 80)
