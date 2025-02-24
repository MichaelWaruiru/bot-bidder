document.addEventListener("DOMContentLoaded", function () {
    const toggleButton = document.getElementById("theme-toggle");
    const body = document.body;
    
    // Load saved theme
    const savedTheme = localStorage.getItem("theme");
    if (savedTheme) {
        body.classList.remove("dark-mode", "light-mode");
        body.classList.add(savedTheme);
        toggleButton.textContent = savedTheme === "dark-mode" ? "🌙" : "☀️";
    }

    // Toggle theme on button click
    toggleButton.addEventListener("click", function () {
        if (body.classList.contains("dark-mode")) {
            body.classList.replace("dark-mode", "light-mode");
            localStorage.setItem("theme", "light-mode");
            toggleButton.textContent = "☀️";
        } else {
            body.classList.replace("light-mode", "dark-mode");
            localStorage.setItem("theme", "dark-mode");
            toggleButton.textContent = "🌙";
        }
    });
});
