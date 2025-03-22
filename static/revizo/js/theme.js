document.addEventListener("DOMContentLoaded", function () {
    const toggleButton = document.getElementById("toggle-theme");
    const body = document.body;
    const logo = document.getElementById("logo");

    const savedTheme = localStorage.getItem("theme") || "light";
    body.classList.toggle("dark-mode", savedTheme === "dark");
    logo.src = savedTheme === "dark" ? logo.dataset.dark : logo.dataset.light;

    toggleButton.addEventListener("click", function () {
        const isDarkMode = !body.classList.contains("dark-mode");
        body.classList.toggle("dark-mode");
        
        logo.src = isDarkMode 
            ? `${logo.dataset.dark}?t=${new Date().getTime()}`
            : `${logo.dataset.light}?t=${new Date().getTime()}`;

        localStorage.setItem("theme", isDarkMode ? "dark" : "light");
    });
});
