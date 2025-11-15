//verificamos la sesion

document.addEventListener("DOMContentLoaded", async () => {
  try {
    // 1. Verificamos la sesión REAL contra el servidor
    const res = await fetch("http://10.96.17.30:5000/api/perfil", {
      method: "GET",
      credentials: "include" // ¡Esencial para enviar la cookie!
    });

    if (!res.ok) {
      // Si la sesión no es válida (error 401) o hay otro error
      throw new Error("Sesión no válida o expirada");
    }

    const data = await res.json();

    cargarFamosos();

  } catch (error) {
    console.error(error.message);
    alert("Debes iniciar sesión primero para ver esta página.");
    window.location.href = "login.html";
  }
});

//buscador

const form = document.getElementById("form-buscar");
form.addEventListener("submit", async (e) => {
  e.preventDefault();
  const nombre = document.getElementById("nombre").value.toLowerCase();
  const res = await fetch(`https://pokeapi.co/api/v2/pokemon/${nombre}`);
  if (res.ok) {
    const data = await res.json();
    mostrarPokemon(data, "pokemmon");
  } else {
    alert("pokemon no encontrado")
  }
});

//mostrar pokemon

// =====================
// 🎴 MOSTRAR POKÉMON
// =====================
function mostrarPokemon(data, contenedorId) {
  const div = document.getElementById(contenedorId);
  div.innerHTML = `
    <div class="card">
      <h3>${data.name}</h3>
      <img src="${data.sprites.front_default}" alt="${data.name}">
      <p>Altura: ${data.height} | Peso: ${data.weight}</p>
      <p>Tipo: ${data.types.map(t => t.type.name).join(", ")}</p> 
      <button class="btn-fav" data-id="${data.id}" data-nombre="${data.name}" data-img="${data.sprites.front_default}">⭐ Favorito</button>
      <button class="btn-carrito" data-id="${data.id}" data-nombre="${data.name}" data-img="${data.sprites.front_default}">🛒 Agregar al Carrito</button>
      <button class="btn-comprar" data-id="${data.id}" data-nombre="${data.name}" data-img="${data.sprites.front_default}">💰 Comprar</button>
    </div>
  `;
}
document.addEventListener("click", (e) => {

  // Revisa si el clic fue en un botón de favorito
  if (e.target.classList.contains("btn-fav")) {
    // e.target es el botón exacto al que le diste clic
    agregarFavorito(e);
  }

  // Revisa si el clic fue en un botón de carrito
  if (e.target.classList.contains("btn-carrito")) {
    agregarCarrito(e);
  }

  // Revisa si el clic fue en un botón de comprar
  if (e.target.classList.contains("btn-comprar")) {
    comprarPokemon(e);
  }
});

// =====================
// ⭐ Enviar Favorito a Flask
// =====================
async function agregarFavorito(e) {
  const data = {
    id_pokemon: e.target.dataset.id,
    nombre_pokemon: e.target.dataset.nombre,
    sprite_url: e.target.dataset.img
  };
  await fetch("http://10.96.17.30:5000/agregar_favorito", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    credentials: "include",
    body: JSON.stringify(data)
  });
  alert(`${data.nombre_pokemon} agregado a favoritos`);
}

// =====================
// 🛒 Enviar Carrito a Flask
// =====================
// En tu pokestore.js o index.js
async function agregarCarrito(e) {
  const data = {
    id_pokemon: e.target.dataset.id,
    nombre_pokemon: e.target.dataset.nombre,
    sprite_url: e.target.dataset.img,
    cantidad: 1
  };

  try {
    // (Asegúrate de que la IP sea la correcta)
    const res = await fetch("http://10.96.17.30:5000/agregar_carrito", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify(data)
    });

    const respuesta = await res.json(); // Leer la respuesta del servidor

    // ¡Solo mostramos la alerta si el servidor dice que fue un éxito!
    if (res.ok && respuesta.exito) {
      alert(respuesta.mensaje || `${data.nombre_pokemon} agregado al carrito`);
    } else {
      // Si no, mostramos el mensaje de error del servidor
      alert(`Error: ${respuesta.mensaje}`);
    }
  } catch (error) {
    // Esto es para errores de red
    alert("Error de conexión al agregar al carrito");
  }
}

// =====================
// 💰 Comprar Pokémon
// =====================
// js/pokestore.js (o index.js)

async function comprarPokemon(e) {
    const data = {
        id_pokemon: e.target.dataset.id,
        nombre_pokemon: e.target.dataset.nombre,
        sprite_url: e.target.dataset.img,
        precio: 500 // Como acordamos, el precio lo manda el JS
    };

    // 1. Añadimos una confirmación
    if (!confirm(`¿Estás seguro de que quieres comprar ${data.nombre_pokemon} por $${data.precio}?`)) {
        return; // El usuario canceló
    }

    try {
        // (Asegúrate de que la IP sea la correcta)
        const res = await fetch("http://10.96.17.30:5000/comprar", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            credentials: "include", // ¡Muy importante!
            body: JSON.stringify(data)
        });

        // 2. Leemos la respuesta del servidor
        const respuesta = await res.json(); 

        // 3. ¡Solo mostramos éxito SI EL SERVIDOR lo dice!
        if (res.ok && respuesta.exito) {
            alert(`${respuesta.mensaje} Tu nuevo saldo es $${respuesta.nuevo_saldo.toFixed(2)}`);
        } else {
            // 4. Si no, mostramos el MENSAJE DE ERROR del servidor
            alert(`Error: ${respuesta.mensaje}`); // Ej: "Saldo insuficiente"
        }

    } catch (error) {
        // 5. Esto es para errores de red (el servidor está caído)
        console.error("Error en fetch de comprar:", error);
        alert("Error: Error de conexión con el servidor.");
    }
}

// =====================
// 🌟 Cargar Pokémon Famosos
// =====================
const famosos = [
  "bulbasaur", "charmander", "squirtle", "pikachu", "jigglypuff", "meowth", "psyduck", "snorlax"
];
async function cargarFamosos() {
  const contenedor = document.getElementById("populares");
  for (let nombre of famosos) {
    const res = await fetch(`https://pokeapi.co/api/v2/pokemon/${nombre}`);
    if (res.ok) {
      const data = await res.json();
      const card = document.createElement("div");
      card.className = "card";
      card.innerHTML = `
        <h3>${data.name}</h3>
        <img src="${data.sprites.front_default}" alt="${data.name}">
        <p>Altura: ${data.height} | Peso: ${data.weight}</p>
        <p>Tipo: ${data.types.map(t => t.type.name).join(", ")}</p>
        <button class="btn-fav" data-id="${data.id}" data-nombre="${data.name}" data-img="${data.sprites.front_default}">⭐ Favorito</button>
        <button class="btn-carrito" data-id="${data.id}" data-nombre="${data.name}" data-img="${data.sprites.front_default}">🛒 Carrito</button>
        <button class="btn-comprar" data-id="${data.id}" data-nombre="${data.name}" data-img="${data.sprites.front_default}">💰 Comprar</button>
      `;
      contenedor.appendChild(card);
    }
  }
}
cargarFamosos();