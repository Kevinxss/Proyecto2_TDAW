// js/compras.js

const API_URL = "http://10.96.17.30:5000"; // (Usa la IP que corresponda)
const POKEAPI_URL = "https://pokeapi.co/api/v2/pokemon";

// 1. Verificar sesión
document.addEventListener("DOMContentLoaded", async () => {
    try {
        const res = await fetch(`${API_URL}/api/perfil`, {
            method: "GET",
            credentials: "include"
        });
        if (!res.ok) throw new Error("Sesión no válida");
        
        cargarCompras(); // Cargar historial
    } catch (error) {
        alert("Debes iniciar sesión primero.");
        window.location.href = "login.html";
    }
});

// 2. Cargar historial de compras
async function cargarCompras() {
    const contenedor = document.getElementById("compras-container");
    contenedor.innerHTML = ""; // Limpiar "Cargando..."
    
    try {
        const res = await fetch(`${API_URL}/api/compras`, {
            method: "GET",
            credentials: "include"
        });
        const data = await res.json();

        if (!data.exito || data.compras.length === 0) {
            contenedor.innerHTML = "<p>No has realizado ninguna compra.</p>";
            return;
        }

        // data.compras es: [{id_compra: 1, total: 1000, fecha: "...", detalles: [{id_pokemon: 25, ...}, ...]}, ...]
        for (let compra of data.compras) {
            const compraCard = document.createElement("div");
            compraCard.className = "compra-card"; // Puedes estilizar .compra-card en CSS
            
            let detallesHTML = "<ul>"; // Lista de detalles
            
            // Recorremos los detalles de CADA compra
            for (let item of compra.detalles) {
                // Buscamos el nombre e imagen en la PokéAPI
                // (Nota: esto puede ser lento si hay muchas compras, pero funciona)
                let nombrePoke = `Pokémon (ID: ${item.id_pokemon})`;
                let imgPoke = "";
                
                try { // Usamos un try/catch por si la PokéAPI falla
                    const pokeRes = await fetch(`${POKEAPI_URL}/${item.id_pokemon}`);
                    if (pokeRes.ok) {
                        const pokeData = await pokeRes.json();
                        nombrePoke = pokeData.name;
                        imgPoke = `<img src="${pokeData.sprites.front_default}" alt="${nombrePoke}" style="width: 50px;">`;
                    }
                } catch (e) { /* Ignorar error de PokéAPI, usar datos default */ }
                
                detallesHTML += `
                    <li>
                        ${imgPoke} ${nombrePoke} (x${item.cantidad}) - Subtotal: $${item.subtotal}
                    </li>
                `;
            }
            detallesHTML += "</ul>"; // Cerramos la lista
            
            // Armamos la tarjeta de la compra
            compraCard.innerHTML = `
                <h3>Compra #${compra.id_compra}</h3>
                <p><strong>Fecha:</strong> ${compra.fecha_compra}</p>
                <p><strong>Total Pagado: $${compra.total}</strong></p>
                <h4>Detalles:</h4>
                ${detallesHTML}
                <hr>
            `;
            contenedor.appendChild(compraCard);
        }
    } catch (error) {
        console.error(error);
        contenedor.innerHTML = "<p>Error al cargar el historial de compras.</p>";
    }
}