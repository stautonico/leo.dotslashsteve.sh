const LOADER = document.getElementById("loader");
const LOADER_IMAGE_DARK = "static/img/loader_dark.svg";
const LOADER_IMAGE_LIGHT = "static/img/loader_light.svg";

let elements = {};

function display_element(element, value) {
    if (value === 0) {
        if (element === "seconds") {
            elements[element].element.innerHTML = "X";
        } else {
            elements[element].container.style.display = "none";
        }
    } else {
        elements[element].container.style.display = "inline-block";
        elements[element].element.innerHTML = value;
        if (value === 1) {
            elements[element].label.innerHTML = elements[element].singular_name;
        } else {
            elements[element].label.innerHTML = elements[element].plural_name;
        }
    }
}

function make_time_string(seconds) {
    let y = Math.floor(seconds / 31536000);
    let mo = Math.floor((seconds % 31536000) / 2628000);
    let d = Math.floor(((seconds % 31536000) % 2628000) / 86400);
    let h = Math.floor((seconds % (3600 * 24)) / 3600);
    let m = Math.floor((seconds % 3600) / 60);
    let s = Math.floor(seconds % 60);

    display_element("years", y);
    display_element("months", mo);
    display_element("days", d);
    display_element("hours", h);
    display_element("minutes", m);
    display_element("seconds", s);
}

async function delay(seconds) {
    return new Promise(resolve => setTimeout(resolve, seconds * 1000));
}

function setup_elements() {
    const element_base_names = ["years", "months", "days", "hours", "minutes", "seconds"];
    for (let i = 0; i < element_base_names.length; i++) {
        let element_name = element_base_names[i];

        elements[element_name] = {
            container: document.getElementById(element_name + "_container"),
            element: document.getElementById(element_name),
            label: document.getElementById(element_name + "_label"),
            singular_name: element_name.charAt(0).toUpperCase() + element_name.slice(1, -1),
            plural_name: element_name.charAt(0).toUpperCase() + element_name.slice(1)
        }

        // Make them all hidden by default
        elements[element_name].container.style.display = "none";
    }
}

function toggle_theme(to = null) {
    if (to === null) {
        // Just toggle to the opposite of what we have
        if (document.body.classList.contains("dark"))
            to = "light";
        else
            to = "dark";
    }

    // Remove the old theme
    document.body.classList.remove("dark");
    document.body.classList.remove("light");

    // Add the new theme
    document.body.classList.add(to);
    localStorage.setItem("theme", to);
}

function setup_theme() {
    // Check if we have a local storage theme
    let theme = localStorage.getItem("theme");
    if (theme)
        toggle_theme(theme);
    else {
        // Try to get the theme from the media query
        if (window.matchMedia("(prefers-color-scheme: dark)").matches) {
            theme = "dark";
            toggle_theme("dark");
        } else {
            theme = "light";
            toggle_theme("light");
        }
    }

    // Set the initial position of the theme selector
    let theme_selector = document.getElementById("theme_selector");
    theme_selector.checked = theme === "dark";

    // Decide which loader image to use
    if (theme === "dark") {
        LOADER.src = LOADER_IMAGE_DARK;
    } else {
        LOADER.src = LOADER_IMAGE_LIGHT;
    }
}

function hide_loader() {
    LOADER.style.display = "none";
}

(async function () {
    setup_elements();
    setup_theme();
    //connect to the socket server.
    let socket = io.connect(document.domain + ':' + location.port + '/status');

    let status;
    let counter = 0;

    socket.on('status', (msg) => {
        status = msg;
    });


    while (true) {
        if (status) {
            let difference = parseInt((new Date().valueOf() - status.last_updated + counter) / 1000);
            make_time_string(difference);
            hide_loader();

            counter++;
        }
        await delay(1);
    }
})();
