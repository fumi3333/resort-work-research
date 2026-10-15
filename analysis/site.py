"""公開サイト（docs/）を、集計結果（docs/data/）から作る。数字は全部 summary.json と CSV から入れる。"""

from __future__ import annotations

import csv
import html
import json
import pathlib
import sys

DOCS = pathlib.Path(__file__).resolve().parents[1] / "docs"
TITLE = "リゾートワーク労働条件レポート"
AUTHOR = "松田晴史（武蔵野大学 経済学部）"
REPO = "https://github.com/fumi3333/resort-work-research"

CSS = """
:root{--ink:#1a1d23;--sub:#5b6472;--line:#dfe3e8;--bg:#ffffff;--panel:#eef2f3;--navy:#1c2e5e;--navy2:#2e4a8c;--bar:#9fb0d0}
@media (prefers-color-scheme:dark){:root{--ink:#e9edf3;--sub:#a3adbb;--line:#2b3442;--bg:#0f141c;--panel:#171e29;--navy:#a9bde6;--navy2:#c9d6f0;--bar:#4a5f8f}}
*{box-sizing:border-box}html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--bg);color:var(--ink);font:400 15px/1.95 "Noto Sans JP",system-ui,sans-serif;letter-spacing:.04em;font-feature-settings:"palt"}
.num,.v,td.n{font-family:"Inter","Noto Sans JP",sans-serif;font-variant-numeric:tabular-nums;letter-spacing:0}
a{color:var(--navy2);text-underline-offset:3px}
.wrap{max-width:1040px;margin:0 auto;padding:0 20px}
header{border-bottom:1px solid var(--line);background:var(--bg)}
.top{display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:6px 24px;padding:18px 0}
.brand{text-decoration:none;color:var(--ink)}.brand b{display:block;font-size:17px;font-weight:700;letter-spacing:.08em}.brand span{font-size:11px;color:var(--sub);letter-spacing:.12em}
nav a{margin-right:22px;font-size:13px;font-weight:500;text-decoration:none;color:var(--ink)}nav a:last-child{margin-right:0}
.hero{background:var(--panel);padding:56px 0 48px}
.eyebrow{font-size:12px;font-weight:500;color:var(--navy2);letter-spacing:.16em;margin:0 0 12px}
.hero h1{font-size:clamp(24px,4vw,36px);line-height:1.5;font-weight:700;margin:0 0 16px;color:var(--ink);letter-spacing:.06em}
.hero p{margin:0;color:var(--sub);max-width:760px}
main section{padding:8px 0}
h2{font-size:22px;font-weight:700;margin:56px 0 20px;letter-spacing:.06em}
h2::before{content:"";display:block;width:32px;height:3px;background:var(--navy);margin-bottom:14px}
.lead{color:var(--sub);max-width:780px}
.kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));border-top:1px solid var(--line);border-left:1px solid var(--line)}
.kpi{padding:22px 20px;border-right:1px solid var(--line);border-bottom:1px solid var(--line)}
.kpi .k{font-size:12px;color:var(--sub);letter-spacing:.08em}.kpi .v{font-size:34px;font-weight:600;color:var(--navy);line-height:1.3}.kpi .v small{font-size:15px;margin-left:2px}.kpi .v.r{font-size:26px;white-space:nowrap}
.reports{border-top:1px solid var(--line)}
.report{display:grid;grid-template-columns:120px 1fr;gap:4px 20px;padding:22px 4px;border-bottom:1px solid var(--line);text-decoration:none;color:var(--ink)}
.report:hover .t{text-decoration:underline}
.report .d{font-family:Inter,sans-serif;font-size:13px;color:var(--sub)}.report .tag{display:inline-block;font-size:11px;border:1px solid var(--navy2);color:var(--navy2);padding:0 8px;margin-bottom:6px}
.report .t{font-size:17px;font-weight:700}
@media (max-width:560px){.report{grid-template-columns:1fr}}
.panel{background:var(--panel);padding:24px}
table{border-collapse:collapse;width:100%;font-size:13.5px}th,td{border-bottom:1px solid var(--line);padding:10px 8px;text-align:left;vertical-align:middle}
th{font-weight:500;color:var(--sub);font-size:12px;letter-spacing:.06em;border-bottom:2px solid var(--ink)}td.n{text-align:right}
.scroll{overflow-x:auto}.sm{font-size:12.5px;color:var(--sub)}
.dl{display:flex;flex-wrap:wrap;gap:10px}.dl a{border:1px solid var(--ink);padding:9px 16px;text-decoration:none;color:var(--ink);font-size:13px;font-weight:500}
.dl a::after{content:" ↓"}
svg.chart{max-width:780px;display:block}.chart text{font:12px "Noto Sans JP",sans-serif;fill:var(--sub)}.chart .val{font-family:Inter,sans-serif;fill:var(--ink);font-weight:600}
.chart .bar{fill:var(--bar)}.chart .mid{stroke:var(--navy);stroke-width:2}.chart .axis{stroke:var(--line)}.chart .ci{stroke:var(--navy);stroke-width:2}.chart .dot{fill:var(--navy)}
.tool{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:14px;align-items:end}
.tool label{display:flex;flex-direction:column;gap:6px;font-size:12px;color:var(--sub);letter-spacing:.06em}
.tool select,.tool input{font:500 15px "Noto Sans JP",sans-serif;padding:10px;border:1px solid var(--line);background:var(--bg);color:var(--ink)}
.result{margin-top:20px;font-size:15px}.result .big{font-family:Inter,sans-serif;font-size:28px;font-weight:600;color:var(--navy)}
.cta{border:1px solid var(--line);padding:24px;display:flex;flex-wrap:wrap;gap:12px 24px;align-items:center;justify-content:space-between}
.cta a{background:var(--navy);color:#fff;padding:10px 18px;text-decoration:none;font-size:13px;font-weight:500}
@media (prefers-color-scheme:dark){.cta a{color:#0f141c}}
footer{border-top:1px solid var(--line);margin-top:72px;padding:28px 0 48px;font-size:12px;color:var(--sub)}
"""


