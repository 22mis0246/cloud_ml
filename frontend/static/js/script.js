const revealItems = document.querySelectorAll("[data-reveal]");

const revealObserver = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
        if (entry.isIntersecting) {
            entry.target.classList.add("is-visible");
            revealObserver.unobserve(entry.target);
        }
    });
}, { threshold: 0.18 });

revealItems.forEach((item) => revealObserver.observe(item));

const liveClock = document.querySelector("[data-live-clock]");

if (liveClock) {
    const renderClock = () => {
        const now = new Date();
        liveClock.textContent = now.toLocaleString([], {
            year: "numeric",
            month: "short",
            day: "2-digit",
            hour: "2-digit",
            minute: "2-digit",
            second: "2-digit",
        });
    };

    renderClock();
    window.setInterval(renderClock, 1000);
}
