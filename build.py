"""くるま整備ノート ビルド: python build.py → docs/ にサイト一式（GitHub Pagesは /docs を公開）"""
import html
from pathlib import Path

from data_keikoku import LIGHTS
from data_koukan import ITEMS, CATS, CHECK_ALWAYS, ADDITIVES

ROOT = Path(__file__).parent
OUT = ROOT / "docs"
SITE = "くるま整備ノート"
UPDATED = "2026-11-14"
# 整備士チェックが終わったら True にする（それまでは「チェック済み」と書かない）
REVIEWED = True
CHECK_TXT_TODO = "現役の自動車整備士による内容チェックを順次行っています"
CHECK_TXT = "一級自動車整備士・自動車検査員の資格をもつ現役の整備士がチェックしています" if REVIEWED else "現役の自動車整備士による内容チェックを順次行っています"

COLOR = {"red": "赤", "yellow": "黄・オレンジ", "green": "緑", "blue": "青"}
LEVEL = {
    "stop": ("すぐ停車", "安全な場所に停めて相談"),
    "soon": ("早めに点検", "近いうちに整備工場へ"),
    "info": ("お知らせ", "状況を確認すればOKなことが多い"),
}

e = lambda s: html.escape(s, quote=True)


def page(title, desc, body, depth=1, path="", check_txt=None):
    up = "../" * depth
    check = check_txt or CHECK_TXT
    full = SITE if not title else f"{title}｜{SITE}"
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
<link rel="stylesheet" href="{up}assets/style.css">
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
  <p><a href="{up}about/">運営・免責事項</a>　最終更新 {UPDATED}</p>
</div></footer>
</body>
</html>
"""


def write(rel, text):
    p = OUT / rel
    p.parent.mkdir(parents=True, exist_ok=True)
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
    <h2>消耗品の交換時期、整備士の本音</h2>
    <p>見積もりに並んだ交換、今やるべき？ ブレーキパッド・タイヤ・バッテリーなど16項目を3段階で。</p>
  </a>
  <a class="card" href="shaken/">
    <span class="card-ic">📋</span>
    <h2>車検費用の目安計算</h2>
    <p>重量税・自賠責・印紙代は最新の公式の金額で。お店の費用は整備士に聞いた相場。見積もりのポイントも。</p>
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
    <h2>{e(L['name'])}</h2>
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
# 係数は整備士のオーナーさんが調整ラボ（02_お願い/oil-lab.html）で決めた値（2026-11-13）
OIL_P = dict(baseKm=4500, baseOil=3.7, oilExp=0.85, tireExp=0.9, kei=0.9,
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

<div id="out" class="result" aria-live="polite" hidden></div>

<section class="box">
  <h2>計算の考え方</h2>
  <p>基準は<b>1.5Lのガソリン車（オイル3.7L・タイヤ175/65R15）で、おすすめ4,500km</b>。そこから次の3つで早めたり遅めたりしています。</p>
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
    var km,lim,mo,note='';
    if(type==='custom'){km=n($('ckm').value);mo=Math.min(n($('cmo').value)||0,36);lim=null;if(!km||!mo){out.hidden=true;return}}
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
                .replace("__OT__", json.dumps(OIL_TABLE)))
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
<p class="lead">車の種類・重さ・年数を選ぶと、車検にかかる費用の<b>目安</b>を計算します。
国に払う<b>法定費用</b>（重量税・自賠責保険・印紙代）は公式の最新の金額で、<b>お店の費用</b>は現役の整備士に聞いた目安の幅で出します。<br>
<span class="small">※このページの文章は、整備士のチェック前です。</span></p>

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
  <h3>よく足される交換部品</h3>
  <p>スタビライザーリンク、ブーツ類（タイロッドエンドブーツ・ロワアームブーツ・ドライブシャフトブーツなど）、ブレーキパッドは、車検の見積もりによく入ってきます。
  今やるべきかは<a href="../koukan/">消耗品の交換時期、整備士の本音</a>も参考にしてください。</p>
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
  <p>1年ごとの点検もきちんと受けておきましょう。車検の当日に不具合を伝えても、症状によっては保証が使えない場合があります。</p>
</section>

<section class="box">
  <h2>そのほかに知っておきたいこと</h2>
  <ul>
    <li>車検は、有効期間が切れる日の<b>2か月前から</b>受けても、次の有効期間は短くなりません（2025年4月1日から。それまでは1か月前からでした）。年度末はお店が混むので、早めの予約がおすすめです。</li>
  </ul>
</section>

<section class="box">
  <h2>このページの情報のもと</h2>
  <ul>
    __SRC__
  </ul>
  <p class="small">法定費用は、AIの小太郎が上の公式資料で確認しました。お店の費用と見積もりのポイントは、現役の整備士に聞いた現場の声をもとにしています。このページの文章の整備士チェックはこれからです。</p>
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
    write("shaken/index.html", page("車検費用の目安計算", "自家用の普通車・軽自動車の車検費用の目安を計算。重量税・自賠責保険・印紙代は2026年11月時点の公式の金額、お店の費用は現役の整備士に聞いた目安。見積もりを見るときのポイントも。", body, check_txt=CHECK_TXT_TODO))


# ---------------- 消耗品の交換時期 ----------------
LV3 = [("red", "🔴 今すぐ"), ("yellow", "🟡 近いうちに"), ("white", "⚪ 様子見でいい")]


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
  <div class="light-head"><h2>{e(it['name'])}</h2><span class="badge b-info">{CATS[it['cat']]}</span></div>
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
<h1>消耗品の交換時期、整備士の本音</h1>
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
    write("koukan/index.html", page("消耗品の交換時期、整備士の本音",
          "ブレーキパッド・タイヤ・バッテリー・CVTフルードなど、見積もりに出てくる消耗品16項目の交換時期を、現役の一級整備士の基準で「今すぐ／近いうちに／様子見」の3段階に。お店に聞くといい質問も。", body))


# ---------------- このサイトについて ----------------
def build_about():
    body = f"""
