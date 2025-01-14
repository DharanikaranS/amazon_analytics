const navbarMenu = document.querySelector(".navbar .links");
const hamburgerBtn = document.querySelector(".hamburger-btn");
const hideMenuBtn = navbarMenu.querySelector(".close-btn");
const showPopupBtn = document.querySelector(".login-btn");
const formPopup = document.querySelector(".form-popup");
const hidePopupBtn = formPopup.querySelector(".close-btn");
const signupLoginLink = formPopup.querySelectorAll(".bottom-link a");
const signupForm = document.querySelector(".signup form");
const loginForm = document.querySelector(".login form");

hamburgerBtn.addEventListener("click", () => {
    navbarMenu.classList.toggle("show-menu");
});

hideMenuBtn.addEventListener("click", () => {
    navbarMenu.classList.remove("show-menu");
});

showPopupBtn.addEventListener("click", () => {
    document.body.classList.toggle("show-popup");
});

hidePopupBtn.addEventListener("click", () => {
    document.body.classList.remove("show-popup");
});

signupLoginLink.forEach(link => {
    link.addEventListener("click", (e) => {
        e.preventDefault();
        formPopup.classList[link.id === 'signup-link' ? 'add' : 'remove']("show-signup");
    });
});

// Handle Signup Form Submission
signupForm.addEventListener("submit", async (e) => {
    e.preventDefault();

    const formData = new FormData(signupForm);
    const data = {
        email: formData.get('email'),
        password: formData.get('password'),
    };

    try {
        const response = await fetch("/signup", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify(data),
        });

        const result = await response.json();
        console.log("Signup response:", result);  // Debugging line
        if (response.ok) {
            alert("Signup successful!");
            document.body.classList.remove("show-popup");
            signupForm.reset();
        } else {
            alert(`Error: ${result.message}`);
        }
    } catch (error) {
        console.error("Error during signup:", error);
        alert("An error occurred. Please try again.");
    }
});

// Handle Login Form Submission
loginForm.addEventListener("submit", async (e) => {
    e.preventDefault();

    const formData = new FormData(loginForm);
    const data = {
        email: formData.get('email'),
        password: formData.get('password'),
    };

    try {
        const response = await fetch("/login", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify(data),
        });

        const result = await response.json();
        console.log("Login response:", result);  // Debugging line
        if (response.ok) {
            // Redirect to dashboard
            window.location.href = '/dashboard';
        } else {
            alert(`Error: ${result.message}`);
        }
    } catch (error) {
        console.error("Error during login:", error);
        alert("An error occurred. Please try again.");
    }
});
