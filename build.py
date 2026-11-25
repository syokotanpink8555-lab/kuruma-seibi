"""くるま整備ノート ビルド: python build.py → docs/ にサイト一式（GitHub Pagesは /docs を公開）"""
import datetime
import html
import json
import re
from pathlib import Path

from data_keikoku import LIGHTS
from data_koukan import ITEMS, CATS, CHECK_ALWAYS, ADDITIVES

ROOT = Path(__file__).parent
OUT = ROOT / "docs"
# style.css を変えたら版番号が変わり、ブラウザが古いCSSを使い続けないようにする
import hashlib
CSS_VER = hashlib.md5((ROOT / "style.css").read_bytes()).hexdigest()[:8]
SITE = "くるま整備ノート"
DOMAIN = "seibi-note.com"
BASE = f"https://{DOMAIN}/"
URL_MARK = "__PAGE_URL__"  # write() がページのURLに置きかえる
# 「最終更新」はページごと：中身が前回と同じなら前の日付のまま、変わったら今日（write() が入れる）
DATE_MARK = "__UPDATED__"
TODAY = datetime.date.today().isoformat()
PAGE_DATES = {}  # rel → 最終更新日（サイトマップの lastmod に使う）
# 整備士チェックが終わったら True にする（それまでは「チェック済み」と書かない）
REVIEWED = True
AD_CARNEXT = '<a href="https://px.a8.net/svt/ejp?a8mat=4BGK84+AMTRIY+32YG+HYFLU" rel="nofollow sponsored noopener">カーネクスト</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4BGK84+AMTRIY+32YG+HYFLU" alt="">'
AD_AUTOWAY = '<a href="https://px.a8.net/svt/ejp?a8mat=4BGK84+AINQAI+130Q+63WO2" rel="nofollow sponsored noopener">株式会社オートウェイ</a><img border="0" width="1" height="1" src="https://www12.a8.net/0.gif?a8mat=4BGK84+AINQAI+130Q+63WO2" alt="">'
AD_TIRE = '''
<section class="box ad">
  <p class="ad-label">広告</p>
  <h2>タイヤをネットで買って、お店で付けてもらう方法も</h2>
  <p>交換するタイヤは、お店で買うほかに、ネットで買って取り付けだけお店に頼む方法もあります。</p>
  <p>__AD_AUTOWAY__：輸入タイヤを中心に、タイヤ・ホイールを売っている通販です（広告主の案内では、海外のメーカーなどから直輸入）。オートウェイが運営する取付サービス「タイヤピット」の取付店に商品を直接送ってもらい、予約した日にそのお店で取り付けてもらえます。取り付けの工賃のほか、古いタイヤの処分料やバルブ交換料なども別にかかります。</p>
  <p class="small">このリンクから購入があると、このサイトに紹介料が入ります。この枠は広告で、整備士がすすめているものではありません。タイヤは、工賃や処分料も含めた総額で、ほかのお店とも比べてから決めてください。サイズは、今のタイヤの横の表示（例：195/65R15 91H。最後の数字と記号まで同じものを）や取扱説明書で確認できます。注文する前に、製造時期がいつのものかも確かめておくと安心です（このページの基準は、製造から5年で交換）。</p>
</section>
'''.replace("__AD_AUTOWAY__", AD_AUTOWAY)
CHECK_TXT_TODO = "現役の自動車整備士による内容チェックを順次行っています"
CHECK_TXT = "一級自動車整備士・自動車検査員の資格をもつ現役の整備士がチェックしています" if REVIEWED else "現役の自動車整備士による内容チェックを順次行っています"

COLOR = {"red": "赤", "yellow": "黄・オレンジ", "green": "緑", "blue": "青"}
LEVEL = {
    "stop": ("すぐ停車", "安全な場所に停めて相談"),
    "soon": ("早めに点検", "近いうちに整備工場へ"),
    "info": ("お知らせ", "状況を確認すればOKなことが多い"),
}

e = lambda s: html.escape(s, quote=True)


def ld_json(data):
    # 検索結果にパンくず・サイト名を出してもらうための構造化データ（schema.org）
    return '<script type="application/ld+json">' + json.dumps(data, ensure_ascii=False) + '</script>'


def page(title, desc, body, depth=1, path="", check_txt=None, crumbs=None):
    up = "../" * depth
    check = check_txt or CHECK_TXT
    full = SITE if not title else f"{title}｜{SITE}"
    if depth == 0:
        ld = ld_json({"@context": "https://schema.org", "@type": "WebSite", "name": SITE, "url": BASE})
    elif crumbs:  # [(名前, "keikoku/" のような相対パス), ...]。最後はそのページ
        ld = ld_json({"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": i, "name": n, "item": BASE + r}
            for i, (n, r) in enumerate([("トップ", "")] + crumbs, 1)]})
    else:
        ld = ""
    return f"""<!doctype html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(full)}</title>
<meta name="description" content="{e(desc)}">
<meta property="og:title" content="{e(full)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:type" content="website">
<meta property="og:url" content="{URL_MARK}">
<meta property="og:site_name" content="{SITE}">
<meta property="og:image" content="{BASE}assets/ogp.png">
<meta name="twitter:card" content="summary_large_image">
<link rel="canonical" href="{URL_MARK}">
<link rel="stylesheet" href="{up}assets/style.css?v={CSS_VER}">
{ld}
</head>
<body>
<header class="site-head"><div class="wrap">
  <a class="logo" href="{up or './'}">🔧 {SITE}</a>
  <nav><a href="{up}keikoku/">警告灯</a><a href="{up}oil/">オイル交換</a><a href="{up}koukan/">交換時期</a><a href="{up}shaken/">車検費用</a><a href="{up}about/">このサイトについて</a></nav>
</div></header>
<main class="wrap">
{body}
</main>
<footer class="site-foot"><div class="wrap">
  <p>このサイトは、AIの「小太郎」が作り、{check}。
  車の状態は車種や年式で違います。最終的には取扱説明書と整備工場の判断に従ってください。</p>
  <p><a href="{up}about/">運営・免責事項</a>　最終更新 {DATE_MARK}</p>
</div></footer>
</body>
</html>
"""


def _same(old, new):
    """日付とCSSの版番号を除いて、前回と同じ中身か"""
    norm = lambda t: re.sub(r"style\.css\?v=\w+", "", re.sub(r"最終更新 [\w-]+", "", t))
    return norm(old) == norm(new)


def write(rel, text):
    p = OUT / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    text = text.replace(URL_MARK, BASE + rel.removesuffix("index.html"))
    if DATE_MARK in text:
        old = p.read_text(encoding="utf-8") if p.exists() else ""
        m = re.search(r"最終更新 ([\d-]+)", old)
        date = m.group(1) if m and _same(old, text) else TODAY
        PAGE_DATES[rel] = date
        text = text.replace(DATE_MARK, date)
    p.write_text(text, encoding="utf-8")


# ---------------- トップ ----------------
def build_index():
    body = f"""
<section class="hero">
  <h1>車の「これ大丈夫？」を、整備士の目線でかんたんに。</h1>
  <p>メーターの警告灯の意味や、オイル交換の時期など、車に乗っていてふと気になることをまとめています。</p>
</section>
<div class="cards">
  <a class="card" href="keikoku/">
    <span class="card-ic">⚠️</span>
    <h2>警告灯の意味一覧</h2>
    <p>メーターに出たランプの意味と、まずやることがわかる。色で緊急度の目安をチェック。</p>
  </a>
  <a class="card" href="oil/">
    <span class="card-ic">🛢️</span>
    <h2>オイル交換時期の計算</h2>
    <p>排気量・オイル量・タイヤサイズと前回の交換日から、次の交換の目安を計算します。</p>
  </a>
  <a class="card" href="koukan/">
    <span class="card-ic">🧰</span>
    <h2>消耗品の交換時期一覧、整備士の本音</h2>
    <p>見積もりに並んだ交換、今やるべき？ ブレーキパッド・タイヤ・バッテリーなど16項目を3段階で。</p>
  </a>
  <a class="card" href="shaken/">
    <span class="card-ic">📋</span>
    <h2>車検費用の目安計算</h2>
    <p>重量税・自賠責・印紙代は最新の公式の金額で。お店の費用は整備士に聞いた相場。見積もりのポイントも。</p>
  </a>
  <a class="card" href="shien/">
    <span class="card-ic">🚘</span>
    <h2>自動ブレーキ・オートクルーズ・オートハイビーム</h2>
    <p>新車を買ってすぐの点検で「これ何？」とよく聞かれる3つの機能。何をしてくれて、何はしてくれないか。</p>
  </a>
</div>
<section class="box">
  <h2>困ったときは</h2>
  <p>走行中に赤い警告灯が点いた、煙や異音がする、ブレーキの効きがおかしい――そんなときは無理に走らず、
  安全な場所に停めてロードサービス（JAFは <b>#8139</b>）や加入している自動車保険のロードサービスに連絡してください。</p>
  <p>高速道路で止まったときは、ハザードランプをつけ、停止表示器材（三角表示板）を置いて、人はガードレールの外など安全な場所へ避難してください。
  道路上の危険の通報は道路緊急ダイヤル <b>#9910</b> です。</p>
  <p>自分で走れそうでも不安なときは、レッカーを呼ぶのも手です。保険によっては、レッカーで運んだときだけ代車（レンタカー）の費用が出ることがあります。</p>
</section>
"""
    write("index.html", page("", "車の警告灯の意味、オイル交換時期の計算など。AIが作り、一級自動車整備士がチェックする車のお役立ち情報サイトです。", body, depth=0))


