"""くるま整備ノート ビルド: python build.py → docs/ にサイト一式（GitHub Pagesは /docs を公開）"""
import html
from pathlib import Path

from data_keikoku import LIGHTS
from data_koukan import ITEMS, CATS, CHECK_ALWAYS, ADDITIVES

ROOT = Path(__file__).parent
OUT = ROOT / "docs"
SITE = "くるま整備ノート"
UPDATED = "2026-11-13"
# 整備士チェックが終わったら True にする（それまでは「チェック済み」と書かない）
REVIEWED = True
CHECK_TXT = "現役の自動車整備士が内容をチェックしています" if REVIEWED else "現役の自動車整備士による内容チェックを順次行っています"

COLOR = {"red": "赤", "yellow": "黄・オレンジ", "green": "緑", "blue": "青"}
LEVEL = {
    "stop": ("すぐ停車", "安全な場所に停めて相談"),
    "soon": ("早めに点検", "近いうちに整備工場へ"),
    "info": ("お知らせ", "状況を確認すればOKなことが多い"),
}

e = lambda s: html.escape(s, quote=True)


def page(title, desc, body, depth=1, path=""):
    up = "../" * depth
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
  <nav><a href="{up}keikoku/">警告灯</a><a href="{up}oil/">オイル交換</a><a href="{up}koukan/">交換時期</a><a href="{up}about/">このサイトについて</a></nav>
