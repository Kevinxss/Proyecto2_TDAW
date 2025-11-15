// js/favoritos.js

const API_URL = "http://10.96.17.30:5000"; // (Usa la IP que corresponda)
const POKEAPI_URL = "https://pokeapi.co/api/v2/pokemon";

// 1. Verificar sesión (¡Igual que en index.js!)
document.addEventListener("DOMContentLoaded", async () => {
    try {
        const res = await fetch(`${API_URL}/api/perfil`, {
            method: "GET",
            credentials: "include"
        });
        if (!res.ok) throw new Error("Sesión no válida");
        
        // Si la sesión es válida, cargar los favoritos
        cargarFavoritos();
    } catch (error) {
        alert("Debes iniciar sesión primero.");
        window.location.href = "login.html";
    }
});

// 2. Cargar los favoritos
async function cargarFavoritos() {
    const contenedor = document.getElementById("favoritos-container");
    contenedor.innerHTML = ""; // Limpiar "Cargando..."
    
    try {
        const res = await fetch(`${API_URL}/api/favoritos`, {
            method: "GET",
            credentials: "include"
        });
        const data = await res.json();

        if (!data.exito || data.favoritos.length === 0) {
            contenedor.innerHTML = "<p>No tienes ningún Pokémon favorito.</p>";
            return;
        }

        // data.favoritos es una lista: [{'id_pokemon': 25}, {'id_pokemon': 4}]
        // Debemos buscar los detalles de CADA uno en la PokéAPI
        for (let item of data.favoritos) {
            const pokeRes = await fetch(`${POKEAPI_URL}/${item.id_pokemon}`);
            if (pokeRes.ok) {
                const pokeData = await pokeRes.json();
                const card = document.createElement("div");
                card.className = "card"; // Usa tu clase CSS
                card.innerHTML = `
                    <h3>${pokeData.name}</h3>
                    <img src="${pokeData.sprites.front_default}" alt="${pokeData.name}">
                    <button class="btn-remove-fav" data-id="${pokeData.id}">❌ Quitar</button>
                `;
                contenedor.appendChild(card);
            }
        }
    } catch (error) {
        contenedor.innerHTML = "<p>Error al cargar favoritos.</p>";
    }
}

// 3. Delegación de eventos para los botones de "Quitar"
document.addEventListener("click", async (e) => {
    if (e.target.classList.contains("btn-remove-fav")) {
        const pokemonId = e.target.dataset.id;
        if (!confirm(`¿Seguro que quieres quitar este Pokémon de favoritos?`)) {
            return;
        }

        try {
            const res = await fetch(`${API_URL}/api/favoritos/${pokemonId}`, {
                method: "DELETE",
                credentials: "include"
            });
            const data = await res.json();
            alert(data.mensaje);

            if (data.exito) {
                // Si se eliminó, recargamos la lista de favoritos
                cargarFavoritos(); 
            }
        } catch (error) {
            alert("Error de conexión al eliminar.");
        }
    }
});