const input = document.getElementById("movie");
const suggestions = document.getElementById("suggestions");

input.addEventListener("input", async () => {

    const query = input.value.trim();

    if (query.length === 0) {
        suggestions.innerHTML = "";
        return;
    }

    const response = await fetch(`/autocomplete?q=${encodeURIComponent(query)}`);
    const movies = await response.json();

    suggestions.innerHTML = "";

    movies.forEach(movie => {

        const item = document.createElement("div");

        item.className = "suggestion-item";

        item.textContent = movie;

        item.onclick = () => {

            input.value = movie;
            suggestions.innerHTML = "";

        };

        suggestions.appendChild(item);

    });

});

document.addEventListener("click", (e) => {

    if (!e.target.closest(".search-box")) {
        suggestions.innerHTML = "";
    }

});