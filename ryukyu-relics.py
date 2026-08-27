import streamlit as st
import pandas as pd
import os
import streamlit.components.v1 as components
import json

st.set_page_config(
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ===================== 自定义CSS 原版恢复，只保留hover悬浮下划线 =====================
CSS_STYLE = """
<style>
[data-testid="stHeader"] { display: none; }
[data-testid="stAppViewContainer"] {
    background-color: #f3e5d3;
    margin: 0 !important;
    padding-top: 0 !important;
}
.block-container {
    padding: 0 2rem !important;
    max-width: 100% !important;
}
.top-nav {
    background-color: transparent;
    width: 100%;
    padding: 30px 0 10px 0;
}
.nav-brand {
    font-size: 28px;
    font-weight: bold;
    color: #B03A2E;
    border-bottom: 3px solid #B03A2E;
    padding-bottom: 15px;
    margin-bottom: 10px;
    width: 100%;
}
[data-testid="stButton"] button {
    background: transparent !important;
    color: #B03A2E !important;
    border: none !important;
    font-size: 16px;
    padding: 10px 0;
    width: 100%;
}
[data-testid="stButton"] button:hover {
    border-bottom: 2px solid #B03A2E !important;
}
footer {visibility:hidden;}
</style>
"""
st.markdown(CSS_STYLE, unsafe_allow_html=True)


# ===================== 读取CSV数据（合并介绍） =====================
@st.cache_data
def load_artifact_data():
    csv_path = "ryukyu-relics-images-data.csv"
    desc_csv_path = "琉球文化素材介绍.csv"

    if not os.path.exists(csv_path):
        st.error(f"找不到数据文件：{csv_path}，请确认和py脚本放在同一文件夹！")
        return pd.DataFrame()
    df = pd.read_csv(csv_path, encoding="utf-8-sig")
    df["二级分类"] = df["二级分类"].fillna("")

    if os.path.exists(desc_csv_path):
        try:
            df_desc = pd.read_csv(desc_csv_path, encoding="utf-8-sig")
            desc_map = dict(zip(df_desc["素材名"], df_desc["介绍"]))
            df["介绍"] = df["素材文件夹名"].map(desc_map).fillna("暂无详细介绍")
        except Exception as e:
            st.warning(f"读取介绍文件失败，无法合并介绍：{e}")
            df["介绍"] = df[df.columns[-1]].fillna("暂无详细介绍")
    else:
        if df.shape[1] > 0:
            df["介绍"] = df[df.columns[-1]].fillna("暂无详细介绍")
        else:
            df["介绍"] = "暂无详细介绍"

    return df


df_data = load_artifact_data()
COL_NAME = "素材文件夹名"
COL_URL = "完整访问URL"
COL_CAT1 = "一级分类"
COL_CAT2 = "二级分类"
COL_DESC = "介绍"

if not df_data.empty:
    # 兼容CSV不存在"图片序号"列，避免报错
    if "图片序号" in df_data.columns:
        df_unique = df_data.sort_values("图片序号").drop_duplicates(subset=[COL_NAME], keep="first").reset_index(drop=True)
    else:
        df_unique = df_data.drop_duplicates(subset=[COL_NAME], keep="first").reset_index(drop=True)
else:
    df_unique = pd.DataFrame()

if "page" not in st.session_state:
    st.session_state.page = "首页"

nav_pages = ["首页", "藏品概览", "历史脉络", "文创商店", "联系我们"]

with st.container():
    st.markdown('<div class="top-nav">', unsafe_allow_html=True)
    # ========== 这里替换logo，把下面 YOUR_LOGO_URL 替换成你的真实图片链接 ==========
    st.markdown("""
    <div class="nav-brand" style="display:flex;align-items:center;gap:8px;">
        <img src="https://echo-eternalflames.github.io/picx-images-hosting/汉韵琉球logo.webp" style="height:60px;width:auto;object-fit:contain;position:relative; top:-14px;">
        汉韵琉球
    </div>
    """, unsafe_allow_html=True)

    nav_cols = st.columns(len(nav_pages))
    for idx, page_name in enumerate(nav_pages):
        with nav_cols[idx]:
            # 当前页使用markdown粗体 **xxx**，文字加粗，盒子高度不变，不会挤压页面
            display_label = f"**{page_name}**" if page_name == st.session_state.page else page_name
            if st.button(display_label, use_container_width=True):
                st.session_state.page = page_name
                st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

current_page = st.session_state.page

# ===================== 首页 =====================
if current_page == "首页":
    # 页面切入时：清除残留的商店toast通知
    components.html("""
    <script>
    const pDoc = window.parent.document;
    const leftoverToast = pDoc.querySelector('.shop-toast');
    if(leftoverToast) leftoverToast.remove();
    </script>
    """, height=0)

    all_data = []
    for _, row in df_unique.iterrows():
        group = df_data[df_data[COL_NAME] == row[COL_NAME]]
        images = group[COL_URL].dropna().tolist()
        if not images:
            images = [row[COL_URL]]
        all_data.append({
            "name": row[COL_NAME],
            "cat": f"{row[COL_CAT1]}{' / ' + row[COL_CAT2] if row[COL_CAT2] else ''}",
            "desc": row[COL_DESC],
            "images": images
        })

    data_json = json.dumps(all_data, ensure_ascii=False)

    home_html = f"""
    <style>
        .home-container {{
            display: flex;
            align-items: center;
            padding: 20px 10px 40px 10px;
            gap: 30px;
            height: 760px;
            margin-top: -120px;
        }}
        .left-carousel {{
            width: 50%;
            height: 660px;
            overflow: hidden;
            display: flex;
            justify-content: center;
            align-items: center;
            position: relative;
            padding: 20px;
        }}
        .carousel-img {{
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            height: 530px;
            width: auto;
            max-width: 100%;
            object-fit: contain;
            opacity: 1;
            transition: opacity 0.8s ease-in-out;
            box-shadow: 0 20px 40px rgba(0,0,0,0.3);
            border-radius: 10px;
        }}
        .date-badge {{
            position: absolute;
            bottom: 25px;
            right: 25px;
            background: #ffffff;
            border-radius: 12px;
            box-shadow: 0 8px 20px rgba(0,0,0,0.3);
            padding: 15px 20px;
            text-align: center;
            display: flex;
            flex-direction: column;
            align-items: center;
            font-family: sans-serif;
            z-index: 30;
            pointer-events: none;
        }}
        .date-badge .day {{
            font-size: 42px;
            font-weight: bold;
            color: #203050;
            line-height: 1;
        }}
        .date-badge .month {{
            font-size: 16px;
            font-weight: bold;
            color: #B03A2E;
            letter-spacing: 5px;
            margin-top: 5px;
            text-transform: uppercase;
        }}
        .right-info {{
            width: 50%;
            display: flex;
            flex-direction: column;
            justify-content: flex-start;
            padding-top: 30px;
            padding-right: 10px;
        }}
        .right-wrapper {{
            padding: 30px 35px;
            border-radius: 20px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.08);
            background: rgba(255, 255, 255, 0.2);
        }}
        .main-title {{
            font-size: 46px;
            font-weight: bold;
            color: #203050;
            line-height: 1.25;
            border-bottom: 2px solid #B03A2E;
            padding-bottom: 15px;
            margin-bottom: 20px;
        }}
        .sub-caption {{
            font-size: 18px;
            color: #333333;
            margin: 12px 0 26px 0;
            line-height: 1.8;
        }}
        .info-card {{
            background: #fffaf0;
            padding: 25px;
            border-radius: 15px;
            border: 1px solid #E0C7A0;
            position: relative;
        }}
        .info-card::before {{
            content: "❖";
            position: absolute;
            top: -10px;
            left: 20px;
            color: #B03A2E;
            font-size: 24px;
            background: #fffaf0;
            padding: 0 5px;
        }}
        .data-line {{
            font-size: 18px;
            margin: 12px 0;
            color: #333;
        }}
        #txt-name, #txt-cat {{
            display: inline-block;
            transition: opacity 0.8s ease-in-out;
        }}
        .wave-decoration {{
            margin-top: -80px;
            width: 100vw;
            margin-left: calc(50% - 50vw);
            height: 120px;
            pointer-events: none;
        }}
        .wave-decoration svg {{
            display: block;
            width: 100%;
            height: 100%;
        }}
    </style>

    <div class="home-container">
        <div class="left-carousel" id="carousel">
            <div class="date-badge">
                <div class="day" id="date-day"></div>
                <div class="month" id="date-month"></div>
            </div>
        </div>

        <div class="right-info">
            <div class="right-wrapper">
                <div class="main-title">琉球文物：<br>海洋与岛屿的记忆</div>
                <div class="sub-caption">从陶片、织物与器具中看见琉球群岛的生活美学，探索这片古国深厚的历史底蕴与人文风情。</div>
                <div class="info-card">
                    <div style="border-bottom: 2px solid #B03A2E; padding-bottom:10px; margin-bottom:15px; color:#203050; font-size: 22px;"><b>馆藏精选</b></div>
                    <div class="data-line"><b>名称:</b> <span id="txt-name"></span></div>
                    <div class="data-line"><b>分类:</b> <span id="txt-cat"></span></div>
                </div>
            </div>
        </div>
    </div>

    <div class="wave-decoration">
        <svg viewBox="0 0 1440 120" preserveAspectRatio="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M0,60 C240,110 480,10 720,60 C960,110 1200,10 1440,60"
                  fill="none" stroke="#B03A2E" stroke-width="4" stroke-linecap="round" stroke-linejoin="round" opacity="0.9"/>
            <path d="M0,80 C180,50 360,110 540,80 C720,50 900,110 1080,80 C1260,50 1440,110 1440,80"
                  fill="none" stroke="#B03A2E" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" opacity="0.6"/>
            <path d="M0,40 C120,80 240,0 360,40 C480,80 600,0 720,40 C840,80 960,0 1080,40 C1200,80 1320,0 1440,40"
                  fill="none" stroke="#B03A2E" stroke-width="1.5" stroke-dasharray="12, 12" stroke-linecap="round" opacity="0.4"/>
        </svg>
    </div>

    <script>
        const allData = {data_json};
        let currentIdx = 0;
        const now = new Date();
        const monthNames = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"];
        document.getElementById('date-day').innerText = now.getDate();
        document.getElementById('date-month').innerText = monthNames[now.getMonth()];

        function getRandomIndex() {{
            let randomIndex;
            do {{
                randomIndex = Math.floor(Math.random() * allData.length);
            }} while (randomIndex === currentIdx && allData.length > 1);
            return randomIndex;
        }}

        function loadItem(index) {{
            if (allData.length === 0) return;
            if (index < 0) index = allData.length - 1;
            if (index >= allData.length) index = 0;
            currentIdx = index;
            const item = allData[currentIdx];
            if (!item || !item.images || item.images.length === 0) return;
            const container = document.getElementById('carousel');
            const nameEl = document.getElementById('txt-name');
            const catEl = document.getElementById('txt-cat');
            nameEl.style.opacity = '0';
            catEl.style.opacity = '0';
            const currentImg = container.querySelector('.carousel-img');
            if (currentImg) {{
                currentImg.style.opacity = '0';
                setTimeout(() => {{
                    currentImg.remove();
                    nameEl.innerText = item.name;
                    catEl.innerText = item.cat;
                    const newImg = document.createElement('img');
                    newImg.src = item.images[0];
                    newImg.className = 'carousel-img';
                    newImg.style.opacity = '0';
                    newImg.onerror = function() {{ this.style.display = 'none'; }};
                    container.appendChild(newImg);
                    requestAnimationFrame(() => {{
                        newImg.style.opacity = '1';
                        nameEl.style.opacity = '1';
                        catEl.style.opacity = '1';
                    }});
                }}, 1000);
            }} else {{
                nameEl.innerText = item.name;
                catEl.innerText = item.cat;
                const newImg = document.createElement('img');
                newImg.src = item.images[0];
                newImg.className = 'carousel-img';
                newImg.style.opacity = '0';
                newImg.onerror = function() {{ this.style.display = 'none'; }};
                container.appendChild(newImg);
                requestAnimationFrame(() => {{
                    newImg.style.opacity = '1';
                    nameEl.style.opacity = '1';
                    catEl.style.opacity = '1';
                }});
            }}
        }}
        function startAutoPlay() {{
            setInterval(() => {{ loadItem(getRandomIndex()); }}, 5000);
        }}
        loadItem(getRandomIndex());
        startAutoPlay();
    </script>
    """
    components.html(home_html, height=800)

# ===================== 藏品概览 =====================
elif current_page == "藏品概览":
    # 页面切入时：清除残留的商店toast通知
    components.html("""
    <script>
    const pDoc = window.parent.document;
    const leftoverToast = pDoc.querySelector('.shop-toast');
    if(leftoverToast) leftoverToast.remove();
    </script>
    """, height=0)

    st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] { height: 100vh; overflow: hidden; }
    .block-container { padding-top: 0px !important; }
    </style>
    """, unsafe_allow_html=True)

    df_sorted = df_data.sort_values("图片序号")
    gallery_data = []

    for name, group in df_sorted.groupby(COL_NAME):
        images = group[COL_URL].dropna().tolist()
        if not images:
            continue
        first_row = group.iloc[0]
        gallery_data.append({
            "img": images[0],
            "images": images,
            "name": first_row[COL_NAME],
            "cat": f"{first_row[COL_CAT1]}{' / ' + first_row[COL_CAT2] if first_row[COL_CAT2] else ''}",
            "desc": first_row[COL_DESC]
        })

    data_json = json.dumps(gallery_data, ensure_ascii=False)

    html_code = f"""
    <style>
        #viewport {{ width: 100%; height: 675px; overflow: hidden; position: relative; background: transparent; cursor: crosshair; }}
        #grid {{ position: absolute; top: 0; left: 50%; transform: translateX(-50%); display: flex; flex-wrap: wrap; gap: 48px; padding: 30px 20px 220px 20px; width: 3000px; will-change: transform; justify-content: center; }}
        .card {{ background: #fff; border-radius: 6px; border: 1px solid #ddd; box-shadow: 0 4px 10px rgba(0,0,0,0.1); padding: 2px; display: flex; flex-direction: column; align-items: center; justify-content: flex-start; position: relative; flex-shrink: 0; transition: transform 0.1s linear, opacity 0.1s linear; will-change: transform; cursor: pointer; }}
        .card img {{ display: block; width: auto; height: 120px; max-width: none; object-fit: contain; border-radius: 4px; margin-bottom: 2px; }}
        .card-name {{ width: 100%; height: 24px; font-size: 12px; font-weight: bold; color: #203050; text-align: center; line-height: 24px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }}

        /* 新增四边触控按钮样式 */
        .scroll-ctrl-btn {{
            position:absolute;
            background:rgba(32,48,80,0.6);
            color:#ffffff;
            font-size:22px;
            display:flex;
            align-items:center;
            justify-content:center;
            z-index:200;
            user-select:none;
            touch-action:none;
            border-radius:4px;
        }}
        .scroll-ctrl-btn:active{{background:rgba(32,48,80,0.9);}}

        /* 左右：竖长方形 */
        .btn-left {{ 
            left:5px; top:50%; transform:translateY(-50%);
            width:36px; height:70px;
        }}
        .btn-right {{ 
            right:5px; top:50%; transform:translateY(-50%);
            width:36px; height:70px;
        }}

        /* 上下：横长方形，横过来 */
        .btn-top {{ 
            top:5px; left:50%; transform:translateX(-50%);
            width:70px; height:36px;
        }}
        .btn-bottom {{ 
            bottom:12px; left:50%; transform:translateX(-50%);
            width:70px; height:36px;
        }}

    </style>

    <div id="viewport">
        <div id="grid"></div>
        <!-- 四个长按滑动按钮，恢复原始实心三角箭头 -->
        <div class="scroll-ctrl-btn btn-left" data-dir="left">◀</div>
        <div class="scroll-ctrl-btn btn-right" data-dir="right">▶</div>
        <div class="scroll-ctrl-btn btn-top" data-dir="top">▲</div>
        <div class="scroll-ctrl-btn btn-bottom" data-dir="bottom">▼</div>
    </div>

    <script>
        const galleryData = {data_json};
        const viewport = document.getElementById('viewport');
        const grid = document.getElementById('grid');
        let html = '';
        galleryData.forEach((item, index) => {{
            html += `<div class="card" onclick="openModal(${{index}})">
                        <img src="${{item.img}}" onerror="this.parentNode.style.background='#ccc'">
                        <div class="card-name">${{item.name}}</div>
                     </div>`;
        }});
        grid.innerHTML = html;
        const cards = document.querySelectorAll('.card');
        const MAX_X = 800; const MIN_X = -800; const MIN_Y = -800;
        let offsetX = 0, offsetY = 0, targetSpeedX = 0, targetSpeedY = 0, currentSpeedX = 0, currentSpeedY = 0;
        let mousePos = {{ x: viewport.clientWidth / 2, y: viewport.clientHeight / 2 }};

        // ========== 新增长按按钮控制逻辑 ==========
        let holdTimer = null;
        const holdSpeed = 4.5; //长按滑动速度，可以调大小

        function startHoldScroll(direction){{
            stopHoldScroll();
            holdTimer = setInterval(()=>{{
                switch(direction){{
                    case "left": targetSpeedX = holdSpeed; break;
                    case "right": targetSpeedX = -holdSpeed; break;
                    case "top": targetSpeedY = holdSpeed; break;
                    case "bottom": targetSpeedY = -holdSpeed; break;
                }}
            }},25);
        }}
        function stopHoldScroll(){{
            if(holdTimer){{
                clearInterval(holdTimer);
                holdTimer = null;
            }}
        }}

        document.querySelectorAll('.scroll-ctrl-btn').forEach(btn=>{{
            const dir = btn.dataset.dir;
            //鼠标事件
            btn.addEventListener('mousedown', ()=>startHoldScroll(dir));
            btn.addEventListener('mouseup', stopHoldScroll);
            btn.addEventListener('mouseleave', stopHoldScroll);
            //触屏事件
            btn.addEventListener('touchstart', (e)=>{{
                e.preventDefault();
                startHoldScroll(dir);
            }});
            btn.addEventListener('touchend', (e)=>{{
                e.preventDefault();
                stopHoldScroll();
            }});
        }});
        // =========================================

        viewport.addEventListener('mousemove', (e) => {{
            const rect = viewport.getBoundingClientRect();
            mousePos.x = e.clientX - rect.left;
            mousePos.y = e.clientY - rect.top;
        }});
        viewport.addEventListener('mouseleave', () => {{
            targetSpeedX = 0; targetSpeedY = 0;
        }});

        function update() {{
            let desiredSpeedX = (viewport.clientWidth / 2 - mousePos.x) * 0.04;
            let desiredSpeedY = (viewport.clientHeight / 2 - mousePos.y) * 0.05;

            // 如果按钮长按正在运行，不被鼠标位置覆盖速度
            if(!holdTimer){{
                if ((desiredSpeedX > 0 && offsetX >= MAX_X) || (desiredSpeedX < 0 && offsetX <= MIN_X)) desiredSpeedX = 0;
                if ((desiredSpeedY > 0 && offsetY >= 0) || (desiredSpeedY < 0 && offsetY <= MIN_Y)) desiredSpeedY = 0;
                targetSpeedX = desiredSpeedX; targetSpeedY = desiredSpeedY;
            }}

            currentSpeedX += (targetSpeedX - currentSpeedX) * 0.1;
            currentSpeedY += (targetSpeedY - currentSpeedY) * 0.1;
            currentSpeedX *= 0.95; currentSpeedY *= 0.95;

            offsetX += currentSpeedX; offsetY += currentSpeedY;
            if (offsetX > MAX_X) offsetX = MAX_X; if (offsetX < MIN_X) offsetX = MIN_X;
            if (offsetY > 0) offsetY = 0; if (offsetY < MIN_Y) offsetY = MIN_Y;

            grid.style.transform = `translate(calc(-50% + ${{offsetX}}px), ${{offsetY}}px)`;

            cards.forEach(card => {{
                const rect = card.getBoundingClientRect();
                const cardCenterX = rect.left + rect.width / 2;
                const cardCenterY = rect.top + rect.height / 2;
                const distance = Math.sqrt(Math.pow(cardCenterX - mousePos.x, 2) + Math.pow(cardCenterY - mousePos.y, 2));
                let scale = 1.0; let opacity = 1.0;
                if (distance < 500) {{ scale = 1.2; opacity = 1.0; }}
                else {{ scale = Math.max(0.8, 1.2 - (distance - 500) / 1500); opacity = Math.max(0.5, 1 - (distance - 500) / 1200); }}
                card.style.transform = `scale(${{scale}})`; card.style.opacity = opacity;
                card.style.zIndex = scale > 1 ? 10 : 1;
            }});
            requestAnimationFrame(update);
        }}

        let currentImages = []; let currentImageIndex = 0;
        const parentDoc = window.parent.document;

        const modalStyle = `
            .gallery-modal-mask {{
                position: fixed;
                top: 0;
                left: 0;
                width: 100vw;
                height: 100vh;
                background: rgba(0,0,0,0.8);
                z-index: 99999;
                display: flex;
                justify-content: center;
                align-items: center;
            }}
            .gallery-modal-body {{
                background: #f8f5eb;
                width: 80vw;
                height: 70vh;
                border-radius: 15px;
                display: flex;
                overflow: hidden;
                position: relative;
            }}
            .gallery-modal-img-box {{
                width: 60%;
                background: #fff;
                display: flex;
                justify-content: center;
                align-items: center;
                position: relative;
            }}
            .gallery-modal-img-box img {{
                max-width: 100%;
                max-height: 100%;
                object-fit: contain;
                min-width: 50%;
                min-height: 50%;
            }}
            .gallery-prev-btn, .gallery-next-btn {{
                position: absolute;
                top: 50%;
                transform: translateY(-50%);
                width: 50px;
                height: 50px;
                border-radius: 50%;
                background: rgba(255,255,255,0.7);
                border: 2px solid #B03A2E;
                display: none;
                justify-content: center;
                align-items: center;
                cursor: pointer;
                font-size: 28px;
                color: #B03A2E;
                user-select: none;
                z-index: 10;
            }}
            .gallery-prev-btn {{ left: 15px; }}
            .gallery-next-btn {{ right: 15px; }}
            .gallery-page-indicator {{
                position: absolute;
                bottom: 10px;
                left: 50%;
                transform: translateX(-50%);
                color: #B03A2E;
                font-size: 14px;
                background: rgba(255,255,255,0.8);
                border-radius: 12px;
                padding: 2px 10px;
            }}
            .gallery-modal-text {{
                width: 40%;
                padding: 60px 40px 40px 40px;
                display: flex;
                flex-direction: column;
                overflow-y: auto;
            }}
            .gallery-modal-text h1 {{
                color: #B03A2E;
                margin: 0 0 8px 0;
                border-bottom: 4px solid #B03A2E;
                padding-bottom: 10px;
                font-size: 28px;
            }}
            .gallery-modal-text .cat {{
                color: #888;
                margin: 0 0 20px 0;
                font-size: 15px;
            }}
            .gallery-modal-text .desc {{
                color: #333;
                line-height: 1.8;
            }}
            .gallery-modal-text .desc p {{
                margin-bottom: 18px;
                text-indent: 2em;
            }}
            .gallery-modal-close {{
                position: absolute;
                top: 15px;
                right: 25px;
                font-size: 40px;
                color: black;
                cursor: pointer;
                font-weight: bold;
                z-index: 10;
                line-height: 1;
            }}
        `;

        if (!parentDoc.getElementById('gallery-modal-style')) {{
            const style = parentDoc.createElement('style');
            style.id = 'gallery-modal-style';
            style.innerHTML = modalStyle;
            parentDoc.head.appendChild(style);
        }}

        function openModal(index) {{
            const item = galleryData[index];
            currentImages = item.images || [item.img];
            currentImageIndex = 0;
            const descParagraphs = item.desc.split('\\n').filter(p => p.trim());
            let descHtml = '';
            descParagraphs.forEach(p => {{
                descHtml += `<p>${{p.trim()}}</p>`;
            }});
            const mask = parentDoc.createElement('div');
            mask.className = 'gallery-modal-mask';
            mask.innerHTML = `
                <div class="gallery-modal-body">
                    <div class="gallery-modal-close">&times;</div>
                    <div class="gallery-modal-img-box">
                        <img class="gallery-modal-img" src="${{currentImages[0]}}">
                        <div class="gallery-prev-btn">&#10094;</div>
                        <div class="gallery-next-btn">&#10095;</div>
                        <div class="gallery-page-indicator"></div>
                    </div>
                    <div class="gallery-modal-text">
                        <h1>${{item.name}}</h1>
                        <p class="cat">${{item.cat}}</p>
                        <div class="desc">${{descHtml}}</div>
                    </div>
                </div>
            `;
            parentDoc.body.appendChild(mask);
            mask.querySelector('.gallery-modal-close').addEventListener('click', closeModal);
            mask.addEventListener('click', function(e) {{ if (e.target === mask) closeModal(); }});
            mask.querySelector('.gallery-prev-btn').addEventListener('click', function(e){{e.stopPropagation();changeImage(-1);}});
            mask.querySelector('.gallery-next-btn').addEventListener('click', function(e){{e.stopPropagation();changeImage(1);}});
            updatePagination();
        }}
        function changeImage(direction) {{
            if (currentImages.length <= 1) return;
            currentImageIndex += direction;
            if (currentImageIndex < 0) currentImageIndex = currentImages.length - 1;
            if (currentImageIndex >= currentImages.length) currentImageIndex = 0;
            parentDoc.querySelector('.gallery-modal-img').src = currentImages[currentImageIndex];
            updatePagination();
        }}
        function updatePagination() {{
            const prevBtn = parentDoc.querySelector('.gallery-prev-btn');
            const nextBtn = parentDoc.querySelector('.gallery-next-btn');
            const indicator = parentDoc.querySelector('.gallery-page-indicator');
            if (currentImages.length > 1) {{
                prevBtn.style.display = 'flex';
                nextBtn.style.display = 'flex';
                indicator.innerText = (currentImageIndex + 1) + " / " + currentImages.length;
            }} else {{
                prevBtn.style.display = 'none';
                nextBtn.style.display = 'none';
                indicator.innerText = "";
            }}
        }}
        function closeModal() {{
            const mask = parentDoc.querySelector('.gallery-modal-mask');
            if (mask) mask.remove();
        }}
        update();
    </script>
    """
    components.html(html_code, height=675)



# ===================== 历史脉络 =====================
elif current_page == "历史脉络":
    # 页面切入时：清除残留的商店toast通知
    components.html("""
    <script>
    const pDoc = window.parent.document;
    const leftoverToast = pDoc.querySelector('.shop-toast');
    if(leftoverToast) leftoverToast.remove();
    </script>
    """, height=0)

    st.divider()

    @st.cache_data
    def load_wechat_articles():
        img_csv = "公众号文章图片注释.csv"
        img_df = pd.read_csv(img_csv, encoding="utf-8-sig") if os.path.exists(img_csv) else pd.DataFrame()
        article_configs = [
            ("公众号文章1-琉球服饰红型.csv", "汉韵琉球-琉球服饰1-红型-"),
            ("公众号文章2-琉球建筑首里城.csv", "汉韵琉球-琉球建筑1-首里城-"),
            ("公众号文章3-琉球艺术三线.csv", "汉韵琉球-琉球艺术1-琉球三线-"),
        ]
        articles = []
        for csv_file, img_prefix in article_configs:
            if os.path.exists(csv_file):
                df_art = pd.read_csv(csv_file, encoding="utf-8-sig")
                if not df_art.empty:
                    title = str(df_art.iloc[0]["标题"])
                    content = str(df_art.iloc[0]["正文"])
                    cover_url = ""
                    cover_candidate = img_df[img_df["图片文件名"].str.startswith(img_prefix, na=False)]
                    if not cover_candidate.empty:
                        cover_url = str(cover_candidate.iloc[0]["图片链接"])
                    article_imgs = img_df[img_df["图片文件名"].str.startswith(img_prefix, na=False)] if not img_df.empty else pd.DataFrame()
                    images = []
                    for _, row in article_imgs.iterrows():
                        images.append({"url": str(row["图片链接"]), "caption": str(row["图片注释"])});
                    articles.append({"title": title, "content": content, "cover": cover_url, "images": images})
        return articles

    articles = load_wechat_articles()
    if not articles:
        st.error("未找到公众号文章CSV文件，请确认4个CSV与本py文件在同一目录")
    else:
        data_json = json.dumps(articles, ensure_ascii=False)
        html_code = f"""
        <style>
            * {{box-sizing: border-box;margin:0;padding:0;}}
            body {{margin:0;padding:0;overflow:hidden;}}
            .history-page-wrapper {{position:absolute;top:0;left:0;width:100%;height:100%;overflow:hidden;padding-top:8px;}}
            .history-grid {{display:grid;grid-template-columns:repeat(3,1fr);gap:24px;padding:10px 10px 24px 10px;max-width:700px;margin:0 auto;margin-top:-10px;}}
            .history-card {{background:#fff;border-radius:10px;overflow:hidden;box-shadow:0 2px 6px rgba(0,0,0,0.08);cursor:pointer;transition:transform 0.2s ease,box-shadow 0.2s ease;}}
            .history-card:hover {{transform:translateY(-3px);box-shadow:0 5px 12px rgba(0,0,0,0.12);}}
            .history-card-img {{height:130px;overflow:hidden;}}
            .history-card-img img {{width:100%;height:100%;object-fit:cover;display:block;}}
            .history-card-title {{padding:10px 12px;font-size:15px;font-weight:600;color:#203050;text-align:center;}}
        </style>
        <div class="history-page-wrapper"><div class="history-grid" id="historyGrid"></div></div>
        <script>
            const articles = {data_json};
            const parentDoc = window.parent.document;
            const grid = document.getElementById('historyGrid');
            let cardHtml='';
            articles.forEach((item,index)=>{{
                cardHtml+=`<div class="history-card" onclick="openModal(${{index}})"><div class="history-card-img"><img src="${{item.cover}}" alt="${{item.title}}"></div><div class="history-card-title">${{item.title}}</div></div>`;
            }});
            grid.innerHTML=cardHtml;
            const modalCss = `
                .full-modal-mask {{position:fixed;top:0;left:0;width:100vw;height:100vh;background:rgba(0,0,0,0.65);z-index:99999;display:flex;justify-content:center;align-items:center;}}
                .full-modal-body {{width:90vw;height:90vh;background:#fff;border-radius:16px;display:flex;overflow:hidden;position:relative;}}
                .full-modal-images {{width:50%;height:100%;overflow-y:auto;padding:24px;border-right:1px solid #e5e5e5;box-sizing:border-box;}}
                .full-img-item {{margin-bottom:28px;}}
                .full-img-item img {{max-width:100%;max-height:40vh;border-radius:10px;display:block;margin:0 auto;}}
                .full-img-caption {{text-align:center;font-size:14px;color:#666;margin-top:8px;}}
                .full-img-row {{display:flex;gap:14px;margin-bottom:28px;}}
                .full-img-row .full-img-item {{flex:1;margin-bottom:0;}}
                .full-modal-text {{width:50%;height:100%;overflow-y:auto;padding:28px 32px;box-sizing:border-box;}}
                .full-modal-text h2 {{margin-top:0;margin-bottom:24px;color:#B03A2E;border-bottom:3px solid #B03A2E;padding-bottom:10px;}}
                .full-modal-text p {{font-size:18px;line-height:1.9;color:#333;margin-bottom:18px;text-indent:2em;}}
                .full-modal-close {{position:absolute;top:15px;right:25px;font-size:40px;color:black;cursor:pointer;font-weight:bold;z-index:10;line-height:1;}}
            `;
            if(!parentDoc.getElementById('full-modal-style')){{
                const style=parentDoc.createElement('style');
                style.id='full-modal-style';
                style.innerHTML=modalCss;
                parentDoc.head.appendChild(style);
            }}
            function openModal(index){{
                const article=articles[index];
                const imgGroups={{}};
                article.images.forEach(img=>{{if(!imgGroups[img.caption]) imgGroups[img.caption]=[];imgGroups[img.caption].push(img);}});
                let imgHtml='';
                for(const cap in imgGroups){{
                    const group=imgGroups[cap];
                    if(group.length>1){{
                        imgHtml+='<div class="full-img-row">';
                        group.forEach(img=>{{imgHtml+=`<div class="full-img-item"><img src="${{img.url}}"><div class="full-img-caption">${{cap}}</div></div>`;}});
                        imgHtml+='</div>';
                    }}else{{
                        imgHtml+=`<div class="full-img-item"><img src="${{group[0].url}}"><div class="full-img-caption">${{cap}}</div></div>`;
                    }}
                }}
                const paragraphs=article.content.split('\\n').filter(p=>p.trim());
                let textHtml=`<h2>${{article.title}}</h2>`;
                paragraphs.forEach(p=>{{textHtml+=`<p>${{p.trim()}}</p>`;}});
                const mask=parentDoc.createElement('div');
                mask.className='full-modal-mask';
                mask.innerHTML=`<div class="full-modal-body"><div class="full-modal-close">&times;</div><div class="full-modal-images">${{imgHtml}}</div><div class="full-modal-text">${{textHtml}}</div></div>`;
                parentDoc.body.appendChild(mask);
                mask.querySelector('.full-modal-close').addEventListener('click',closeModal);
                mask.addEventListener('click',e=>{{if(e.target===mask) closeModal();}});
            }}
            function closeModal(){{const mask=parentDoc.querySelector('.full-modal-mask');if(mask) mask.remove();}}
        </script>
        """
        components.html(html_code, height=880)
        st.markdown("---")
        st.markdown("<br><br>", unsafe_allow_html=True)

# ===================== 文创商店 =====================
elif current_page == "文创商店":
    st.divider()


    # ---------- 读取两份CSV数据 ----------
    @st.cache_data
    def load_shop_items():
        desc_csv = "文创产品介绍.csv"
        img_csv = "文创产品图片链接.csv"

        if not os.path.exists(desc_csv) or not os.path.exists(img_csv):
            return []

        df_desc = pd.read_csv(desc_csv, encoding="utf-8-sig")
        df_img = pd.read_csv(img_csv, encoding="utf-8-sig")

        # 单价+单位配置
        price_map = {
            "汉韵琉球主题明信片": {"price": 18, "unit": "/套（一套六张）"},
            "汉韵琉球主题帆布袋": {"price": 39, "unit": "/支"},
            "汉韵琉球主题书签": {"price": 12, "unit": "/对"},
        }

        items = []
        for name, group in df_img.groupby("产品名称"):
            images = []
            for _, row in group.iterrows():
                images.append({
                    "url": str(row["图片链接"]),
                    "caption": str(row["图片注释"]),
                })

            desc_row = df_desc[df_desc["产品名称"] == name]
            desc = str(desc_row.iloc[0]["产品介绍"]) if not desc_row.empty else "暂无介绍"
            info = price_map.get(name, {"price": 0, "unit": ""})

            items.append({
                "name": str(name),
                "category": "文创周边",
                "cover": images[0]["url"] if images else "",
                "images": images,
                "desc": desc,
                "price": info["price"],
                "unit": info["unit"],
            })
        return items


    shop_items = load_shop_items()

    if not shop_items:
        st.info("请将「文创产品介绍.csv」和「文创产品图片链接.csv」放在脚本同目录")
    else:
        data_json = json.dumps(shop_items, ensure_ascii=False)

        html_code = f"""
        <style>
            * {{
                box-sizing: border-box;
                margin: 0;
                padding: 0;
            }}
            body {{
                margin: 0;
                padding: 0;
                overflow: hidden;
            }}
            .shop-page-wrapper {{
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                overflow: hidden;
                padding-top: 8px;
            }}

            /* 3列商品卡片网格 */
            .shop-grid {{
                display: grid;
                grid-template-columns: repeat(3, 1fr);
                gap: 24px;
                padding: 10px 10px 24px 10px;
                max-width: 700px;
                margin: 0 auto;
                margin-top: -10px;
            }}
            .shop-card {{
                background: #fff;
                border-radius: 10px;
                overflow: hidden;
                box-shadow: 0 2px 6px rgba(0,0,0,0.08);
                cursor: pointer;
                transition: transform 0.2s ease, box-shadow 0.2s ease;
            }}
            .shop-card:hover {{
                transform: translateY(-3px);
                box-shadow: 0 5px 12px rgba(0,0,0,0.12);
            }}
            .shop-card-img {{
                height: 130px;
                overflow: hidden;
            }}
            .shop-card-img img {{
                width: 100%;
                height: 100%;
                object-fit: cover;
                display: block;
            }}
            .shop-card-info {{
                padding: 10px 12px;
                text-align: center;
            }}
            .shop-card-name {{
                font-size: 15px;
                font-weight: 600;
                color: #203050;
            }}
            .shop-card-price {{
                font-size: 18px;
                color: #B03A2E;
                font-weight: bold;
                margin-top: 6px;
            }}
            .price-unit {{
                color: #999;
                font-size: 14px;
                font-weight: normal;
                margin-left: 2px;
            }}

            /* 弹窗样式 */
            .shop-modal-mask {{
                position: fixed;
                top: 0;
                left: 0;
                width: 100vw;
                height: 100vh;
                background: rgba(0,0,0,0.65);
                z-index: 99999;
                display: flex;
                justify-content: center;
                align-items: center;
            }}
            .shop-modal-body {{
                width: 90vw;
                height: 90vh;
                background: #fff;
                border-radius: 16px;
                display: flex;
                overflow: hidden;
                position: relative;
            }}
            .shop-modal-images {{
                width: 50%;
                height: 100%;
                overflow-y: auto;
                padding: 24px;
                border-right: 1px solid #e5e5e5;
                box-sizing: border-box;
            }}
            .shop-img-item {{
                margin-bottom: 28px;
            }}
            .shop-img-item img {{
                max-width: 100%;
                max-height: 40vh;
                border-radius: 10px;
                display: block;
                margin: 0 auto;
            }}
            .shop-img-caption {{
                text-align: center;
                font-size: 14px;
                color: #666;
                margin-top: 8px;
            }}
            .shop-img-row {{
                display: flex;
                gap: 14px;
                margin-bottom: 28px;
                align-items: center;
            }}
            .shop-img-row .shop-img-item {{
                flex: 1;
                margin-bottom: 0;
            }}

            .shop-modal-text {{
                width: 50%;
                height: 100%;
                overflow-y: auto;
                padding: 28px 32px;
                box-sizing: border-box;
                display: flex;
                flex-direction: column;
            }}
            .shop-modal-text h2 {{
                margin-top: 0;
                margin-bottom: 10px;
                color: #203050;
                border-bottom: 3px solid #B03A2E;
                padding-bottom: 10px;
            }}
            .shop-modal-cat {{
                color: #888;
                font-size: 15px;
                margin-bottom: 16px;
            }}
            .shop-modal-price {{
                font-size: 30px;
                color: #B03A2E;
                font-weight: bold;
                margin-bottom: 20px;
            }}
            .shop-modal-desc {{
                flex: 1;
                font-size: 18px;
                line-height: 1.9;
                color: #333;
            }}
            .shop-modal-desc p {{
                margin-bottom: 18px;
                text-indent: 2em;
            }}

            /* 购买区域 */
            .shop-buy-section {{
                margin-top: 24px;
                padding-top: 20px;
                border-top: 1px solid #eee;
            }}
            .quantity-row {{
                display: flex;
                align-items: center;
                gap: 15px;
                margin-bottom: 18px;
            }}
            .quantity-label {{
                font-size: 16px;
                color: #333;
            }}
            .quantity-control {{
                display: flex;
                align-items: center;
                border: 1px solid #ddd;
                border-radius: 6px;
                overflow: hidden;
            }}
            .quantity-btn {{
                width: 38px;
                height: 38px;
                border: none;
                background: #f5f5f5;
                cursor: pointer;
                font-size: 20px;
                color: #333;
            }}
            .quantity-btn:disabled {{
                opacity: 0.4;
                cursor: not-allowed;
            }}
            .quantity-btn:hover:not(:disabled) {{
                background: #eee;
            }}
            .quantity-num {{
                width: 54px;
                text-align: center;
                font-size: 16px;
                border: none;
                border-left: 1px solid #ddd;
                border-right: 1px solid #ddd;
                height: 38px;
                background: #fff;
                outline: none;
            }}
            .total-price-row {{
                margin-bottom: 18px;
            }}
            .total-price-label {{
                font-size: 15px;
                color: #666;
            }}
            .total-price {{
                font-size: 28px;
                color: #B03A2E;
                font-weight: bold;
            }}
            .buy-btn {{
                width: 100%;
                padding: 14px 0;
                background: #B03A2E;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 18px;
                font-weight: bold;
                cursor: pointer;
                transition: 0.2s;
            }}
            .buy-btn:disabled {{
                background: #ccc;
                cursor: not-allowed;
                box-shadow: none;
                transform: none;
            }}
            .buy-btn:hover:not(:disabled) {{
                opacity: 0.9;
                transform: translateY(-1px);
                box-shadow: 0 4px 10px rgba(176,58,46,0.3);
            }}

            .shop-modal-close {{
                position: absolute;
                top: 15px;
                right: 25px;
                font-size: 40px;
                color: black;
                cursor: pointer;
                font-weight: bold;
                z-index: 10;
                line-height: 1;
            }}

            /* 顶部浮动提示 */
            .shop-toast {{
                position: fixed;
                top: 30px;
                left: 50%;
                transform: translateX(-50%);
                background: #2ecc71;
                color: white;
                padding: 12px 30px;
                border-radius: 8px;
                font-size: 16px;
                font-weight: 500;
                z-index: 100000;
                box-shadow: 0 4px 12px rgba(0,0,0,0.15);
                opacity: 0;
                transition: opacity 0.3s ease, top 0.3s ease;
                pointer-events: none;
            }}
            .shop-toast.show {{
                opacity: 1;
                top: 50px;
            }}
        </style>

        <div class="shop-page-wrapper">
            <div class="shop-grid" id="shopGrid"></div>
        </div>

        <script>
            const shopItems = {data_json};
            const parentDoc = window.parent.document;
            let currentPrice = 0;
            let currentItemName = '';
            let currentUnit = '';

            // 渲染首页商品卡片
            const grid = document.getElementById('shopGrid');
            let cardHtml = '';
            shopItems.forEach((item, index) => {{
                cardHtml += `
                <div class="shop-card" onclick="openShopModal(${{index}})">
                    <div class="shop-card-img">
                        <img src="${{item.cover}}" alt="${{item.name}}">
                    </div>
                    <div class="shop-card-info">
                        <div class="shop-card-name">${{item.name}}</div>
                        <div class="shop-card-price">¥${{item.price}}<span class="price-unit">${{item.unit}}</span></div>
                    </div>
                </div>
                `;
            }});
            grid.innerHTML = cardHtml;

            // 注入样式到父页面
            if (!parentDoc.getElementById('shop-modal-style')) {{
                const style = parentDoc.createElement('style');
                style.id = 'shop-modal-style';
                style.innerHTML = document.querySelector('style').innerHTML;
                parentDoc.head.appendChild(style);
            }}

            // 打开弹窗
            function openShopModal(index) {{
                const item = shopItems[index];
                currentPrice = item.price;
                currentItemName = item.name;
                currentUnit = item.unit;

                // 按注释分组图片，相同则并排
                const imgGroups = {{}};
                item.images.forEach(img => {{
                    if (!imgGroups[img.caption]) imgGroups[img.caption] = [];
                    imgGroups[img.caption].push(img);
                }});

                // 拼装左侧图片区
                let imgHtml = '';
                for (const cap in imgGroups) {{
                    const group = imgGroups[cap];
                    if (group.length > 1) {{
                        imgHtml += '<div class="shop-img-row">';
                        group.forEach(img => {{
                            imgHtml += `
                            <div class="shop-img-item">
                                <img src="${{img.url}}">
                                <div class="shop-img-caption">${{cap}}</div>
                            </div>
                            `;
                        }});
                        imgHtml += '</div>';
                    }} else {{
                        imgHtml += `
                        <div class="shop-img-item">
                            <img src="${{group[0].url}}">
                            <div class="shop-img-caption">${{cap}}</div>
                        </div>
                        `;
                    }}
                }}

                // 拼装右侧文字区
                const paragraphs = item.desc.split('\\n').filter(p => p.trim());
                let descHtml = '';
                paragraphs.forEach(p => {{
                    descHtml += `<p>${{p.trim()}}</p>`;
                }});

                // 创建遮罩
                const mask = parentDoc.createElement('div');
                mask.className = 'shop-modal-mask';
                mask.innerHTML = `
                    <div class="shop-modal-body">
                        <div class="shop-modal-close">&times;</div>
                        <div class="shop-modal-images">${{imgHtml}}</div>
                        <div class="shop-modal-text">
                            <h2>${{item.name}}</h2>
                            <div class="shop-modal-cat">${{item.category}}</div>
                            <div class="shop-modal-price">¥${{item.price}}<span class="price-unit">${{item.unit}}</span></div>
                            <div class="shop-modal-desc">${{descHtml}}</div>

                            <div class="shop-buy-section">
                                <div class="quantity-row">
                                    <span class="quantity-label">购买数量</span>
                                    <div class="quantity-control">
                                        <button class="quantity-btn" id="btnMinus" disabled>−</button>
                                        <input type="text" class="quantity-num" id="quantityVal" value="0">
                                        <button class="quantity-btn" id="btnPlus">+</button>
                                    </div>
                                </div>
                                <div class="total-price-row">
                                    <span class="total-price-label">合计：</span>
                                    <span class="total-price" id="totalPrice">¥0</span>
                                </div>
                                <button class="buy-btn" id="btnBuy" disabled>立即购买</button>
                            </div>
                        </div>
                    </div>
                `;

                parentDoc.body.appendChild(mask);

                // 绑定关闭事件
                mask.querySelector('.shop-modal-close').addEventListener('click', closeShopModal);
                mask.addEventListener('click', function(e) {{
                    if (e.target === mask) closeShopModal();
                }});

                // 绑定数量控制
                const btnMinus = mask.querySelector('#btnMinus');
                const btnPlus = mask.querySelector('#btnPlus');
                const quantityInput = mask.querySelector('#quantityVal');
                const totalPriceEl = mask.querySelector('#totalPrice');
                const btnBuy = mask.querySelector('#btnBuy');

                function updateQuantity(num) {{
                    num = parseInt(num);
                    if (isNaN(num) || num < 0) num = 0;
                    quantityInput.value = num;
                    totalPriceEl.innerText = '¥' + (currentPrice * num);
                    btnMinus.disabled = num <= 0;
                    btnBuy.disabled = num <= 0;
                }}

                // 加减按钮
                btnMinus.addEventListener('click', function() {{
                    updateQuantity(parseInt(quantityInput.value) - 1);
                }});
                btnPlus.addEventListener('click', function() {{
                    updateQuantity(parseInt(quantityInput.value) + 1);
                }});

                // 手动输入控制
                quantityInput.addEventListener('keydown', function(e) {{
                    // 只允许数字、退格、删除、左右箭头
                    if (!/[0-9]|Backspace|Delete|ArrowLeft|ArrowRight/.test(e.key)) {{
                        e.preventDefault();
                        return;
                    }}

                    // 当前值为0且输入数字时，直接替换
                    if (quantityInput.value === '0' && /[0-9]/.test(e.key)) {{
                        e.preventDefault();
                        updateQuantity(e.key);
                    }}
                }});

                // 输入变化时修正
                quantityInput.addEventListener('input', function() {{
                    // 删空自动变回0
                    if (quantityInput.value === '') {{
                        updateQuantity(0);
                        return;
                    }}
                    // 过滤非数字
                    const num = parseInt(quantityInput.value.replace(/\D/g, ''));
                    updateQuantity(isNaN(num) ? 0 : num);
                }});

                // 失焦修正
                quantityInput.addEventListener('blur', function() {{
                    updateQuantity(quantityInput.value);
                }});

                // 绑定购买按钮
                btnBuy.addEventListener('click', function() {{
                    const num = parseInt(quantityInput.value);
                    if (num <= 0) return;
                    closeShopModal();
                    showToast(`购买成功！${{currentItemName}} ×${{num}} 合计：¥${{currentPrice * num}}`);
                }});
            }}

            // 【已加入防御判断，修复页面跳转toast残留】
            function showToast(text){{
                const oldToast=parentDoc.querySelector('.shop-toast');
                if(oldToast) oldToast.remove();
                const toast=parentDoc.createElement('div');
                toast.className='shop-toast';toast.innerText=text;
                parentDoc.body.appendChild(toast);
                setTimeout(()=>toast.classList.add('show'),10);
                setTimeout(()=>{{toast.classList.remove('show');setTimeout(()=>{{if(toast && toast.parentNode) toast.remove();}},300);}},2000);
            }}

            // 关闭弹窗
            function closeShopModal() {{
                const mask = parentDoc.querySelector('.shop-modal-mask');
                if (mask) mask.remove();
            }}
        </script>
        """

        components.html(html_code, height=880)

        # 底部分割线与留白，和其他页面统一
        st.markdown("---")
        st.markdown("<br><br>", unsafe_allow_html=True)


# ===================== 联系我们 =====================
elif current_page == "联系我们":
    # 页面切入时：清除残留的商店toast通知
    components.html("""
    <script>
    const pDoc = window.parent.document;
    const leftoverToast = pDoc.querySelector('.shop-toast');
    if(leftoverToast) leftoverToast.remove();
    </script>
    """, height=0)

    st.header("联系我们")
    st.divider()
    st.subheader("微信公众号")
    qr_image_url = "https://echo-eternalflames.github.io/picx-images-hosting/qrcode_wechat.webp"
    st.image(qr_image_url, width=320, caption="扫描关注汉韵琉球公众号")
    st.markdown("---")
    st.markdown("<br><br>", unsafe_allow_html=True)
