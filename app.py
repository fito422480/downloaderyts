import streamlit as st
import requests
from bs4 import BeautifulSoup
import subprocess

st.set_page_config(page_title="YTS Torrent Downloader", page_icon="🎬", layout="centered")

st.title("🎬 Descargador de Torrents desde YTS.mx")

def buscar_peliculas(nombre):
    nombre_formateado = nombre.replace(" ", "+")
    url = f"https://yts.mx/browse-movies/{nombre_formateado}/all/all/0/latest"
    headers = {"User-Agent": "Mozilla/5.0"}

    res = requests.get(url, headers=headers)
    soup = BeautifulSoup(res.text, "html.parser")
    peliculas = soup.select(".browse-movie-wrap")

    resultados = []
    for p in peliculas:
        try:
            titulo = p.select_one(".browse-movie-title").text
            anio = p.select_one(".browse-movie-year").text
            url_detalle = p.select_one("a.browse-movie-link")["href"]
            resultados.append({"titulo": f"{titulo} ({anio})", "url": url_detalle})
        except:
            continue
    return resultados

def obtener_magnets(url_pelicula):
    headers = {"User-Agent": "Mozilla/5.0"}
    res = requests.get(url_pelicula, headers=headers)
    soup = BeautifulSoup(res.text, "html.parser")

    links = soup.select("a[href^=magnet]")
    resultados = []
    for link in links:
        calidad = link.find_parent("p").text if link.find_parent("p") else "Desconocida"
        resultados.append({"calidad": calidad.strip(), "magnet": link["href"]})
    return resultados

def descargar(magnet_link):
    try:
        subprocess.Popen(["qbittorrent", magnet_link])
        st.success("¡Descarga iniciada con qBittorrent!")
    except Exception as e:
        st.error(f"Error al lanzar qBittorrent: {e}")

# ================== UI ==================

busqueda = st.text_input("🔍 Buscar película en YTS.mx")

if busqueda:
    with st.spinner("Buscando películas..."):
        peliculas = buscar_peliculas(busqueda)

    if not peliculas:
        st.warning("No se encontraron resultados.")
    else:
        for peli in peliculas[:5]:  # Mostrar solo los 5 primeros
            with st.expander(peli["titulo"]):
                opciones = obtener_magnets(peli["url"])
                for op in opciones:
                    col1, col2 = st.columns([4, 1])
                    with col1:
                        st.markdown(f"- 🎞️ **{op['calidad']}**")
                    with col2:
                        if st.button("Descargar", key=op["magnet"]):
                            descargar(op["magnet"])

