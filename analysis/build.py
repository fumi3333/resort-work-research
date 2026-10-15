"""リゾートバイトの労働条件の集計と分析（月次）。

入力：求人データ（非公開。運営者の手元にある jobs_all.json のパスを引数で渡す）
出力：docs/data/ の集計CSV・分析結果のJSON（公開。CC BY 4.0）

公開に使うのは、利用条件を確認した派遣会社5社（ALLOWED）の、掲載中・時給表示の求人だけ。
個別の求人・会社名・施設名は出力しない。集計の枠ごとに次の条件を満たすものだけを出す（SUPPRESS）。
"""

from __future__ import annotations

import argparse
import csv
import datetime
import json
import math
import pathlib
import statistics
from collections import Counter, defaultdict

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

OUT = pathlib.Path(__file__).resolve().parents[1] / "docs" / "data"

# 利用条件を確認した会社（会社名の一部で照合）。他社のデータは読み込んだ時点で捨てる。
# 会社名は公開しない方針のため、一覧は公開リポジトリに置かず、運営者の手元のファイル（--allowed、1行1社）から読む
ALLOWED: tuple[str, ...] = ()

# 集計の枠を出す条件（1つでも満たさなければ「データ不足」）
SUPPRESS = {"min_jobs": 10, "min_agencies": 3, "max_agency_share": 0.6, "min_workplaces": 5}

# 会社ごとに違う職種名を、共通の区分にそろえる（先に当たったもの）
JOB_GROUPS = [
    ("仲居", ("仲居",)),
    ("フロント", ("フロント", "ベル", "受付", "予約")),
    ("調理", ("調理", "料理", "キッチン", "厨房")),
    ("洗い場", ("洗い場", "洗い", "皿洗")),
    ("レストラン・ホール", ("レストラン", "ホール", "配膳", "宴会", "カフェ", "ラウンジ", "バー")),
    ("清掃・裏方", ("清掃", "裏方", "ベッドメイク", "ハウスキーピング", "リネン", "客室")),
    ("売店・販売", ("売店", "販売", "ショップ", "レジ")),
    ("スキー場・レジャー", ("リフト", "スキー", "インストラクター", "レンタル", "ゲレンデ", "マリン", "アクティビティ")),
    ("館内全般", ("館内全般", "全般", "マルチ")),
]


def job_group(name: str) -> str:
    for g, keys in JOB_GROUPS:
        if any(k in (name or "") for k in keys):
            return g
    return "その他"


def load(path: pathlib.Path) -> pd.DataFrame:
    j = json.loads(path.read_text(encoding="utf-8"))
    j = j if isinstance(j, list) else j.get("jobs", [])
    rows = []
    for x in j:
        ag = x.get("agency") or ""
        if not any(a in ag for a in ALLOWED):
            continue
        if x.get("is_closed") or x.get("wage_type") != "時給" or not x.get("wage_min"):
            continue
        w = float(x["wage_min"])
        if not 900 <= w <= 3000:  # 時給として読めない値は除く
            continue
        months = x.get("start_months") or []
        dorm = x.get("dorm_type") or "不明"
        rows.append({
            "agency": ag.split("（")[0],
            "workplace": x.get("workplace_key") or f"_{x.get('id')}",
            "region": x.get("region") or "不明",
            "prefecture": x.get("prefecture") or "不明",
            "job": job_group(x.get("job_category")),
            "wage": w,
            "start_month": int(months[0]) if months else None,
            "dorm_private": 1 if dorm == "完全個室" else 0,
            "dorm_shared": 1 if dorm == "相部屋" else 0,
            "dorm_none": 1 if dorm == "寮なし" else 0,
            "dorm_free": 1 if x.get("dorm_cost") == 0 else 0,
            "meals3": 1 if x.get("meals_per_day") == 3 else 0,
            "wifi": 1 if x.get("dorm_wifi") else 0,
            "travel": 1 if x.get("travel_support") else 0,
            "inexperienced_ok": 1 if x.get("inexperienced_ok") else 0,
        })
    return pd.DataFrame(rows)


def r10(v: float) -> int:
    return int(round(v / 10.0) * 10)


def cell_ok(g: pd.DataFrame) -> bool:
    if len(g) < SUPPRESS["min_jobs"]:
        return False
    share = g["agency"].value_counts(normalize=True)
    return (g["agency"].nunique() >= SUPPRESS["min_agencies"] and share.iloc[0] <= SUPPRESS["max_agency_share"]
            and g["workplace"].nunique() >= SUPPRESS["min_workplaces"])


