from django.http import HttpResponse, HttpResponseNotFound, JsonResponse

def home(request):
    html = """
    <html>
    <head>
        <title>DevFocus API</title>
        <style>
            body {
                background-color: #000;
                color: #00ff00;
                font-family: 'Courier New', monospace;
                overflow: hidden;
                margin: 0;
                padding: 0;
            }
            #matrix {
                position: absolute;
                width: 100%;
                height: 100%;
                top: 0;
                left: 0;
                z-index: 0;
            }
            .overlay {
                position: absolute;
                width: 100%;
                height: 100%;
                top: 0;
                left: 0;
                background: rgba(0, 0, 0, 0.1); 
                backdrop-filter: blur(6px);     
                -webkit-backdrop-filter: blur(6px); 
                z-index: 1;
            }

            .content {
                padding-top: 30%;
                position: relative;
                z-index: 2;
                text-align: center;
                top: 50%;
                transform: translateY(-50%);
            }
            h1 {
                font-size: 3em;
                color: #ffffff;
                text-shadow: 2px 2px 10px #00ff00;
                margin: 0.2em 0;
            }
            p {
                font-size: 1.5em;
                color: #ffffff;
                text-shadow: 1px 1px 5px #000;
                margin: 0.3em 0;
                font-weight: bold;
            }
        </style>
    </head>
    <body>
        <canvas id="matrix"></canvas>
        <div class="overlay"></div>
        <div class="content">
            <h1>DevFocus API RUNNED</h1>
            <p>⚡ The system hums quietly... <br> Do you dare to explore?</p>
        </div>
                <script>
            const canvas = document.getElementById('matrix');
            const ctx = canvas.getContext('2d');

            canvas.width = window.innerWidth;
            canvas.height = window.innerHeight;

            const letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789@#$%^&*()*&^%";
            const fontSize = 16;
            const columns = canvas.width / fontSize;
            const drops = Array(Math.floor(columns)).fill(1);

            function draw() {
                ctx.fillStyle = "rgba(0, 0, 0, 0.05)";
                ctx.fillRect(0, 0, canvas.width, canvas.height);
                ctx.fillStyle = "#00ff00";
                ctx.font = fontSize + "px monospace";

                for (let i = 0; i < drops.length; i++) {
                    const text = letters.charAt(Math.floor(Math.random() * letters.length));
                    ctx.fillText(text, i * fontSize, drops[i] * fontSize);
                    if (drops[i] * fontSize > canvas.height && Math.random() > 0.975) {
                        drops[i] = 0;
                    }
                    drops[i]++;
                }
            }

            setInterval(draw, 50);
        </script>
    </body>
    </html>
    """
    return HttpResponse(html)


def custom_404_view(request, exception):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({"detail": "404 — Lost in the Shadows"}, status=404)

    html = """
    <html>
    <head>
        <title>404 — Security Breach Detected</title>
        <style>
            body {
                background-color: #000;
                color: #00ff00;
                font-family: 'Courier New', monospace;
                overflow: hidden;
                margin: 0;
                padding: 0;
            }

            #matrix {
                position: absolute;
                width: 100%;
                height: 100%;
                top: 0;
                left: 0;
                z-index: 0;
            }
            .overlay {
                position: absolute;
                width: 100%;
                height: 100%;
                top: 0;
                left: 0;
                background: rgba(0, 0, 0, 0.1); 
                backdrop-filter: blur(6px);     
                -webkit-backdrop-filter: blur(6px); 
                z-index: 1;
            }

            .content {
                padding-top: 30%;
                position: relative;
                z-index: 2;
                text-align: center;
                top: 50%;
                transform: translateY(-50%);
            }
            h1 {
                font-size: 3em;
                color: #ffffff;
                text-shadow: 2px 2px 10px #00ff00;
                margin: 0.2em 0;
            }
            h6 {
                font-size: 2em;
                color: #ff3333;
                text-shadow: 1px 1px 5px #000;
                margin: 0.5em 0;
            }
            p {
                font-size: 1.5em;
                color: #ffffff;
                text-shadow: 1px 1px 5px #000;
                margin: 0.3em 0;
                font-weight: bold;
            }

            a {
                color: #00ff00;
                font-weight: bold;
                text-decoration: underline;
                font-size: 1.2em;
            }
        </style>
    </head>
    <body>
        <canvas id="matrix"></canvas>
        <div class="overlay"></div>
        <div class="content">
            <h1>404 — Lost in the Shadows</h1>
            <h6>⚠ SECURITY BREACH DETECTED</h6>
            <p>Access denied… the DevFocus whispers in the shadows</p>
            <p>Are you sure you should be here?</p>
            <a href="/">Return to Safe Zone</a>
        </div>
        <script>
            const canvas = document.getElementById('matrix');
            const ctx = canvas.getContext('2d');

            canvas.width = window.innerWidth;
            canvas.height = window.innerHeight;

            const letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789@#$%^&*()*&^%";
            const fontSize = 16;
            const columns = canvas.width / fontSize;
            const drops = Array(Math.floor(columns)).fill(1);

            function draw() {
                ctx.fillStyle = "rgba(0, 0, 0, 0.05)";
                ctx.fillRect(0, 0, canvas.width, canvas.height);
                ctx.fillStyle = "#00ff00";
                ctx.font = fontSize + "px monospace";

                for (let i = 0; i < drops.length; i++) {
                    const text = letters.charAt(Math.floor(Math.random() * letters.length));
                    ctx.fillText(text, i * fontSize, drops[i] * fontSize);
                    if (drops[i] * fontSize > canvas.height && Math.random() > 0.975) {
                        drops[i] = 0;
                    }
                    drops[i]++;
                }
            }

            setInterval(draw, 50);
        </script>
    </body>
    </html>
    """

    return HttpResponseNotFound(html)

