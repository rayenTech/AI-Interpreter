from flask import Flask, request, render_template_string, send_from_directory
from interpreter import run_interpreter
import os

app = Flask(__name__)

@app.route('/')
def index():
    message = request.args.get('query', '').strip()
    interpretation = run_interpreter(message) if message else ''
    return render_template_string("""
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <title>🤖 Your AI Interpretation Friend for SOC Analysts</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: #0f172a;
            color: #e2e8f0;
            padding: 2rem;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
        }
        .box {
            background-color: #1e293b;
            padding: 2rem;
            border-radius: 10px;
            box-shadow: 0 0 10px rgba(0,255,255,0.1);
            max-width: 1000px;
            margin: auto;
            flex-grow: 1;
        }
        h2, h4 {
            color: #38bdf8;
        }
        .section-title {
            color: #38bdf8;
            font-size: 1.2rem;
            margin-bottom: 0.5rem;
            font-weight: bold;
        }
        textarea {
            width: 100%;
            padding: 1rem;
            border-radius: 6px;
            border: none;
            background-color: #334155;
            color: #f8fafc;
            font-size: 1rem;
            resize: vertical;
        }
        button {
            padding: 0.8rem 1.5rem;
            background-color: #22c55e;
            border: none;
            border-radius: 5px;
            font-weight: bold;
            color: white;
            cursor: pointer;
            margin-top: 1rem;
        }
        button:hover {
            background-color: #16a34a;
        }
        pre {
            background-color: #0f172a;
            color: #f1f5f9;
            padding: 1rem;
            border-left: 4px solid #38bdf8;
            overflow-x: auto;
            white-space: pre-wrap;
            word-wrap: break-word;
            position: relative;
        }
        .copy-icon {
            background-image: url('data:image/svg+xml;utf8,<svg fill="%23ffffff" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path d="M16 1H4c-1.1 0-2 .9-2 2v14h2V3h12V1zm3 4H8c-1.1 0-2 .9-2 2v16h14c1.1 0 2-.9 2-2V7c0-1.1-.9-2-2-2zm0 18H8V7h11v16z"/></svg>');
            background-repeat: no-repeat;
            background-size: 20px 20px;
            background-position: center;
            border: none;
            width: 36px;
            height: 36px;
            cursor: pointer;
            background-color: transparent;
            position: absolute;
            bottom: 10px;
            right: 10px;
        }
        .copy-icon:hover {
            filter: brightness(1.2);
        }
        p.interpretation {
            background-color: #334155;
            padding: 1rem;
            border-radius: 6px;
            white-space: pre-wrap;
            line-height: 1.6;
            color: #e2e8f0;
            margin-top: 0.5rem;
        }
        .header-right {
            text-align: right;
        }
        .logo {
            height: 50px;
            display: block;
            margin-left: auto;
            filter: drop-shadow(0 0 10px cyan);
            position: relative;
            animation: glow 2.5s ease-in-out infinite alternate;
        }
        @keyframes glow {
            0% {
                filter: drop-shadow(0 0 5px cyan);
            }
            50% {
                filter: drop-shadow(0 0 20px cyan);
            }
            100% {
                filter: drop-shadow(0 0 5px cyan);
            }
        }
        .credit {
            font-size: 0.75rem;
            color: #94a3b8;
            margin-top: 0.2rem;
            text-align: right;
        }
        .footer {
            text-align: center;
            margin-top: 2rem;
            font-size: 0.8rem;
            color: #C71585; /* Rose foncé */
        }
        .footer div {
            display: inline-block;
            animation: neonGlow 3s ease-in-out infinite alternate;
            color: #C71585; /* Rose foncé */
            margin: 0 5px;
        }
        @keyframes neonGlow {
            0% {
                color: #C71585; /* Rose foncé */
                text-shadow: none;
            }
            50% {
                color: #FF1493; /* Rose plus vif pour l'effet de lueur */
                text-shadow:
                    0 0 8px #FF1493,
                    0 0 16px #FF1493,
                    0 0 24px #DB7093; /* Rose pâle pour lueur diffuse */
            }
            100% {
                color: #C71585; /* Retour au rose foncé */
                text-shadow: none;
            }
        }
        a {
            color: #38bdf8;
            text-decoration: none;
        }
        a:hover {
            text-decoration: underline;
        }
        .golden-link {
            color: #B8860B; /* Doré foncé proche du marron */
            animation: goldenGlow 2.5856s ease-in-out infinite alternate;
        }
        .golden-link:hover {
            text-decoration: underline;
            color: #B8860B; /* Maintien du doré foncé au survol */
        }
        @keyframes goldenGlow {
            0% {
                text-shadow: 0 0 5px #B8860B;
            }
            50% {
                text-shadow:
                    0 0 10px #B8860B,
                    0 0 20px #8B5A2B; /* Marron-doré pour lueur */
            }
            100% {
                text-shadow: 0 0 5px #B8860B;
            }
        }
    </style>
</head>
<body>
    <div class="box">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <h2>🤖 Your AI Interpretation Friend for SOC Analysts</h2>
            <div class="header-right">
                <img src="/talan.png" alt="Talan Logo" class="logo">
                <div class="credit">© Rayen Gaied</div>
            </div>
        </div>

        {% if message %}
            <div class="section-title">🔎 Message d'alerte reçu :</div>
            <pre id="alertText">{{ message }}
                <button class="copy-icon" onclick="copyToClipboard()" title="Copier"></button>
            </pre>

            <div class="section-title">🧠 Interprétation :</div>
            <p class="interpretation">{{ interpretation | safe }}</p>

            <br>
            <a href="/" class="golden-link">🔁 Analyser un autre message</a>
        {% else %}
            <form method="get">
                <textarea name="query" rows="12" placeholder="Colle ici ton alerte JSON de Security Onion..."></textarea><br>
                <button type="submit">Analyser</button>
            </form>
        {% endif %}
    </div>

    <div class="footer">
        <div class="footer-line">End-of-Studies Project @ Talan — 2025</div>
        <br><div class="footer-line">PFE réalisé chez Talan — 2025</div>
    </div>

    <script>
    function copyToClipboard() {
        const text = document.getElementById("alertText").textContent;
        navigator.clipboard.writeText(text.trim()).then(() => {
            console.log("Texte copié!");
        });
    }
    </script>
</body>
</html>
""", message=message, interpretation=interpretation)

@app.route('/talan.png')
def serve_logo():
    return send_from_directory(os.path.dirname(__file__), 'talan.png')

if __name__ == "__main__":
    app.run(port=8502, debug=True)
