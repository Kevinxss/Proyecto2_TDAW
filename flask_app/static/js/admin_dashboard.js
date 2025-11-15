document.addEventListener("DOMContentLoaded", async () => {
  const API_URL = "http://127.0.0.1:5000";

  async function cargarLista(endpoint, elementoId, campo, conteoCampo, etiqueta) {
    try {
      const res = await fetch(`${API_URL}${endpoint}`);
      if (!res.ok) throw new Error("Error de conexión con el servidor");
      const datos = await res.json();

      const lista = document.getElementById(elementoId);
      lista.innerHTML = "";

      if (datos.length === 0) {
        lista.innerHTML = "<li class='list-group-item text-muted'>Sin datos disponibles</li>";
        return;
      }

      datos.forEach((item, i) => {
        const li = document.createElement("li");
        li.className = "list-group-item d-flex justify-content-between align-items-center";
        li.innerHTML = `
          <span>#${i + 1} - ${etiqueta} ${item[campo]}</span>
          <span class="badge bg-primary rounded-pill">${item[conteoCampo]}</span>
        `;
        lista.appendChild(li);
      });
    } catch (error) {
      console.error(`Error al cargar ${endpoint}:`, error);
      const lista = document.getElementById(elementoId);
      lista.innerHTML = "<li class='list-group-item text-danger'>Error al obtener datos</li>";
    }
  }

  // 🔥 Top 10 Pokémon más comprados
  cargarLista("/api/top_pokemones_compras", "top-pokemones-compras", "id_pokemon", "total_compras", "Pokémon");

  // 👥 Top 10 usuarios con más compras
  cargarLista("/api/top_usuarios_compras", "top-usuarios-compras", "id_usuario", "total_compras", "Usuario");

  // ⭐ Top 10 Pokémon más favoritos
  cargarLista("/api/top_pokemones_favoritos", "top-pokemones-favoritos", "id_pokemon", "total_favoritos", "Pokémon");
});
