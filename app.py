"""Flask メインアプリケーション - 機器表→見積書 自動生成システム"""

import os
import json
import tempfile
import urllib.parse
from flask import Flask, render_template, request, redirect, url_for, flash, session, Response

from config import UPLOAD_FOLDER, ALLOWED_EXTENSIONS, MAX_CONTENT_LENGTH
from models.equipment import EquipmentList, load_demo_data
from models.quotation import Quotation
from utils.excel_parser import parse_excel
from utils.pdf_generator import generate_pdf

app = Flask(__name__)
app.secret_key = "hashimoto-sougyo-demo-2026"
app.config["MAX_CONTENT_LENGTH"] = MAX_CONTENT_LENGTH

# アップロードフォルダ作成
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/")
def index():
    """トップページ（アップロード画面）"""
    return render_template("index.html")


@app.route("/demo", methods=["POST"])
def demo():
    """デモデータ読込"""
    equipment = load_demo_data()
    session["equipment_data"] = equipment.to_json()
    return redirect(url_for("review"))


@app.route("/upload", methods=["POST"])
def upload():
    """Excelアップロード処理"""
    if "file" not in request.files:
        flash("ファイルが選択されていません。", "warning")
        return redirect(url_for("index"))

    file = request.files["file"]
    if file.filename == "":
        flash("ファイルが選択されていません。", "warning")
        return redirect(url_for("index"))

    if not allowed_file(file.filename):
        flash("Excel形式（.xlsx, .xls）のファイルを選択してください。", "danger")
        return redirect(url_for("index"))

    # 一時ファイルに保存して解析
    with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp:
        file.save(tmp.name)
        try:
            equipment = parse_excel(tmp.name)
            if not equipment.items:
                flash("機器データを検出できませんでした。フォーマットを確認してください。", "warning")
                return redirect(url_for("index"))
            session["equipment_data"] = equipment.to_json()
        except Exception as e:
            flash(f"ファイルの読み込みに失敗しました: {e}", "danger")
            return redirect(url_for("index"))
        finally:
            os.unlink(tmp.name)

    return redirect(url_for("review"))


@app.route("/review")
def review():
    """機器データ確認・編集画面"""
    equipment_json = session.get("equipment_data")
    if not equipment_json:
        flash("データがありません。ファイルをアップロードしてください。", "warning")
        return redirect(url_for("index"))

    equipment = EquipmentList.from_json(equipment_json)
    summary = equipment.get_summary()
    categories = equipment.get_categories()
    category_items = {}
    for cat in categories:
        category_items[cat] = [item.to_dict() for item in equipment.get_by_category(cat)]

    return render_template(
        "review.html",
        equipment=equipment,
        equipment_json=equipment_json,
        summary=summary,
        categories=categories,
        category_items=category_items,
    )


@app.route("/quotation", methods=["POST"])
def quotation():
    """見積書プレビュー画面"""
    equipment_json = request.form.get("equipment_data")
    if not equipment_json:
        equipment_json = session.get("equipment_data")

    if not equipment_json:
        flash("データがありません。", "warning")
        return redirect(url_for("index"))

    equipment = EquipmentList.from_json(equipment_json)
    q = Quotation.from_equipment_list(equipment)
    q_dict = q.to_dict()

    # PDF用にデータをURLエンコードして渡す
    pdf_data = urllib.parse.quote(json.dumps(q_dict, ensure_ascii=False))

    return render_template(
        "quotation.html",
        quotation=q,
        pdf_data=pdf_data,
    )


@app.route("/pdf")
def pdf():
    """PDF出力"""
    data_str = request.args.get("data", "")
    if not data_str:
        flash("データがありません。", "warning")
        return redirect(url_for("index"))

    try:
        quotation_data = json.loads(urllib.parse.unquote(data_str))
    except (json.JSONDecodeError, ValueError):
        flash("データの読み込みに失敗しました。", "danger")
        return redirect(url_for("index"))

    pdf_bytes = generate_pdf(quotation_data)

    filename = f'見積書_{quotation_data.get("estimate_number", "")}.pdf'
    encoded_filename = urllib.parse.quote(filename)

    return Response(
        pdf_bytes,
        mimetype="application/pdf",
        headers={
            "Content-Disposition": f"inline; filename*=UTF-8''{encoded_filename}",
        },
    )


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
