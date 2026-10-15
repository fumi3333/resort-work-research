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
:root{--ink:#14213d;--sub:#4a5568;--line:#d9dee7;--bg:#ffffff;--soft:#f4f6f9;--navy:#0b2545;--accent:#13315c}
@media (prefers-color-scheme:dark){:root{--ink:#e8edf5;--sub:#a9b4c4;--line:#2c3646;--bg:#0f1520;--soft:#162030;--navy:#9db7e0;--accent:#c7d6ee}}
*{box-sizing:border-box}html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--bg);color:var(--ink);font:16px/1.85 "Noto Sans JP",-apple-system,BlinkMacSystemFont,"Hiragino Sans",sans-serif}
a{color:var(--accent)}header{border-bottom:3px solid var(--navy)}
.wrap{max-width:960px;margin:0 auto;padding:0 16px}
.top{display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px;padding:14px 0}
.brand{font-weight:700;color:var(--navy);text-decoration:none;font-size:17px;letter-spacing:.02em}
nav a{margin-left:18px;font-size:14px;text-decoration:none;color:var(--ink)}nav a:first-child{margin-left:0}
.hero{background:var(--soft);border-bottom:1px solid var(--line);padding:40px 0 32px}
.hero h1{font-size:26px;line-height:1.5;margin:0 0 10px;color:var(--navy)}
.hero p{margin:0;color:var(--sub);max-width:720px}
h2{font-size:20px;color:var(--navy);border-left:5px solid var(--navy);padding-left:10px;margin:40px 0 14px}
h3{font-size:16px;margin:24px 0 8px}
.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:12px}
.card{border:1px solid var(--line);border-top:3px solid var(--navy);padding:14px;background:var(--bg)}
.card .k{font-size:13px;color:var(--sub)}.card .v{font-size:26px;font-weight:700;color:var(--navy)}
.report{display:block;border:1px solid var(--line);padding:16px;text-decoration:none;color:var(--ink);margin:0 0 10px}
.report .d{font-size:13px;color:var(--sub)}.report .t{font-weight:700;font-size:17px;color:var(--navy)}
table{border-collapse:collapse;width:100%;font-size:14px}th,td{border-bottom:1px solid var(--line);padding:8px 6px;text-align:left;vertical-align:top}
th{background:var(--soft);font-weight:600}td.n{text-align:right;font-variant-numeric:tabular-nums}
.scroll{overflow-x:auto}.sm{font-size:13px;color:var(--sub)}
.dl a{display:inline-block;border:1px solid var(--navy);padding:6px 12px;margin:0 8px 8px 0;text-decoration:none;font-size:14px}
footer{border-top:1px solid var(--line);margin-top:48px;padding:20px 0 40px;font-size:13px;color:var(--sub)}
"""


def page(title: str, body: str, depth: int = 0) -> str:
    up = "../" * depth
    return f"""<!doctype html>
<html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
<meta name="description" content="リゾート地の短期・住み込みの仕事（リゾートバイト）の時給と寮・食事などの条件を、地域・職種ごとに集計した月次レポート。集計データはCC BY 4.0で自由に使えます。">
<link rel="preconnect" href="https://fonts.googleapis.com"><link href="https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;600;700&display=swap" rel="stylesheet">
<style>{CSS}</style></head><body>
<header><div class="wrap top"><a class="brand" href="{up}index.html">{TITLE}</a>
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


