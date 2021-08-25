// collapse navbar

const btn = document.querySelector(".nav-collapse");
const nav = document.querySelector(".nav-links");
const navLinks = document.querySelectorAll(".nav-links li");

btn.addEventListener("click", () => {
  nav.classList.toggle("nav-active");

  navLinks.forEach((link, index) => {
    if (link.style.animation) {
      link.style.animation = "";
    } else {
      link.style.animation = `navLinkFade 0.5s ease forwards ${index / 8 + .3}s`;
    }
  });

  btn.classList.toggle("nav-toggle");
});

// close alerts

function alertClose (element) {
  element.parentNode.classList.add("alert-hidden");
}

// (de)activate passwords in settings

const checkbox = document.querySelector("#activate-pwd");
const pwd = document.querySelector(".settings-passwords");

checkbox.addEventListener("change", e => {
  pwd.classList.toggle("pwd-hidden");
  document.querySelectorAll(".settings-passwords input").forEach( element => {
    element.value = e.target.checked ? "" : "none";
  });
});

// grow textarea for creating / editing Post

function autoGrow(element) {
  window.setTimeout(() => {
    element.style.height = "auto";
    element.style.height = element.scrollHeight + "px";
  }, 0);
}

// change mode: edit - preview
function changeMode(element, body) {
  if (element.classList.contains("tab-active")) return;
  
  const buttons = document.querySelectorAll(".tab-bar button");
  const windows = document.querySelectorAll(".tab-window")

  buttons.forEach(button => {
    if (button.classList.contains("tab-active")) button.classList.remove("tab-active");
  });

  element.classList.add("tab-active")

  windows.forEach(window => {
    if (window.classList.contains("tab-active")) window.classList.remove("tab-active")
    if (window.classList.contains(body)) window.classList.add("tab-active")
  })
  
  if (body == "tab-preview") {
    let preview = document.querySelector(".tab-preview")
    let req = new XMLHttpRequest();
    let url = "/markdown";
    let param = "data=" + document.querySelector("#data").value.replaceAll("&", "%26");

    req.onreadystatechange = () => {
      if (req.readyState == 4 && req.status == 200) {
        let title = document.querySelector("#title").value;
        let description = document.querySelector("#description").value;
        let banner = `<div class="post-banner"><div class="post-banner-top"><h1>${title}</h1></div><hr><p class "post-banner-description">${description}</p></div>`
        preview.innerHTML = banner + '<div class="markdown-body">' + req.responseText + '</div>';
      }
    }

    req.open("POST", url, true)
    req.setRequestHeader('Content-type', 'application/x-www-form-urlencoded');
    req.send(param);
  }
}