# ---------------- 警告灯 ----------------
def build_keikoku():
    items = []
    for L in LIGHTS:
        lv, lvdesc = LEVEL[L["level"]]
        acts = "".join(f"<li>{e(a)}</li>" for a in L["action"])
        tip = f'<p class="tip">💡 {e(L["tip"])}</p>' if L["tip"] else ""
        items.append(f"""
<article class="light c-{L['color']}" id="{L['id']}" data-color="{L['color']}" data-kw="{e(L['name'] + ' ' + L['keywords'] + ' ' + L['look'])}">
  <div class="light-head">
    <span class="dot" aria-hidden="true"></span>
    <h2><a href="{L['id']}/">{e(L['name'])}</a></h2>
    <span class="badge b-{L['level']}">{lv}</span>
  </div>
  <p class="look">見た目：{e(L['look'])}（色：{COLOR[L['color']]}）</p>
  <p class="meaning">{e(L['meaning'])}</p>
  <h3>どうすればいい？</h3>
  <ul>{acts}</ul>
  {tip}
</article>""")

    toc = "".join(f'<li><a href="#{L["id"]}"><span class="dot dot-{L["color"]}"></span>{e(L["name"])}</a></li>' for L in LIGHTS)
    body = f"""
<h1>車の警告灯の意味一覧｜色でわかる緊急度の目安</h1>
<p class="lead">メーターに見慣れないランプが点いたときに、意味とまずやることを確認できるページです。
ランプの<b>色</b>でおおまかな緊急度がわかります。</p>

<div class="legend">
  <div class="lg c-red"><span class="dot"></span><b>赤</b>：すぐに安全な場所に停めて確認・相談</div>
  <div class="lg c-yellow"><span class="dot"></span><b>黄・オレンジ</b>：すぐ止まらなくてよいことが多いが、早めに点検</div>
  <div class="lg c-green"><span class="dot"></span><b>緑・青</b>：装置が作動中などのお知らせ（異常ではない）</div>
</div>

<section class="box tow" id="tow">
  <h2>レッカーという選択肢</h2>
  <p>「走れる」と書いてある警告灯でも、運転するのが不安なときは無理に走らず、レッカーを呼ぶのも手です。</p>
  <p>加入している自動車保険によっては、<b>レッカーで運んだ場合に代車（レンタカー）の費用が出る</b>ことがあります。
  自分で運転して入庫すると対象外になる場合もあるので、迷ったら先に保険会社のロードサービス窓口に電話して確認しましょう。</p>
</section>

<div class="search">
  <input id="q" type="search" placeholder="例：オレンジ エンジン、びっくりマーク、タイヤ" aria-label="警告灯を検索">
  <div class="chips" role="group" aria-label="色でしぼりこむ">
    <button data-c="" class="on">すべて</button>
    <button data-c="red">赤</button>
    <button data-c="yellow">黄</button>
    <button data-c="blue">青・緑</button>
  </div>
  <p id="count" class="count"></p>
</div>

<details class="toc"><summary>一覧（{len(LIGHTS)}種類）</summary><ul>{toc}</ul></details>

<div id="list">{''.join(items)}</div>
<p id="none" class="none" hidden>見つかりませんでした。別の言葉（形や色）で探してみてください。</p>

<section class="box">
  <h2>警告灯についてよくある質問</h2>
  <h3>エンジンをかけたとき全部のランプが一瞬点くのは？</h3>
  <p>電球や装置が正常かを確かめる「ランプチェック」です。数秒で消えれば問題ありません。消えずに残るものがあれば、そのランプの意味を確認してください。</p>
  <h3>警告灯が点いたままでも車検は通る？</h3>
  <p>エンジン・ブレーキ・ABS・エアバッグの警告灯が点灯していると、車検に合格できません（2017年2月から全国で統一されたルールです）。</p>
  <p>さらに2024年10月からは、2021年10月以降に発売された新型車（輸入車は1年遅れ）を対象に「OBD検査」が始まりました。
  ABS・横滑り防止装置・自動ブレーキ・排ガス関係などの故障の記録がコンピューターに残っていると、ランプが消えていても不合格になります。
  車検の前に警告灯が点いたことがあれば、整備工場で見てもらいましょう。</p>
  <h3>一度点いてすぐ消えた。放っておいていい？</h3>
  <p>一時的な誤作動のこともありますが、異常の記録が車のコンピューターに残っていることがあります。次の点検やオイル交換のときに伝えておくと安心です。</p>
</section>
<p class="small">マークの形や色は車種によって異なることがあります。正確な意味は取扱説明書で確認してください。</p>

<script>
(function(){{
  var q=document.getElementById('q'),list=document.querySelectorAll('.light'),
      chips=document.querySelectorAll('.chips button'),none=document.getElementById('none'),
      count=document.getElementById('count'),color='';
  function norm(s){{return s.toLowerCase().replace(/[！!]/g,'!').replace(/\\s+/g,' ')}}
  function run(){{
    var words=norm(q.value).split(' ').filter(Boolean),n=0;
    list.forEach(function(el){{
      var kw=norm(el.dataset.kw+' '+el.textContent),c=el.dataset.color;
      var okC=!color||(color==='blue'?(c==='blue'||c==='green'):c===color);
      var ok=okC&&words.every(function(w){{return kw.indexOf(w)>=0||(w==='オレンジ'&&c==='yellow')||(w==='黄色'&&c==='yellow')||(w==='赤'&&c==='red')||(w==='青'&&c==='blue')}});
      el.hidden=!ok; if(ok)n++;
    }});
    none.hidden=n>0; count.textContent=(words.length||color)?n+'件':'';
  }}
  q.addEventListener('input',run);
  chips.forEach(function(b){{b.addEventListener('click',function(){{
    chips.forEach(function(x){{x.classList.remove('on')}});b.classList.add('on');color=b.dataset.c;run();
  }})}});
}})();
</script>
"""
    write("keikoku/index.html", page("車の警告灯の意味一覧", "車のメーターの警告灯（赤・黄色・青）の意味と、点いたときにまずやることを一覧で。エンジン警告灯、油圧、水温、ブレーキ、ABSなど。色で緊急度の目安がわかります。", body))


# ---------------- オイル交換 ----------------
# 係数は整備士のオーナーさんが調整ラボ（02_お願い/oil-lab.html）で決めた値（2026-11-13、11/17 基準5,000km・オイル量の効き0.7に変更）
OIL_P = dict(baseKm=5000, baseOil=3.7, oilExp=0.7, tireExp=0.9, kei=0.9,
             turbo=0.65, diesel=0.75, hv=1.5, city=0.8, old=0.8, lateMul=1.5,
             maxRec=10000, maxLate=12000)
# 排気量(L) → オイル量(L・フィルター交換時)の目安（11/14 整備士のオーナーさん確認済み：おおよその量として全タイプ共通でOK）
OIL_TABLE = [[0.66, 2.9], [1.0, 3.2], [1.3, 3.4], [1.5, 3.7], [1.8, 4.2], [2.0, 4.4], [2.5, 4.8], [3.0, 5.5], [3.5, 6.0], [5.0, 7.0]]
OIL_TYPE = {"na": "ガソリン", "turbo": "ターボ", "hv": "ハイブリッド", "diesel": "ディーゼル"}


def _tire_dia(w, a, r):
    return r * 25.4 + 2 * w * a / 100


def oil_calc(disp, oil, tire, typ, use="normal"):
    """build時の例の表用。JS の calc() と同じ式"""
    import math
    P = OIL_P
    r500 = lambda v: max(500, math.floor(v / 500 + 0.5) * 500)
    f = (oil / P["baseOil"]) ** P["oilExp"]
    f *= (_tire_dia(*tire) / _tire_dia(175, 65, 15)) ** P["tireExp"]
    if disp <= 0.7:
        f *= P["kei"]
    if typ != "na":
        f *= P[typ]
    if use == "city":
        f *= P["city"]
    rec = min(P["maxRec"], r500(P["baseKm"] * f))
    late = min(P["maxLate"], max(rec, r500(rec * P["lateMul"])))
    return rec, late


OIL_EXAMPLES = [
    ("軽自動車（ターボなし）", 0.66, 2.9, (155, 65, 14), "na"),
    ("軽自動車（ターボ）", 0.66, 2.9, (165, 55, 15), "turbo"),
    ("1.5Lコンパクトカー", 1.5, 3.7, (175, 65, 15), "na"),
    ("1.5Lハイブリッド", 1.5, 3.7, (175, 65, 15), "hv"),
    ("2.0Lミニバン", 2.0, 4.4, (205, 60, 16), "na"),
    ("2.2Lディーゼル SUV", 2.2, 5.1, (225, 55, 19), "diesel"),
    ("3.5L V6 ミニバン", 3.5, 6.1, (225, 60, 17), "na"),
]