def main(ed: str) -> None:
    s = json.loads((DOCS / "data" / f"{ed}_summary.json").read_text(encoding="utf-8"))
    y, m = ed.split("-")
    label = f"{int(y)}年{int(m)}月"
    h = s["ヘドニック分析"]

    # レポート本文
    rj = read_csv(DOCS / "data" / f"{ed}_region_job.csv")
    rows = "".join(f"<tr><td>{html.escape(r['region'])}</td><td>{html.escape(r['job'])}</td><td class=n>{r['時給_中央値']}円</td>"
                   f"<td class=n>{r['時給_下位25%']}〜{r['時給_上位25%']}円</td><td class=n>{pct(float(r['寮が個室の割合']))}</td>"
                   f"<td class=n>{pct(float(r['1日3食の割合']))}</td><td class=n>{r['件数（10件単位）']}</td></tr>" for r in rj)
    hrows = "".join(f"<tr><td>{html.escape(x['項目'])}</td><td class=n>{x['時給への影響（%）']:+.1f}%</td>"
                    f"<td class=n>{x['95%信頼区間（%）'][0]:+.1f}〜{x['95%信頼区間（%）'][1]:+.1f}%</td></tr>" for x in h["結果"])
    rep = f"""<section class="hero"><div class="wrap"><p class="sm">月次レポート　{label}版</p>
<h1>リゾートバイトの時給と条件：{label}</h1>
<p>掲載中の求人{s['求人件数']:,}件（派遣会社{s['派遣会社数']}社）をもとに、地域・職種ごとの時給の水準と、寮・食事などの条件が時給とどう関係しているかをまとめました。</p></div></section>
<main class="wrap">
<h2>全体の水準</h2>
<div class="cards">
<div class="card"><div class="k">時給の中央値</div><div class="v">{s['時給の中央値']:,}円</div></div>
<div class="card"><div class="k">真ん中の半分の範囲</div><div class="v">{s['時給_下位25%']:,}〜{s['時給_上位25%']:,}円</div></div>
<div class="card"><div class="k">寮が完全個室の求人</div><div class="v">{pct(s['寮が個室の割合'])}</div></div>
<div class="card"><div class="k">1日3食つきの求人</div><div class="v">{pct(s['1日3食の割合'])}</div></div>
</div>

<h2>条件と時給の関係</h2>
<p>同じ職種・都道府県・開始月・派遣会社の求人どうしで比べたとき、各条件がある求人の時給が何%高い（低い）かを推定しました（重回帰分析、{h['n']:,}件、決定係数{h['決定係数']}）。</p>
<div class="scroll"><table><tr><th>条件</th><th>時給への関係</th><th>95%信頼区間</th></tr>{hrows}</table></div>
<p>食事や寮費の負担が軽い求人ほど、時給はわずかに低い傾向がありました。時給だけでなく、寮や食事を含めた条件の全体で働く人を集めている様子がうかがえます。未経験可の求人は時給が3%ほど低めです。</p>
<p class="sm">これは条件と時給の「関係」で、条件を変えれば時給がその分変わる、という因果関係を示すものではありません。1か月分のデータによる結果で、季節による違いは今後の版で確かめます。</p>

<h2>地方×職種の時給</h2>
<p class="sm">件数が少ない枠、特定の1社や施設に偏る枠は「データ不足」として出していません（調べ方を参照）。件数は10件単位に丸めています。</p>
<div class="scroll"><table><tr><th>地方</th><th>職種</th><th>時給の中央値</th><th>真ん中の半分</th><th>寮が個室</th><th>3食つき</th><th>件数</th></tr>{rows}</table></div>

<h2>データのダウンロード</h2>
<div class="dl"><a href="../data/{ed}_region_job.csv">地方×職種（CSV）</a><a href="../data/{ed}_prefecture_job.csv">都道府県×職種（CSV）</a><a href="../data/{ed}_region_startmonth.csv">地方×開始月（CSV）</a><a href="../data/{ed}_summary.json">集計と分析の結果（JSON）</a></div>
</main>"""
    (DOCS / "reports").mkdir(parents=True, exist_ok=True)
    (DOCS / "reports" / f"{ed}.html").write_text(page(f"{label}版 | {TITLE}", rep, 1), encoding="utf-8")

    # トップ
    reps = sorted((DOCS / "reports").glob("20*.html"), reverse=True)
    rl = "".join(f'<a class="report" href="reports/{p.name}"><div class="d">月次レポート</div><div class="t">リゾートバイトの時給と条件：{int(p.stem[:4])}年{int(p.stem[5:7])}月</div></a>' for p in reps)
    top = f"""<section class="hero"><div class="wrap">
<h1>リゾートで働く人と、受け入れる施設のための<br>労働条件の基礎データ</h1>
<p>リゾート地の短期・住み込みの仕事について、時給や寮・食事の条件を地域・職種ごとに集計し、毎月公開しています。働く人が条件を比べるとき、施設や派遣会社が求人の条件を考えるとき、自治体が観光地の人手を考えるときの材料として、無料で使えるようにすることが目的です。</p>
</div></section>
<main class="wrap">
<h2 id="reports">レポート</h2>{rl}
<h2 id="data">データ</h2>
<p>集計した表はCSVで自由にダウンロードできます（CC BY 4.0）。個別の求人・会社名・施設名は含みません。</p>
<div class="dl"><a href="data/{ed}_region_job.csv">地方×職種</a><a href="data/{ed}_prefecture_job.csv">都道府県×職種</a><a href="data/{ed}_region_startmonth.csv">地方×開始月</a><a href="data/{ed}_summary.json">分析結果（JSON）</a></div>
<h2>このレポートについて</h2>
<p>元のデータは、派遣会社各社が公開している求人ページです。利用の条件を確認できた{s['派遣会社数']}社の、掲載中で時給が書かれている求人だけを使っています。集計の手順とコードはすべて公開しているので、同じ計算を誰でも確かめられます。</p>
<p><a href="methods.html">調べ方と、公開の条件</a>　<a href="{REPO}">集計のコード（GitHub）</a></p>
<p>派遣会社・施設・自治体の方からの、分析の見方や使い道についてのご意見を歓迎します。</p>
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