def page(title: str, body: str, depth: int = 0) -> str:
    up = "../" * depth
    return f"""<!doctype html>
<html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
<meta name="description" content="リゾート地の短期・住み込みの仕事（リゾートバイト）の時給と寮・食事などの条件を、地域・職種ごとに集計した月次レポート。集計データはCC BY 4.0で自由に使えます。">
<link rel="preconnect" href="https://fonts.googleapis.com"><link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Noto+Sans+JP:wght@400;500;700&display=swap" rel="stylesheet">
<style>{CSS}</style></head><body>
<header><div class="wrap top"><a class="brand" href="{up}index.html"><b>{TITLE}</b><span>RESORT WORK LABOR CONDITIONS REPORT</span></a>
<nav><a href="{up}index.html#reports">レポート</a><a href="{up}index.html#data">データ</a><a href="{up}methods.html">調べ方</a></nav></div></header>
{body}
<footer><div class="wrap">
<p>作成：{AUTHOR}　連絡先：zax-official@fumiproject.dev</p>
<p>集計データ・レポートは <a href="https://creativecommons.org/licenses/by/4.0/deed.ja">CC BY 4.0</a> で公開しています。使うときは「出典：{TITLE}（{AUTHOR}）」とこのサイトへのリンクを書いてください。集計のコードは <a href="{REPO}">GitHub</a> で公開しています（MITライセンス）。</p>
<p>元の求人は、各派遣会社が公開している求人ページです。個別の求人・会社名・施設名は掲載していません。</p>
</div></footer></body></html>"""