def build_oil():
    import json
    rows = []
    for name, d, o, t, typ in OIL_EXAMPLES:
        rec, late = oil_calc(d, o, t, typ)
        mo = "6ヶ月" if typ in ("turbo", "diesel") else "1年"
        rows.append(f"<tr><td>{name}<br><span class=\"small\">{OIL_TYPE[typ]}・オイル{o}L・{t[0]}/{t[1]}R{t[2]}</span></td>"
                    f"<td>{rec:,}km または {mo}</td><td>{late:,}km</td></tr>")
    rows = "\n      ".join(rows)
    body = """
<h1>オイル交換時期の計算ツール</h1>
<p class="lead">排気量・オイル量・タイヤのサイズと、前回交換した日・走行距離を入れると、次の交換の<b>目安</b>を計算します。
現役の一級自動車整備士の考え方をもとに、<b>「おすすめの時期」</b>と<b>「遅くともここまで」</b>の2段階で表示します。</p>
<p>入力すると、<b>入力欄のすぐ下に結果が自動で出ます</b>（計算ボタンはありません）。最低限、<b>排気量</b>と<b>前回交換した日</b>を入れてください。</p>

<div class="sev warn">
  <b>⚠️ 計算結果は「目安」です。</b>
  <ul>
    <li>計算の係数は、現役の整備士が実際の車で試しながら決めたもので、<b>まだ試した車種は多くありません</b>。使った人の声を聞いて見直していきます。</li>
    <li><b>年式・走行距離は「10年以上、または10万km超」かどうかの2段階だけで見ています。</b>同じ車でも、乗り方やエンジンの状態で汚れ方は変わります。</li>
    <li><b>ディーゼル車は、係数を決めた整備士の専門外です。</b>とくに参考程度にして、取扱説明書の交換時期を優先してください。</li>
    <li><b>「おすすめ」で交換するのが基本</b>です。「遅くとも」は、都合がつかなくても超えないでほしい線で、ここまで延ばしてよいという意味ではありません。</li>
    <li><b>取扱説明書の交換時期（距離・期間）が、このツールの「遅くとも」より短いときは、取扱説明書の時期までに交換してください（シビアコンディションの指定も含みます）。</b></li>
    <li>月に1回くらい、オイルレベルゲージで量を見てください。減っている・漏れている・異音がするなど、いつもと違うときは、時期に関係なくお店で点検を受けてください。走行中に<a href="../keikoku/">油圧の警告灯（赤）</a>がついたら、安全な場所に止めてエンジンを切り、お店やロードサービスに連絡してください。</li>
    <li>この時期で交換すれば故障しない、という保証ではありません。</li>
  </ul>
</div>

<form id="f" class="tool" onsubmit="return false">
  <label>エンジンのタイプ
    <select id="type">
      <option value="na">ガソリン車（ターボなし）</option>
      <option value="turbo">ターボ車（軽ターボ含む）</option>
      <option value="hv">ハイブリッド車</option>
      <option value="diesel">ディーゼル車</option>
      <option value="custom">自分で指定する（取扱説明書の数値など）</option>
    </select>
  </label>
  <div id="spec">
    <div class="row">
      <label>排気量<input id="disp" type="number" inputmode="decimal" min="0" step="any" placeholder="例：1500 または 1.5"><span class="small" style="font-weight:400">cc でも L でもOK。軽自動車は 660</span></label>
      <label><span>オイル量（L）<span class="opt">わかれば</span></span><input id="oil" type="number" inputmode="decimal" min="1" max="12" step="0.1"><span id="oilhint" class="small" style="font-weight:400">取扱説明書の「オイル容量（フィルター交換時）」を見ると正確です。空欄なら排気量からの目安で計算します</span></label>
    </div>
    <fieldset style="margin-top:12px">
      <legend>タイヤのサイズ <span class="opt">わかれば。タイヤの横に「175/65R15」のように書いてあります</span></legend>
      <div style="display:flex;gap:6px;align-items:center;flex-wrap:wrap">
        <input id="tw" type="number" inputmode="numeric" min="100" max="355" placeholder="175" style="width:5.5em" aria-label="タイヤの幅">
        <span>/</span>
        <input id="ta" type="number" inputmode="numeric" min="25" max="90" placeholder="65" style="width:4.5em" aria-label="偏平率">
        <span>R</span>
        <input id="tr" type="number" inputmode="numeric" min="10" max="24" placeholder="15" style="width:4.5em" aria-label="ホイールのインチ">
      </div>
    </fieldset>
    <label style="margin-top:12px">ふだんの乗り方
      <select id="use">
        <option value="normal">ふつう</option>
        <option value="city">街乗り・ちょい乗りが多い</option>
      </select>
    </label>
    <label style="margin-top:12px">車の年数・走行距離
      <select id="age">
        <option value="new">10年未満で、10万km以下</option>
        <option value="old">10年以上、または10万km超</option>
      </select>
    </label>
  </div>
  <div id="custom" class="row" hidden>
    <label>交換の距離（km）<input id="ckm" type="number" inputmode="numeric" min="500" step="500" value="5000"></label>
    <label>交換の期間（ヶ月）<input id="cmo" type="number" inputmode="numeric" min="1" max="24" value="12"></label>
  </div>
  <div class="row">
    <label>前回交換した日<input id="date" type="date" required></label>
    <label>前回交換時の走行距離（km）<input id="odo0" type="number" inputmode="numeric" min="0" placeholder="例：42000"></label>
  </div>
  <label><span>今の走行距離（km）<span class="opt">わかれば</span></span><input id="odo1" type="number" inputmode="numeric" min="0" placeholder="例：45500"></label>
</form>

<div id="out" class="result" aria-live="polite"><p class="small">結果はここに出ます。</p></div>

<section class="box">
  <h2>計算の考え方</h2>
  <p>基準は<b>1.5Lのガソリン車（オイル3.7L・タイヤ175/65R15）で、おすすめ5,000km</b>。そこから次の3つで早めたり遅めたりしています。</p>
  <ul>
    <li><b>オイル量</b>：オイルが多いほど、1Lあたりの負担が減って長持ちします。</li>
    <li><b>タイヤの外径</b>：外径が大きいほど、1km走るあいだのタイヤの回転が少なく、エンジンの回転も少なくてすみます。インチの数字ではなく、タイヤ全体の直径で考えます。</li>
    <li><b>エンジンのタイプ</b>：ターボ・ディーゼルは早め、ハイブリッドはエンジンが止まっている時間があるぶん長め。軽自動車は、オイルが少なく、タイヤが小さく、力がないぶん高回転で回るので早めです。</li>
    <li><b>車の年数・走行距離</b>：10年以上、または10万kmを超えた車は2割早めます。</li>
  </ul>
  <p>おすすめの距離は最大10,000km、遅くともの距離は最大12,000kmで止めています。期間はターボ・ディーゼルが6ヶ月、それ以外は1年です。</p>
  <p class="small">ツールはAIの小太郎が作り、係数は現役の整備士が決めました。</p>
  <table class="tbl">
    <thead><tr><th>車の例</th><th>おすすめ</th><th>遅くとも</th></tr></thead>
    <tbody>
      __ROWS__
    </tbody>
  </table>
  <p class="small">乗り方が「ふつう」、10年未満・10万km以下の場合。係数は、現役の整備士が実際の車で試しながら決めたもので、まだ試した車種は多くありません。使った人の声を聞きながら見直していきます。</p>

  <h3>古い車は？</h3>
  <p>最近のエンジンは汚れにくく、年式の古い車や走行距離が多い車ほど汚れやすい傾向があります。このツールでは、10年以上、または10万kmを超えた車は2割早めて計算します（2割という値は、現役の整備士が決めました）。それより新しくても、抜いたオイルの汚れがひどいときは早めにしてください。</p>

  <h3>取扱説明書には「15,000km」と書いてあるけど？</h3>
  <p>国内メーカーの取扱説明書では、ターボなしのガソリン車で「15,000kmまたは1年」となっている車種も多くあります。
  ただ、整備の現場から見ると<b>15,000kmは遅すぎる</b>というのが正直なところです。
  オイルが汚れたまま走るとエンジンの中が少しずつ削れ、そのスピードが早くなってエンジンの寿命を縮めます。
  逆に、取扱説明書の交換時期（距離・期間）が、このツールの「遅くとも」より短いときは、取扱説明書の時期までに交換してください（シビアコンディションの指定も含みます）。</p>

  <h3>「シビアコンディション」は気にしたほうがいい？</h3>
  <p>取扱説明書には、短い距離の運転や渋滞が多い使い方（シビアコンディション）だと交換時期を短くするよう書かれています。
  このツールでは「街乗り・ちょい乗りが多い」を選ぶと、少し早めに計算します。
  このツールの距離は、取扱説明書のふつうの時期より短めにしてあります。そのうえで期間（1年、ターボ・ディーゼルは6ヶ月）を守っていれば、整備士の目からはそこまで心配しなくてよい、という考えです。
  ただ、取扱説明書でシビアコンディションの時期が決まっている車、とくに新車保証の期間中は、取扱説明書どおりにするのが確実です（保証の条件になっていることがあります）。</p>

  <h3>自分の車に合った時期を知るには</h3>
  <p>いちばん確かなのは、交換のときに<b>抜いたオイルの汚れ具合をお店の人に聞いてみる</b>ことです。
  汚れがひどければ次は早めに、きれいなら今のペースで大丈夫。何回か続けると、自分の乗り方と車に合った交換時期がわかってきます。</p>

  <h3>オイルエレメント（フィルター）は？</h3>
  <p>オイル交換2回に1回の交換が一般的な目安です。ただし、抜いたオイルにライトを当てても全く透けないほど汚れているときは、回数に関係なく交換したほうがいいです。</p>

  <h3>あまり走らないなら交換しなくていい？</h3>
  <p>エンジンオイルは走らなくても時間とともに劣化します。距離が少なくても、1年（ターボ・ディーゼルは6ヶ月）たったら交換しましょう。</p>
</section>

__SHEET__
<section class="box">
  <h2>使ってみた感想を教えてください</h2>
  <p>この計算は、まだ育てている途中です。使ってみて「うちの車だと早すぎる・遅すぎる」と感じたら、小太郎の note の記事<a href="https://note.com/ai_kotaro/n/n47dc546ecfcd" rel="noopener">「オイル交換の目安ツールを作りました（感想募集）」</a>のコメント欄で教えてください。</p>
  <p class="small">あると助かる情報：エンジンのタイプ・排気量・タイヤサイズ・だいたいの年式、計算結果、交換したときのオイルの汚れ具合（お店の人の一言でOK）。コメントするには note のアカウントが必要で、コメントは公開されます。ナンバー・お名前・お店の名前など、個人やお店がわかることは書かないでください。</p>
</section>

<script>
(function(){
  var P=__P__, OT=__OT__;
  var TN={na:'ガソリン',turbo:'ターボ',hv:'ハイブリッド',diesel:'ディーゼル'};
  var $=function(id){return document.getElementById(id)};
  var f=$('f'),out=$('out');
  function addMonths(d,m){var r=new Date(d.getFullYear(),d.getMonth()+m,d.getDate());if(r.getDate()!==d.getDate())r.setDate(0);return r}
  function fmt(d){return d.getFullYear()+'年'+(d.getMonth()+1)+'月'+d.getDate()+'日'}
  function n(v){return v===''?null:Math.max(0,Math.floor(Number(v)))}
  function num(v){v=Number(v);return v>0&&isFinite(v)?v:null}
  function c(x){return x.toLocaleString('ja-JP')}
  function r500(v){return Math.max(500,Math.round(v/500)*500)}
  function dia(w,a,r){return r*25.4+2*w*a/100}
  function guessOil(d){
    if(d<=OT[0][0])return OT[0][1];
    for(var i=1;i<OT.length;i++){var a=OT[i-1],b=OT[i];if(d<=b[0])return Math.round((a[1]+(b[1]-a[1])*(d-a[0])/(b[0]-a[0]))*10)/10}
    return OT[OT.length-1][1];
  }
  function calc(){
    var type=$('type').value,dv=num($('disp').value);
    if(!dv)return null;
    var d=dv>20?dv/1000:dv;                       // cc でも L でも
    if(d<0.3||d>8)return {err:'排気量を確認してください（例：1500 または 1.5）'};
    var kei=d<=0.7;
    var g=guessOil(d),oil=num($('oil').value),oilGuess=!oil;
    if(!oil)oil=g;
    $('oilhint').textContent='取扱説明書の「オイル容量（フィルター交換時）」を見ると正確です。空欄なら排気量からのおおよその量（'+g+'L）で計算します。取扱説明書の値を入れると、より正確になります';
    if(oil<1||oil>12)return {err:'オイル量を確認してください（例：3.7）'};
    var w=num($('tw').value),a=num($('ta').value),r=num($('tr').value),tireGuess=!(w&&a&&r);
    if(!tireGuess&&(w<125||w>335||a<25||a>85||r<10||r>24))return {err:'タイヤサイズを確認してください（例：175/65R15）'};
    if(tireGuess){if(kei){w=155;a=65;r=14}else{w=175;a=65;r=15}}
    var D=dia(w,a,r),D0=dia(175,65,15);
    var x=Math.pow(oil/P.baseOil,P.oilExp)*Math.pow(D/D0,P.tireExp);
    if(kei)x*=P.kei;
    if(type!=='na')x*=P[type];
    var city=$('use').value==='city',old=$('age').value==='old';
    if(city)x*=P.city;
    if(old)x*=P.old;
    var km=Math.min(P.maxRec,r500(P.baseKm*x));
    var lim=Math.min(P.maxLate,Math.max(km,r500(km*P.lateMul)));
    var note=TN[type]+(kei?'（軽自動車）':'')+'・'+(Math.round(d*100)/100)+'L・オイル'+oil+'L'+(oilGuess?'（目安）':'')+
      '・タイヤ'+w+'/'+a+'R'+r+(tireGuess?'（よくあるサイズで計算）':'')+(city?'・街乗り多め':'')+(old?'・10年以上か10万km超':'');
    return {km:km,lim:lim,mo:(type==='turbo'||type==='diesel')?6:12,note:note};
  }
  function run(){
    var type=$('type').value;
    $('custom').hidden=type!=='custom';$('spec').hidden=type==='custom';
    var km,lim,mo,note='',need=[];
    if(type==='custom'){if(!n($('ckm').value)||!n($('cmo').value))need.push('交換の距離と期間')}
    else if(!num($('disp').value))need.push('排気量');
    if(!$('date').value)need.push('前回交換した日');
    if(need.length){out.innerHTML='<h2>次のオイル交換の目安</h2><p class="small">結果はここに出ます。あと<b>「'+need.join('」「')+'」</b>を入れてください。</p>';out.hidden=false;return}
    if(type==='custom'){km=n($('ckm').value);mo=Math.min(n($('cmo').value)||0,36);lim=null}
    else{var r=calc();if(!r){out.hidden=true;return}
      if(r.err){out.innerHTML='<p class="st st-soon">'+r.err+'</p>';out.hidden=false;return}
      km=r.km;lim=r.lim;mo=r.mo;note=r.note}
    var dv=$('date').value;if(!dv){out.hidden=true;return}
    var p=dv.split('-'),d0=new Date(+p[0],p[1]-1,+p[2]);
    if(p.length!==3||isNaN(d0)){out.hidden=true;return}
    var today=new Date();today=new Date(today.getFullYear(),today.getMonth(),today.getDate());
    if(d0>today){out.innerHTML='<p class="st st-soon">前回交換日が未来の日付になっています。日付を確認してください。</p>';out.hidden=false;return}
    var due=addMonths(d0,mo),days=Math.round((due-today)/864e5);
    var o0=n($('odo0').value),o1=n($('odo1').value),driven=null;
    var h='<h2>次のオイル交換の目安</h2><div class="due">';
    h+='<div><span>期間で</span><b>'+fmt(due)+'</b><small>'+(days>=0?'あと'+days+'日':Math.abs(days)+'日過ぎています')+'</small></div>';
    if(o0!==null){
      h+='<div><span>距離で（'+(type==='custom'?'指定した距離':'おすすめ')+'）</span><b>'+c(o0+km)+' km</b>';
      if(lim)h+='<small>遅くとも '+c(o0+lim)+' km</small>';
      if(o1!==null&&o1<o0)h+='<small>今の走行距離が前回より小さくなっています。数字を確認してください。</small>';
      if(o1!==null&&o1>=o0){driven=o1-o0;h+='<small>前回から '+c(driven)+' km 走行</small>'}
      h+='</div>';
    }
    h+='</div>';
    var over=days<0||(driven!==null&&lim!==null&&driven>=lim)||(driven!==null&&lim===null&&driven>=km);
    var time=!over&&((driven!==null&&driven>=km)||days<=30);
    var cls=over?'late':time?'soon':'ok';
    var msg=over?'交換の時期を過ぎています。できるだけ早く交換しましょう。'
      :time?'交換どきです。近いうちに交換しましょう。'
      :'目安の時期まで、まだ余裕があります。距離と期間のどちらか早いほうで交換してください。';
    if(cls==='ok'&&driven===null)msg+='<br>※走行距離が入っていないので、期間だけで判定しています。前回と今の走行距離も入れると、距離でも判定できます。';
    if(cls==='ok'&&driven!==null&&driven>0){
      var used=(today-d0)/864e5;
      if(used>=14){var perDay=driven/used,kmDay=Math.round((km-driven)/perDay);
        if(kmDay<days){var pd=new Date(today.getTime()+kmDay*864e5);
          if(kmDay<=30){cls='soon';msg='もうすぐ交換どきです。予約や準備をしておきましょう。'}
          msg+='<br>今のペース（1日約'+c(Math.round(perDay))+'km）だと、<b>'+fmt(pd)+'ごろ</b>におすすめの距離に届きそうです。'}}
    }
    h+='<p class="st st-'+cls+'">'+msg+'</p>';
    h+='<p class="small">使った目安：'+(type==='custom'?'指定 ':'おすすめ ')+c(km)+'km'+(lim?'（遅くとも '+c(lim)+'km）':'')+' または '+mo+'ヶ月。'+(note?'<br>'+note:'')+'</p>';
    if(type==='diesel')h+='<p class="small">※ ディーゼル車は、係数を決めた整備士の専門外です。とくに参考程度にして、取扱説明書の交換時期を優先してください。</p>';
    h+='<p class="small">※ あくまで目安です。取扱説明書の交換時期（距離・期間）が、このツールの「遅くとも」より短いときは、取扱説明書の時期までに交換してください（シビアコンディションの指定も含みます）。いつもと違うことがあれば、時期に関係なくお店で点検を。走行中に油圧の警告灯（赤）がついたら、安全な場所に止めてエンジンを切ってください。</p>';
    out.innerHTML=h;out.hidden=false;
  }
  f.addEventListener('input',run);f.addEventListener('change',run);run();
})();
</script>
"""
    body = (body.replace("__ROWS__", rows)
                .replace("__P__", json.dumps(OIL_P))
                .replace("__OT__", json.dumps(OIL_TABLE))
                .replace("__SHEET__", OIL_SHEET_BOX))
    write("oil/index.html", page("オイル交換時期の計算ツール", "排気量・オイル量・タイヤサイズと前回の交換日・走行距離から、次のオイル交換の目安を計算。現役の一級整備士の考え方で「おすすめ」と「遅くとも」の2段階表示。ガソリン・軽・ターボ・ハイブリッド・ディーゼルに対応。結果は目安です。", body))


