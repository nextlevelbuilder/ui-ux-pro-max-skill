# HTML Slide Template

Complete HTML structure with navigation, tokens, and Chart.js integration.

## Base Structure

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Presentation Title</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>
    <style>
        /* Paste embed-tokens.cjs output here */
        :root {
            --color-primary: #FF6B6B;
            --color-background: #0D0D0D;
            /* ... more tokens */
        }

        /* Base slide styles */
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            background: var(--color-background);
            color: #fff;
            font-family: var(--typography-font-body, 'Inter', sans-serif);
            overflow: hidden;
        }

        /* 16:9 Aspect Ratio Container (desktop) */
        .slide-deck {
            position: relative;
            width: 100vw;
            height: 100vh;
            overflow: hidden;
        }

        @media (min-width: 769px) {
            .slide-deck {
                /* Lock to 16:9 — letterbox if viewport ratio differs */
                max-width: calc(100vh * 16 / 9);
                max-height: calc(100vw * 9 / 16);
                margin: auto;
                position: absolute;
                inset: 0;
            }
        }

        .slide {
            position: absolute;
            width: 100%; height: 100%;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            text-align: center;
            padding: 60px;
            opacity: 0;
            visibility: hidden;
            transition: opacity 0.4s;
            background: var(--color-background);
            overflow: hidden; /* Prevent content overflow */
        }

        .slide.active { opacity: 1; visibility: visible; }

        /* Slide inner wrapper — constrains content within safe area */
        .slide-content {
            width: 100%;
            max-width: 100%;
            max-height: 100%;
            overflow: hidden;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            gap: 16px;
        }

        /* Typography */
        h1, h2 { font-family: var(--typography-font-heading, 'Space Grotesk', sans-serif); }
        .slide-title {
            font-size: clamp(32px, 6vw, 80px);
            background: var(--primitive-gradient-primary, linear-gradient(135deg, #FF6B6B, #FF8E53));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            line-height: 1.1;
        }

        /* ===== RESPONSIVE BREAKPOINTS ===== */

        /* Tablet (portrait) */
        @media (max-width: 768px) {
            .slide { padding: 32px 24px; }
            .slide-title { font-size: clamp(28px, 5vw, 48px); }
            h2 { font-size: clamp(20px, 4vw, 32px); }
            p, li { font-size: clamp(14px, 2.5vw, 18px); }
        }

        /* Mobile */
        @media (max-width: 480px) {
            .slide { padding: 24px 16px; }
            .slide-title { font-size: clamp(22px, 6vw, 36px); }
            h2 { font-size: clamp(18px, 4.5vw, 28px); }
            p, li { font-size: clamp(12px, 3vw, 16px); }
            .nav-controls { bottom: 16px; gap: 12px; }
            .nav-btn { width: 32px; height: 32px; font-size: 14px; }
        }

        /* Navigation */
        .progress-bar {
            position: fixed;
            top: 0; left: 0;
            height: 3px;
            background: var(--color-primary);
            transition: width 0.3s;
            z-index: 1000;
        }
        .nav-controls {
            position: fixed;
            bottom: 30px;
            left: 50%;
            transform: translateX(-50%);
            display: flex;
            align-items: center;
            gap: 20px;
            z-index: 1000;
        }
        .nav-btn {
            background: rgba(255,255,255,0.1);
            border: none;
            color: #fff;
            width: 40px; height: 40px;
            border-radius: 50%;
            cursor: pointer;
            font-size: 18px;
        }
        .nav-btn:hover { background: rgba(255,255,255,0.2); }
        .slide-counter { color: rgba(255,255,255,0.6); font-size: 14px; }
    </style>
</head>
<body>
    <!-- Progress Bar -->
    <div class="progress-bar" id="progressBar"></div>

    <!-- Slide Deck Container (16:9 on desktop) -->
    <div class="slide-deck">

    <!-- Slides -->
    <div class="slide active">
        <div class="slide-content">
            <h1 class="slide-title">Title Slide</h1>
            <p>Subtitle or tagline</p>
        </div>
    </div>

    <!-- More slides... (always wrap content in .slide-content) -->

    </div><!-- /.slide-deck -->

    <!-- Navigation -->
    <div class="nav-controls">
        <button class="nav-btn" onclick="prevSlide()">←</button>
        <span class="slide-counter"><span id="current">1</span> / <span id="total">9</span></span>
        <button class="nav-btn" onclick="nextSlide()">→</button>
    </div>

    <script>
        let current = 1;
        const total = document.querySelectorAll('.slide').length;
        document.getElementById('total').textContent = total;

        function showSlide(n) {
            if (n < 1) n = 1;
            if (n > total) n = total;
            current = n;
            document.querySelectorAll('.slide').forEach((s, i) => {
                s.classList.toggle('active', i === n - 1);
            });
            document.getElementById('current').textContent = n;
            document.getElementById('progressBar').style.width = (n / total * 100) + '%';
        }

        function nextSlide() { showSlide(current + 1); }
        function prevSlide() { showSlide(current - 1); }

        document.addEventListener('keydown', (e) => {
            if (e.key === 'ArrowRight' || e.key === ' ') { e.preventDefault(); nextSlide(); }
            if (e.key === 'ArrowLeft') { e.preventDefault(); prevSlide(); }
        });

        document.addEventListener('click', (e) => {
            if (!e.target.closest('.nav-controls')) nextSlide();
        });

        showSlide(1);
    </script>
</body>
</html>
```

## Chart.js Integration

```html
<div class="chart-container" style="width: min(80%, 600px); height: clamp(200px, 40vh, 350px);">
    <canvas id="revenueChart"></canvas>
</div>

<script>
new Chart(document.getElementById('revenueChart'), {
    type: 'line', // or 'bar', 'doughnut', 'radar'
    data: {
        labels: ['Sep', 'Oct', 'Nov', 'Dec'],
        datasets: [{
            label: 'MRR ($K)',
            data: [5, 12, 28, 45],
            borderColor: '#FF6B6B',
            backgroundColor: 'rgba(255, 107, 107, 0.1)',
            borderWidth: 3,
            fill: true,
            tension: 0.4
        }]
    },
    options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: {
            x: { grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: '#B8B8D0' } },
            y: { grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: '#B8B8D0' } }
        }
    }
});
</script>
```

## Animation Classes

```css
/* Fade Up */
.animate-fade-up {
    animation: fadeUp 0.6s ease-out forwards;
    opacity: 0;
}
@keyframes fadeUp {
    from { opacity: 0; transform: translateY(30px); }
    to { opacity: 1; transform: translateY(0); }
}

