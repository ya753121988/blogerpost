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
    <title>Advanced Movie & Series Post Creator</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { background: #0f172a; color: #f1f5f9; font-family: 'Inter', sans-serif; padding-bottom: 50px; }
        .card { background: #1e293b; border: 1px solid #334155; border-radius: 12px; margin-top: 20px; }
        .search-item { cursor: pointer; transition: 0.3s; margin-bottom: 15px; border: 1px solid transparent; border-radius: 10px; overflow: hidden; }
        .search-item:hover { border-color: #38bdf8; transform: translateY(-5px); }
        .form-control, .form-select { background: #0f172a; border: 1px solid #334155; color: #fff; border-radius: 8px; }
        .form-control:focus { background: #0f172a; color: #fff; border-color: #38bdf8; box-shadow: none; }
        
        .section-header { background: #334155; padding: 10px 15px; border-radius: 8px; margin: 20px 0 10px; font-weight: bold; color: #38bdf8; }
        .quality-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; margin-top: 10px; }
        .quality-grid input { font-size: 12px; }
        
        .season-box { background: #1e293b; padding: 20px; border-radius: 12px; border: 1px solid #334155; margin-bottom: 20px; }
        .episode-box { background: #0f172a; padding: 15px; border-radius: 10px; border-left: 4px solid #38bdf8; margin-top: 15px; }
        
        .btn-gen { background: linear-gradient(90deg, #0ea5e9, #2563eb); border: none; font-weight: 800; padding: 15px; border-radius: 12px; color: #fff; }
        .code-out { background: #000; color: #10b981; padding: 20px; border-radius: 10px; font-family: monospace; white-space: pre-wrap; display: none; margin-top: 20px; }
    </style>
</head>
<body>
<div class="container mt-4">
    <div class="card p-4">
        <h3 class="text-center mb-4">🎬 Blogger Post Generator (Pro)</h3>
        
        <div class="row g-2 mb-4">
            <div class="col-md-7"><input type="text" id="query" class="form-control" placeholder="Search Movie or Series..."></div>
            <div class="col-md-3">
                <select id="type" class="form-select">
                    <option value="movie">Movie</option>
                    <option value="tv">Web Series</option>
                </select>
            </div>
            <div class="col-md-2"><button class="btn btn-primary w-100" onclick="search()">Search</button></div>
        </div>

        <div id="results" class="row"></div>

        <!-- Detail Editor Area -->
        <div id="editor" style="display:none;">
            <div class="section-header">1. BASIC DETAILS (Editable)</div>
            <div class="row g-3">
                <div class="col-md-12"><label>Title</label><input type="text" id="title" class="form-control"></div>
                <div class="col-md-4"><label>Release Date</label><input type="text" id="release" class="form-control"></div>
                <div class="col-md-4"><label>Language</label><input type="text" id="lang" class="form-control" placeholder="e.g. Dual Audio [Hindi-English]"></div>
                <div class="col-md-4"><label>YouTube Trailer ID</label><input type="text" id="trailer" class="form-control"></div>
                <div class="col-md-12"><label>Storyline</label><textarea id="story" class="form-control" rows="4"></textarea></div>
            </div>

            <!-- Download Links Logic -->
            <div id="movie-links" style="display:none;">
                <div class="section-header">2. DOWNLOAD LINKS (Movie)</div>
                <div class="quality-grid" id="m-q-grid">
                    <div><label>8K</label><input type="text" data-q="8K" class="form-control mq" placeholder="Link"></div>
                    <div><label>4K</label><input type="text" data-q="4K" class="form-control mq" placeholder="Link"></div>
                    <div><label>2K</label><input type="text" data-q="2K" class="form-control mq" placeholder="Link"></div>
                    <div><label>1080p</label><input type="text" data-q="1080p" class="form-control mq" placeholder="Link"></div>
                    <div><label>720p</label><input type="text" data-q="720p" class="form-control mq" placeholder="Link"></div>
                    <div><label>480p</label><input type="text" data-q="480p" class="form-control mq" placeholder="Link"></div>
                    <div><label>360p</label><input type="text" data-q="360p" class="form-control mq" placeholder="Link"></div>
                    <div><label>140p</label><input type="text" data-q="140p" class="form-control mq" placeholder="Link"></div>
                </div>
            </div>

            <div id="series-links" style="display:none;">
                <div class="section-header">2. SEASONS & EPISODES (Series)</div>
                <div id="seasons-container"></div>
                <button class="btn btn-outline-info w-100" onclick="addSeason()">+ Add New Season</button>
            </div>

            <button class="btn btn-gen w-100 mt-5" onclick="generateHTML()">GENERATE BLOGGER HTML</button>
            
            <div id="output" class="code-out"></div>
            <button id="copy-btn" class="btn btn-success w-100 mt-2" style="display:none;" onclick="copyCode()">Copy Code</button>
        </div>
    </div>
</div>

<script>
let selectedData = null;
let seasonCount = 0;

async function search() {
    const q = document.getElementById('query').value;
    const t = document.getElementById('type').value;
    const res = await fetch(`/api/search?q=${q}&type=${t}`);
    const data = await res.json();
    let html = '';
    data.results.forEach(item => {
        const title = item.title || item.name;
        const img = item.backdrop_path ? `https://image.tmdb.org/t/p/w500${item.backdrop_path}` : 'https://via.placeholder.com/500x280?text=No+Thumbnail';
        html += `<div class="col-md-4 search-item" onclick="selectItem('${item.id}', '${t}')">
            <img src="${img}" class="img-fluid">
            <p class="text-center p-2 m-0 small">${title}</p>
        </div>`;
    });
    document.getElementById('results').innerHTML = html;
}

async function selectItem(id, type) {
    const res = await fetch(`/api/details?id=${id}&type=${type}`);
    selectedData = await res.json();
    
    // Auto-fill Editor
    document.getElementById('title').value = selectedData.title || selectedData.name;
    document.getElementById('release').value = selectedData.release_date || selectedData.first_air_date;
    document.getElementById('story').value = selectedData.overview;
    
    // Auto-fill Trailer ID
    let trailerID = '';
    selectedData.videos.results.forEach(v => {
        if(v.type === 'Trailer' && v.site === 'YouTube') trailerID = v.key;
    });
    document.getElementById('trailer').value = trailerID;

    // Show/Hide Sections
    document.getElementById('editor').style.display = 'block';
    document.getElementById('results').innerHTML = '';
    if(type === 'movie') {
        document.getElementById('movie-links').style.display = 'block';
        document.getElementById('series-links').style.display = 'none';
    } else {
        document.getElementById('movie-links').style.display = 'none';
        document.getElementById('series-links').style.display = 'block';
    }
}

function addSeason() {
    seasonCount++;
    const sId = `season_${seasonCount}`;
    const sDiv = document.createElement('div');
    sDiv.className = 'season-box';
    sDiv.id = sId;
    sDiv.innerHTML = `
        <div class="d-flex justify-content-between mb-3">
            <input type="text" class="form-control s-name w-50" placeholder="Season Name (e.g. Season 01)">
            <button class="btn btn-sm btn-info" onclick="addEpisode('${sId}')">+ Add Episode</button>
        </div>
        <div class="ep-container"></div>
    `;
    document.getElementById('seasons-container').appendChild(sDiv);
}

function addEpisode(sId) {
    const epContainer = document.querySelector(`#${sId} .ep-container`);
    const epDiv = document.createElement('div');
    epDiv.className = 'episode-box';
    epDiv.innerHTML = `
        <input type="text" class="form-control ep-name mb-3" placeholder="Episode Name (e.g. Episode 01)">
        <div class="quality-grid">
            <div><label>8K</label><input type="text" data-q="8K" class="form-control eq" placeholder="Link"></div>
            <div><label>4K</label><input type="text" data-q="4K" class="form-control eq" placeholder="Link"></div>
            <div><label>2K</label><input type="text" data-q="2K" class="form-control eq" placeholder="Link"></div>
            <div><label>1080p</label><input type="text" data-q="1080p" class="form-control eq" placeholder="Link"></div>
            <div><label>720p</label><input type="text" data-q="720p" class="form-control eq" placeholder="Link"></div>
            <div><label>480p</label><input type="text" data-q="480p" class="form-control eq" placeholder="Link"></div>
            <div><label>360p</label><input type="text" data-q="360p" class="form-control eq" placeholder="Link"></div>
            <div><label>140p</label><input type="text" data-q="140p" class="form-control eq" placeholder="Link"></div>
        </div>
    `;
    epContainer.appendChild(epDiv);
}

async function generateHTML() {
    // Collect All Data from Editor
    const customData = {
        title: document.getElementById('title').value,
        release: document.getElementById('release').value,
        lang: document.getElementById('lang').value,
        trailer: document.getElementById('trailer').value,
        story: document.getElementById('story').value,
        type: document.getElementById('type').value
    };

    // Movie Links
    const movieLinks = [];
    document.querySelectorAll('.mq').forEach(inp => {
        if(inp.value) movieLinks.push({ q: inp.dataset.q, url: inp.value });
    });

    // Series Links
    const seasons = [];
    document.querySelectorAll('.season-box').forEach(sBox => {
        const sName = sBox.querySelector('.s-name').value;
        const episodes = [];
        sBox.querySelectorAll('.episode-box').forEach(eBox => {
            const eName = eBox.querySelector('.ep-name').value;
            const eLinks = [];
            eBox.querySelectorAll('.eq').forEach(ein => {
                if(ein.value) eLinks.push({ q: ein.dataset.q, url: ein.value });
            });
            episodes.push({ name: eName, links: eLinks });
        });
        seasons.push({ name: sName, episodes: episodes });
    });

    const res = await fetch('/api/generate', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ item: selectedData, custom: customData, movieLinks, seasons })
    });
    const result = await res.json();
    document.getElementById('output').innerText = result.html;
    document.getElementById('output').style.display = 'block';
    document.getElementById('copy-btn').style.display = 'block';
}

function copyCode() {
    navigator.clipboard.writeText(document.getElementById('output').innerText);
    alert("HTML Code Copied!");
}
</script>
</body>
</html>
"""

# --- Backend APIs ---

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
    data = request.json
    item = data['item']
    c = data['custom']
    movieLinks = data['movieLinks']
    seasons = data['seasons']

    backdrop = f"https://image.tmdb.org/t/p/original{item['backdrop_path']}"
    
    # Gallery
    gallery_html = ""
    for img in item.get('images', {}).get('backdrops', [])[:6]:
        gallery_html += f'<img src="https://image.tmdb.org/t/p/w500{img["file_path"]}" alt="Screen">'

    # Cast Slider
    cast_html = ""
    for person in item.get('credits', {}).get('cast', [])[:12]:
        c_img = f"https://image.tmdb.org/t/p/w185{person['profile_path']}" if person['profile_path'] else "https://via.placeholder.com/100"
        cast_html += f'<div class="cast-item"><img src="{c_img}"><p>{person["name"]}</p></div>'

    # Movie Links HTML (2 per row)
    movie_dl_html = '<div class="dl-grid">'
    for link in movieLinks:
        movie_dl_html += f'<a href="{link["url"]}" class="dl-btn">{link["q"]} Download</a>'
    movie_dl_html += '</div>'

    # Series Logic
    series_dl_html = ""
    for s in seasons:
        series_dl_html += f'<div class="s-title">{s["name"]}</div>'
        for ep in s['episodes']:
            series_dl_html += f'<div class="ep-row"><span>{ep["name"]}</span><div class="ep-links">'
            for l in ep['links']:
                series_dl_html += f'<a href="{l["url"]}">{l["q"]}</a>'
            series_dl_html += '</div></div>'

    # --- THE FINAL BLOGGER HTML TEMPLATE ---
    blogger_html = f"""
<style>
    .p-box {{ background: #0b0f19; color: #e2e8f0; padding: 25px; border-radius: 20px; font-family: 'Segoe UI', sans-serif; }}
    .p-thumb {{ width: 100%; border-radius: 15px; box-shadow: 0 10px 30px rgba(0,0,0,0.5); }}
    .p-title {{ color: #38bdf8; font-size: 32px; font-weight: 800; text-align: center; margin-top: 20px; }}
    .p-info {{ text-align: center; font-size: 14px; opacity: 0.7; margin-bottom: 30px; }}
    .h-head {{ border-left: 5px solid #38bdf8; padding-left: 15px; margin: 30px 0 15px; font-size: 20px; font-weight: bold; color: #fff; text-transform: uppercase; }}
    
    .c-slider {{ display: flex; overflow-x: auto; gap: 15px; padding-bottom: 10px; }}
    .c-slider::-webkit-scrollbar {{ display: none; }}
    .cast-item {{ min-width: 90px; text-align: center; }}
    .cast-item img {{ width: 75px; height: 75px; border-radius: 50%; object-fit: cover; border: 3px solid #38bdf8; }}
    .cast-item p {{ font-size: 11px; margin-top: 5px; color: #94a3b8; font-weight: bold; }}
    
    .g-grid {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; }}
    .g-grid img {{ width: 100%; border-radius: 10px; transition: 0.3s; }}
    
    .dl-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-top: 20px; }}
    .dl-btn {{ background: linear-gradient(90deg, #38bdf8, #2563eb); color: #fff !important; text-align: center; padding: 15px; border-radius: 12px; font-weight: bold; text-decoration: none !important; }}
    
    .s-title {{ background: #1e293b; padding: 12px 20px; border-radius: 8px; margin-top: 20px; color: #38bdf8; font-weight: bold; }}
    .ep-row {{ display: flex; justify-content: space-between; align-items: center; padding: 12px; border-bottom: 1px solid #334155; }}
    .ep-links {{ display: flex; gap: 8px; flex-wrap: wrap; }}
    .ep-links a {{ background: #38bdf8; color: #000 !important; padding: 4px 10px; border-radius: 5px; font-size: 12px; font-weight: bold; text-decoration: none !important; }}
    
    .unlock-btn {{ display: block; background: #fbbf24; color: #000 !important; text-align: center; padding: 18px; border-radius: 15px; font-size: 18px; font-weight: 800; cursor: pointer; margin: 30px 0; }}
</style>

<div class="p-box">
    <img src="{backdrop}" class="p-thumb">
    <h1 class="p-title">{c['title']}</h1>
    <div class="p-info">📅 {c['release']} | 🌐 {c['lang']}</div>

    <div class="h-head">Synopsis / Storyline</div>
    <p style="line-height: 1.8; text-align: justify; color: #94a3b8;">{c['story']}</p>

    <div class="h-head">Star Cast</div>
    <div class="c-slider">{cast_html}</div>

    <div class="h-head">ScreenShots / Gallery</div>
    <div class="g-grid">{gallery_html}</div>

    <div class="h-head">Official Trailer</div>
    <div style="position:relative;padding-bottom:56.25%;height:0;overflow:hidden;border-radius:15px;">
        <iframe style="position:absolute;top:0;left:0;width:100%;height:100%;" src="https://www.youtube.com/embed/{c['trailer']}" frameborder="0" allowfullscreen></iframe>
    </div>

    <div class="unlock-btn" onclick="document.getElementById('dl-area').style.display='block';this.style.display='none'">🔓 UNLOCK DOWNLOAD LINKS</div>

    <div id="dl-area" style="display:none;">
        <div class="h-head">Download Options</div>
        {movie_dl_html if c['type'] == 'movie' else series_dl_html}
    </div>
</div>
"""
    return jsonify({"html": blogger_html})

if __name__ == '__main__':
    app.run(debug=True)