# ---------------- 車検費用 ----------------
# 法定費用（2026-11-13 に一次資料で確認。改定されたらここを直す。メモ: 03_事業/05_車検費用ツール_法定費用メモ.md）
SHAKEN = dict(
    asof="2026年11月13日",
    # 自動車重量税（継続検査・2年自家用）2026/5/1からの税額表（国交省）
    # 普通・小型は 0.5t あたり、軽は1台あたり
    tax={"futsu": {"free": 0, "eco": 5000, "no": 8200, "y13": 11400, "y18": 12600},
         "kei": {"free": 0, "eco": 5000, "no": 6600, "y13": 8200, "y18": 8800}},
    # 自賠責 24か月（2026/11/1以降に始まる契約、離島・沖縄県を除く）損害保険料率算出機構
    jibai={"futsu": 18560, "kei": 18660},
    jibai25={"futsu": 19070, "kei": 19170},
    # 検査手数料（継続検査・保安基準適合証）2026/4/1〜 OSS 1,850円／窓口 2,100円
    inshi=[1850, 2100],
    # お店の費用（現役整備士の現場の声。幅で）
    tenken=[20000, 25000], kensa=[10000, 15000], daikou=[0, 8800], obd=[2200, 4000],
)
SHAKEN_SRC = [
    ("自動車重量税：国土交通省「2026年5月1日からの自動車重量税の税額表」", "https://www.mlit.go.jp/jidosha/content/001884517.pdf"),
    ("自賠責保険：損害保険料率算出機構「自動車損害賠償責任保険基準料率（2026年4月30日届出）」", "https://www.giroj.or.jp/ratemaking/cali/pdf/202604_table.pdf"),
    ("検査手数料：国土交通省「自動車の登録・検査の法定手数料変更について（令和8年4月1日）」", "https://www.mlit.go.jp/jidosha/content/001986066.pdf"),
    ("OBD検査：国土交通省「OBD検査とは？（ユーザー向け）」", "https://www.mlit.go.jp/jidosha/jidosha_OBD_user.html"),
    ("車検を受けられる期間：国土交通省 報道発表「車検を受けられる期間が延びます」", "https://www.mlit.go.jp/report/press/jidosha02_hh_000645.html"),
    ("ブーツ類・スタビライザの基準：自動車技術総合機構 審査事務規程 7-22・8-22 緩衝装置", "https://www.naltec.go.jp/publication/regulation/hbh5ss0000002mk7-att/gtg5d20000002iy5.pdf"),
    ("かじ取装置のブーツの基準：自動車技術総合機構 審査事務規程 7-13・8-13 かじ取装置", "https://www.naltec.go.jp/publication/regulation/hbh5ss0000002mk7-att/gtg5d20000002itt.pdf"),
    ("ドライブシャフトのブーツの基準：自動車技術総合機構 審査事務規程 7-9・8-9 原動機及び動力伝達装置", "https://www.naltec.go.jp/publication/regulation/hbh5ss0000002mk7-att/gtg5d20000002is5.pdf"),
    ("1年ごとの点検：道路運送車両法 第48条（e-Gov法令検索）", "https://laws.e-gov.go.jp/law/326AC0000000185"),
    ("1年ごとの点検：国土交通省「点検整備の種類」", "https://www.mlit.go.jp/jidosha/jidosha/tenkenseibi/tenken/t1/t1-2/"),
]


def wareki(y):
    """車検証の表記（H25・R3）に合わせて和暦を先に出す"""
    if y >= 2020:
        return f"R{y - 2018}（{y}年）"
    if y == 2019:
        return "H31・R1（2019年）"
    return f"H{y - 1988}（{y}年）"


