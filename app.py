import streamlit as st
import requests
from bs4 import BeautifulSoup
import subprocess
import webbrowser

st.set_page_config(page_title="YTS Torrent Downloader", page_icon="🎬", layout="centered")

st.title("🎬 Descargador de Torrents desde YTS.mx")

def buscar_peliculas(nombre):
    nombre_formateado = nombre.replace(" ", "+")
    url = f"https://yts.mx/browse-movies/{nombre_formateado}/all/all/0/latest/0/all"
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        res = requests.get(url, headers=headers)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, "html.parser")
        peliculas = soup.select(".browse-movie-wrap")

        resultados = []
        for p in peliculas:
            try:
                titulo = p.select_one(".browse-movie-title").text
                anio = p.select_one(".browse-movie-year").text
                url_detalle = p.select_one("a.browse-movie-link")["href"]
                portada = p.select_one("img.img-responsive")["src"]
                resultados.append({
                    "titulo": f"{titulo} ({anio})", 
                    "url": url_detalle,
                    "portada": portada
                })
            except Exception as e:
                print(f"Error procesando película: {e}")
                continue
        return resultados
    except Exception as e:
        st.error(f"Error al buscar películas: {e}")
        return []

def obtener_magnets(url_pelicula):
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        res = requests.get(url_pelicula, headers=headers)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, "html.parser")

        # Buscar enlaces magnet y torrent
        magnets = soup.select("a[href^=magnet]")
        torrents = soup.select("a[href$=.torrent]")
        
        resultados = []
        
        # Procesar enlaces magnet
        for link in magnets:
            try:
                calidad_element = link.find_previous("span", class_="quality")
                calidad = calidad_element.text if calidad_element else "Desconocida"
                tamaño_element = link.find_next("span", class_="size")
                tamaño = tamaño_element.text if tamaño_element else ""
                resultados.append({
                    "tipo": "magnet",
                    "calidad": calidad.strip(),
                    "tamaño": tamaño.strip(),
                    "enlace": link["href"]
                })
            except Exception as e:
                print(f"Error procesando magnet: {e}")
                continue
        
        # Procesar enlaces torrent
        for link in torrents:
            try:
                calidad_element = link.find_previous("span", class_="quality")
                calidad = calidad_element.text if calidad_element else "Desconocida"
                tamaño_element = link.find_next("span", class_="size")
                tamaño = tamaño_element.text if tamaño_element else ""
                resultados.append({
                    "tipo": "torrent",
                    "calidad": calidad.strip(),
                    "tamaño": tamaño.strip(),
                    "enlace": link["href"]
                })
            except Exception as e:
                print(f"Error procesando torrent: {e}")
                continue
        
        return resultados
    except Exception as e:
        st.error(f"Error al obtener enlaces: {e}")
        return []

def descargar_con_qbittorrent(enlace):
    try:
        subprocess.Popen(["qbittorrent", enlace])
        st.success("¡Descarga iniciada con qBittorrent!")
    except Exception as e:
        st.error(f"Error al lanzar qBittorrent: {e}")
        st.info("Puedes copiar el enlace manualmente y pegarlo en tu cliente de torrents.")

# ================== UI ==================

busqueda = st.text_input("🔍 Buscar película en YTS.mx", key="busqueda")

if busqueda:
    with st.spinner("Buscando películas..."):
        peliculas = buscar_peliculas(busqueda)

    if not peliculas:
        st.warning("No se encontraron resultados.")
    else:
        st.subheader(f"Resultados para: {busqueda}")
        
        for peli in peliculas[:5]:  # Mostrar solo los 5 primeros
            with st.expander(peli["titulo"]):
                col1, col2 = st.columns([1, 3])
                with col1:
                    st.image(peli["portada"], width=150)
                with col2:
                    st.write(f"**Título:** {peli['titulo']}")
                
                st.markdown("---")
                st.subheader("Opciones de descarga")
                
                with st.spinner("Obteniendo enlaces..."):
                    opciones = obtener_magnets(peli["url"])
                
                if not opciones:
                    st.warning("No se encontraron enlaces de descarga.")
                else:
                    for op in opciones:
                        col1, col2, col3 = st.columns([3, 2, 2])
                        with col1:
                            st.markdown(f"**🎞️ Calidad:** {op['calidad']}")
                            st.markdown(f"**📦 Tamaño:** {op['tamaño']}")
                            st.markdown(f"**🔗 Tipo:** {op['tipo'].upper()}")
                        with col2:
                            # Mostrar el enlace acortado
                            enlace_corto = op['enlace'][:50] + "..." if len(op['enlace']) > 50 else op['enlace']
                            st.text(enlace_corto)
                        with col3:
                            if op['tipo'] == 'magnet':
                                if st.button("Descargar Magnet", key=op["enlace"]):
                                    descargar_con_qbittorrent(op["enlace"])
                            else:
                                if st.button("Descargar Torrent", key=op["enlace"]):
                                    webbrowser.open_new_tab(op["enlace"])
                        
                        st.markdown("---")
