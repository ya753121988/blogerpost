import os
from flask import Flask, render_template_string, request, jsonify
import requests

app = Flask(__name__)

# TMDB API Key (Get it from themoviedb.org)
TMDB_API_KEY = "7dc544d9253bccc3cfecc1c677f69819"

# --- UI Layout ---
UI_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Premium Blogger Post Generator</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { background-color: #f8f9fa; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
        .main-card { border-radius: 15px; box-shadow: 0 4px 20px rgba(0,0,0,0.1); border: none; margin-top: 30px; }
        .search-item { cursor: pointer; transition: 0.3s; border-radius: 10px; overflow: hidden; }
        .search-item:hover { transform: scale(1.03); box-shadow: 0 5px 15px rgba(0,0,0,0.2); }
        .code-box { background: #1e1e1e; color: #d4d4d4; padding: 20px; border-radius: 10px; font-family: 'Courier New', monospace; max-height: 400px; overflow-y: auto; white-space: pre-wrap; display: none; }
        .btn-premium { background: linear-gradient(135deg, #6e8efb, #a777e3); border: none; color: white; }
        .btn-premium:hover { background: linear-gradient(135deg, #a777e3, #6e8efb); color: white; }
    </style>
</head>
<body>

<div class="container mb-5">
    <div class="card main-card p-4">
        <h2 class="text-center fw-bold mb-4">🎬 Movie & Web Series Blogger Post Creator</h2>
        
        <!-- Search Section -->
        <div class="row g-2">
            <div class="col-md-7">
                <input type="text" id="query" class="form-control form-control-lg" placeholder="Enter Movie or Series Name...">
            </div>
            <div class="col-md-3">
                <select id="type" class="form-select form-select-lg">
                    <option value="movie">Movie</option>
                    <option value="tv">Web Series</option>
                </select>
            </div>
            <div class="col-md-2">
                <button class="btn btn-dark btn-lg w-100" onclick="search()">Search</button>
            </div>
        </div>

        <div id="results" class="row mt-4"></div>

        <!-- Editor Section -->
        <div id="editor" class="mt-5" style="display:none;">
            <hr>
            <h4 class="mb-3">Customize Post Details</h4>
            <div class="row">
                <div class="col-md-6 mb-3">
                    <label>Language</label>
                    <input type="text" id="lang" class="form-control" placeholder="e.g. Hindi - English">
                </div>
                <div class="col-md-6 mb-3">
                    <label>Youtube Trailer ID</label>
                    <input type="text" id="trailer" class="form-control" placeholder="e.g. d9MyW72ELq0">
                </div>
            </div>

            <div id="download-section">
                <h5 class="mt-3">Download Links (Leave empty if not needed)</h5>
                <div class="row g-2">
                    <div class="col-md-4"><input type="text" id="l8k" class="form-control" placeholder="8K Link"></div>
                    <div class="col-md-4"><input type="text" id="l4k" class="form-control" placeholder="4K Link"></div>
                    <div class="col-md-4"><input type="text" id="l1080" class="form-control" placeholder="1080p Link"></div>
                    <div class="col-md-4"><input type="text" id="l720" class="form-control" placeholder="720p Link"></div>
                    <div class="col-md-4"><input type="text" id="l480" class="form-control" placeholder="480p Link"></div>
                    <div class="col-md-4"><input type="text" id="l360" class="form-control" placeholder="360p Link"></div>
                </div>
            </div>

            <div id="series-extra" class="mt-4" style="display:none;">
                <h5>Web Series: Seasons & Episodes</h5>
                <textarea id="episodes_data" class="form-control" rows="4" placeholder="Season 1: Episode 1|link1, Episode 2|link2&#10;Season 2: Episode 1|link1"></textarea>
                <p class="small text-muted mt-1">Format: Season Name: Episode Name|Link, Episode Name|Link (Use comma to separate episodes)</p>
            </div>

            <button class="btn btn-premium btn-lg w-100 mt-4" onclick="generateHTML()">Generate Premium Blogger HTML</button>
        </div>

        <!-- Output Section -->
        <div id="output-wrapper" class="mt-5" style="display:none;">
            <div class="d-flex justify-content-between align-items-center mb-2">
                <h5>Final Blogger HTML Code:</h5>
                <button class="btn btn-sm btn-outline-success" onclick="copyCode()">Copy HTML</button>
            </div>
            <div id="output" class="code-box"></div>
        </div>
    </div>
</div>

<script>
let selectedItem = null;

async function search() {
    const q = document.getElementById('query').value;
    const t = document.getElementById('type').value;
    const res = await fetch(`/api/search?q=${q}&type=${t}`);
    const data = await res.json();
    
    let html = '';
    data.results.forEach(item => {
        const title = item.title || item.name;
        const img = item.backdrop_path ? `https://image.tmdb.org/t/p/w500${item.backdrop_path}` : 'https://via.placeholder.com/500x281?text=No+Image';
        html += `
            <div class="col-md-4 mb-3">
                <div class="card search-item" onclick="selectItem('${item.id}', '${t}')">
                    <img src="${img}" class="card-img-top">
                    <div class="card-body p-2 text-center">
                        <h6 class="m-0 text-truncate">${title}</h6>
                    </div>
                </div>
            </div>`;
    });
    document.getElementById('results').innerHTML = html;
}

async function selectItem(id, type) {
    const res = await fetch(`/api/details?id=${id}&type=${type}`);
    selectedItem = await res.json();
    document.getElementById('editor').style.display = 'block';
    document.getElementById('series-extra').style.display = type === 'tv' ? 'block' : 'none';
    window.scrollTo(0, document.getElementById('editor').offsetTop);
}

async function generateHTML() {
    const lang = document.getElementById('lang').value;
    const trailer = document.getElementById('trailer').value;
    const ep_data = document.getElementById('episodes_data').value;
    const links = {
        "8K UHD": document.getElementById('l8k').value,
        "4K UHD": document.getElementById('l4k').value,
        "1080p FHD": document.getElementById('l1080').value,
        "720p HD": document.getElementById('l720').value,
        "480p SD": document.getElementById('l480').value,
        "360p": document.getElementById('l360').value
    };

    const res = await fetch('/api/generate', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({item: selectedItem, lang, trailer, links, ep_data})
    });
    const data = await res.json();
    document.getElementById('output').innerText = data.html;
    document.getElementById('output').style.display = 'block';
    document.getElementById('output-wrapper').style.display = 'block';
}

function copyCode() {
    const code = document.getElementById('output').innerText;
    navigator.clipboard.writeText(code);
    alert("Blogger HTML Copied!");
}
</script>
</body>
</html>
"""

# --- API Routes ---

@app.route('/')
def index():
    return render_template_string(UI_HTML)

@app.route('/api/search')
def search_api():
    q = request.args.get('q')
    t = request.args.get('type')
    url = f"https://api.themoviedb.org/3/search/{t}?api_key={TMDB_API_KEY}&query={q}"
    return jsonify(requests.get(url).json())

@app.route('/api/details')
def details_api():
    id = request.args.get('id')
    t = request.args.get('type')
    url = f"https://api.themoviedb.org/3/{t}/{id}?api_key={TMDB_API_KEY}&append_to_response=credits,videos"
    return jsonify(requests.get(url).json())

@app.route('/api/generate', methods=['POST'])
def generate_api():
    data = request.json
    item = data['item']
    lang = data['lang']
    trailer = data['trailer']
    links = data['links']
    ep_data = data['ep_data']

    title = item.get('title') or item.get('name')
    overview = item.get('overview')
    backdrop = f"https://image.tmdb.org/t/p/original{item['backdrop_path']}"
    date = item.get('release_date') or item.get('first_air_date')
    
    # Cast & Crew Logic
    cast_list = item.get('credits', {}).get('cast', [])[:10]
    cast_html = ""
    for c in cast_list:
        c_img = f"https://image.tmdb.org/t/p/w185{c['profile_path']}" if c['profile_path'] else "https://via.placeholder.com/100"
        cast_html += f'''
        <div class="cast-card">
            <img src="{c_img}" alt="{c['name']}">
            <p>{c['name']}</p>
        </div>'''

    # Download Links Logic
    dl_btns = ""
    for res, link in links.items():
        if link:
            dl_btns += f'<a href="{link}" class="premium-dl-btn" target="_blank">Download {res}</a>'

    # Web Series Logic
    series_html = ""
    if ep_data:
        seasons = ep_data.split('\\n')
        for s in seasons:
            if ':' in s:
                s_name, eps = s.split(':', 1)
                series_html += f'<div class="season-title">{s_name}</div><div class="episodes-grid">'
                for ep in eps.split(','):
                    if '|' in ep:
                        name, url = ep.split('|')
                        series_html += f'<a href="{url.strip()}" target="_blank">{name.strip()}</a>'
                series_html += '</div>'

    # --- FINAL BLOGGER TEMPLATE ---
    blogger_html = f"""<!-- Blogger Post Start -->
<style>
    .p-post-body {{ font-family: 'Helvetica', Arial, sans-serif; color: #222; max-width: 800px; margin: auto; }}
    .p-thumb {{ width: 100%; border-radius: 12px; margin-bottom: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.15); }}
    .p-title {{ font-size: 28px; font-weight: bold; color: #000; margin-bottom: 10px; text-align: center; }}
    .p-meta {{ text-align: center; color: #666; margin-bottom: 20px; font-size: 14px; }}
    .p-heading {{ border-left: 5px solid #ff4757; padding-left: 15px; margin: 25px 0 15px; font-size: 20px; font-weight: bold; }}
    .p-story {{ line-height: 1.8; text-align: justify; }}
    .cast-container {{ display: flex; overflow-x: auto; gap: 15px; padding: 10px 0; scrollbar-width: none; }}
    .cast-card {{ text-align: center; min-width: 90px; }}
    .cast-card img {{ width: 75px; height: 75px; border-radius: 50%; object-fit: cover; border: 3px solid #ff4757; margin-bottom: 5px; }}
    .cast-card p {{ font-size: 11px; margin: 0; font-weight: bold; }}
    .premium-dl-btn {{ display: block; text-align: center; background: linear-gradient(90deg, #ff4757, #ff6b81); color: #fff !important; padding: 15px; border-radius: 50px; text-decoration: none !important; font-weight: bold; margin: 10px 0; transition: 0.3s; box-shadow: 0 4px 15px rgba(255, 71, 87, 0.3); }}
    .premium-dl-btn:hover {{ transform: translateY(-3px); box-shadow: 0 6px 20px rgba(255, 71, 87, 0.5); }}
    .season-title {{ background: #2f3542; color: #fff; padding: 10px 20px; border-radius: 8px; margin-top: 20px; font-weight: bold; }}
    .episodes-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(120px, 1fr)); gap: 10px; margin-top: 10px; }}
    .episodes-grid a {{ background: #f1f2f6; color: #2f3542; text-align: center; padding: 10px; border-radius: 5px; text-decoration: none; font-size: 13px; font-weight: bold; transition: 0.2s; }}
    .episodes-grid a:hover {{ background: #ff4757; color: #fff; }}
    iframe {{ border-radius: 12px; margin-top: 15px; }}
</style>

<div class="p-post-body">
    <img src="{backdrop}" class="p-thumb" alt="{title}">
    <h1 class="p-title">{title}</h1>
    <p class="p-meta">📅 Release: {date} | 🌐 Language: {lang}</p>

    <div class="p-heading">The Storyline</div>
    <p class="p-story">{overview}</p>

    <div class="p-heading">Star Cast</div>
    <div class="cast-container">
        {cast_html}
    </div>

    <div class="p-heading">Official Trailer</div>
    <iframe width="100%" height="350" src="https://www.youtube.com/embed/{trailer}" frameborder="0" allowfullscreen></iframe>

    <div class="p-heading">Download Links</div>
    {dl_btns}

    {series_html}
</div>
<!-- Blogger Post End -->"""

    return jsonify({"html": blogger_html})

if __name__ == '__main__':
    app.run(debug=True)
