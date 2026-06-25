import os
from flask import Flask, render_template_string, request, jsonify
import requests

app = Flask(__name__)

# Your TMDB API Key
TMDB_API_KEY = "7dc544d9253bccc3cfecc1c677f69819"

# --- Generator UI ---
UI_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Premium Blogger Post Creator</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { background: #0b0f19; color: #cbd5e1; font-family: 'Segoe UI', sans-serif; }
        .card { background: #161e2d; border: 1px solid #1e293b; border-radius: 12px; }
        .form-control { background: #0b0f19; border: 1px solid #334155; color: #fff; }
        .form-control:focus { background: #0b0f19; color: #fff; border-color: #3b82f6; box-shadow: none; }
        .search-res { cursor: pointer; transition: 0.3s; }
        .search-res:hover { transform: scale(1.02); }
        .search-res img { border-radius: 8px; border: 1px solid #334155; }
        .season-box { background: #1e293b; padding: 15px; border-radius: 10px; margin-bottom: 15px; border-left: 5px solid #3b82f6; }
        .ep-box { background: #0f172a; padding: 10px; border-radius: 8px; margin-top: 10px; border: 1px dashed #334155; }
        .quality-row { display: flex; gap: 5px; margin-top: 5px; }
        .btn-premium { background: #3b82f6; color: white; font-weight: 600; }
        .code-out { background: #000; color: #10b981; padding: 15px; border-radius: 8px; font-family: monospace; white-space: pre-wrap; display: none; }
    </style>
</head>
<body>
<div class="container py-5">
    <div class="card p-4">
        <h2 class="text-center text-white mb-4">🎬 Blogger Post Generator</h2>
        
        <div class="input-group mb-4">
            <input type="text" id="query" class="form-control" placeholder="Search Movie or Web Series...">
            <select id="type" class="form-select" style="max-width: 150px;">
                <option value="movie">Movie</option>
                <option value="tv">Web Series</option>
            </select>
            <button class="btn btn-premium" onclick="search()">Search</button>
        </div>

        <div id="results" class="row"></div>

        <!-- Editor -->
        <div id="editor" class="mt-4" style="display:none;">
            <hr>
            <h4 class="text-white">Custom Details</h4>
            <input type="text" id="lang" class="form-control mb-3" placeholder="Language (e.g. Hindi - English)">

            <!-- Movie Links -->
            <div id="movie-links-ui">
                <h5>Movie Qualities & Links (Resolution|Link)</h5>
                <textarea id="m_links" class="form-control" placeholder="1080p|https://link.com, 720p|https://link.com"></textarea>
            </div>

            <!-- Series Links (Advanced) -->
            <div id="series-links-ui" style="display:none;">
                <h5>Series Seasons & Episodes</h5>
                <div id="seasons-area"></div>
                <button class="btn btn-sm btn-outline-info mt-2" onclick="addSeason()">+ Add New Season</button>
            </div>

            <button class="btn btn-premium btn-lg w-100 mt-4" onclick="generateHTML()">GENERATE BLOGGER HTML</button>
        </div>

        <div class="mt-5">
            <div id="output" class="code-out"></div>
            <button id="copy-btn" class="btn btn-success w-100 mt-2" style="display:none;" onclick="copyCode()">Copy HTML Code</button>
        </div>
    </div>
</div>

<script>
let selectedItem = null;
let seasonIdx = 0;

async function search() {
    const q = document.getElementById('query').value;
    const t = document.getElementById('type').value;
    const res = await fetch(`/api/search?q=${q}&type=${t}`);
    const data = await res.json();
    let html = '';
    data.results.forEach(item => {
        const title = item.title || item.name;
        const img = item.backdrop_path ? `https://image.tmdb.org/t/p/w500${item.backdrop_path}` : 'https://via.placeholder.com/500x280';
        html += `<div class="col-md-4 mb-3 search-res" onclick="selectItem('${item.id}', '${t}')">
            <img src="${img}" class="img-fluid mb-1">
            <p class="text-center small">${title}</p>
        </div>`;
    });
    document.getElementById('results').innerHTML = html;
}

async function selectItem(id, type) {
    const res = await fetch(`/api/details?id=${id}&type=${type}`);
    selectedItem = await res.json();
    document.getElementById('editor').style.display = 'block';
    if(type === 'tv') {
        document.getElementById('series-links-ui').style.display = 'block';
        document.getElementById('movie-links-ui').style.display = 'none';
    } else {
        document.getElementById('series-links-ui').style.display = 'none';
        document.getElementById('movie-links-ui').style.display = 'block';
    }
}

function addSeason() {
    seasonIdx++;
    const div = document.createElement('div');
    div.className = 'season-box';
    div.id = `season-${seasonIdx}`;
    div.innerHTML = `
        <input type="text" class="form-control mb-2 fw-bold" placeholder="Season Name (e.g. Season 01)">
        <div class="ep-area"></div>
        <button class="btn btn-sm btn-dark mt-2" onclick="addEpisode(this)">+ Add Episode</button>
    `;
    document.getElementById('seasons-area').appendChild(div);
}

function addEpisode(btn) {
    const epArea = btn.previousElementSibling;
    const div = document.createElement('div');
    div.className = 'ep-box';
    div.innerHTML = `
        <input type="text" class="form-control form-control-sm mb-2" placeholder="Episode Name (e.g. Episode 01)">
        <textarea class="form-control form-control-sm" placeholder="Qualities (Format: 1080p|link, 720p|link)"></textarea>
    `;
    epArea.appendChild(div);
}

async function generateHTML() {
    const lang = document.getElementById('lang').value;
    const m_links = document.getElementById('m_links').value;
    
    // Get Series Data
    const seriesData = [];
    document.querySelectorAll('.season-box').forEach(sBox => {
        const sName = sBox.querySelector('input').value;
        const episodes = [];
        sBox.querySelectorAll('.ep-box').forEach(eBox => {
            episodes.push({
                name: eBox.querySelector('input').value,
                links: eBox.querySelector('textarea').value
            });
        });
        seriesData.push({ season: sName, episodes });
    });

    const res = await fetch('/api/generate', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({item: selectedItem, lang, m_links, seriesData})
    });
    const data = await res.json();
    document.getElementById('output').innerText = data.html;
    document.getElementById('output').style.display = 'block';
    document.getElementById('copy-btn').style.display = 'block';
}

function copyCode() {
    navigator.clipboard.writeText(document.getElementById('output').innerText);
    alert("Copied!");
}
</script>
</body>
</html>
"""

# --- Backend API ---

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
    url = f"https://api.themoviedb.org/3/{t}/{id}?api_key={TMDB_API_KEY}&append_to_response=credits,videos,images"
    return jsonify(requests.get(url).json())

@app.route('/api/generate', methods=['POST'])
def generate_api():
    req = request.json
    item = req['item']
    lang = req['lang']
    m_links = req['m_links']
    seriesData = req['seriesData']

    title = item.get('title') or item.get('name')
    overview = item.get('overview')
    backdrop = f"https://image.tmdb.org/t/p/original{item['backdrop_path']}"
    date = item.get('release_date') or item.get('first_air_date')
    
    # Trailer
    trailer_id = ""
    for v in item.get('videos', {}).get('results', []):
        if v['site'] == 'YouTube': trailer_id = v['key']; break

    # Gallery
    gallery_html = "".join([f'<img src="https://image.tmdb.org/t/p/w500{img["file_path"]}">' for img in item.get('images', {}).get('backdrops', [])[:6]])

    # Cast
    cast_html = "".join([f'<div class="c-card"><img src="https://image.tmdb.org/t/p/w185{c["profile_path"]}"><p>{c["name"]}</p></div>' for c in item.get('credits', {}).get('cast', [])[:10] if c['profile_path']])

    # Movie Links Grid (2 per row)
    movie_btn_html = ""
    if m_links:
        movie_btn_html = '<div class="m-grid">'
        for l in m_links.split(','):
            if '|' in l:
                q, url = l.split('|')
                movie_btn_html += f'<a href="{url.strip()}" class="btn-dl">{q.strip()} Download</a>'
        movie_btn_html += '</div>'

    # Series System
    series_btn_html = ""
    for s in seriesData:
        series_btn_html += f'<div class="s-title">{s["season"]}</div>'
        for ep in s['episodes']:
            series_btn_html += f'<div class="ep-row"><span>{ep["name"]}</span><div class="ep-links">'
            for l in ep['links'].split(','):
                if '|' in l:
                    q, url = l.split('|')
                    series_btn_html += f'<a href="{url.strip()}">{q.strip()}</a>'
            series_btn_html += '</div></div>'

    # FINAL HTML
    final_html = f"""
<!-- Blogger Post -->
<style>
    .post-box {{ background: #0f172a; color: #e2e8f0; padding: 20px; border-radius: 15px; font-family: sans-serif; }}
    .post-img {{ width: 100%; border-radius: 12px; box-shadow: 0 5px 20px rgba(0,0,0,0.5); }}
    .post-title {{ color: #3b82f6; font-size: 28px; font-weight: 800; text-align: center; margin-top: 15px; }}
    .post-meta {{ text-align: center; font-size: 14px; opacity: 0.7; margin-bottom: 20px; }}
    .h-head {{ border-left: 4px solid #3b82f6; padding-left: 10px; margin: 25px 0 10px; font-weight: bold; font-size: 18px; color: #fff; }}
    .c-slider {{ display: flex; overflow-x: auto; gap: 15px; padding-bottom: 10px; }}
    .c-card {{ min-width: 80px; text-align: center; }}
    .c-card img {{ width: 65px; height: 65px; border-radius: 50%; object-fit: cover; border: 2px solid #3b82f6; }}
    .c-card p {{ font-size: 10px; margin-top: 5px; }}
    .gallery-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }}
    .gallery-grid img {{ width: 100%; border-radius: 8px; }}
    .m-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-top: 15px; }}
    .btn-dl {{ background: linear-gradient(to right, #3b82f6, #2563eb); color: #fff !important; text-align: center; padding: 12px; border-radius: 8px; font-weight: bold; text-decoration: none !important; }}
    .s-title {{ background: #1e293b; padding: 10px; margin-top: 15px; font-weight: bold; border-radius: 5px; color: #3b82f6; }}
    .ep-row {{ display: flex; justify-content: space-between; align-items: center; padding: 10px; border-bottom: 1px solid #1e293b; }}
    .ep-links {{ display: flex; gap: 5px; }}
    .ep-links a {{ background: #3b82f6; color: #fff !important; padding: 4px 10px; border-radius: 4px; font-size: 12px; font-weight: bold; text-decoration: none !important; }}
    .unlock-btn {{ display: block; background: #fbbf24; color: #000 !important; text-align: center; padding: 15px; border-radius: 10px; font-weight: 800; margin: 20px 0; cursor: pointer; }}
</style>

<div class="post-box">
    <img src="{backdrop}" class="post-img">
    <h1 class="post-title">{title}</h1>
    <p class="post-meta">📅 {date} | 🌐 {lang}</p>

    <div class="h-head">STORYLINE</div>
    <p style="font-size: 15px; line-height: 1.6; color: #94a3b8;">{overview}</p>

    <div class="h-head">CAST</div>
    <div class="c-slider">{cast_html}</div>

    <div class="h-head">SCREENSHOTS</div>
    <div class="gallery-grid">{gallery_html}</div>

    <div class="h-head">OFFICIAL TRAILER</div>
    <iframe width="100%" height="315" src="https://www.youtube.com/embed/{trailer_id}" frameborder="0" allowfullscreen style="border-radius:10px;"></iframe>

    <div class="unlock-btn" onclick="document.getElementById('dl-section').style.display='block';this.style.display='none'">🔓 UNLOCK DOWNLOAD LINKS</div>

    <div id="dl-section" style="display:none;">
        <div class="h-head">DOWNLOAD OPTIONS</div>
        {movie_btn_html}
        {series_btn_html}
    </div>
</div>
"""
    return jsonify({"html": final_html})

if __name__ == '__main__':
    app.run(debug=True)
