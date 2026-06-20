const fileInput = document.getElementById("fileInput");
const selectedFile = document.getElementById("selectedFile");

const convertBtn = document.getElementById("convertBtn");

const output = document.getElementById("output");

const progressBar =
document.getElementById("progressBar");

let currentFilename = "output";

fileInput.addEventListener("change", () => {

    const file = fileInput.files[0];

    if (!file) return;

    currentFilename =
    file.name.replace(/\.[^/.]+$/, "");

    selectedFile.innerHTML =
    `<strong>${file.name}</strong>`;
});

convertBtn.addEventListener("click", () => {

    const file = fileInput.files[0];

    if (!file) {
        alert("Please select a file.");
        return;
    }

    const formData =
    new FormData();

    formData.append(
        "file",
        file
    );

    output.value = "";

    const xhr =
    new XMLHttpRequest();

    xhr.upload.onprogress = e => {

        if (!e.lengthComputable)
            return;

        const percent =
        Math.round(
            (e.loaded / e.total) * 100
        );

        progressBar.style.width =
        percent + "%";
    };

    xhr.onreadystatechange = () => {

        if (xhr.readyState === 2) {

            progressBar.style.width =
            "90%";
        }
    };

    xhr.onload = () => {

        progressBar.style.width =
        "100%";

        if (xhr.status !== 200) {
            return;
        }

        const response =
        JSON.parse(xhr.responseText);

        output.value =
        response.markdown || "";
    };

    xhr.open(
        "POST",
        "/convert"
    );

    xhr.send(formData);
});

document
.getElementById("copyBtn")
.addEventListener("click", async () => {

    await navigator.clipboard.writeText(
        output.value
    );
});

document
.getElementById("downloadBtn")
.addEventListener("click", () => {

    const blob =
    new Blob(
        [output.value],
        { type:"text/markdown" }
    );

    const link =
    document.createElement("a");

    link.href =
    URL.createObjectURL(blob);

    link.download =
    currentFilename + ".md";

    link.click();
});