def build_shaken():
    import json
    S = SHAKEN
    t, j = S["tax"], S["jibai"]
    yen = lambda v: f"{v:,}円"
    rows = "\n      ".join(
        f"<tr><td>{lab}</td><td>{yen(t['futsu'][k])}</td><td>{yen(t['futsu'][k] * 3)}</td><td>{yen(t['kei'][k])}</td></tr>"
        for k, lab in [("eco", "エコカー（本則税率）"), ("no", "エコカー以外（13年未満）"), ("y13", "13年経過"), ("y18", "18年経過")])
    src = "\n    ".join(f'<li>{e(a)}<br><a href="{u}" rel="noopener">{u}</a></li>' for a, u in SHAKEN_SRC)
    wopts = "".join(f'<option value="{i}"{" selected" if i == 3 else ""}>{f"{(i - 1) * 500 + 1:,}" if i > 1 else ""}{"〜" if i > 1 else ""}{i * 500:,}kg{"以下" if i == 1 else ""}</option>'
                    for i in range(1, 7))
    body = """
<h1>車検費用の目安計算</h1>
<p class="pr">このページには広告が含まれています（ページ下の「広告」の枠）</p>
<p class="lead">車の種類・重さ・年数を選ぶと、車検にかかる費用の<b>目安</b>を計算します。
国に払う<b>法定費用</b>（重量税・自賠責保険・印紙代）は公式の最新の金額で、<b>お店の費用</b>は現役の整備士に聞いた目安の幅で出します。</p>

<div class="sev warn">
  <b>⚠️ このツールについて</b>
  <ul>
    <li>対象は<b>自家用の乗用車（普通・小型・軽）</b>だけです（新車から初回は3年、その後は2年ごとの車検）。事業用（緑・黒ナンバー）、貨物車（4ナンバー・軽バンなど）、沖縄県・離島は金額が違うので対象外です。</li>
    <li>法定費用は__ASOF__時点の金額です。お店の費用は、お店や車種によって幅があります。</li>
    <li><b>エンジンオイルなどの交換部品の代金と工賃は入っていません。</b>実際の車検代は、計算した金額に交換部品と工賃が足されたものになります。</li>
    <li>重量税の正確な金額は、車検証を見ながら国土交通省の「次回自動車重量税額照会サービス」（<a href="https://www.nextmvtt.mlit.go.jp/nextmvtt-web/" rel="noopener">登録車</a>／<a href="https://www.kei-nextmvtt.jp/kei_nextmvtt-web/" rel="noopener">軽自動車</a>）で調べられます。</li>
  </ul>
</div>

<form id="f" class="tool" onsubmit="return false">
  <label>車の種類
    <select id="kind">
      <option value="futsu">普通車・小型車（白ナンバー）</option>
      <option value="kei">軽自動車（黄色ナンバー）</option>
    </select>
  </label>
  <label id="wl">車両重量 <span class="small" style="font-weight:400">車検証の「車両重量」。「車両総重量」ではありません</span>
    <select id="w">__WOPTS__</select>
  </label>
  <div class="row">
    <fieldset>
      <legend>初度登録年月 <span class="opt">車検証の「初度登録年月」（軽は「初度検査年月」）。「H25」「R3」のように和暦で書いてあります</span></legend>
      <div style="display:flex;gap:6px">
        <select id="y1" aria-label="初度登録の年">__Y1__</select>
        <select id="m1" aria-label="初度登録の月">__M__</select>
      </div>
    </fieldset>
    <fieldset>
      <legend>車検を受ける年月 <span class="opt">予定</span></legend>
      <div style="display:flex;gap:6px">
        <select id="y2" aria-label="車検を受ける年">__Y2__</select>
        <select id="m2" aria-label="車検を受ける月">__M2__</select>
      </div>
    </fieldset>
  </div>
  <p id="agemsg" class="small" style="margin:0"></p>
  <div class="row">
    <label id="ecol">エコカー減税
      <select id="eco">
        <option value="unknown">わからない</option>
        <option value="eco">対象（本則税率）</option>
        <option value="no">対象外</option>
        <option value="free">免税（照会サービスで免税と出た）</option>
      </select>
    </label>
  </div>
  <label>OBD検査の対象 <span class="small" style="font-weight:400">車検証の備考欄に「OBD検査対象」と書いてあれば対象</span>
    <select id="obd">
      <option value="unknown">わからない</option>
      <option value="yes">対象（書いてある）</option>
      <option value="no">対象外（書いていない）</option>
    </select>
  </label>
</form>

<div id="out" class="result" aria-live="polite"></div>

<section class="box">
  <h2>車検費用の中身</h2>
  <p>車検費用は、大きく分けて<b>法定費用</b>（どのお店でも同じ）と<b>お店の費用</b>（お店で違う）、そして<b>部品の交換代</b>の3つです。</p>
  <h3>法定費用（__ASOF__時点）</h3>
  <ul>
    <li><b>自賠責保険（24か月）</b>：普通・小型 __J_F__／軽 __J_K__。2026年11月1日以降に始まる契約から値上がりしました。お店によっては25か月で入ることがあり、その場合は少し高くなります（普通・小型 __J25_F__／軽 __J25_K__）。</li>
    <li><b>印紙代（検査手数料）</b>：ディーラーや整備工場（指定工場）で受けるときは 1,850円〜2,100円（オンライン申請か窓口かで違います）。指定工場でない整備工場やユーザー車検（持込検査）では、普通車2,600円・小型車と軽2,500円です。2026年4月1日に上がりました（このツールは指定工場の金額で計算）。</li>
    <li><b>自動車重量税（2年分）</b>：車の重さと年数、エコカーかどうかで決まります（下の表）。</li>
  </ul>
  <table class="tbl">
    <thead><tr><th>重量税（2年分）</th><th>普通・小型 0.5tごと</th><th>例：1.5tまで</th><th>軽自動車</th></tr></thead>
    <tbody>
      __ROWS__
    </tbody>
  </table>
  <p class="small">2026年5月1日からの税額。普通・小型は初度登録年月から12年10か月以後、軽は初度検査年から13年たった年の11月以後に受ける車検から「13年経過」の税額になります（18年も同じ考え方）。エコカー減税で免税になる車もあります。ハイブリッド車・電気自動車などは、13年を過ぎても重量税が上がらない場合があります。年数の長い車は照会サービスで確かめるのが確実です。</p>
  <h3>お店の費用（現役の整備士に聞いた目安）</h3>
  <ul>
    <li><b>24か月点検</b>：2万円ちょっと（車種によって違います。このツールでは20,000〜25,000円で計算）</li>
    <li><b>検査費用</b>：1万円ちょっと（このツールでは10,000〜15,000円で計算）</li>
    <li><b>代行手数料</b>：8,800円の例があります（名前や金額はお店によって違います。このツールでは0円〜8,800円の幅にしています）</li>
    <li><b>OBD検査料</b>：2,200円くらいのお店から4,000円くらいのお店まで。<b>OBD検査の対象の車だけ</b>にかかります</li>
  </ul>
  <p class="small">このツールでは、上の幅をそのまま足しています。大きなお店は税込で書いていることがほとんどですが、見積もりが税込かどうかは一応確認してください。</p>
</section>

<section class="box">
  <h2>見積もりを見るときのポイント（現役の整備士の声）</h2>
  <h3>車検の点検でよく見つかる部品</h3>
  <p><b>スタビライザーリンク</b>や<b>ブーツ類</b>（タイロッドエンドブーツ・ロワアームブーツ・ドライブシャフトブーツなど）は、ガタや破れがあると<b>車検に通りません</b>（国の検査の基準で、不適合と決められています）。
  車検の点検で見つかると、車検に通すために交換が見積もりに入ります。「今回はやめておく」とは言えない部品です。</p>
  <p><b>ブレーキパッド</b>も、車検の見積もりによく入ってくる部品です。残りの厚みを聞いて、今やるべきかは<a href="../koukan/">消耗品の交換時期、整備士の本音</a>も参考にしてください。</p>
  <h3>タイヤとバッテリーは先に下調べを</h3>
  <p>タイヤとバッテリーは、車検でほぼ必ず見られます。車検の当日に交換をすすめられると、「ほかの銘柄がよかった」と選び直すのが難しくなります。
  車検の前に、お店で状態を聞いておくか自分で見ておいて、付けたいものがあれば値段も含めて下調べしておくと安心です。</p>
  <h3>「今回はやらなくていい」と言いやすいもの</h3>
  <p>洗車関係や添加剤類は、必要なければ断っても車検には関係ありません。</p>
  <p>ただし、<b>下回りの洗浄</b>は洗車とは別に考えてください。ゴム部品を長持ちさせられるので、やったほうがいいものです（別料金で6,000円くらいのお店もあります）。
  <b>海の近くや、冬に融雪剤（塩カル）をまく地域</b>では、<b>下回りの防錆</b>もやっておくのがおすすめです。錆びてしまってからでは元に戻せません。</p>
  <h3>OBD検査の対象外なのに、検査料が入っていないか</h3>
  <p>OBD検査の対象は、2021年10月1日以降（輸入車は2022年10月1日以降）にフルモデルチェンジした新しい型の車などです。車検証の備考欄に「OBD検査対象」と書いてあれば対象です。
  対象ではないのにOBD検査料が入っていた例もあるので、見積もりに入っていたら確かめてみてください。</p>
  <h3>代車</h3>
  <p>代車は無料のお店が多いですが、お店の好意で用意してもらっているものです。台数に限りがあるので、早めに予約しておくと安心です。</p>
</section>

<section class="box">
  <h2>新車保証が残っているうちは、買ったお店で</h2>
  <p>新車には、一般的に3年（主要な部品は5年）のメーカー保証がついています（期間や条件はメーカーや車で違うので、保証書で確認してください）。保証が残っているうちは、安さだけで選んで、買ったお店以外に車検や点検を出すのはあまりおすすめしません（同じメーカーのディーラーなら保証は使えます）。
  <b>保証で直せたはずの部品を、有料で交換していた</b>ということがたまに起きるからです。</p>
  <p><b>1年ごとの点検（12か月点検）は、法律で決められた、車の使用者の義務です</b>（道路運送車両法第48条。自家用の乗用車は1年ごと。車検のない年も受ける点検です）。
  点検で早く見つかれば、保証期間のうちに直せることもあります。車検の当日に不具合を伝えても、症状によっては保証が使えない場合があります。</p>
  <p>点検を受けなくても罰則はありません。でも、点検をしないまま、たとえば<b>走っている途中にタイヤが外れて、ほかの人にけがをさせてしまったら取り返しがつきません</b>。自分と周りの人を守るために、点検は大事です。</p>
</section>

<section class="box">
  <h2>そのほかに知っておきたいこと</h2>
  <ul>
    <li>車検は、有効期間が切れる日の<b>2か月前から</b>受けても、次の有効期間は短くなりません（2025年4月1日から。それまでは1か月前からでした）。年度末はお店が混むので、早めの予約がおすすめです。</li>
  </ul>
</section>

<section class="box ad">
  <p class="ad-label">広告</p>
  <h2>車検を受けるか、手放すかで迷ったら</h2>
  <p>年数がたつと、重量税が上がる車が多くあります（13年・18年経過。ハイブリッド車などは例外あり。上の表）。車検を受けて乗り続ける費用と比べるために、手放した場合の買取額を聞いてみるのもひとつの方法です。</p>
  <p>__AD_CARNEXT__：電話とWEBで査定を申し込める、車の買取サービスです（広告主の案内では、お店への持ち込みや出張査定は不要）。</p>
  <p class="small">このリンクから申し込みがあると、このサイトに紹介料が入ります。買取額は車の状態や時期で変わるので、ほかの買取店やお店の下取りとも比べてから決めてください。</p>
</section>

<section class="box">
  <h2>このページの情報のもと</h2>
  <ul>
    __SRC__
  </ul>
  <p class="small">法定費用は、AIの小太郎が上の公式資料で確認しました。お店の費用と見積もりのポイントは、現役の整備士に聞いた現場の声をもとにしています。このページの文章は、一級自動車整備士・自動車検査員の資格をもつ現役の整備士がチェックしています（2026年11月）。</p>
</section>

<script>
(function(){
  var S=__S__;
  var $=function(id){return document.getElementById(id)};
  function c(x){return x.toLocaleString('ja-JP')+'円'}
  function rng(a,b){return a===b?c(a):c(a)+'〜'+c(b)}
  function run(){
    var kind=$('kind').value,eco=$('eco').value,obd=$('obd').value;
    var y1=Number($('y1').value),m1=Number($('m1').value),y2=Number($('y2').value),m2=Number($('m2').value),age='lt13',am='';
    if(y1===1900){age='y18';am='→ この車検は「18年経過」の重量税になります。'}
    else if(y1&&m1){
      // 国交省：普通・小型は初度登録年月から12年10か月以後、軽は初度検査年から13年たった年の11月以後に受ける車検から（18年も同じ）
      function over(n){return kind==='kei'?(y2>y1+n||(y2===y1+n&&m2>=11)):((y2*12+m2)-(y1*12+m1)>=n*12-2)}
      if((y2*12+m2)<(y1*12+m1)){am='車検を受ける年月が、初度登録年月より前になっています。'}
      else{age=over(18)?'y18':over(13)?'y13':'lt13';
        am=age==='y18'?'→ この車検は「18年経過」の重量税になります。':age==='y13'?'→ この車検は「13年経過」の重量税になります。':'→ この車検は、13年経過の前の重量税です。'}
    }else{am='初度登録の年と月を選ぶと、13年・18年経過の重量税かどうかも自動で判定します（選ばないときは13年経過の前として計算）。'}
    $('agemsg').textContent=am;
    var kei=kind==='kei';
    $('wl').hidden=kei; $('ecol').hidden=age!=='lt13';
    var units=kei?1:Number($('w').value);
    var T=S.tax[kind],tx;
    if(age!=='lt13'){tx=[T[age]*units,T[age]*units]}
    else if(eco==='unknown'){tx=[T.eco*units,T.no*units]}
    else{tx=[T[eco]*units,T[eco]*units]}
    var jb=S.jibai[kind];
    var legal=[tx[0]+jb+S.inshi[0],tx[1]+jb+S.inshi[1]];
    var ob=obd==='yes'?S.obd:obd==='no'?[0,0]:[0,S.obd[1]];
    var shop=[S.tenken[0]+S.kensa[0]+S.daikou[0]+ob[0],S.tenken[1]+S.kensa[1]+S.daikou[1]+ob[1]];
    var h='<h2>車検費用の目安</h2>';
    h+='<div class="sev warn" style="margin-top:0"><b>⚠️ この金額で車検が終わるわけではありません。</b><br>下の金額に、<b>エンジンオイルなどの交換部品の代金と、その工賃</b>が足されます。何をどれだけ交換するかは車の状態しだいなので、実際の金額はお店の見積もりで確かめてください。</div>';
    h+='<div class="due">';
    h+='<div><span>車検の基本料金（交換部品・工賃は別）</span><b>'+rng(legal[0]+shop[0],legal[1]+shop[1])+'</b><small>＋ 交換部品の代金と工賃</small></div>';
    h+='<div><span>うち法定費用（どのお店でも同じ）</span><b>'+rng(legal[0],legal[1])+'</b></div></div>';
    h+='<table class="tbl" style="margin-top:12px"><tbody>';
    h+='<tr><td>自動車重量税（2年分）</td><td>'+rng(tx[0],tx[1])+'</td></tr>';
    h+='<tr><td>自賠責保険（24か月）</td><td>'+c(jb)+'</td></tr>';
    h+='<tr><td>印紙代（検査手数料）</td><td>'+rng(S.inshi[0],S.inshi[1])+'</td></tr>';
    h+='<tr><td>24か月点検</td><td>'+rng(S.tenken[0],S.tenken[1])+'</td></tr>';
    h+='<tr><td>検査費用</td><td>'+rng(S.kensa[0],S.kensa[1])+'</td></tr>';
    h+='<tr><td>代行手数料</td><td>'+rng(S.daikou[0],S.daikou[1])+'</td></tr>';
    h+='<tr><td>OBD検査料</td><td>'+(obd==='no'?'かからない':rng(ob[0],ob[1]))+'</td></tr>';
    h+='</tbody></table>';
    var notes=[];
    if(age==='lt13'&&eco==='unknown')notes.push('エコカー減税がわからないので、重量税は「エコカー（本則税率）」から「エコカー以外」までの幅で出しています。免税の車もあります。');
    if(age!=='lt13')notes.push('ハイブリッド車・電気自動車などは、13年を過ぎても重量税が上がらない場合があります。照会サービスで確かめると確実です。');
    if(obd==='unknown')notes.push('OBD検査の対象かわからないので、OBD検査料は0円〜'+c(S.obd[1])+'の幅にしています。車検証の備考欄を見てみてください。');
    if(obd==='no')notes.push('OBD検査の対象外なら、見積もりにOBD検査料が入っていないか確認しましょう。');
    notes.push('タイヤとバッテリーは、車検の前に状態を聞いて下調べしておくと、当日あわてずにすみます。');
    h+='<ul class="small">'+notes.map(function(x){return '<li>'+x+'</li>'}).join('')+'</ul>';
    h+='<p class="small">※ あくまで目安です。法定費用は'+S.asof+'時点の金額（自賠責は離島・沖縄県を除く）。お店の費用はお店や車種によって違います。</p>';
    $('out').innerHTML=h;
  }
  (function(){var d=new Date(),y=d.getFullYear(),s=$('y2'),h='';
    function wa(n){return n>=2020?'R'+(n-2018)+'（'+n+'年）':n===2019?'H31・R1（2019年）':'H'+(n-1988)+'（'+n+'年）'}
    for(var i=0;i<3;i++)h+='<option value="'+(y+i)+'">'+wa(y+i)+'</option>';
    s.innerHTML=h;s.value=String(y);$('m2').value=String(d.getMonth()+1)})();
  $('f').addEventListener('input',run);$('f').addEventListener('change',run);run();
})();
</script>
"""
    import datetime
    y_now = datetime.date.today().year
    rep0 = {"__Y1__": '<option value="">年</option>' + "".join(f'<option value="{y}">{wareki(y)}</option>' for y in range(y_now, 1989, -1)) + '<option value="1900">S64・H1（1989年）以前</option>',
            "__Y2__": "".join(f'<option value="{y}"{" selected" if y == y_now else ""}>{wareki(y)}</option>' for y in range(y_now, y_now + 3)),
            "__M__": '<option value="">月</option>' + "".join(f'<option value="{m}">{m}月</option>' for m in range(1, 13)),
            "__M2__": "".join(f'<option value="{m}"{" selected" if m == datetime.date.today().month else ""}>{m}月</option>' for m in range(1, 13))}
    for k, v in rep0.items():
        body = body.replace(k, v)
    rep = {"__ROWS__": rows, "__SRC__": src, "__WOPTS__": wopts, "__ASOF__": S["asof"],
           "__J_F__": yen(j["futsu"]), "__J_K__": yen(j["kei"]),
           "__J25_F__": yen(S["jibai25"]["futsu"]), "__J25_K__": yen(S["jibai25"]["kei"]),
           "__S__": json.dumps(S, ensure_ascii=False)}
    for k, v in rep.items():
        body = body.replace(k, v)
    body = body.replace("__AD_CARNEXT__", AD_CARNEXT)
    write("shaken/index.html", page("車検費用の目安計算（13年・18年経過の重量税も）", "自家用の普通車・軽自動車の車検費用の目安を計算。13年・18年経過で上がる重量税も、初度登録の年月から自動で判定。重量税・自賠責保険・印紙代は2026年11月時点の公式の金額、お店の費用は現役の整備士に聞いた目安。見積もりを見るときのポイントも。", body))


# ---------------- 消耗品の交換時期 ----------------
LV3 = [("red", "🔴 今すぐ"), ("yellow", "🟡 近いうちに"), ("white", "⚪ 様子見でいい")]



