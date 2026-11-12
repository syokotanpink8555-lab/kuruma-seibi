"""くるま整備ノート ビルド: python build.py → docs/ にサイト一式（GitHub Pagesは /docs を公開）"""
import html
from pathlib import Path

from data_keikoku import LIGHTS

ROOT = Path(__file__).parent
OUT = ROOT / "docs"
SITE = "くるま整備ノート"
UPDATED = "2026-11-12"
# 整備士チェックが終わったら True にする（それまでは「チェック済み」と書かない）
REVIEWED = False
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
  <nav><a href="{up}keikoku/">警告灯</a><a href="{up}oil/">オイル交換</a><a href="{up}about/">このサイトについて</a></nav>
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
</div>
<section class="box">
  <h2>困ったときは</h2>
  <p>走行中に赤い警告灯が点いた、煙や異音がする、ブレーキの効きがおかしい――そんなときは無理に走らず、
  安全な場所に停めてロードサービス（JAFは <b>#8139</b>）や加入している自動車保険のロードサービスに連絡してください。</p>
  <p>高速道路で止まったときは、ハザードランプをつけ、停止表示器材（三角表示板）を置いて、人はガードレールの外など安全な場所へ避難してください。
  道路上の危険の通報は道路緊急ダイヤル <b>#9910</b> です。</p>
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
  <p>エンジン・ブレーキ・ABS・エアバッグなどの警告灯が点灯・点滅していると、車検に合格できません。車検の前に点検・修理が必要です。</p>
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
<p class="lead">前回オイル交換した日と走行距離を入れると、次の交換の目安（日付と距離）を計算します。
<b>「距離」と「期間」のどちらか早いほう</b>が交換のタイミングです。</p>

<form id="f" class="tool" onsubmit="return false">
  <label>車のタイプ
    <select id="type">
      <option value="na">ガソリン車（ターボなし・軽自動車含む）</option>
      <option value="turbo">ターボ車（軽ターボ含む）</option>
      <option value="diesel">ディーゼル車</option>
      <option value="custom">自分で指定する（取扱説明書の数値など）</option>
    </select>
  </label>
  <fieldset>
    <legend>車の使い方</legend>
    <label class="radio"><input type="radio" name="cond" value="normal" checked> ふつう</label>
    <label class="radio"><input type="radio" name="cond" value="severe"> シビアコンディション
      <button type="button" class="q" id="sev-btn" aria-expanded="false">これは何？</button></label>
    <div id="sev" class="sev" hidden>
      次のどれかに当てはまる使い方は、エンジンへの負担が大きい「シビアコンディション」です。
      <ul>
        <li>近所の買い物など、短い距離（1回8km以下が目安）の運転をくり返す</li>
        <li>渋滞やのろのろ運転、アイドリングが多い</li>
        <li>山道・坂道が多い（走行距離の3割以上が目安）</li>
        <li>砂利道・雪道などの悪路が多い（走行距離の3割以上が目安）</li>
        <li>1年に2万km以上走る</li>
      </ul>
      街乗り中心の車でも、当てはまることが少なくありません。
    </div>
  </fieldset>
  <div id="custom" class="row" hidden>
    <label>交換の距離（km）<input id="ckm" type="number" inputmode="numeric" min="500" step="500" value="5000"></label>
    <label>交換の期間（ヶ月）<input id="cmo" type="number" inputmode="numeric" min="1" max="24" value="6"></label>
  </div>
  <div class="row">
    <label>前回交換した日<input id="date" type="date" required></label>
    <label>前回交換時の走行距離（km）<input id="odo0" type="number" inputmode="numeric" min="0" placeholder="例：42000"></label>
  </div>
  <label><span>今の走行距離（km）<span class="opt">わかれば</span></span><input id="odo1" type="number" inputmode="numeric" min="0" placeholder="例：45500"></label>
</form>

<div id="out" class="result" aria-live="polite" hidden></div>

