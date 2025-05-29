console.log("main.js successfully loaded!");

document.addEventListener("DOMContentLoaded", function () {
    console.log("Sayfa tamamen yüklendi!");

    // Basit bir buton etkileşimi ekleyelim
    let btn = document.getElementById("testButton");
    if (btn) {
        btn.addEventListener("click", function () {
            alert("Butona tıkladınız!");
        });
    }
});
