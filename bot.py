import os
import json
import base64
from flask import Flask, render_template_string, request, jsonify
import requests

app = Flask(__name__)

# TMDB API Key & Ad Links
TMDB_API_KEY = "7dc544d9253bccc3cfecc1c677f69819"
AD_LINKS = [
    "https://www.effectivecpmnetwork.com/xqmb731x1?key=0267816362fc4320de630e064b317db1",
    "https://www.effectivecpmnetwork.com/qw8kn1x7h?key=5fdb7c5ecd8aff08f9ffb43334a9d3e6",
    "https://www.effectivecpmnetwork.com/vrstnq7p2s?key=257dbfc9920ae1f06a0a7b33cbeb410d",
    "https://www.effectivecpmnetwork.com/tpxm5krbv?key=a9a3e08835e93a54ffdaad1597bfe6cb",
    "https://www.effectivecpmnetwork.com/wsck7gj1?key=2f49c16a80560c9b810503b65da32363",
    "https://www.effectivecpmnetwork.com/iqs1w6v06c?key=19b65cbb2964d6f0a3c934b5ee855f18"
]

UI_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Ultimate Blogger Generator PRO</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        :root { --accent: #38bdf8; --bg: #0b0f1a; --card: #161e2e; }
        body { background: var(--bg); color: #e2e8f0; font-family: 'Inter', sans-serif; }
        .editor-card { background: var(--card); border: 1px solid #1e293b; border-radius: 15px; margin-top: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.5); }
        .form-control, .form-select { background: #0f172a; border: 1px solid #334155; color: #fff; border-radius: 8px; }
        .form-control:focus { background: #0f172a; border-color: var(--accent); color: #fff; box-shadow: none; }
        .section-title { border-left: 4px solid var(--accent); padding-left: 15px; margin: 30px 0 15px; font-weight: bold; text-transform: uppercase; color: var(--accent); }
        
        /* Grid Layouts */
        .grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
        .quality-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 8px; margin-top: 5px; }
        .quality-grid input { font-size: 11px; padding: 5px; }
        
        .cast-box, .screenshot-box { background: #0f172a; padding: 10px; border-radius: 8px; margin-bottom: 10px; border: 1px solid #1e293b; }
        .season-item { background: #1e293b; border-radius: 12px; padding: 15px; margin-bottom: 20px; border: 1px solid #334155; }
        .episode-item { background: #0f172a; border-radius: 10px; padding: 12px; margin-top: 10px; border-left: 3px solid var(--accent); }
        
        .btn-sky { background: var(--accent); color: #000; font-weight: bold; border: none; }
        .btn-sky:hover { background: #0ea5e9; }
        .code-box { background: #000; color: #10b981; padding: 15px; border-radius: 10px; font-family: monospace; white-space: pre-wrap; display: none; }
    </style>
</head>
<body>
<div class="container my-5">
    <div class="editor-card p-4">
        <h2 class="text-center fw-bold mb-4">🚀 ULTIMATE BLOGGER POST GENERATOR</h2>
        
        <!-- Import Tool -->
        <div class="mb-4 p-3 border border-dashed rounded border-info">
            <label class="text-info fw-bold">RE-EDIT OLD POST?</label>
            <textarea id="import_html" class="form-control mb-2" placeholder="Paste your old Blogger HTML code here to edit..."></textarea>
            <button class="btn btn-info btn-sm w-100 fw-bold" onclick="importOldCode()">IMPORT & EDIT</button>
        </div>

        <div class="row g-2 mb-4">
            <div class="col-md-7"><input type="text" id="query" class="form-control" placeholder="Search Movie/Series Name..."></div>
            <div class="col-md-3">
                <select id="type" class="form-select">
                    <option value="movie">Movie</option><option value="tv">Web Series</option>
                </select>
            </div>
            <div class="col-md-2"><button class="btn btn-sky w-100" onclick="searchTMDB()">SEARCH</button></div>
        </div>

        <div id="results" class="row"></div>

        <!-- Editor Area -->
        <div id="editor_area" style="display:none;">
            <div class="section-title">1. Edit Details (Auto-Filled)</div>
            <div class="row g-3">
                <div class="col-md-6"><label>Main Title</label><input type="text" id="m_title" class="form-control"></div>
                <div class="col-md-6"><label>Backdrop Image (Landscape)</label><input type="text" id="m_backdrop" class="form-control"></div>
                <div class="col-md-4"><label>Language</label><input type="text" id="m_lang" class="form-control"></div>
                <div class="col-md-4"><label>Release Date</label><input type="text" id="m_date" class="form-control"></div>
                <div class="col-md-4"><label>YouTube Trailer ID</label><input type="text" id="m_trailer" class="form-control"></div>
                <div class="col-md-12"><label>Storyline</label><textarea id="m_story" class="form-control" rows="3"></textarea></div>
                <div class="col-md-6"><label>Director Name</label><input type="text" id="m_dir_name" class="form-control"></div>
                <div class="col-md-6"><label>Director Photo URL</label><input type="text" id="m_dir_img" class="form-control"></div>
            </div>

            <div class="section-title">2. Cast & Gallery (Edit if needed)</div>
            <div id="cast_list" class="row"></div>
            <div id="gallery_list" class="row mt-3"></div>

            <div class="section-title">3. Ad Control</div>
            <div class="col-md-4">
                <label>Pop-up Ads per Click (1-10)</label>
                <select id="m_ad_count" class="form-select">
                    <script>for(let i=1;i<=10;i++) document.write(`<option value="${i}">${i} Ads</option>`)</script>
                </select>
            </div>

            <!-- Movie Links Grid (2 per line) -->
            <div id="movie_links_ui" style="display:none;">
                <div class="section-title">4. Movie Download Links (8K to 140p)</div>
                <div class="quality-grid" id="movie_q_boxes">
                    <div>8K<input type="text" data-q="8K" class="form-control mq"></div>
                    <div>4K<input type="text" data-q="4K" class="form-control mq"></div>
                    <div>2K<input type="text" data-q="2K" class="form-control mq"></div>
                    <div>1080p<input type="text" data-q="1080p" class="form-control mq"></div>
                    <div>720p<input type="text" data-q="720p" class="form-control mq"></div>
                    <div>480p<input type="text" data-q="480p" class="form-control mq"></div>
                    <div>360p<input type="text" data-q="360p" class="form-control mq"></div>
                    <div>140p<input type="text" data-q="140p" class="form-control mq"></div>
                </div>
            </div>

            <!-- Series Links UI -->
            <div id="series_links_ui" style="display:none;">
                <div class="section-title">4. Seasons & Episodes</div>
                <div id="season_container"></div>
                <button class="btn btn-outline-info w-100 fw-bold mt-3" onclick="addSeason()">+ ADD SEASON</button>
            </div>

            <button class="btn btn-sky btn-lg w-100 mt-5 py-3" onclick="generateHTML()">🚀 GENERATE FINAL BLOGGER HTML</button>
            <div id="output" class="code-box mt-3"></div>
            <button id="copyBtn" class="btn btn-success w-100 mt-2 fw-bold" style="display:none;" onclick="copyCode()">COPY CODE</button>
        </div>
    </div>
</div>

<script>
let seasonCount = 0;
let tmdbData = null;

async function searchTMDB() {
    const q = document.getElementById('query').value;
    const t = document.getElementById('type').value;
    const res = await fetch(`/api/search?q=${q}&type=${t}`);
    const data = await res.json();
    let html = '';
    data.results.forEach(item => {
        html += `<div class="col-md-4 mb-3" onclick="selectItem('${item.id}', '${t}')" style="cursor:pointer">
            <div class="card bg-dark border-secondary p-1">
                <img src="https://image.tmdb.org/t/p/w500${item.backdrop_path}" class="img-fluid rounded">
                <p class="text-center small mt-1 mb-0">${item.title || item.name}</p>
            </div>
        </div>`;
    });
    document.getElementById('results').innerHTML = html;
}

async function selectItem(id, type) {
    const res = await fetch(`/api/details?id=${id}&type=${type}`);
    tmdbData = await res.json();
    document.getElementById('results').innerHTML = '';
    document.getElementById('editor_area').style.display = 'block';
    
    // Auto-fill inputs
    document.getElementById('m_title').value = tmdbData.title || tmdbData.name;
    document.getElementById('m_backdrop').value = `https://image.tmdb.org/t/p/original${tmdbData.backdrop_path}`;
    document.getElementById('m_date').value = tmdbData.release_date || tmdbData.first_air_date;
    document.getElementById('m_story').value = tmdbData.overview;
    
    const dir = tmdbData.credits.crew.find(c => c.job === 'Director');
    document.getElementById('m_dir_name').value = dir ? dir.name : '';
    document.getElementById('m_dir_img').value = dir ? `https://image.tmdb.org/t/p/w185${dir.profile_path}` : '';
    
    const trailer = tmdbData.videos.results.find(v => v.type === 'Trailer');
    document.getElementById('m_trailer').value = trailer ? trailer.key : '';

    // Cast & Gallery list
    let c_html = '';
    tmdbData.credits.cast.slice(0, 6).forEach((c, i) => {
        c_html += `<div class="col-md-4 cast-box">
            <input type="text" class="form-control form-control-sm mb-1 cast-n" value="${c.name}">
            <input type="text" class="form-control form-control-sm cast-i" value="https://image.tmdb.org/t/p/w185${c.profile_path}">
        </div>`;
    });
    document.getElementById('cast_list').innerHTML = c_html;

    let g_html = '';
    tmdbData.images.backdrops.slice(0, 4).forEach((img, i) => {
        g_html += `<div class="col-md-6 screenshot-box">
            <input type="text" class="form-control form-control-sm g-img" value="https://image.tmdb.org/t/p/w500${img.file_path}">
        </div>`;
    });
    document.getElementById('gallery_list').innerHTML = g_html;

    if(type === 'movie') {
        document.getElementById('movie_links_ui').style.display = 'block';
        document.getElementById('series_links_ui').style.display = 'none';
    } else {
        document.getElementById('movie_links_ui').style.display = 'none';
        document.getElementById('series_links_ui').style.display = 'block';
    }
}

function addSeason(name = "") {
    seasonCount++;
    const sId = `season_${seasonCount}`;
    const sNum = String(seasonCount).padStart(2, '0');
    const sName = name || `Season ${sNum}`;
    
    const div = document.createElement('div');
    div.className = 'season-item';
    div.id = sId;
    div.innerHTML = `
        <div class="d-flex justify-content-between mb-2">
            <input type="text" class="form-control w-50 fw-bold s-title" value="${sName}">
            <button class="btn btn-sm btn-info fw-bold" onclick="addEpisode('${sId}')">+ ADD EPISODE</button>
        </div>
        <div class="ep-container" data-count="0"></div>
    `;
    document.getElementById('season_container').appendChild(div);
}

function addEpisode(sId, name = "", links = {}) {
    const epCont = document.querySelector(`#${sId} .ep-container`);
    let count = parseInt(epCont.dataset.count) + 1;
    epCont.dataset.count = count;
    const eNum = String(count).padStart(2, '0');
    const epName = name || `Episode ${eNum}`;
    
    const div = document.createElement('div');
    div.className = 'episode-item';
    div.innerHTML = `
        <input type="text" class="form-control form-control-sm mb-2 fw-bold e-title" value="${epName}">
        <div class="quality-grid">
            ${['8K','4K','2K','1080p','720p','480p','360p','140p'].map(q => 
                `<div>${q}<input type="text" data-q="${q}" class="form-control eq" value="${links[q] || ''}"></div>`
            ).join('')}
        </div>
    `;
    epCont.appendChild(div);
}

// IMPORT FEATURE (Re-editing)
function importOldCode() {
    try {
        const html = document.getElementById('import_html').value;
        const b64 = html.match(/<!--DATA:(.*)-->/)[1];
        const data = JSON.parse(atob(b64));
        
        document.getElementById('editor_area').style.display = 'block';
        document.getElementById('m_title').value = data.title;
        document.getElementById('m_backdrop').value = data.backdrop;
        document.getElementById('m_lang').value = data.lang;
        document.getElementById('m_date').value = data.date;
        document.getElementById('m_story').value = data.story;
        document.getElementById('m_dir_name').value = data.dir_name;
        document.getElementById('m_dir_img').value = data.dir_img;
        document.getElementById('m_ad_count').value = data.ad_count;
        document.getElementById('m_trailer').value = data.trailer;

        if(data.type === 'movie') {
            document.getElementById('movie_links_ui').style.display = 'block';
            data.movieLinks.forEach(l => {
                const inp = document.querySelector(`.mq[data-q="${l.q}"]`);
                if(inp) inp.value = l.url;
            });
        } else {
            document.getElementById('series_links_ui').style.display = 'block';
            document.getElementById('season_container').innerHTML = '';
            seasonCount = 0;
            data.seasons.forEach(s => {
                addSeason(s.name);
                const sId = `season_${seasonCount}`;
                s.episodes.forEach(e => {
                    const lObj = {};
                    e.links.forEach(ln => lObj[ln.q] = ln.url);
                    addEpisode(sId, e.name, lObj);
                });
            });
        }
        alert("Import Successful! Now you can edit and re-generate.");
    } catch(e) {
        alert("Invalid HTML! Make sure this post was generated by this tool.");
    }
}

async function generateHTML() {
    const cast = [];
    document.querySelectorAll('.cast-box').forEach(b => {
        cast.push({ name: b.querySelector('.cast-n').value, img: b.querySelector('.cast-i').value });
    });

    const gallery = [];
    document.querySelectorAll('.g-img').forEach(i => gallery.push(i.value));

    const movieLinks = [];
    document.querySelectorAll('.mq').forEach(i => { if(i.value) movieLinks.push({q: i.dataset.q, url: i.value}); });

    const seasons = [];
    document.querySelectorAll('.season-item').forEach(sBox => {
        const eps = [];
        sBox.querySelectorAll('.episode-item').forEach(eBox => {
            const eLinks = [];
            eBox.querySelectorAll('.eq').forEach(ei => { if(ei.value) eLinks.push({q: ei.dataset.q, url: ei.value}); });
            eps.push({ name: eBox.querySelector('.e-title').value, links: eLinks });
        });
        seasons.push({ name: sBox.querySelector('.s-title').value, episodes: eps });
    });

    const fullData = {
        title: document.getElementById('m_title').value,
        backdrop: document.getElementById('m_backdrop').value,
        lang: document.getElementById('m_lang').value,
        date: document.getElementById('m_date').value,
        story: document.getElementById('m_story').value,
        dir_name: document.getElementById('m_dir_name').value,
        dir_img: document.getElementById('m_dir_img').value,
        trailer: document.getElementById('m_trailer').value,
        ad_count: document.getElementById('m_ad_count').value,
        cast, gallery, movieLinks, seasons,
        type: document.getElementById('type').value
    };

    const res = await fetch('/api/generate', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(fullData)
    });
    const result = await res.json();
    document.getElementById('output').innerText = result.html;
    document.getElementById('output').style.display = 'block';
    document.getElementById('copyBtn').style.display = 'block';
}

function copyCode() {
    navigator.clipboard.writeText(document.getElementById('output').innerText);
    alert("Copied!");
}
</script>
</body>
</html>
"""

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
    
    # Meta data for re-editing
    json_meta = base64.b64encode(json.dumps(data).encode()).decode()
    
    cast_html = "".join([f'<div class="cast-c"><img src="{c["img"]}"><p>{c["name"]}</p></div>' for c in data['cast']])
    gallery_html = "".join([f'<img src="{img}">' for img in data['gallery']])
    
    # MOVIE BUTTONS (2 PER ROW)
    movie_btn_html = ""
    if data['type'] == 'movie':
        movie_btn_html = '<div class="btn-grid-2">'
        for l in data['movieLinks']:
            movie_btn_html += f'<a href="javascript:void(0)" onclick="openLink(\'{l["url"]}\')" class="btn-main">{l["q"]} Download</a>'
        movie_btn_html += '</div>'

    # SERIES SYSTEM (2 PER ROW SEASONS & EPISODES)
    series_btn_html = '<div class="btn-grid-2">'
    for i, s in enumerate(data['seasons']):
        series_btn_html += f'<button class="btn-s" onclick="toggleS(\'s{i}\')">📂 {s["name"]}</button>'
    series_btn_html += '</div>'
    
    for i, s in enumerate(data['seasons']):
        series_btn_html += f'<div id="s{i}" class="ep-area" style="display:none;"><div class="btn-grid-2">'
        for ep in s['episodes']:
            # Quality logic for episodes
            main_url = ep['links'][0]['url'] if ep['links'] else "#"
            series_btn_html += f'<a href="javascript:void(0)" onclick="openLink(\'{main_url}\')" class="btn-e">{ep["name"]} Link</a>'
        series_btn_html += '</div></div>'

    # AD JS
    ad_script = f"const ads={AD_LINKS}; const adCount={data['ad_count']};"

    blogger_html = f"""
<!--BLOGGER POST START-->
<style>
    .p-body {{ background: #0f172a; color: #f1f5f9; padding: 20px; border-radius: 15px; font-family: sans-serif; }}
    .p-main-img {{ width: 100%; border-radius: 10px; box-shadow: 0 5px 25px rgba(0,0,0,0.5); }}
    .p-title {{ color: #38bdf8; text-align: center; font-size: 30px; font-weight: bold; margin: 15px 0; }}
    .h-title {{ border-left: 4px solid #38bdf8; padding-left: 12px; margin: 25px 0 15px; font-weight: bold; font-size: 18px; }}
    .cast-slider {{ display: flex; overflow-x: auto; gap: 12px; padding-bottom: 10px; }}
    .cast-c {{ min-width: 85px; text-align: center; }}
    .cast-c img {{ width: 70px; height: 70px; border-radius: 50%; border: 2px solid #38bdf8; object-fit: cover; }}
    .gal-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }}
    .gal-grid img {{ width: 100%; border-radius: 8px; }}
    .btn-grid-2 {{ display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-top: 15px; }}
    .btn-main, .btn-s, .btn-e {{ display: block; background: linear-gradient(90deg, #38bdf8, #2563eb); color: #fff !important; text-align: center; padding: 12px; border-radius: 8px; text-decoration: none !important; font-weight: bold; border: none; width: 100%; cursor: pointer; }}
    .btn-s {{ background: #1e293b; border: 1px solid #38bdf8; }}
    .btn-e {{ background: #38bdf8; color: #000 !important; font-size: 12px; }}
    .ep-area {{ background: #1e293b; padding: 10px; border-radius: 10px; margin-top: 5px; }}
    .unlock-btn {{ display: block; background: #fbbf24; color: #000 !important; text-align: center; padding: 18px; border-radius: 12px; font-weight: 800; font-size: 20px; cursor: pointer; margin: 25px 0; }}
</style>

<div class="p-body">
    <img src="{data['backdrop']}" class="p-main-img">
    <h1 class="p-title">{data['title']}</h1>
    <p style="text-align:center;opacity:0.8;">📅 {data['date']} | 🌐 {data['lang']} | 👤 {data['dir_name']}</p>

    <div class="h-title">STORYLINE</div>
    <p style="line-height:1.6;color:#94a3b8;">{data['story']}</p>

    <div class="h-title">STAR CAST</div>
    <div class="cast-slider">{cast_html}</div>

    <div class="h-title">SCREENSHOTS</div>
    <div class="gal-grid">{gallery_html}</div>

    <div class="h-title">OFFICIAL TRAILER</div>
    <iframe width="100%" height="315" src="https://www.youtube.com/embed/{data['trailer']}" frameborder="0" allowfullscreen style="border-radius:10px;"></iframe>

    <div class="unlock-btn" onclick="document.getElementById('dl-box').style.display='block';this.style.display='none'">🔓 UNLOCK DOWNLOAD LINKS</div>

    <div id="dl-box" style="display:none;">
        <div class="h-title">DOWNLOAD OPTIONS</div>
        {movie_btn_html if data['type']=='movie' else series_btn_html}
    </div>
</div>

<script>
    {ad_script}
    function toggleS(id) {{
        document.querySelectorAll('.ep-area').forEach(a => {{ if(a.id !== id) a.style.display = 'none'; }});
        var x = document.getElementById(id);
        x.style.display = (x.style.display === "none") ? "block" : "none";
    }}
    function openLink(url) {{
        for(let i=0; i<adCount; i++) {{ window.open(ads[Math.floor(Math.random()*ads.length)], '_blank'); }}
        window.location.href = url;
    }}
</script>
<!--DATA:{json_meta}-->
<!--BLOGGER POST END-->
"""
    return jsonify({"html": blogger_html})

if __name__ == '__main__':
    app.run(debug=True)
