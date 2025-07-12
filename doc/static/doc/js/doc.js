let back_to_top_button = document.getElementById("btn-back-to-top");
let nav_back_to_top = document.getElementById("nav-back-to-top");

window.onscroll = function () {
    scrollFunction();
};
function scrollFunction() {
    if (
        document.body.scrollTop > 800 ||
        document.documentElement.scrollTop > 800
    ) {
        back_to_top_button.style.display = "block";
        nav_back_to_top.style.display = "block";
    } else {
        back_to_top_button.style.display = "none";
        nav_back_to_top.style.display = "none";
    }
}
back_to_top_button.addEventListener("click", backToTop);
nav_back_to_top.addEventListener("click", backToTop);
function backToTop() {
    document.body.scrollTop = 0;
    document.documentElement.scrollTop = 0;
}