</div></header>
<main class="wrap">
{body}
</main>
<footer class="site-foot"><div class="wrap">
  <p>このサイトは、AIの「小太郎」が作り、{CHECK_TXT}。
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
    <p>前回の交換日と走行距離を入れるだけで、次の交換の目安を計算します。</p>
  </a>
  <a class="card" href="koukan/">
    <span class="card-ic">🧰</span>
    <h2>消耗品の交換時期、整備士の本音</h2>
    <p>見積もりに並んだ交換、今やるべき？ ブレーキパッド・タイヤ・バッテリーなど16項目を3段階で。</p>
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
    write("index.html", page("", "車の警告灯の意味、オイル交換時期の計算など。AIが作り、自動車整備士がチェックする車のお役立ち情報サイトです。", body, depth=0))


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
def build_oil():
    body = """
<h1>オイル交換時期の計算ツール</h1>
<p class="lead">前回オイル交換した日と走行距離を入れると、次の交換の目安を計算します。
現役の自動車整備士の基準で、<b>「おすすめの時期」</b>と<b>「遅くともここまで」</b>の2段階で表示します。</p>

<form id="f" class="tool" onsubmit="return false">
  <label>車のタイプ
    <select id="type">
      <option value="na">ガソリン車（ターボなし・普通車）</option>
      <option value="kei">軽自動車（ターボなし）</option>
      <option value="turbo">ターボ車（軽ターボ含む）</option>
      <option value="diesel">ディーゼル車</option>
      <option value="custom">自分で指定する（取扱説明書の数値など）</option>
    </select>
  </label>
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
  <h2>整備士の基準</h2>
  <table class="tbl">
    <thead><tr><th>車のタイプ</th><th>おすすめ</th><th>遅くとも</th></tr></thead>
    <tbody>
      <tr><td>ガソリン車（ターボなし・普通車）</td><td>5,000km または 1年</td><td>10,000km</td></tr>
      <tr><td>軽自動車（ターボなし）</td><td>5,000km または 1年</td><td>7,500km</td></tr>
      <tr><td>ターボ車（軽ターボ含む）</td><td>2,500km または 6ヶ月</td><td>5,000km</td></tr>
      <tr><td>ディーゼル車</td><td>2,500km または 6ヶ月</td><td>5,000km</td></tr>
    </tbody>
  </table>
  <p class="small">1.5Lクラスのガソリン車を基準にした目安です。車種によって違うので、取扱説明書の指定も確認してください。</p>

  <h3>取扱説明書には「15,000km」と書いてあるけど？</h3>
  <p>国内メーカーの取扱説明書では、ターボなしのガソリン車で「15,000kmまたは1年」となっている車種も多くあります。
  ただ、整備の現場から見ると<b>15,000kmは遅すぎる</b>というのが正直なところです。
  オイルが汚れたまま走るとエンジンの中が少しずつ削れ、そのスピードが早くなってエンジンの寿命を縮めます。
  おすすめは5,000km、<b>どんなに遅くても10,000km</b>で交換してください。軽自動車はそれより少し早め、ターボ車はその半分くらいが目安です。</p>

  <h3>「シビアコンディション」は気にしたほうがいい？</h3>
  <p>取扱説明書には、短い距離の運転や渋滞が多い使い方（シビアコンディション）だと交換時期を短くするよう書かれています。
  ただ、<b>1年ごとにきちんと替えていれば、そこまで気にしなくて大丈夫</b>です。たくさん走る人は、期間より距離で判断してください。</p>

  <h3>自分の車に合った時期を知るには</h3>
  <p>交換のときに、抜いたオイルの汚れ具合をお店の人に聞いてみてください。
  汚れがひどければ次は早めに、きれいなら今のペースで大丈夫。何回か続けると、自分の乗り方と車に合った交換時期がわかってきます。</p>

  <h3>オイルエレメント（フィルター）は？</h3>
  <p>オイル交換2回に1回の交換が一般的な目安です。ただし、抜いたオイルにライトを当てても全く透けないほど汚れているときは、回数に関係なく交換したほうがいいです。</p>

  <h3>あまり走らないなら交換しなくていい？</h3>
  <p>エンジンオイルは走らなくても時間とともに劣化します。距離が少なくても、1年たったら交換しましょう。</p>
</section>

<script>
(function(){
  // [おすすめkm, 遅くともkm, 期間(月)]
  var T={na:[5000,10000,12],kei:[5000,7500,12],turbo:[2500,5000,6],diesel:[2500,5000,6]};
  var $=function(id){return document.getElementById(id)};
  var f=$('f'),out=$('out');
  function addMonths(d,m){var r=new Date(d.getFullYear(),d.getMonth()+m,d.getDate());if(r.getDate()!==d.getDate())r.setDate(0);return r}
  function fmt(d){return d.getFullYear()+'年'+(d.getMonth()+1)+'月'+d.getDate()+'日'}
  function n(v){return v===''?null:Math.max(0,Math.floor(Number(v)))}
  function c(x){return x.toLocaleString('ja-JP')}
  function run(){
    var type=$('type').value;
    $('custom').hidden=type!=='custom';
    var km,lim,mo;
    if(type==='custom'){km=n($('ckm').value);mo=Math.min(n($('cmo').value)||0,36);lim=null;if(!km||!mo){out.hidden=true;return}}
    else{km=T[type][0];lim=T[type][1];mo=T[type][2]}
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
      h+='<div><span>距離で（おすすめ）</span><b>'+c(o0+km)+' km</b>';
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
      :'まだ大丈夫です。距離と期間のどちらか早いほうで交換してください。';
    if(cls==='ok'&&driven!==null&&driven>0){
      var used=(today-d0)/864e5;
      if(used>=14){var perDay=driven/used,kmDay=Math.round((km-driven)/perDay);
        if(kmDay<days){var pd=new Date(today.getTime()+kmDay*864e5);
          if(kmDay<=30){cls='soon';msg='もうすぐ交換どきです。予約や準備をしておきましょう。'}
          msg+='<br>今のペース（1日約'+c(Math.round(perDay))+'km）だと、<b>'+fmt(pd)+'ごろ</b>におすすめの距離に届きそうです。'}}
    }
    h+='<p class="st st-'+cls+'">'+msg+'</p>';
    h+='<p class="small">使った目安：おすすめ '+c(km)+'km'+(lim?'（遅くとも '+c(lim)+'km）':'')+' または '+mo+'ヶ月。</p>';
    out.innerHTML=h;out.hidden=false;
  }
  f.addEventListener('input',run);f.addEventListener('change',run);run();
})();
</script>
"""
    write("oil/index.html", page("オイル交換時期の計算ツール", "前回のオイル交換日と走行距離を入れるだけで、次のオイル交換の目安を計算。現役整備士の基準で「おすすめ」と「遅くとも」の2段階表示。ガソリン車・軽自動車・ターボ車・ディーゼル車に対応。", body))


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
そんなときのために、<b>現役の自動車整備士が、見積もりを見て優先度を決めるときの基準</b>をまとめました。</p>

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
  <p>「🔴🟡⚪」の基準と「整備士の本音」は、現役の自動車整備士が、見積もりの優先度を判断するために自分で書いた表がもとになっています。
  「一般的な目安」は、メーカーや業界団体の公開情報をもとにAIの小太郎が調べて書いたもので、<b>整備士のチェックはこれから</b>です（確認できしだい更新します）。</p>
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
          "ブレーキパッド・タイヤ・バッテリー・CVTフルードなど、見積もりに出てくる消耗品16項目の交換時期を、現役整備士の基準で「今すぐ／近いうちに／様子見」の3段階に。お店に聞くといい質問も。", body))


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
  <p><a href="https://github.com/syokotanpink8555-lab/kuruma-seibi/issues" rel="noopener">GitHubのIssue</a> から教えてください。確認して直します。</p>
</section>
"""
    write("about/index.html", page("このサイトについて", "くるま整備ノートの運営者・免責事項。AIが作り、自動車整備士が内容をチェックしています。", body))


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
    lines += ["## オイル交換ツールの目安（優先度ルール表の基準に合わせた）",
              "- ガソリン（ターボなし）おすすめ5,000km/1年・遅くとも10,000km",
              "- 軽（ターボなし）おすすめ5,000km/1年・遅くとも7,500km",
              "- ターボ・ディーゼル おすすめ2,500km/6ヶ月・遅くとも5,000km",
              "- シビアコンディションの選択はなし（1年ごとに替えていれば気にしなくてよい）", ""]
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
BASE = "https://syokotanpink8555-lab.github.io/kuruma-seibi/"
GSC_FILE = "google64c86059b3bde811.html"  # 消さないこと（消すと Search Console の確認が外れる）


def build_search():
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
    build_index(); build_keikoku(); build_oil(); build_koukan(); build_about(); build_check()
    build_search()
    print("built:", sorted(str(p.relative_to(OUT)) for p in OUT.rglob("*") if p.is_file()))


if __name__ == "__main__":
    main()