<section class="box">
  <h2>目安の考え方</h2>
  <p>このツールは、国内メーカーの取扱説明書でよく見られる交換時期をもとにしています。</p>
  <table class="tbl">
    <thead><tr><th>車のタイプ</th><th>ふつう</th><th>シビア</th></tr></thead>
    <tbody>
      <tr><td>ガソリン車（ターボなし）</td><td>15,000km または 1年</td><td>7,500km または 6ヶ月</td></tr>
      <tr><td>ターボ車</td><td>5,000km または 6ヶ月</td><td>2,500km または 3ヶ月</td></tr>
      <tr><td>ディーゼル車</td><td>10,000km または 1年</td><td>5,000km または 6ヶ月</td></tr>
    </tbody>
  </table>
  <p>実際の交換時期は車種・年式・使うオイルによって違います。<b>いちばん確かなのは、あなたの車の取扱説明書（メンテナンスノート）</b>です。
  その数値がわかる場合は「自分で指定する」を選んでください。</p>
  <h3>オイルエレメント（フィルター）は？</h3>
  <p>オイル交換2回に1回の交換が一般的な目安です。</p>
  <h3>あまり走らないなら交換しなくていい？</h3>
  <p>エンジンオイルは走らなくても時間とともに劣化します。距離が少なくても、期間の目安が来たら交換するのがおすすめです。</p>
</section>

