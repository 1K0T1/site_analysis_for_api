document.querySelector(".grid_register").addEventListener("submit", (e) => {
    const { username, password, email } = e.target;

    const hasSpace = /\s/;
    const invalidUsername = /[^a-zA-Z0-9_]/;

    if (
        hasSpace.test(username.value) ||
        hasSpace.test(password.value) ||
        hasSpace.test(email.value) ||
        invalidUsername.test(username.value)
    ) {
        e.preventDefault();
        alert("❗ Данные введены неверно.\nУберите пробелы и недопустимые символы.");
    }
});