def table(df: pd.DataFrame, keys: list[str], path: pathlib.Path) -> tuple[int, int]:
    rows, shown, hidden = [], 0, 0
    for k, g in df.groupby(keys, dropna=False):
        k = k if isinstance(k, tuple) else (k,)
        base = dict(zip(keys, k))
        if cell_ok(g):
            q = g["wage"].quantile([0.25, 0.5, 0.75])
            base.update({"件数（10件単位）": r10(len(g)), "時給_下位25%": r10(q[0.25]), "時給_中央値": r10(q[0.5]),
                         "時給_上位25%": r10(q[0.75]), "寮が個室の割合": round(g["dorm_private"].mean(), 2),
                         "1日3食の割合": round(g["meals3"].mean(), 2), "寮費0円の割合": round(g["dorm_free"].mean(), 2)})
            rows.append(base)
            shown += 1
        else:
            hidden += 1
    cols = keys + ["件数（10件単位）", "時給_下位25%", "時給_中央値", "時給_上位25%", "寮が個室の割合", "1日3食の割合", "寮費0円の割合"]
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for r in rows:
            w.writerow({c: ("" if (c in r and isinstance(r[c], float) and math.isnan(r[c])) else r.get(c, "")) for c in cols})
    return shown, hidden


def hedonic(df: pd.DataFrame) -> dict:
    """時給（対数）を、地域・職種・条件・会社の違いで説明する重回帰（ヘドニック分析）。
    会社の違い（固定効果）は推定には入れるが、会社ごとの値は公開しない。"""
    d = df.copy()
    d["lw"] = np.log(d["wage"])
    d["sm"] = d["start_month"].fillna(0).astype(int).astype(str)
    m = smf.ols("lw ~ dorm_private + dorm_shared + dorm_none + dorm_free + meals3 + wifi + travel + inexperienced_ok"
                " + C(job) + C(prefecture) + C(sm) + C(agency)", data=d).fit(cov_type="HC1")
    label = {"dorm_private": "寮が完全個室（相部屋・不明との比較）", "dorm_shared": "寮が相部屋", "dorm_none": "寮なし",
             "dorm_free": "寮費0円", "meals3": "1日3食つき", "wifi": "寮にWi-Fiあり", "travel": "交通費の支給あり",
             "inexperienced_ok": "未経験可"}
    res = []
    for k, name in label.items():
        b, lo, hi = m.params[k], m.conf_int().loc[k, 0], m.conf_int().loc[k, 1]
        res.append({"項目": name, "時給への影響（%）": round((math.exp(b) - 1) * 100, 1),
                    "95%信頼区間（%）": [round((math.exp(lo) - 1) * 100, 1), round((math.exp(hi) - 1) * 100, 1)],
                    "p値": round(float(m.pvalues[k]), 4)})
    return {"n": int(m.nobs), "決定係数": round(float(m.rsquared), 3), "結果": res,
            "制御した要因": "職種・都道府県・開始月・派遣会社（会社ごとの値は非公開）",
            "標準誤差": "不均一分散に頑健（HC1）"}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("jobs_all", type=pathlib.Path)
    ap.add_argument("--edition", default=datetime.date.today().strftime("%Y-%m"))
    ap.add_argument("--allowed", type=pathlib.Path, required=True, help="使ってよい会社の一覧（非公開のファイル）")
    a = ap.parse_args()
    global ALLOWED
    ALLOWED = tuple(l.strip() for l in a.allowed.read_text(encoding="utf-8").splitlines() if l.strip() and not l.startswith("#"))
    if not ALLOWED:
        raise SystemExit("使ってよい会社の一覧が空です")
    OUT.mkdir(parents=True, exist_ok=True)
    df = load(a.jobs_all)
    ed = a.edition
    s1 = table(df, ["region", "job"], OUT / f"{ed}_region_job.csv")
    s2 = table(df, ["prefecture", "job"], OUT / f"{ed}_prefecture_job.csv")
    s3 = table(df[df["start_month"].notna()].assign(start_month=lambda x: x["start_month"].astype(int)),
               ["region", "start_month"], OUT / f"{ed}_region_startmonth.csv")
    model = hedonic(df)
    summary = {
        "edition": ed, "generated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
        "求人件数": int(len(df)), "派遣会社数": int(df["agency"].nunique()), "施設数（推定）": int(df["workplace"].nunique()),
        "時給の中央値": r10(df["wage"].median()), "時給_下位25%": r10(df["wage"].quantile(0.25)), "時給_上位25%": r10(df["wage"].quantile(0.75)),
        "寮が個室の割合": round(df["dorm_private"].mean(), 3), "1日3食の割合": round(df["meals3"].mean(), 3),
        "公開の条件": SUPPRESS,
        "表": {"地方×職種": {"出した枠": s1[0], "データ不足の枠": s1[1]},
              "都道府県×職種": {"出した枠": s2[0], "データ不足の枠": s2[1]},
              "地方×開始月": {"出した枠": s3[0], "データ不足の枠": s3[1]}},
        "ヘドニック分析": model,
    }
    (OUT / f"{ed}_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=1)[:3000])


if __name__ == "__main__":
    main()