def read_csv(p: pathlib.Path) -> list[dict]:
    with p.open(encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def pct(v: float) -> str:
    return f"{round(v * 100)}%"


def wavg_rows(groups: dict) -> list[tuple[str, int, int, int]]:
    """枠ごとの値を件数で重み付けして、まとまり（地方・職種）ごとの目安にする"""
    out = []
    for name, rs in groups.items():
        tot = sum(int(r["件数（10件単位）"]) for r in rs) or 1
        w = lambda k: int(round(sum(int(r[k]) * int(r["件数（10件単位）"]) for r in rs) / tot / 10) * 10)
        out.append((name, w("時給_下位25%"), w("時給_中央値"), w("時給_上位25%")))
    return sorted(out, key=lambda r: -r[2])


def bars(rows: list[tuple[str, int, int, int]]) -> str:
    """横棒：下位25%〜上位25%の帯と、中央値の縦線"""
    lo = min(r[1] for r in rows) - 50
    hi = max(r[3] for r in rows) + 50
    W, L, R, H = 640, 130, 74, 30
    x = lambda v: L + (v - lo) / (hi - lo) * (W - L - R)
    out = [f'<svg class="chart" viewBox="0 0 {W} {H * len(rows) + 26}" width="100%" role="img" aria-label="時給の範囲">']
    for i, (name, q1, md, q3) in enumerate(rows):
        y = i * H + 6
        out.append(f'<text x="0" y="{y + 15}">{html.escape(name)}</text>')
        out.append(f'<rect class="bar" x="{x(q1):.1f}" y="{y + 4}" width="{max(2, x(q3) - x(q1)):.1f}" height="14"/>')
        out.append(f'<line class="mid" x1="{x(md):.1f}" x2="{x(md):.1f}" y1="{y + 1}" y2="{y + 21}"/>')
        out.append(f'<text class="val" x="{W - R + 8}" y="{y + 15}">{md:,}円</text>')
    yb = H * len(rows) + 20
    for v in range((lo // 100 + 1) * 100, hi, 100):
        out.append(f'<text x="{x(v) - 14:.1f}" y="{yb}">{v:,}</text>')
    out.append("</svg>")
    return "".join(out)


def coef(rows: list[dict]) -> str:
    """推定値（点）と95%信頼区間（線）。0%の線つき"""
    lo = min(r["95%信頼区間（%）"][0] for r in rows) - 1
    hi = max(r["95%信頼区間（%）"][1] for r in rows) + 1
    W, L, R, H = 640, 250, 74, 30
    x = lambda v: L + (v - lo) / (hi - lo) * (W - L - R)
    out = [f'<svg class="chart" viewBox="0 0 {W} {H * len(rows) + 8}" width="100%" role="img" aria-label="条件と時給の関係">',
           f'<line class="axis" x1="{x(0):.1f}" x2="{x(0):.1f}" y1="0" y2="{H * len(rows)}"/>']
    for i, r in enumerate(rows):
        y = i * H + 15
        a_, b_ = r["95%信頼区間（%）"]
        out.append(f'<text x="0" y="{y + 4}">{html.escape(r["項目"])}</text>')
        out.append(f'<line class="ci" x1="{x(a_):.1f}" x2="{x(b_):.1f}" y1="{y}" y2="{y}"/>')
        out.append(f'<circle class="dot" cx="{x(r["時給への影響（%）"]):.1f}" cy="{y}" r="5"/>')
        out.append(f'<text class="val" x="{W - R + 8}" y="{y + 4}">{r["時給への影響（%）"]:+.1f}%</text>')
    out.append("</svg>")
    return "".join(out)


TOOL_JS = """
const R=document.getElementById('tr'),J=document.getElementById('tj'),W=document.getElementById('tw'),O=document.getElementById('tres');
[...new Set(T.map(t=>t.r))].forEach(v=>R.add(new Option(v,v)));
const big=T.slice().sort((a,b)=>b.n-a.n)[0];R.value=big.r;
function fillJ(){const cur=J.value;J.innerHTML='';T.filter(t=>t.r===R.value).forEach(t=>J.add(new Option(t.j,t.j)));if([...J.options].some(o=>o.value===cur))J.value=cur;else{const b=T.filter(t=>t.r===R.value&&t.j!=='その他').sort((a,b)=>b.n-a.n)[0];if(b)J.value=b.j;}show();}
function show(){const t=T.find(t=>t.r===R.value&&t.j===J.value);if(!t){O.textContent='';return;}
const w=+W.value;let pos='';if(w){pos=w<t.q1?'下位25%より低い水準です':w<t.md?'中央値より低く、下位25%以上の水準です':w<t.q3?'中央値以上、上位25%未満の水準です':'上位25%以上の高い水準です';}
O.innerHTML='<div class="sm">'+t.r+'・'+t.j+'（約'+t.n+'件）</div><div><span class="big">'+t.md.toLocaleString()+'円</span>　中央値</div><div class="sm">真ん中の半分：'+t.q1.toLocaleString()+'〜'+t.q3.toLocaleString()+'円</div>'+(pos?'<p>入力した時給 '+w.toLocaleString()+'円は、'+pos+'</p>':'');}
R.onchange=fillJ;J.onchange=show;W.oninput=show;fillJ();
"""

CTA = ('<section><div class="cta"><div><b>地域・職種を絞った集計のご相談</b><div class="sm">特定の温泉地・スキー場周辺など、公開版より細かい集計や、'
       '自社の求人条件との比較をご希望の方はご連絡ください。</div></div>'
       '<a href="mailto:zax-official@fumiproject.dev?subject=%E9%9B%86%E8%A8%88%E3%81%AE%E3%81%94%E7%9B%B8%E8%AB%87">問い合わせる</a></div></section>')


def kpi(k: str, v: str, unit: str, cls: str = "") -> str:
    return f'<div class="kpi"><div class="k">{k}</div><div class="v {cls}">{v}<small>{unit}</small></div></div>'


def main(ed: str) -> None:
    s = json.loads((DOCS / "data" / f"{ed}_summary.json").read_text(encoding="utf-8"))
    y, m = ed.split("-")
    label = f"{int(y)}年{int(m)}月"
    h = s["ヘドニック分析"]
    rj = read_csv(DOCS / "data" / f"{ed}_region_job.csv")
    by_r, by_j = {}, {}
    for r in rj:
        by_r.setdefault(r["region"], []).append(r)
        by_j.setdefault(r["job"], []).append(r)

    rows = "".join(f"<tr><td>{html.escape(r['region'])}</td><td>{html.escape(r['job'])}</td><td class=n>{int(r['時給_中央値']):,}</td>"
                   f"<td class=n>{int(r['時給_下位25%']):,}–{int(r['時給_上位25%']):,}</td><td class=n>{pct(float(r['寮が個室の割合']))}</td>"
                   f"<td class=n>{pct(float(r['1日3食の割合']))}</td><td class=n>{r['件数（10件単位）']}</td></tr>" for r in rj)
    tool_data = json.dumps([{"r": r["region"], "j": r["job"], "q1": int(r["時給_下位25%"]), "md": int(r["時給_中央値"]),
                             "q3": int(r["時給_上位25%"]), "n": int(r["件数（10件単位）"])} for r in rj], ensure_ascii=False)
    tool = ('<section><h2>時給の目安を調べる</h2><p class="lead">地方と職種を選び、時給を入れると、同じ地方・職種の求人の中でどのあたりかを表示します。'
            '求人の条件を決めるとき、応募先を比べるときの目安にしてください。</p><div class="panel"><div class="tool">'
            '<label>地方<select id="tr"></select></label><label>職種<select id="tj"></select></label>'
            '<label>時給（円）<input id="tw" type="number" inputmode="numeric" min="900" max="3000" step="10" placeholder="例 1300"></label></div>'
            f'<div class="result" id="tres"></div></div></section><script>const T={tool_data};{TOOL_JS}</script>')
    k4 = (kpi("時給の中央値", f"{s['時給の中央値']:,}", "円") + kpi("真ん中の半分の範囲", f"{s['時給_下位25%']:,}–{s['時給_上位25%']:,}", "円", "r")
          + kpi("寮が完全個室の求人", str(round(s["寮が個室の割合"] * 100)), "%") + kpi("1日3食つきの求人", str(round(s["1日3食の割合"] * 100)), "%"))

    rep = f"""<section class="hero"><div class="wrap"><p class="eyebrow">MONTHLY REPORT　{label}版</p>
<h1>リゾートバイトの時給と条件　{label}</h1>
<p>掲載中の求人{s['求人件数']:,}件（派遣会社{s['派遣会社数']}社）をもとに、地域・職種ごとの時給の水準と、寮・食事などの条件が時給とどう関係しているかをまとめました。</p></div></section>
<main class="wrap">
<section><h2>全体の水準</h2><div class="kpis">{k4}</div></section>
<section><h2>地方別の時給</h2><p class="lead">帯は真ん中の半分（下位25%〜上位25%）、縦線は中央値です。</p>{bars(wavg_rows(by_r))}</section>
<section><h2>職種別の時給</h2>{bars(wavg_rows(by_j))}</section>
<section><h2>条件と時給の関係</h2>
<p class="lead">同じ職種・都道府県・開始月・派遣会社の求人どうしで比べたとき、各条件がある求人の時給が何%高い（低い）か。点は推定値、線は95%信頼区間です（重回帰分析、{h['n']:,}件）。</p>
{coef(h['結果'])}
<p>食事や寮費の負担が軽い求人ほど、時給はわずかに低い傾向がありました。時給だけでなく、寮や食事を含めた条件の全体で働く人を集めている様子がうかがえます。</p>
<p class="sm">条件と時給の関係を示すもので、条件を変えれば時給がその分変わるという因果関係ではありません。1か月分のデータによる結果です。</p></section>
{tool}
<section><h2>地方×職種の時給</h2>
<p class="sm">件数が少ない枠、特定の1社や施設に偏る枠は出していません（<a href="../methods.html">調べ方</a>）。時給は円、件数は10件単位。</p>
<div class="scroll"><table><tr><th>地方</th><th>職種</th><th>中央値</th><th>真ん中の半分</th><th>寮が個室</th><th>3食つき</th><th>件数</th></tr>{rows}</table></div></section>
<section><h2>データのダウンロード</h2>
<div class="dl"><a href="../data/{ed}_region_job.csv">地方×職種 CSV</a><a href="../data/{ed}_prefecture_job.csv">都道府県×職種 CSV</a><a href="../data/{ed}_region_startmonth.csv">地方×開始月 CSV</a><a href="../data/{ed}_summary.json">分析結果 JSON</a></div>
<p class="sm">CC BY 4.0。出典「{TITLE}（{AUTHOR}）」とリンクを書けば、自由に使えます。</p></section>
{CTA}
</main>"""
    (DOCS / "reports").mkdir(parents=True, exist_ok=True)
    (DOCS / "reports" / f"{ed}.html").write_text(page(f"{label}版 | {TITLE}", rep, 1), encoding="utf-8")

    reps = sorted((DOCS / "reports").glob("20*.html"), reverse=True)
    rl = "".join(f'<a class="report" href="reports/{p.name}"><div class="d">{p.stem[:4]}.{p.stem[5:7]}</div>'
                 f'<div><span class="tag">月次レポート</span><div class="t">リゾートバイトの時給と条件　{int(p.stem[:4])}年{int(p.stem[5:7])}月</div></div></a>' for p in reps)
    k3 = kpi("対象の求人", f"{s['求人件数']:,}", "件") + kpi("時給の中央値", f"{s['時給の中央値']:,}", "円") + kpi("寮が完全個室の求人", str(round(s["寮が個室の割合"] * 100)), "%")
    top = f"""<section class="hero"><div class="wrap"><p class="eyebrow">RESORT WORK LABOR CONDITIONS REPORT</p>
<h1>リゾートで働く人と、受け入れる施設のための<br>労働条件の基礎データ</h1>
<p>リゾート地の短期・住み込みの仕事について、時給や寮・食事の条件を地域・職種ごとに集計し、毎月公開しています。働く人が条件を比べるとき、施設や派遣会社が求人の条件を考えるとき、自治体が観光地の人手を考えるときの材料として、無料で使えるようにすることが目的です。</p></div></section>
<main class="wrap">
<section><h2 id="reports">レポート</h2><div class="reports">{rl}</div></section>
<section><h2>最新の水準（{label}）</h2><div class="kpis">{k3}</div></section>
<section><h2 id="data">データ</h2>
<p class="lead">集計した表はCSVで自由にダウンロードできます（CC BY 4.0）。個別の求人・会社名・施設名は含みません。</p>
<div class="dl"><a href="data/{ed}_region_job.csv">地方×職種</a><a href="data/{ed}_prefecture_job.csv">都道府県×職種</a><a href="data/{ed}_region_startmonth.csv">地方×開始月</a><a href="data/{ed}_summary.json">分析結果 JSON</a></div></section>
<section><h2>このレポートについて</h2>
<p class="lead">元のデータは、派遣会社各社が公開している求人ページです。利用の条件を確認できた{s['派遣会社数']}社の、掲載中で時給が書かれている求人だけを使っています。集計の手順とコードは公開しており、同じ計算を誰でも確かめられます。</p>
<p><a href="methods.html">調べ方と、公開の条件</a>　／　<a href="{REPO}">集計のコード（GitHub）</a></p></section>
{CTA}
</main>"""
    (DOCS / "index.html").write_text(page(TITLE, top), encoding="utf-8")

    c = s["公開の条件"]
    meth = f"""<section class="hero"><div class="wrap"><h1>調べ方と、公開の条件</h1></div></section>
<main class="wrap">
<h2>元のデータ</h2>
<p>リゾートバイトの派遣会社が自社サイトで公開している求人ページを、毎日1回読み取っています。このレポートに使うのは、利用の条件を確認できた派遣会社{s['派遣会社数']}社の、掲載中で時給が書かれている求人です。利用規約で集計や商業目的の利用を制限している会社の求人は使っていません。</p>
<h2>そろえ方</h2>
<p>職種名は会社ごとに違うため、「フロント」「調理」「レストラン・ホール」などの共通の区分にそろえています。時給が900円未満・3,000円を超える値は、読み取りの誤りとして除いています。開始月は、求人に書かれた入社可能な月のうち最も早い月です。</p>
<h2>公開の条件（特定を防ぐため）</h2>
<p>集計の枠（例：関東×フロント）ごとに、次の条件をすべて満たすときだけ数字を出します。満たさない枠は「データ不足」として出しません。</p>
<ul><li>求人が{c['min_jobs']}件以上</li><li>{c['min_agencies']}社以上の求人を含む</li><li>1社の求人が全体の{int(c['max_agency_share']*100)}%以下</li><li>施設が{c['min_workplaces']}か所以上</li></ul>
<p>時給は10円単位、件数は10件単位に丸め、中央値と上位・下位25%だけを出します。最高値・最低値は出しません。</p>
<h2>条件と時給の関係（重回帰分析）</h2>
<p>時給の対数を、寮の種類・寮費0円・1日3食・寮のWi-Fi・交通費の支給・未経験可で説明し、職種・都道府県・開始月・派遣会社の違いを固定効果として取り除いています（ヘドニック分析）。標準誤差は不均一分散に頑健なもの（HC1）です。派遣会社ごとの推定値は公開していません。</p>
<h2>限界</h2>
<ul><li>求人に書かれた時給で、実際に支払われた額ではありません。</li><li>今月の版は1か月分のデータで、季節による違いは含みません。</li><li>求人が掲載から消えたことは、採用が決まったことと同じではありません。埋まるまでの日数の分析は、会社ごとの違いを取り除く方法を確かめてから出します。</li></ul>
</main>"""
    (DOCS / "methods.html").write_text(page(f"調べ方 | {TITLE}", meth), encoding="utf-8")
    (DOCS / ".nojekyll").write_text("", encoding="utf-8")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "2026-10")