/* Count Animation */
.animate-count { animation: countUp 1s ease-out forwards; }

/* Scale */
.animate-scale {
    animation: scaleIn 0.5s ease-out forwards;
}
@keyframes scaleIn {
    from { opacity: 0; transform: scale(0.9); }
    to { opacity: 1; transform: scale(1); }
}

/* Stagger Children */
.animate-stagger > * {
    opacity: 0;
    animation: fadeUp 0.5s ease-out forwards;
}
.animate-stagger > *:nth-child(1) { animation-delay: 0.1s; }
.animate-stagger > *:nth-child(2) { animation-delay: 0.2s; }
.animate-stagger > *:nth-child(3) { animation-delay: 0.3s; }
.animate-stagger > *:nth-child(4) { animation-delay: 0.4s; }
```

## Background Images

```html
<div class="slide slide-with-bg" style="background-image: url('https://images.pexels.com/...')">
    <div class="overlay" style="background: linear-gradient(135deg, rgba(13,13,13,0.9), rgba(13,13,13,0.7))"></div>
    <div class="content" style="position: relative; z-index: 1;">
        <!-- Slide content -->
    </div>
</div>
```

## CSS Variables Reference

| Variable | Usage |
|----------|-------|
| `--color-primary` | Brand primary (CTA, highlights) |
| `--color-background` | Slide background |
| `--color-secondary` | Secondary elements |
| `--primitive-gradient-primary` | Title gradients |
| `--typography-font-heading` | Headlines |
| `--typography-font-body` | Body text |
