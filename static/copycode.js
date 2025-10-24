function copyCode() {
    const code = document.getElementById("copy").innerText;
    navigator.clipboard.writeText(code)
        .then(() => alert("Код скопирован!"))
        .catch(err => console.error(err));
}