SHEET_IDS = {"oil","element","brakefluid","cvt","battery","tire","wiper","acfilter","aircleaner","plug","pad","vbelt"}
SHEET_BOX = """<section class="box" id="sheet">
  <h2>交換の記録を残すシート（BOOTH・300円）</h2>
  <p>いつ・どこで・何km時点で替えたかを記録すると、次の交換時期の目安が🔴🟡⚪で出る、ExcelとGoogleスプレッドシート用のシートです。このサイトの基準（整備士のチェックを受けた年数・距離）をもとにしています。ほかのお店や自分で交換したものも、すべて記録しておくのがコツです。</p>
  <ul>
    <li>価格：300円（2026年12月31日まで。そのあとは500円の予定）</li>
    <li>AIの小太郎が作りました。表示は目安で、取扱説明書の指定が優先です。ディーゼル車は目安の対象外です。</li>
  </ul>
  <p><a href="https://kotaro-tools.booth.pm/items/9169139" rel="noopener">→ BOOTHで見る：【車のメンテ記録】オイル・バッテリー・タイヤの交換時期が目安でわかる</a></p>
</section>
"""
# オイル交換ツールのページ用：ツールの結果をシートの「設定」に入れる使い方を1文足す
OIL_SHEET_BOX = SHEET_BOX.replace("  <ul>", "  <p>エンジンオイルは、このページで出た目安の距離（km）を、シートの「設定」の「オイル交換の目安（km）」に入れて使います（車ごとに目安が違うので、一律の距離は使っていません）。</p>\n  <ul>", 1)


def build_koukan():
    items = []
    for it in ITEMS:
        rows = "".join(
            f'<tr class="lv-{k}"><th>{lab}</th><td>{"<br>".join(e(x) for x in it[k])}</td></tr>'
            for k, lab in LV3 if it[k])
        ask = "".join(f"<li>{e(a)}</li>" for a in it["ask"])
        ask = f'<h3>お店に聞くといい質問</h3><ul class="ask">{ask}</ul>' if ask else ""
        note = it.get("note", "")
        note = note if it.get("html_note") else e(note)
        note = f'<p class="tip">💡 {note}</p>' if note else ""
        alias = f'<p class="look">別の書き方：{e(it["alias"])}</p>' if it["alias"] else ""
        items.append(f"""
<article class="part" id="{it['id']}" data-cat="{it['cat']}" data-kw="{e(it['name'] + ' ' + it['alias'])}">
  <div class="light-head"><h2><a href="{it['id']}/">{e(it['name'])}</a></h2><span class="badge b-info">{CATS[it['cat']]}</span></div>
  {alias}
  <p class="honne"><span>整備士の本音</span>{e(it['honne'])}</p>
  <table class="lv">{rows}</table>
  <h3>放っておくと</h3>
  <p>{e(it['risk'])}</p>
  {ask}
  {note}
  <p class="gen"><b>一般的な目安（AIの小太郎が調べたもの）：</b>{e(it['general'])}</p>
</article>""")

    toc = "".join(f'<li><a href="#{it["id"]}">{e(it["name"])}</a></li>' for it in ITEMS)
    chips = '<button data-c="" class="on">すべて</button>' + "".join(
        f'<button data-c="{k}">{v}</button>' for k, v in CATS.items())
    always = "".join(f"<tr><td>{e(a)}</td><td><b>{e(b)}</b></td><td>{e(c)}</td></tr>" for a, b, c in CHECK_ALWAYS)
    adds = "".join(f"<h3>{e(n)}</h3><ul><li><b>いらない人：</b>{e(no)}</li><li><b>入れてもいい人：</b>{e(yes)}</li></ul>"
                   for n, no, yes in ADDITIVES)
    body = f"""
<h1>車の消耗品の交換時期一覧｜整備士の本音で3段階に</h1>
<p class="lead">点検や車検の見積もりに、交換の項目がずらっと並んでいる。でも、どれを今やるべきなの？――
そんなときのために、<b>現役の一級自動車整備士が、見積もりを見て優先度を決めるときの基準</b>をまとめました。</p>

<div class="legend">
  <div class="lg c-red"><b>🔴 今すぐ</b>：先延ばしにしないで、今回やったほうがいい</div>
  <div class="lg c-yellow"><b>🟡 近いうちに</b>：今回でなくてもいいが、次の点検までには</div>
  <div class="lg c-white"><b>⚪ 様子見でいい</b>：まだ急がなくていいことが多い</div>
</div>

<section class="box">
  <h2>見積もりを見るときの3つのコツ</h2>
  <ol>
    <li><b>数字で聞く。</b>「そろそろ交換です」ではなく、「残り何mm？」「何年前に替えた？」と聞くと、自分で判断できます。</li>
    <li><b>「ついでに替えたほうがいい部品はありますか？」はどの項目でも使える質問。</b>部品を外すついでに作業すると、工賃が安くすむことがあります。</li>
    <li><b>交換の記録は自分でも持っておく。</b>お店の人も人間なので、まちがいはあります（例：最近1本だけ替えたタイヤまで4本分の見積もりが出る）。いつ・何を替えたか、メモしておくと安心です。</li>
  </ol>
  <p><b>やる・やらないは、説明を聞いて自分で決める。</b>お店は、替えないと困る項目について「このままだとこうなります」と説明し、やるかどうかをお客さんに決めてもらうのが普通です。
  説明がなかったら「替えないとどうなりますか？」と聞いてみてください。そのうえで納得して決めましょう。
  ただし<b>🔴の項目、とくにブレーキとタイヤは先延ばしにしない</b>でください。</p>
  <p class="small">見積もりの項目を「今すぐ・近いうちに・様子見」に分ける考え方は、小太郎の note<a href="https://note.com/ai_kotaro/n/nba405c39e2b0" rel="noopener">「車検の見積もり、全部いま必要？」</a>にも書いています。</p>
</section>

<div class="search">
  <input id="q" type="search" placeholder="例：タイヤ、ATF、ファンベルト" aria-label="項目を検索">
  <div class="chips" role="group" aria-label="種類でしぼりこむ">{chips}</div>
  <p id="count" class="count"></p>
</div>

<details class="toc"><summary>一覧（{len(ITEMS)}項目）</summary><ul>{toc}</ul></details>

<div id="list">{''.join(items)}</div>
<p id="none" class="none" hidden>見つかりませんでした。別の言葉で探してみてください。</p>

<section class="box" id="always">
  <h2>見積もりに無くても、自分から確認したい項目</h2>
  <p>見積もりに入っていないからといって、問題がないとは限りません。次の条件に当てはまったら、自分から聞いてみてください。</p>
  <table class="tbl">
    <thead><tr><th>こんなとき</th><th>確認する項目</th><th>理由</th></tr></thead>
    <tbody>{always}</tbody>
  </table>
</section>

<section class="box" id="additive">
  <h2>添加剤は入れたほうがいい？</h2>
  <p>エンジン内部洗浄・燃料添加剤・オイル添加剤は、<b>入れるも入れないも自由</b>です。整備士の考えはこうです。</p>
  {adds}
  <p class="tip">⚠️ 自分で選んだ添加剤を入れるときは注意。オイルと添加剤の組み合わせによっては、エンジンを傷めたり、オイルが固まったりすることがあります。
  整備士によると、ディーラーで売っているものは、そのディーラーで使うオイルに入れても問題ないことが確認されているそうです。</p>
</section>

{SHEET_BOX}

<section class="box">
  <h2>このページについて</h2>
  <p>「🔴🟡⚪」の基準と「整備士の本音」は、現役の一級自動車整備士が、見積もりの優先度を判断するために自分で書いた表がもとになっています。
  「一般的な目安」は、メーカーや業界団体の公開情報をもとにAIの小太郎が調べて書いたもので、一級自動車整備士がチェックしています（2026年11月）。</p>
  <p>参考：<a href="https://www.jatma.or.jp/tekisei/pdf/long-term.pdf" rel="noopener">日本自動車タイヤ協会「長期経過タイヤの点検・交換について」</a></p>
  <p class="small">交換時期は車種・年式・使い方で変わります。自分の車の指定は、取扱説明書とメンテナンスノートで確認してください。走っていて異常を感じたら、時期に関係なく点検を受けてください。</p>
</section>

<script>
(function(){{
  var q=document.getElementById('q'),list=document.querySelectorAll('.part'),
      chips=document.querySelectorAll('.chips button'),none=document.getElementById('none'),
      count=document.getElementById('count'),cat='';
  function norm(s){{return s.toLowerCase().replace(/\s+/g,' ')}}
  function run(){{
    var words=norm(q.value).split(' ').filter(Boolean),n=0;
    list.forEach(function(el){{
      var kw=norm(el.dataset.kw+' '+el.textContent);
      var ok=(!cat||el.dataset.cat===cat)&&words.every(function(w){{return kw.indexOf(w)>=0}});
      el.hidden=!ok; if(ok)n++;
    }});
    none.hidden=n>0; count.textContent=(words.length||cat)?n+'件':'';
  }}
  q.addEventListener('input',run);
  chips.forEach(function(b){{b.addEventListener('click',function(){{
    chips.forEach(function(x){{x.classList.remove('on')}});b.classList.add('on');cat=b.dataset.c;run();
  }})}});
}})();
</script>
"""
    write("koukan/index.html", page("車の消耗品の交換時期一覧（16項目）、整備士の本音",
          "車の消耗品の交換時期を一覧で。ブレーキパッド・タイヤ・バッテリー・CVTフルードなど、見積もりに出てくる16項目の交換時期を、現役の一級整備士の基準で「今すぐ／近いうちに／様子見」の3段階に。お店に聞くといい質問も。", body))



# ---------------- 個別ページ（検索の入口。中身は一覧と同じ、チェック済みのデータだけを使う） ----------------
# 警告灯 → 関係する消耗品の交換時期（ページどうしの案内だけ。本文は変えない）
KEIKOKU_KOUKAN = {
    "brake": ["brakefluid", "pad"],
    "oil": ["oil"],
    "charge": ["battery", "vbelt"],
    "water-hot": ["llc"],
    "tpms": ["tire"],
    "washer": ["wiper"],
}
DIESEL_IDS = {"glow", "dpf"}
DIESEL_TXT = "現役の整備士がチェックしています。ただし、ディーゼル車の内容は、その整備士の専門外です"


def build_keikoku_pages():
    for L in LIGHTS:
        lv, lvdesc = LEVEL[L["level"]]
        acts = "".join(f"<li>{e(a)}</li>" for a in L["action"])
        tip = f'<p class="tip">💡 {e(L["tip"])}</p>' if L["tip"] else ""
        diesel = L["id"] in DIESEL_IDS
        dnote = ('<p class="small">※ ディーゼル車は、このサイトをチェックしている整備士の専門外です。'
                 'とくに参考程度にして、取扱説明書を優先してください。</p>') if diesel else ""
        rel = [x for x in LIGHTS if x["color"] == L["color"] and x["id"] != L["id"]]
        rel = "".join(f'<li><a href="../{x["id"]}/"><span class="dot dot-{x["color"]}"></span>{e(x["name"])}</a></li>' for x in rel)
        parts = [x for k in KEIKOKU_KOUKAN.get(L["id"], []) for x in ITEMS if x["id"] == k]
        parts = "".join(f'<li><a href="../../koukan/{x["id"]}/">{e(x["name"])}の交換時期</a></li>' for x in parts)
        parts = f"""
<section class="box">
  <h2>関係する消耗品の交換時期（整備士の基準）</h2>
  <ul class="rel">{parts}</ul>
</section>
""" if parts else ""
        more = ""
        if L.get("more"):
            secs = "".join(f"<h2>{e(h)}</h2>" + "".join(f"<p>{p}</p>" for p in ps) for h, ps in L["more"])
            srcs = "".join(f'<li><a href="{u}" rel="noopener">{e(n)}</a></li>' for n, u in L.get("src", []))
            more = f"""
<section class="box">
  {secs}
  <p class="small">この欄は整備士のチェックを受けていません。AIの小太郎が下の公的資料と法令で調べてまとめたものです（2026年11月時点）。</p>
  <ul class="small">{srcs}</ul>
</section>
"""
        body = f"""
<p class="crumb"><a href="../../">トップ</a> ＞ <a href="../">警告灯の意味一覧</a></p>
<article class="light c-{L['color']}">
  <div class="light-head">
    <span class="dot" aria-hidden="true"></span>
    <h1>{e(L['name'])}が点いたら</h1>
    <span class="badge b-{L['level']}">{lv}</span>
  </div>
  <p class="look">見た目：{e(L['look'])}（色：{COLOR[L['color']]}）</p>
  <p class="meaning">{e(L['meaning'])}</p>
  <h2>どうすればいい？</h2>
  <ul>{acts}</ul>
  {tip}
  {dnote}
</article>
{more}
<section class="box">
  <h2>色でわかる緊急度</h2>
  <p>このランプは<b>{COLOR[L['color']]}</b>（{lv}：{lvdesc}）です。</p>
  <ul>
    <li><b>赤</b>：すぐに安全な場所に停めて確認・相談</li>
    <li><b>黄・オレンジ</b>：すぐ止まらなくてよいことが多いが、早めに点検</li>
    <li><b>緑・青</b>：装置が作動中などのお知らせ（異常ではない）</li>
  </ul>
  <p>「走れる」警告灯でも、運転するのが不安なときは無理に走らず、レッカーを呼ぶのも手です（<a href="../#tow">レッカーという選択肢</a>）。</p>
</section>
{parts}
<section class="box">
  <h2>同じ色のほかの警告灯</h2>
  <ul class="rel">{rel}</ul>
  <p><a href="../">→ 警告灯の意味一覧（{len(LIGHTS)}種類・検索つき）</a></p>
</section>
<p class="small">マークの形や色は車種によって異なることがあります。正確な意味は取扱説明書で確認してください。</p>
"""
        # 検索結果で色と緊急度が先に見えるように。説明は文の途中で切らない
        c1 = COLOR[L['color']][0]
        desc = f"【{c1}・{lv}】{L['name']}（{L['look']}）が点いたときの意味と、まずやること。"
        if len(desc + L['meaning']) > 120:
            desc = (desc + L['meaning'])[:120]
        else:
            desc += L['meaning']
            if L['tip'] and len(desc + L['tip']) <= 120:
                desc += L['tip']
        write(f"keikoku/{L['id']}/index.html",
              page(f"{L['name']}が点いたら｜{c1}・{lv}｜意味と対処", desc, body, depth=2,
                   check_txt=DIESEL_TXT if diesel else None,
                   crumbs=[("警告灯の意味一覧", "keikoku/"), (f"{L['name']}が点いたら", f"keikoku/{L['id']}/")]))


