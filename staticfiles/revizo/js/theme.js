document.addEventListener("DOMContentLoaded", function () {
    const toggleButton = document.getElementById("toggle-theme");
    const body = document.body;
    const logo = document.getElementById("logo");

    if (localStorage.getItem("theme") === "dark") {
        body.classList.add("dark-mode");
        logo.src = logo.dataset.dark;
    }

    updateLogo();

    toggleButton.addEventListener("click", function () {
        body.classList.toggle("dark-mode");
        const isDarkMode = body.classList.contains("dark-mode");

        logo.src = isDarkMode ? logo.dataset.dark : logo.dataset.light;
        localStorage.setItem("theme", isDarkMode ? "dark" : "light");
    });
});
