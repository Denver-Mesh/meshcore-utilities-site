const form = document.getElementById("repeater-form");

form.addEventListener("submit", async (e) => {
    e.preventDefault();

    const data = Object.fromEntries(new FormData(form).entries());

    const res = await fetch(form.action, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
    });

    // handle response as needed // const result = await res.json();
    const result = await res.json();
    console.log(result);
});