def build_koukan_pages():
    for it in ITEMS:
        rows = "".join(
            f'<tr class="lv-{k}"><th>{lab}</th><td>{"<br>".join(e(x) for x in it[k])}</td></tr>'
            for k, lab in LV3 if it[k])
        ask = "".join(f"<li>{e(a)}</li>" for a in it["ask"])
        ask = f'<h2>お店に聞くといい質問</h2><ul class="ask">{ask}</ul>' if ask else ""
        note = it.get("note", "")
        note = note.replace('href="../', 'href="../../') if it.get("html_note") else e(note)
        note = f'<p class="tip">💡 {note}</p>' if note else ""
        alias = f'<p class="look">別の書き方：{e(it["alias"])}</p>' if it["alias"] else ""
        rel = [x for x in ITEMS if x["cat"] == it["cat"] and x["id"] != it["id"]]
        rel = "".join(f'<li><a href="../{x["id"]}/">{e(x["name"])}の交換時期</a></li>' for x in rel)
        rel = f'<h2>同じ種類のほかの項目（{CATS[it["cat"]]}）</h2><ul class="rel">{rel}</ul>' if rel else ""
        lights = [L for L in LIGHTS if it["id"] in KEIKOKU_KOUKAN.get(L["id"], [])]
        lights = "".join(f'<li><a href="../../keikoku/{L["id"]}/"><span class="dot dot-{L["color"]}"></span>{e(L["name"])}が点いたら</a></li>' for L in lights)
        rel += f'<h2>関係する警告灯</h2><ul class="rel">{lights}</ul>' if lights else ""
        has_ad = it["id"] == "tire"
        sheet = SHEET_BOX if it["id"] in SHEET_IDS else ""
        pr = '<p class="pr">このページには広告が含まれています（ページ下の「広告」の枠）</p>' if has_ad else ""
        ad = AD_TIRE if has_ad else ""
        body = f"""
<p class="crumb"><a href="../../">トップ</a> ＞ <a href="../">消耗品の交換時期、整備士の本音</a></p>
{pr}
<article class="part">
  <div class="light-head"><h1>{e(it['name'])}の交換時期</h1><span class="badge b-info">{CATS[it['cat']]}</span></div>
  {alias}
  <p class="honne"><span>整備士の本音</span>{e(it['honne'])}</p>
  <h2>交換の目安（整備士の基準）</h2>
  <table class="lv">{rows}</table>
  <h2>放っておくと</h2>
  <p>{e(it['risk'])}</p>
  {ask}
  {note}
  <p class="gen"><b>一般的な目安（AIの小太郎が調べたもの）：</b>{e(it['general'])}</p>{chr(10) + '  ' + it['extra_html'] if it.get('extra_html') else ''}
</article>

<section class="box">
  <h2>見積もりを見るときのコツ</h2>
  <ul>
    <li><b>数字で聞く。</b>「そろそろ交換です」ではなく、「残り何mm？」「何年前に替えた？」と聞くと、自分で判断できます。</li>
    <li><b>やる・やらないは、説明を聞いて自分で決める。</b>説明がなかったら「替えないとどうなりますか？」と聞いてみてください。ただし🔴の項目、とくにブレーキとタイヤは先延ばしにしないでください。</li>
  </ul>
  {rel}
  <p><a href="../">→ 消耗品{len(ITEMS)}項目の一覧（今すぐ・近いうちに・様子見）</a>　<a href="../../shaken/">→ 車検費用の目安計算</a></p>
</section>
{sheet}
{ad}
<p class="small">交換時期は車種・年式・使い方で変わります。自分の車の指定は、取扱説明書とメンテナンスノートで確認してください。</p>
"""
        desc = f"{it['name']}の交換時期を、現役の一級整備士の基準で「今すぐ・近いうちに・様子見」に。整備士の本音：{it['honne']}"
        write(f"koukan/{it['id']}/index.html",
              page(f"{it['name']}の交換時期｜整備士の基準", desc[:120], body, depth=2,
                   crumbs=[("消耗品の交換時期、整備士の本音", "koukan/"), (f"{it['name']}の交換時期", f"koukan/{it['id']}/")]))


# ---------------- 運転支援の3機能（「これ何？」と聞かれるもの） ----------------
# ネタ元：オーナーさん（現役整備士）「新車の点検で、自動ブレーキ系・オートクルーズ・オートマチックハイビームの使い方をよく聞かれる」（11/15）
# 機能の説明・注意は、国土交通省・警察庁・JAFの公開情報で小太郎が調べたもの。
SHIEN_SRC = [
    ("国土交通省「衝突被害軽減ブレーキは万能ではありません！」", "https://www.mlit.go.jp/jidosha/carinf/rcl/carsafety_sub/carsafety031.html"),
    ("国土交通省「運転支援システムの特性や限界を知ってみよう！」（2025年4月18日・不要作動）", "https://www.mlit.go.jp/report/press/jidosha08_hh_005420.html"),
    ("国土交通省「『運転支援システム』を過信・誤解しないでください！」", "https://www.mlit.go.jp/jidosha/carinf/rcl/carsafety_sub/carsafety034.html"),
    ("JAF「ACC（車間距離制御装置）」", "https://jaf.or.jp/common/safety-drive/new-technology/acc"),
    ("JAF「ACC（車間距離制御装置）のこんな使い方は危ないよ」", "https://jaf.or.jp/common/safety-drive/new-technology/acc/using-method/do-not-use"),
    ("警察庁「ハイビームの上手な活用で夜間の歩行者事故防止」", "https://www.npa.go.jp/bureau/traffic/anzen/highbeam.html"),
    ("JAFユーザーテスト「オートハイビームを使えば、手動での切り替えは不要？」（2019年1月のテスト）", "https://jaf.or.jp/common/safety-drive/car-learning/user-test/blind_spot/auto-high-beam"),
]


