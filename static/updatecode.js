// подстановка кода
function updateCode(newCode, lang = "") {
    const codeBlock = document.querySelector('main.view_analysis_api .viewcode code');
    codeBlock.className = lang ? `language-${lang}` : "";
    codeBlock.innerText = newCode;
    hljs.highlightElement(codeBlock);
}

setTimeout(() => {
    updateCode(`Пусто...`, "js");
}, 1000);