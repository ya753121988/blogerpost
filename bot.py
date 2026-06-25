import os
import json
import base64
from flask import Flask, render_template_string, request, jsonify
import requests

app = Flask(__name__)

# CONFIGURATION
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
    <title>Ultimate Blogger Engine PRO v8.0</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        :root { --sky: #38bdf8; --bg: #0b0f1a; --dark-card: #161e2e; }
        body { background: var(--bg); color: #e2e8f0; font-family: 'Inter', sans-serif; padding-bottom: 80px; }
        .main-editor { background: var(--dark-card); border: 1px solid #1e293b; border-radius: 20px; padding: 30px; box-shadow: 0 10px 50px rgba(0,0,0,0.8); margin-top: 30px; }
        .form-control, .form-select { background: #0f172a; border: 1px solid #334155; color: #fff; margin-bottom: 15px; border-radius: 10px; }
        .form-control:focus { background: #0f172a; border-color: var(--sky); color: #fff; box-shadow: none; }
        .section-label { border-left: 6px solid var(--sky); padding-left: 15px; margin: 40px 0 20px; font-weight: 900; color: var(--sky); text-transform: uppercase; letter-spacing: 2px; }
        
        .grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 15px; }
        .grid-4 { display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; }
        
        .season-card { background: #1e293b; border: 2px solid #334155; padding: 25px; border-radius: 20px; margin-bottom: 30px; }
        .episode-card { background: #0f172a; padding: 20px; border-radius: 15px; margin-top: 15px; border-left: 5px solid var(--sky); }
        
        .btn-sky { background: var(--sky); color: #000; font-weight: 900; border: none; padding: 18px; border-radius: 12px; transition: 0.3s; width: 100%; }
        .btn-sky:hover { background: #0ea5e9; transform: translateY(-3px); }
        
        .code-output { background: #000; color: #10b981; padding: 20px; border-radius: 15px; font-family: monospace; white-space: pre-wrap; margin-top: 20px; border: 1px solid #334155; }
        .search-result-img { cursor: pointer; transition: 0.3s; border-radius: 12px; }
        .search-result-img:hover { transform: scale(1.05); border: 2px solid var(--sky); }
    </style>
</head>
<body>
<div class="container">
    <div class="main-editor">
        <h2 class="text-center fw-bold mb-4 text-info">🚀 ULTIMATE BLOGGER POST GENERATOR</h2>
        
        <!-- Re-Edit System -->
        <div class="mb-5 p-4 border border-primary border-dashed rounded text-center">
            <h6 class="text-primary fw-bold mb-3">RE-EDIT POST (PASTE BLOGGER HTML)</h6>
            <textarea id="import_html" class="form-control" rows="2" placeholder="Paste generated code here to edit..."></textarea>
            <button class="btn btn-primary btn-sm w-100 fw-bold" onclick="importPost()">IMPORT & EDIT DATA</button>
        </div>

        <!-- Search Area -->
        <div class="row g-3 mb-5">
            <div class="col-md-7"><input type="text" id="sq" class="form-control" placeholder="Movie or Series Name..."></div>
            <div class="col-md-3">
                <select id="st" class="form-select">
                    <option value="movie">Movie</option><option value="tv">Web Series</option>
                </select>
            </div>
            <div class="col-md-2"><button class="btn btn-sky" onclick="searchTMDB()">SEARCH</button></div>
        </div>
        <div id="results" class="row"></div>

        <!-- Main Editor Form -->
        <div id="editor_form" style="display:none;">
            <div class="section-label">1. BASIC DETAILS & POSTER</div>
            <div class="row g-3">
                <div class="col-md-6"><label>Full Title</label><input type="text" id="e_title" class="form-control"></div>
                <div class="col-md-6"><label>Main Backdrop Link</label><input type="text" id="e_backdrop" class="form-control"></div>
                <div class="col-md-4"><label>Language</label><input type="text" id="e_lang" class="form-control"></div>
                <div class="col-md-4"><label>Release Date</label><input type="text" id="e_date" class="form-control"></div>
                <div class="col-md-4"><label>Trailer ID</label><input type="text" id="e_trailer" class="form-control"></div>
                <div class="col-md-12"><label>Storyline</label><textarea id="e_story" class="form-control" rows="4"></textarea></div>
                <div class="col-md-6"><label>Director Name</label><input type="text" id="e_dir_name" class="form-control"></div>
                <div class="col-md-6"><label>Director Photo</label><input type="text" id="e_dir_img" class="form-control"></div>
            </div>

            <div class="section-label">2. CAST (NAYOK/NAYIKA) - ALL DETAILS</div>
            <div id="cast_editor" class="row g-3"></div>

            <div class="section-label">3. ALL LANDSCAPE SCREENSHOTS</div>
            <div id="gallery_editor" class="row g-2"></div>

            <div class="section-label">4. AD CONTROL (STEPS)</div>
            <div class="col-md-4">
                <label>Ads Per Click (1-10)</label>
                <select id="e_ad_count" class="form-select">
                    <script>for(let i=1;i<=10;i++) document.write(`<option value="${i}">${i} Ads</option>`)</script>
                </select>
            </div>

            <!-- Movie UI -->
            <div id="movie_links_section" style="display:none;">
                <div class="section-label">5. MOVIE DOWNLOAD LINKS (8K to 140p)</div>
                <div class="grid-4">
                    ${['8K','4K','2K','1080p','720p','480p','360p','140p'].map(q => `<div>${q}<input type="text" data-q="${q}" class="form-control mq"></div>`).join('')}
                </div>
            </div>

            <!-- Series UI -->
            <div id="series_links_section" style="display:none;">
                <div class="section-label">5. SERIES SEASONS & EPISODES</div>
                <div id="seasons_area"></div>
                <button class="btn btn-outline-info w-100 fw-bold mt-3" onclick="addSeason()">+ ADD NEW SEASON</button>
            </div>

            <button class="btn btn-sky btn-lg mt-5 py-4" onclick="finalGenerate()">🚀 GENERATE PREMUM BLOGGER HTML</button>

            <!-- Final Area -->
            <div id="final_area" class="mt-5" style="display:none;">
                <div class="d-flex gap-3 mb-3">
                    <button class="btn btn-success flex-grow-1 fw-bold py-3" onclick="copyCode()">COPY HTML CODE</button>
                    <button class="btn btn-warning flex-grow-1 fw-bold py-3" onclick="previewPost()">PREVIEW POST</button>
                </div>
                <div id="preview_box" class="bg-white text-dark p-4 rounded mb-3" style="display:none;"></div>
                <div id="code_box" class="code-output"></div>
            </div>
        </div>
    </div>
</div>

<script>
let seasonCount = 0;
let currentTMDB = null;

async function searchTMDB() {
    const q = document.getElementById('sq').value;
    const t = document.getElementById('st').value;
    const res = await fetch(`/api/search?q=${q}&type=${t}`);
    const data = await res.json();
    let h = '';
    data.results.forEach(i => {
        h += `<div class="col-md-4 mb-3" onclick="loadItem('${i.id}', '${t}')"><img src="https://image.tmdb.org/t/p/w500${i.backdrop_path}" class="img-fluid search-result-img"><p class="text-center small mt-1">${i.title || i.name}</p></div>`;
    });
    document.getElementById('results').innerHTML = h;
}

async function loadItem(id, type) {
    const res = await fetch(`/api/details?id=${id}&type=${type}`);
    currentTMDB = await res.json();
    document.getElementById('results').innerHTML = '';
    document.getElementById('editor_form').style.display = 'block';
    
    document.getElementById('e_title').value = currentTMDB.title || currentTMDB.name;
    document.getElementById('e_backdrop').value = `https://image.tmdb.org/t/p/original${currentTMDB.backdrop_path}`;
    document.getElementById('e_date').value = currentTMDB.release_date || currentTMDB.first_air_date;
    document.getElementById('e_story').value = currentTMDB.overview;
    
    const d = currentTMDB.credits.crew.find(c => c.job === 'Director');
    document.getElementById('e_dir_name').value = d ? d.name : '';
    document.getElementById('e_dir_img').value = d ? `https://image.tmdb.org/t/p/w185${d.profile_path}` : '';
    
    const t = currentTMDB.videos.results.find(v => v.type === 'Trailer');
    document.getElementById('e_trailer').value = t ? t.key : '';

    // Cast Editor
    let cH = '';
    currentTMDB.credits.cast.slice(0, 6).forEach(c => {
        cH += `<div class="col-md-4 p-2 border border-secondary rounded"><input type="text" class="form-control form-control-sm cn" value="${c.name}"><input type="text" class="form-control form-control-sm ci" value="https://image.tmdb.org/t/p/w185${c.profile_path}"><input type="hidden" class="cid" value="${c.id}"></div>`;
    });
    document.getElementById('cast_editor').innerHTML = cH;

    // Gallery Editor
    let gH = '';
    currentTMDB.images.backdrops.slice(0, 10).forEach(img => {
        gH += `<div class="col-md-6"><input type="text" class="form-control form-control-sm gi" value="https://image.tmdb.org/t/p/original${img.file_path}"></div>`;
    });
    document.getElementById('gallery_editor').innerHTML = gH;

    if(type === 'movie') {
        document.getElementById('movie_links_section').style.display = 'block';
        document.getElementById('series_links_section').style.display = 'none';
    } else {
        document.getElementById('movie_links_section').style.display = 'none';
        document.getElementById('series_links_section').style.display = 'block';
    }
}

function addSeason(name = "") {
    seasonCount++;
    const sId = `s_${seasonCount}`;
    const sName = name || `Season ${String(seasonCount).padStart(2, '0')}`;
    const d = document.createElement('div');
    d.className = 'season-card';
    d.id = sId;
    d.innerHTML = `<div class="d-flex gap-3 mb-3"><input type="text" class="form-control fw-bold st" value="${sName}"><button class="btn btn-info fw-bold" onclick="addEp('${sId}')">+ ADD EPISODE</button></div><div class="ep-wrap" data-count="0"></div>`;
    document.getElementById('seasons_area').appendChild(d);
}

function addEp(sId, name = "", links = {}) {
    const wrap = document.querySelector(`#${sId} .ep-wrap`);
    let count = parseInt(wrap.dataset.count) + 1;
    wrap.dataset.count = count;
    const eName = name || `Episode ${String(count).padStart(2, '0')}`;
    const d = document.createElement('div');
    d.className = 'episode-card';
    d.innerHTML = `<input type="text" class="form-control fw-bold et mb-2" value="${eName}"><div class="grid-4">${['8K','4K','2K','1080p','720p','480p','360p','140p'].map(q => `<div>${q}<input type="text" data-q="${q}" class="form-control eq" value="${links[q] || ''}"></div>`).join('')}</div>`;
    wrap.appendChild(d);
}

async function finalGenerate() {
    const castData = [];
    const castEls = document.querySelectorAll('.cid');
    for(let i=0; i<castEls.length; i++){
        const res = await fetch(`/api/person?id=${castEls[i].value}`);
        const p = await res.json();
        castData.push({
            name: document.querySelectorAll('.cn')[i].value,
            img: document.querySelectorAll('.ci')[i].value,
            born: p.birthday || 'Unknown',
            place: p.place_of_birth || 'Unknown',
            bio: p.biography ? p.biography.slice(0, 500).replace(/'/g, "") + "..." : "No Biography.",
            count: p.combined_credits.cast.length,
            best: p.combined_credits.cast.sort((a,b) => b.vote_count - a.vote_count).slice(0,4).map(m => m.title || m.name).join(', ')
        });
    }

    const data = {
        title: document.getElementById('e_title').value,
        backdrop: document.getElementById('e_backdrop').value,
        lang: document.getElementById('e_lang').value,
        date: document.getElementById('e_date').value,
        story: document.getElementById('e_story').value,
        dir_name: document.getElementById('e_dir_name').value,
        dir_img: document.getElementById('e_dir_img').value,
        trailer: document.getElementById('e_trailer').value,
        ad_count: document.getElementById('e_ad_count').value,
        type: document.getElementById('st').value,
        cast: castData,
        gallery: Array.from(document.querySelectorAll('.gi')).map(i => i.value),
        movieLinks: Array.from(document.querySelectorAll('.mq')).filter(i => i.value).map(i => ({q: i.dataset.q, url: i.value})),
        seasons: Array.from(document.querySelectorAll('.season-card')).map(s => ({
            name: s.querySelector('.st').value,
            episodes: Array.from(s.querySelectorAll('.episode-card')).map(e => ({
                name: e.querySelector('.et').value,
                links: Array.from(e.querySelectorAll('.eq')).filter(i => i.value).map(i => ({q: i.dataset.q, url: i.value}))
            }))
        }))
    };

    const res = await fetch('/api/generate', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(data) });
    const result = await res.json();
    document.getElementById('code_box').innerText = result.html;
    document.getElementById('preview_box').innerHTML = result.html;
    document.getElementById('final_area').style.display = 'block';
}

function importPost() {
    try {
        const raw = document.getElementById('import_html').value;
        const meta = JSON.parse(atob(raw.match(/<!--DATAMETA:(.*)-->/)[1]));
        document.getElementById('editor_form').style.display = 'block';
        document.getElementById('e_title').value = meta.title;
        document.getElementById('e_backdrop').value = meta.backdrop;
        document.getElementById('e_lang').value = meta.lang;
        document.getElementById('e_date').value = meta.date;
        document.getElementById('e_story').value = meta.story;
        document.getElementById('e_dir_name').value = meta.dir_name;
        document.getElementById('e_dir_img').value = meta.dir_img;
        document.getElementById('e_trailer').value = meta.trailer;
        document.getElementById('e_ad_count').value = meta.ad_count;
        document.getElementById('st').value = meta.type;
        
        if(meta.type === 'movie') {
            document.getElementById('movie_links_section').style.display = 'block';
            meta.movieLinks.forEach(l => { const i = document.querySelector(`.mq[data-q="${l.q}"]`); if(i) i.value = l.url; });
        } else {
            document.getElementById('series_links_section').style.display = 'block';
            document.getElementById('seasons_area').innerHTML = ''; seasonCount = 0;
            meta.seasons.forEach(s => {
                addSeason(s.name); const sId = `s_${seasonCount}`;
                s.episodes.forEach(e => { const lObj = {}; e.links.forEach(ln => lObj[ln.q] = ln.url); addEp(sId, e.name, lObj); });
            });
        }
        alert("Imported Successfully!");
    } catch(e) { alert("Invalid HTML Code!"); }
}

function copyCode() { navigator.clipboard.writeText(document.getElementById('code_box').innerText); alert("Copied!"); }
function previewPost() { const p = document.getElementById('preview_box'); p.style.display = p.style.display==='none'?'block':'none'; }
</script>
</body>
</html>
"""

@app.route('/')
def index(): return render_template_string(UI_HTML)

@app.route('/api/search')
def search_api():
    try:
        q = request.args.get('q'); t = request.args.get('type')
        url = f"https://api.themoviedb.org/3/search/{t}?api_key={TMDB_API_KEY}&query={q}"
        return jsonify(requests.get(url).json())
    except: return jsonify({"results": []})

@app.route('/api/details')
def details_api():
    try:
        id = request.args.get('id'); t = request.args.get('type')
        url = f"https://api.themoviedb.org/3/{t}/{id}?api_key={TMDB_API_KEY}&append_to_response=credits,videos,images"
        return jsonify(requests.get(url).json())
    except: return jsonify({})

@app.route('/api/person')
def person_api():
    try:
        id = request.args.get('id')
        url = f"https://api.themoviedb.org/3/person/{id}?api_key={TMDB_API_KEY}&append_to_response=combined_credits"
        return jsonify(requests.get(url).json())
    except: return jsonify({})

@app.route('/api/generate', methods=['POST'])
def generate_api():
    try:
        data = request.json
        meta_b64 = base64.b64encode(json.dumps(data).encode()).decode()
        
        # Cast
        cast_h = "".join([f'<div class="c-item" onclick="shA(\'{c["name"]}\',\'{c["img"]}\',\'{c["born"]}\',\'{c["place"]}\',\'{c["count"]}\',\'{c["best"]}\',`{c["bio"]}`)"><img src="{c["img"]}"><p>{c["name"]}</p></div>' for c in data['cast']])
        # Gallery
        gal_h = "".join([f'<img src="{i}">' for i in data['gallery']])
        
        # Movie
        m_btns = '<div class="btn-grid">'
        if data['type'] == 'movie':
            for l in data['movieLinks']:
                m_btns += f'<a href="javascript:void(0)" onclick="go(\'{l["url"]}\')" class="p-btn">{l["q"]} Download</a>'
        m_btns += '</div>'

        # Series
        s_btns = '<div class="btn-grid">'
        for i, s in enumerate(data['seasons']):
            s_btns += f'<button class="p-btn s-btn" onclick="tS(\'s{i}\')">📂 {s["name"]}</button>'
        s_btns += '</div>'

        for i, s in enumerate(data['seasons']):
            s_btns += f'<div id="s{i}" class="ep-box" style="display:none;"><div class="btn-grid">'
            for j, e in enumerate(s['episodes']):
                s_btns += f'<button class="p-btn e-btn" onclick="tE(\'s{i}e{j}\')">🎬 {e["name"]}</button>'
            s_btns += '</div>'
            for j, e in enumerate(s['episodes']):
                s_btns += f'<div id="s{i}e{j}" class="q-box" style="display:none;"><div class="btn-grid">'
                for l in e['links']:
                    s_btns += f'<a href="javascript:void(0)" onclick="go(\'{l["url"]}\')" class="p-btn q-btn">{l["q"]} Link</a>'
                s_btns += '</div></div>'
            s_btns += '</div>'

        blogger_html = f"""
<!--MASTERPOST-->
<style>
    .p-wrp {{ background: #0b0f1a; color: #f1f5f9; padding: 25px; border-radius: 20px; font-family: sans-serif; position: relative; }}
    .p-tm {{ width: 100%; border-radius: 15px; box-shadow: 0 10px 40px rgba(0,0,0,0.7); }}
    .p-tl {{ color: #38bdf8; font-size: 32px; font-weight: 900; text-align: center; margin: 25px 0; }}
    .p-hd {{ border-left: 6px solid #38bdf8; padding-left: 15px; margin: 35px 0 15px; font-weight: 800; font-size: 19px; color: #fff; }}
    .c-sl {{ display: flex; overflow-x: auto; gap: 15px; padding-bottom: 10px; scrollbar-width: none; }}
    .c-item {{ min-width: 95px; text-align: center; cursor: pointer; transition: 0.3s; }}
    .c-item img {{ width: 80px; height: 80px; border-radius: 50%; border: 3px solid #38bdf8; object-fit: cover; }}
    .g-gr {{ display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }}
    .g-gr img {{ width: 100%; border-radius: 12px; }}
    .btn-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-top: 15px; }}
    .p-btn {{ display: block; background: linear-gradient(135deg, #38bdf8, #2563eb); color: #fff !important; text-align: center; padding: 16px; border-radius: 15px; text-decoration: none !important; font-weight: 800; border: none; cursor: pointer; font-size: 14px; box-shadow: 0 4px 15px rgba(37, 99, 235, 0.4); }}
    .s-btn {{ background: #1e293b; border: 1px solid #38bdf8; }}
    .ep-box, .q-box {{ background: #111827; padding: 15px; border-radius: 15px; border: 1px solid #1e293b; margin-top: 15px; }}
    .e-btn {{ background: #334155; border: 1px solid #475569; }}
    .q-btn {{ background: #38bdf8; color: #000 !important; }}
    .u-btn {{ display: block; background: #fbbf24; color: #000 !important; text-align: center; padding: 22px; border-radius: 15px; font-weight: 900; font-size: 20px; cursor: pointer; margin: 40px 0; border: none; width: 100%; }}
    .ac-m {{ position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%); background: #161e2e; border: 3px solid #38bdf8; width: 90%; max-width: 450px; padding: 25px; border-radius: 20px; z-index: 99999; display: none; color: #fff; box-shadow: 0 0 100px rgba(0,0,0,0.9); }}
    .ac-m img {{ width: 120px; height: 120px; border-radius: 50%; border: 4px solid #38bdf8; margin: 0 auto 20px; display: block; object-fit: cover; }}
    .ac-m h2 {{ text-align: center; color: #38bdf8; margin-bottom: 10px; font-weight: 900; }}
    .ac-m p {{ font-size: 14px; line-height: 1.6; text-align: justify; margin-bottom: 10px; color: #cbd5e1; max-height: 200px; overflow-y: auto; }}
</style>

<div class="p-wrp">
    <img src="{data['backdrop']}" class="p-tm">
    <h1 class="p-tl">{data['title']}</h1>
    <p style="text-align:center; opacity:0.8;">📅 {data['date']} | 🌐 {data['lang']} | 🎥 {data['dir_name']}</p>
    <div class="p-hd">STORYLINE</div>
    <p style="line-height:1.7; color:#94a3b8; text-align: justify;">{data['story']}</p>
    <div class="p-hd">STAR CAST (CLICK TO SEE BIO)</div>
    <div class="c-sl">{cast_h}</div>
    <div class="p-hd">SCREENSHOTS GALLERY</div>
    <div class="g-gr">{gal_h}</div>
    <div class="p-hd">OFFICIAL TRAILER</div>
    <iframe width="100%" height="380" src="https://www.youtube.com/embed/{data['trailer']}" frameborder="0" allowfullscreen style="border-radius:20px;"></iframe>
    <button class="u-btn" onclick="document.getElementById('dl-zone').style.display='block';this.style.display='none'">🔓 UNLOCK DOWNLOAD LINKS</button>
    <div id="dl-zone" style="display:none;">
        <div class="p-hd">DOWNLOAD OPTIONS</div>
        {m_btns if data['type']=='movie' else s_btns}
    </div>
</div>

<div id="ac-modal" class="ac-m">
    <img id="ac-i" src="">
    <h2 id="ac-n"></h2>
    <div style="font-size:12px; margin-bottom:15px; color:#38bdf8; text-align:center;">
        <span id="ac-b"></span> | <span id="ac-p"></span><br>
        <b>Projects:</b> <span id="ac-c"></span> | <b>Top:</b> <span id="ac-w"></span>
    </div>
    <p id="ac-bio"></p>
    <button style="background:#38bdf8;color:#000;font-weight:900;border:none;padding:12px;border-radius:10px;width:100%;cursor:pointer;" onclick="document.getElementById('ac-modal').style.display='none'">CLOSE</button>
</div>

<script>
    const ads = {AD_LINKS}; const adCount = {data['ad_count']};
    function tS(id) {{ document.querySelectorAll('.ep-box').forEach(el => {{ if(el.id !== id) el.style.display = 'none'; }}); var x = document.getElementById(id); x.style.display = (x.style.display==='none')?'block':'none'; }}
    function tE(id) {{ document.querySelectorAll('.q-box').forEach(el => {{ if(el.id !== id) el.style.display = 'none'; }}); var x = document.getElementById(id); x.style.display = (x.style.display==='none')?'block':'none'; }}
    function go(u) {{ for(let i=0; i<adCount; i++) {{ window.open(ads[Math.floor(Math.random()*ads.length)], '_blank'); }} window.location.href = u; }}
    function shA(n,i,b,p,c,w,bio) {{
        document.getElementById('ac-n').innerText = n; document.getElementById('ac-i').src = i;
        document.getElementById('ac-b').innerText = "Born: "+b; document.getElementById('ac-p').innerText = p;
        document.getElementById('ac-c').innerText = c; document.getElementById('ac-w').innerText = w;
        document.getElementById('ac-bio').innerText = bio; document.getElementById('ac-modal').style.display = 'block';
    }}
</script>
<!--DATAMETA:{meta_b64}-->
"""
        return jsonify({"html": blogger_html})
    except Exception as e:
        return jsonify({"html": f"Error: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True)