def build_shien():
    src = "".join(f'<li><a href="{u}" rel="noopener">{e(n)}</a></li>' for n, u in SHIEN_SRC)
    body = f"""
<h1>自動ブレーキ・オートクルーズ・オートハイビーム、何をしてくれる？</h1>
<p class="lead">最近の車は、運転を助けてくれる機能とボタンがたくさんあります。
現役の整備士によると、<b>新車を買ってすぐの点検（1か月点検など）で「これ何？」とよく聞かれるのが、自動ブレーキ、オートクルーズ、オートマチックハイビーム</b>だそうです。
この3つが何をしてくれて、何はしてくれないのかを、国の資料をもとにまとめました。</p>

<section class="box">
  <h2>まず大事なこと：どれも「自動運転」ではありません</h2>
  <p>国土交通省は、運転支援システムは「自動運転」ではなく、あくまでアシスト機能だと説明しています。
  故障していなくても、天気や道路の状況によっては働かないことがあり、使っている途中で急に機能が止まることもあります。<b>安全運転の責任は運転する人にあります</b>。</p>
  <p>どの機能も、メーカーや車種によって名前・ボタン・働く条件がちがいます。自分の車のことは、取扱説明書で確認してください。</p>
</section>

<section class="box" id="brake">
  <h2>① 自動ブレーキ（衝突被害軽減ブレーキ）</h2>
  <p><b>何をしてくれる？</b>　カメラやレーダーで前の車や人を見て、ぶつかりそうになると、まず警報で知らせます。運転する人がブレーキを踏まないと、車が自動でブレーキをかけます。
  国の呼び方は「衝突被害軽減ブレーキ」で、名前のとおり<b>ぶつかったときの被害を軽くする</b>ための装置です。</p>
  <h3>してくれないこと</h3>
  <ul>
    <li>どんなときでも止まってくれるわけではありません。国土交通省は「完全に事故を防ぐことができません」としています。</li>
    <li>雨・雪・霧などの悪天候や、カメラの前のフロントガラスの汚れなどで、前のものを正しく見つけられなかったり、ぶつかるのを避けきれなかったりすることがあります。</li>
  </ul>
  <h3>知っておくと慌てないこと</h3>
  <ul>
    <li><b>ぶつかりそうにない場面で作動することがあります</b>（国は「不要作動」と呼んでいます。めったにないことです）。そなえとして、シートベルトをしっかり締め、止まったあとは落ち着いてブレーキを踏みます。</li>
    <li><b>カメラの前のフロントガラスはきれいに。</b>汚れていると、正しく見えなくなります。</li>
    <li>警報は「ブレーキを踏んで」という合図です。鳴ったら自分でブレーキを踏みます。</li>
    <li>スイッチやメーターの表示の意味は、車によってちがいます。取扱説明書で確かめておきましょう。</li>
  </ul>
</section>

<section class="box" id="cruise">
  <h2>② オートクルーズ（クルーズコントロール）</h2>
  <p><b>何をしてくれる？</b>　アクセルを踏まなくても、決めた速さで走ってくれる機能です。高速道路で足が疲れにくくなります。</p>
  <p><b>ここが大事：「前の車についていく」タイプかどうか。</b></p>
  <ul>
    <li><b>速さを保つだけのタイプ</b>：前の車に近づいたら、自分でブレーキを踏みます。ただし、<b>ブレーキを踏むとクルーズが解除される</b>ので、整備士いわく「こまめな速度の調整はなかなか難しい」。交通量の少ない道向きです。</li>
    <li><b>前の車についていくタイプ</b>（「アダプティブクルーズコントロール（ACC）」「車間距離制御装置」などの名前）：前の車との間をあけて、速さを自動で調整します。止まるところまでついていく車もあります。止まったあとそのまま止まっているか、数秒で解除されるかも、車によってちがいます。</li>
  </ul>
  <p>どちらのタイプかは、取扱説明書かお店で確認しておきましょう。</p>
  <h3>使わないほうがいい場面</h3>
  <ul>
    <li><b>一般道</b>：メーカーは高速道路・自動車専用道路での使用をすすめていて、国土交通省も一般道では使わないよう呼びかけています。センサーは前を見ているので、割り込みへの反応が遅れたり、車によってはバイクや自転車を見つけにくかったりします。</li>
    <li><b>料金所の近く</b>：手前で解除します。</li>
    <li><b>合流と出口</b>：合流は使わずに自分で加速し、出口は降りる前に解除します。</li>
    <li><b>カーブが続く道</b>：前の車を見失うと、決めた速さまで加速することがあります。</li>
    <li><b>大雨・雪</b>：センサーが前をうまく見られなくなることがあります。</li>
  </ul>
  <p>使っている間も、ナビの画面を見続けたり、スマホを操作したりするのは危険で、法律違反にもなります。</p>
</section>

<section class="box" id="highbeam">
  <h2>③ オートマチックハイビーム</h2>
  <p><b>何をしてくれる？</b>　夜、前の車や向こうから来る車に合わせて、ハイビーム（遠くまで照らす）とロービームを自動で切り替えてくれます。</p>
  <p><b>そもそも、夜はハイビームが基本です。</b>警察庁の案内（交通の方法に関する教則）では、交通量の多い市街地などを除き、ライトは上向き（ハイビーム）にして、歩行者などを早く見つけるようにとされています。
  向こうから車が来るときや、前の車のすぐ後ろを走るときは、下向き（ロービーム）に切り替えます。</p>
  <h3>してくれないこと</h3>
  <ul>
    <li>JAFのテスト（2019年）では、<b>歩行者や自転車に対しては、ハイビームのまま切り替わりませんでした</b>。歩行者や自転車を見つけたら、自分でロービームに切り替えます。</li>
    <li>街灯やガードレールの反射板、標識などがあると、切り替わらなかったり、不安定になったりすることがあります。</li>
  </ul>
</section>

<section class="box" id="repair">
  <h2>ぶつけたときの修理代は、高くなることがあります</h2>
  <p>カメラやセンサーが増えたぶん、ちょっとぶつけただけでも修理代がかさむことがあります。整備士に聞いた例です。</p>
  <ul>
    <li><b>バンパー</b>：車によっては、直したあとにセンサーの調整が必要で、その調整代がさらにかかります。</li>
    <li><b>ドアミラー</b>：カメラが付いているミラーだと、ミラーをぶつけて壊しただけで10万円ほどかかる場合もあります。</li>
    <li><b>ハンドル</b>：オートクルーズなどのために、ハンドルの中にセンサーが付いている車があり、ハンドルだけで10万円ほどすることもあります。</li>
  </ul>
  <p>金額は車種や部品で大きく変わります。ぶつけたときは、見積もりで「センサーの調整（エーミング）は入っていますか？」と聞いておくと安心です。</p>
  <p class="small">修理代が高くなる理由は、小太郎の note<a href="https://note.com/ai_kotaro/n/n6dc2204c573a" rel="noopener">「ミラーをぶつけただけで10万円？ カメラやセンサー付きの車の修理代が高くなる理由」</a>にもまとめています。</p>
</section>

<section class="box">
  <h2>わからないことは、点検のときに聞いていい</h2>
  <p>整備士によると、新車を買ってすぐの点検では、こうした機能やナビ、ボタンの使い方をよく聞かれるそうです。
  1か月点検ではナビの使い方、6か月点検ではオイル交換の時期を聞かれることが多いとのこと（オイル交換の時期は<a href="../oil/">オイル交換時期の計算ツール</a>でも目安を出せます）。
  点検は、車を見てもらうだけでなく、<b>使い方を聞くいい機会</b>です。「このボタンは何ですか？」と気軽に聞いてみてください。</p>
  <p>メーターに見なれないランプや表示が出たら、取扱説明書で意味を確かめ、消えないときはお店で見てもらいましょう（よく出る警告灯は<a href="../keikoku/">警告灯の意味一覧</a>にまとめています）。
  また、自動ブレーキなどの故障の記録がコンピューターに残っていると、対象の車は車検（OBD検査）に通りません（<a href="../keikoku/">警告灯ページ</a>の「よくある質問」）。</p>
</section>

<section class="box">
  <h2>このページについて</h2>
  <p>「新車を買ってすぐの点検でよく聞かれる」話や修理代の例は、現役の整備士から聞いたものです。機能の説明と注意点は、次の公開情報をもとにAIの小太郎がまとめ、一級自動車整備士・自動車検査員の資格をもつ現役の整備士がチェックしています（2026年11月）。</p>
  <ul>{src}</ul>
  <p class="small">機能の名前・ボタン・働く条件は、メーカーや車種によってちがいます。最終的には取扱説明書で確認してください。</p>
</section>
"""
    write("shien/index.html", page("自動ブレーキ・オートクルーズ・オートハイビームとは",
          "自動ブレーキ（衝突被害軽減ブレーキ）・オートクルーズ・オートマチックハイビームは何をしてくれて、何はしてくれない？ 新車の点検で整備士がよく聞かれる3つの機能を、国土交通省・警察庁・JAFの資料をもとにやさしく解説。",
          body))

# ---------------- このサイトについて ----------------
def build_about():
    body = f"""
<h1>このサイトについて</h1>
<section class="box">
  <h2>だれが作っているか</h2>
  <p>このサイトの文章・ツールは、AIの「小太郎」が作っています。
  内容は{CHECK_TXT}（チェックがまだのページには、そのことを書いています）。まちがいがあれば直しています。</p>
  <p>小太郎は「自分でお金を稼ぐ」挑戦をしているAIで、その記録は
  <a href="https://note.com/ai_kotaro" rel="noopener">note</a> に書いています。</p>
</section>
<section class="box">
  <h2>広告について</h2>
  <p>このサイトは、A8.net のアフィリエイト広告を使っています。広告を置いたページには、ページの上に「広告が含まれています」と書き、広告の部分には「広告」と表示します。</p>
  <p>広告のリンクから申し込みがあると、このサイトに紹介料が入ります。紹介料があるかどうかで、ツールの計算結果や記事の内容を変えることはありません。</p>
</section>
<section class="box">
  <h2>免責事項</h2>
  <ul>
    <li>掲載している情報は一般的な目安です。車の状態は車種・年式・使い方によって違います。</li>
    <li>点検・整備の最終的な判断は、取扱説明書と整備工場・ディーラーの指示に従ってください。</li>
    <li>このサイトの情報を使ったことで起きたトラブルについて、運営者は責任を負いかねます。</li>
    <li>走行中に異常を感じたときは、無理に走らず安全な場所に停めてください。</li>
  </ul>
</section>
<section class="box">
  <h2>まちがいを見つけたら</h2>
  <p>小太郎の <a href="https://note.com/ai_kotaro" rel="noopener">note</a> のコメント欄から教えてください。確認して直します。</p>
</section>
"""
    write("about/index.html", page("このサイトについて", "くるま整備ノートの運営者・免責事項。AIが作り、一級自動車整備士が内容をチェックしています。", body))


# ---------------- 見つからないページ（GitHub Pages はどの階層でも /404.html を返す） ----------------
def build_404():
    body = """
<h1>ページが見つかりませんでした</h1>
<p>URLがまちがっているか、ページの場所が変わった可能性があります。下の一覧から探してください。</p>
<div class="cards">
  <a class="card" href="keikoku/"><span class="card-ic">⚠️</span><h2>警告灯の意味一覧</h2><p>メーターに出たランプの意味と、まずやること。</p></a>
  <a class="card" href="koukan/"><span class="card-ic">🧰</span><h2>消耗品の交換時期一覧</h2><p>ブレーキパッド・タイヤ・バッテリーなど16項目。</p></a>
  <a class="card" href="oil/"><span class="card-ic">🛢️</span><h2>オイル交換時期の計算</h2><p>前回の交換日から、次の目安を計算。</p></a>
  <a class="card" href="shaken/"><span class="card-ic">📋</span><h2>車検費用の目安計算</h2><p>重量税・自賠責・印紙代と、お店の費用の相場。</p></a>
</div>
<p><a href="./">トップページへ</a></p>
"""
    text = page("ページが見つかりませんでした", "お探しのページは見つかりませんでした。", body, depth=0)
    # どの階層で表示されても相対リンクが切れないよう / を基準にし、検索には載せない
    text = "\n".join(l for l in text.split("\n") if URL_MARK not in l and "application/ld+json" not in l)
    text = text.replace("<head>\n", '<head>\n<base href="/">\n<meta name="robots" content="noindex">\n', 1)
    write("404.html", text)


# ---------------- 整備士チェック表 ----------------
def build_check():
    lines = ["# 整備士チェック表（警告灯）", "",
             "オーナーさんへ：まちがい・言いすぎ・足りないところがあれば、番号と一言だけ教えてください（例：「3 ベルトの話はいらない」）。OKなら「全部OK」で大丈夫です。", ""]
    for i, L in enumerate(LIGHTS, 1):
        lines.append(f"## {i}. {L['name']}（{COLOR[L['color']]}／{LEVEL[L['level']][0]}）")
        lines.append(f"- 意味：{L['meaning']}")
        for a in L["action"]:
            lines.append(f"- 対処：{a}")
        if L["tip"]:
            lines.append(f"- ひとこと：{L['tip']}")
        lines.append("")
    lines += ["## オイル交換ツールの目安（調整ラボでオーナーさんが決めた係数）",
              f"- 係数：{OIL_P}",
              "- 公開ツールの例（乗り方ふつう）："]
    for name, d, o, t, typ in OIL_EXAMPLES:
        rec, late = oil_calc(d, o, t, typ)
        lines.append(f"  - {name}（{OIL_TYPE[typ]}・{d}L・オイル{o}L・{t[0]}/{t[1]}R{t[2]}）おすすめ{rec:,}km・遅くとも{late:,}km")
    lines += ["- おすすめは最大10,000km、遅くともは最大12,000kmで頭打ち（小太郎が安全側に追加。バディ指摘：15,000kmは本文の「遅すぎる」と矛盾）", ""]
    out = ROOT.parent.parent / "02_お願い" / "整備士チェック_警告灯とオイル.md"
    out.write_text("\n".join(lines), encoding="utf-8")

    # 交換時期ページ（整備士の表を小太郎が言い換えた部分の確認用）
    lines = ["# 整備士チェック表（消耗品の交換時期）", "",
             "オーナーさんへ：ルール表をもとに小太郎が書き直した文章です。言い換えでニュアンスが変わったところがあれば「番号＋一言」で。OKなら「全部OK」で大丈夫です。",
             "「一般的な目安」は小太郎が公開情報で調べたもの（まちがいがあれば教えてください）。", ""]
    for i, it in enumerate(ITEMS, 1):
        lines.append(f"## {i}. {it['name']}")
        lines.append(f"- 本音：{it['honne']}")
        for k, lab in LV3:
            for x in it[k]:
                lines.append(f"- {lab}：{x}")
        lines.append(f"- 放っておくと：{it['risk']}")
        if it.get("note"):
            lines.append(f"- ひとこと：{it['note']}")
        lines.append(f"- 一般的な目安（小太郎が調べた）：{it['general']}")
        lines.append("")
    out = ROOT.parent.parent / "02_お願い" / "整備士チェック_交換時期.md"
    out.write_text("\n".join(lines), encoding="utf-8")


# ---------------- 検索エンジン用（Search Console 確認ファイル・サイトマップ・robots） ----------------
GSC_FILE = "google64c86059b3bde811.html"  # 消さないこと（消すと Search Console の確認が外れる）


def build_search():
    write("CNAME", DOMAIN + "\n")  # GitHub Pages の独自ドメイン
    write(GSC_FILE, f"google-site-verification: {GSC_FILE}")
    rels = sorted(str(p.relative_to(OUT)) for p in OUT.rglob("index.html"))
    items = "\n".join(f"  <url><loc>{BASE + r.removesuffix('index.html')}</loc><lastmod>{PAGE_DATES.get(r, TODAY)}</lastmod></url>"
                      for r in rels)
    write("sitemap.xml", f'<?xml version="1.0" encoding="UTF-8"?>\n'
          f'<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{items}\n</urlset>\n')
    write("robots.txt", f"User-agent: *\nAllow: /\nSitemap: {BASE}sitemap.xml\n")


def main():
    css = (ROOT / "style.css").read_text(encoding="utf-8")
    write("assets/style.css", css)
    write(".nojekyll", "")
    (OUT / "assets" / "ogp.png").write_bytes((ROOT / "ogp.png").read_bytes())  # 作り直すときは ogp.py
    build_index(); build_keikoku(); build_keikoku_pages(); build_oil(); build_koukan(); build_koukan_pages(); build_shien(); build_shaken(); build_about(); build_404(); build_check()
    build_search()
    print("built:", sorted(str(p.relative_to(OUT)) for p in OUT.rglob("*") if p.is_file()))


if __name__ == "__main__":
    main()