<script>
(function(){
  var T={na:{normal:[15000,12],severe:[7500,6]},turbo:{normal:[5000,6],severe:[2500,3]},diesel:{normal:[10000,12],severe:[5000,6]}};
  var $=function(id){return document.getElementById(id)};
  var f=$('f'),out=$('out');
  $('sev-btn').addEventListener('click',function(){var s=$('sev');s.hidden=!s.hidden;this.setAttribute('aria-expanded',!s.hidden)});
  function addMonths(d,m){var r=new Date(d.getFullYear(),d.getMonth()+m,d.getDate());if(r.getDate()!==d.getDate())r.setDate(0);return r}
  function fmt(d){return d.getFullYear()+'年'+(d.getMonth()+1)+'月'+d.getDate()+'日'}
  function n(v){return v===''?null:Math.max(0,Math.floor(Number(v)))}
  function c(x){return x.toLocaleString('ja-JP')}
  function run(){
    var type=$('type').value,cond=f.querySelector('input[name=cond]:checked').value;
    $('custom').hidden=type!=='custom';
    f.querySelectorAll('input[name=cond]').forEach(function(r){r.disabled=type==='custom'});
    var km,mo;
    if(type==='custom'){km=n($('ckm').value);mo=Math.min(n($('cmo').value)||0,36);if(!km||!mo){out.hidden=true;return}}
    else{km=T[type][cond][0];mo=T[type][cond][1]}
    var dv=$('date').value;if(!dv){out.hidden=true;return}
    var p=dv.split('-'),d0=new Date(+p[0],p[1]-1,+p[2]);
    if(p.length!==3||isNaN(d0)){out.hidden=true;return}
    var today=new Date();today=new Date(today.getFullYear(),today.getMonth(),today.getDate());
    if(d0>today){out.innerHTML='<p class="st st-soon">前回交換日が未来の日付になっています。日付を確認してください。</p>';out.hidden=false;return}
    var due=addMonths(d0,mo),days=Math.round((due-today)/864e5);
    var o0=n($('odo0').value),o1=n($('odo1').value);
    var h='<h2>次のオイル交換の目安</h2><div class="due">';
    h+='<div><span>期間で</span><b>'+fmt(due)+'</b><small>'+(days>=0?'あと'+days+'日':Math.abs(days)+'日過ぎています')+'</small></div>';
    var leftKm=null;
    if(o0!==null){
      var dueKm=o0+km;
      h+='<div><span>距離で</span><b>'+c(dueKm)+' km</b>';
      if(o1!==null&&o1<o0)h+='<small>今の走行距離が前回より小さくなっています。数字を確認してください。</small>';
      if(o1!==null&&o1>=o0){leftKm=dueKm-o1;h+='<small>'+(leftKm>=0?'あと'+c(leftKm)+' km':c(-leftKm)+' km 超えています')+'</small>'}
      h+='</div>';
    }
    h+='</div>';
    var late=days<0||(leftKm!==null&&leftKm<0),soon=!late&&(days<=30||(leftKm!==null&&leftKm<=500));
    var cls=late?'late':soon?'soon':'ok';
    var msg=late?'交換の目安を過ぎています。早めに交換しましょう。':soon?'そろそろ交換の時期です。予約や準備をしておきましょう。':'まだ大丈夫です。どちらか早いほうを目安にしてください。';
    if(o0!==null&&o1!==null&&o1>o0&&!late){
      var used=(today-d0)/864e5;
      if(used>=14){var perDay=(o1-o0)/used,kmDay=Math.round(leftKm/perDay);
        if(kmDay<days){var pd=new Date(today.getTime()+kmDay*864e5);
          if(kmDay<=30&&cls==='ok'){cls='soon';msg='そろそろ交換の時期です。予約や準備をしておきましょう。'}
          msg+='<br>今のペース（1日約'+c(Math.round(perDay))+'km）だと、<b>'+fmt(pd)+'ごろ</b>に距離の目安に届きそうです。'}}
    }
    h+='<p class="st st-'+cls+'">'+msg+'</p>';
    h+='<p class="small">使った目安：'+c(km)+'km または '+mo+'ヶ月。取扱説明書の指定があればそちらを優先してください。</p>';
    out.innerHTML=h;out.hidden=false;
  }
  f.addEventListener('input',run);f.addEventListener('change',run);run();
})();
</script>
"""
    write("oil/index.html", page("オイル交換時期の計算ツール", "前回のオイル交換日と走行距離を入れるだけで、次のオイル交換の目安（日付・距離）を計算。ガソリン車・ターボ車・ディーゼル車、シビアコンディションに対応。", body))


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
    lines += ["## オイル交換ツールの目安",
              "- ガソリン（ターボなし）15,000km/1年、シビア 7,500km/6ヶ月",
              "- ターボ 5,000km/6ヶ月、シビア 2,500km/3ヶ月",
              "- ディーゼル 10,000km/1年、シビア 5,000km/6ヶ月 ← 車種差が大きいので特に見てほしい",
              "- エレメントは2回に1回",
              "- 整備士として「実際はこのくらいで替えて」というおすすめがあれば、ツールに『整備士のおすすめ』として載せます", "",
              "## 特に聞きたいこと", 
              "1. 車検に通らない警告灯：ブレーキ・ABS・エンジン・エアバッグに書いた。横滑り防止（ESC）も対象？ OBD検査（故障コードが残っていると不合格）の説明はエンジン警告灯のひとことで足りる？",
              "2. 軽自動車（ターボなし）も 15,000km/1年 でいい？ ディーゼルの数字は？",
              "3. 充電警告灯：ベルト切れ以外なら近くの工場まで走っていい、と書くべき？",
              "4. 水温警告灯：冷えたあと冷却水を足せば近くの工場まで走れる、と書く？ 今は『自走しない』にしている",
              "5. グロー：プッシュスタートの今の車でも『消えてからかける』の説明でいい？",
              "6. 現場でのおすすめ交換時期（取説より早め）があれば教えてほしい", ""]
    out = ROOT.parent.parent / "02_お願い" / "整備士チェック_警告灯とオイル.md"
    out.write_text("\n".join(lines), encoding="utf-8")


def main():
    css = (ROOT / "style.css").read_text(encoding="utf-8")
    write("assets/style.css", css)
    write(".nojekyll", "")
    build_index(); build_keikoku(); build_oil(); build_about(); build_check()
    print("built:", sorted(str(p.relative_to(OUT)) for p in OUT.rglob("*") if p.is_file()))


if __name__ == "__main__":
    main()
