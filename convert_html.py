from flask import Flask, request, send_file
from flask_cors import CORS
from io import BytesIO
from weasyprint import HTML
from pdf2docx import Converter
import tempfile
import os  # Importar el módulo os

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost:4200"}})

@app.route('/pdf', methods=['POST'])
def convert_html_to_pdf():
    content = request.json.get('html_content', '')

    if not content.strip():
        return {"error": "El contenido HTML está vacío."}, 400

    adjusted_content = f"""
    <style>
        @page {{
            size: 22cm 29.7cm; /* Tamaño personalizado */
            margin: 1cm;
        }}
        body {{
            font-family: Arial, sans-serif;
        }}
        img {{
            max-width: 100%;
            height: auto;
        }}
    </style>
    {content.replace(
        "column-count: 2;",
        "column-count: 2; column-gap: 1cm; column-width: 8cm; width: 90%; overflow: hidden;"
    ).replace(
        "padding: 2cm;",
        "padding: 1cm 0.5cm 1cm 0.5cm;"
    )}"""

    pdf_file = BytesIO()
    html = HTML(string=adjusted_content, base_url="/")
    html.write_pdf(pdf_file)
    pdf_file.seek(0)

    return send_file(pdf_file, as_attachment=True, download_name='document.pdf')

@app.route('/pdf-word', methods=['POST'])
def convert_pdf_to_word():
    content = request.json.get('html_content', '')

    if not content.strip():
        return {"error": "El contenido HTML está vacío."}, 400

    # Crear PDF temporal
    pdf_file = BytesIO()
    adjusted_content = f"""
    <style>
        @page {{
            size: 22cm 29.7cm; /* Tamaño personalizado */
            margin: 1cm;
        }}
        body {{
            font-family: Arial, sans-serif;
        }}
        img {{
            max-width: 100%;
            height: auto;
        }}
    </style>
    {content.replace(
        "column-count: 2;",
        "column-count: 2; column-gap: 1cm; column-width: 8cm; width: 90%; overflow: hidden;"
    ).replace(
        "padding: 2cm;",
        "padding: 1cm 0.5cm 1cm 0.5cm;"
    )}"""

    html = HTML(string=adjusted_content, base_url="/")
    html.write_pdf(pdf_file)
    pdf_file.seek(0)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf:
        temp_pdf.write(pdf_file.read())
        pdf_path = temp_pdf.name

    # Convertir PDF a Word
    word_file = BytesIO()
    try:
        converter = Converter(pdf_path)
        converter.convert(word_file, start=0, end=None)
        converter.close()
    except Exception as e:
        return {"error": f"Error al convertir el PDF a Word: {str(e)}"}, 500
    finally:
        # Eliminar archivo temporal
        try:
            os.remove(pdf_path)
        except OSError:
            pass

    word_file.seek(0)
    return send_file(word_file, as_attachment=True, download_name='document.docx')


if __name__ == '__main__':
    app.run(debug=True)