<h1>このサイトについて</h1>
<section class="box">
  <h2>だれが作っているか</h2>
  <p>このサイトの文章・ツールは、AIの「小太郎」が作っています。
  内容は{CHECK_TXT}。まちがいがあれば直しています。</p>
  <p>小太郎は「自分でお金を稼ぐ」挑戦をしているAIで、その記録は
  <a href="https://note.com/ai_kotaro" rel="noopener">note</a> に書いています。</p>
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
DOMAIN = "seibi-note.com"
BASE = f"https://{DOMAIN}/"
GSC_FILE = "google64c86059b3bde811.html"  # 消さないこと（消すと Search Console の確認が外れる）


def build_search():
    write("CNAME", DOMAIN + "\n")  # GitHub Pages の独自ドメイン
    write(GSC_FILE, f"google-site-verification: {GSC_FILE}")
    urls = sorted(str(p.parent.relative_to(OUT)) for p in OUT.rglob("index.html"))
    locs = [BASE + ("" if u == "." else u + "/") for u in urls]
    items = "\n".join(f"  <url><loc>{u}</loc><lastmod>{UPDATED}</lastmod></url>" for u in locs)
    write("sitemap.xml", f'<?xml version="1.0" encoding="UTF-8"?>\n'
          f'<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{items}\n</urlset>\n')
    write("robots.txt", f"User-agent: *\nAllow: /\nSitemap: {BASE}sitemap.xml\n")


def main():
    css = (ROOT / "style.css").read_text(encoding="utf-8")
    write("assets/style.css", css)
    write(".nojekyll", "")
    build_index(); build_keikoku(); build_oil(); build_koukan(); build_shaken(); build_about(); build_check()
    build_search()
    print("built:", sorted(str(p.relative_to(OUT)) for p in OUT.rglob("*") if p.is_file()))


if __name__ == "__main__":
    main()
