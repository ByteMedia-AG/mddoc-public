import io
import os
import shutil
import subprocess
import tempfile

import markdown
from bs4 import BeautifulSoup
from django.conf import settings
from django.contrib.staticfiles import finders
from django.core.files.base import ContentFile
from django.core.serializers import serialize
from django.template.loader import render_to_string
from django.utils.timezone import now
from pikepdf import Pdf, AttachedFileSpec
from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration

from doc.models import Doc, File


def doc_pdf(doc_id):
    """"""

    try:
        doc = Doc.objects.get(pk=doc_id)
    except Doc.DoesNotExist:
        return False

    if doc.is_markdown:
        html_body = markdown.markdown(
            doc.text,
            extensions=['fenced_code', 'codehilite', 'tables'],
            extension_configs={
                'codehilite': {
                    'guess_lang': True,
                    'noclasses': False,
                }
            },
            output_format='html5',
        )
        soup = BeautifulSoup(html_body, 'html.parser')
        for img in soup.find_all('img'):
            alt = img.get('alt', '')
            src = img.get('src', '')
            title = img.get('title', '')
            figure = soup.new_tag('figure', **{'class': ''})
            new_img = soup.new_tag('img', src=src, alt=alt, **{
                'class': ''
            })
            figure.append(new_img)
            if title:
                caption = soup.new_tag('figcaption', **{'class': ''})
                caption.string = title
                figure.append(caption)
            img.replace_with(figure)
        html_body = str(soup)
    else:
        html_body = f'<pre>{doc.text}</pre>'

    html = f"""<!DOCTYPE html><html lang="de"><head><meta charset="UTF-8">
        <title>{doc.title}</title></head>
        <body>{html_body}</body></html>"""

    css_string = render_to_string('pdf/md2pdf.css', {
        'path_to_fonts': finders.find('doc/fonts/'),
        'path_to_images': finders.find('doc/images/'),
        'title': doc.title,
        'footer': doc.updated_at,
    })

    font_config = FontConfiguration()
    css = CSS(string=css_string, font_config=font_config)

    pdf_buffer = io.BytesIO()
    HTML(string=html).write_pdf(pdf_buffer, stylesheets=[css], font_config=font_config)
    pdf_buffer.seek(0)

    timestamp = now().strftime("%Y%m%d%H%M%S")
    filename = f"Content-{doc_id}-{timestamp}.pdf"

    file = File()
    file.name = filename
    file.file.save(filename, ContentFile(pdf_buffer.read()))
    file.file.close()
    file.is_volatile = True
    file.save()

    return file


def doc_pdfa(doc_id):
    """"""

    try:
        doc = Doc.objects.get(pk=doc_id)
        file = doc_pdf(doc.id)
    except Doc.DoesNotExist:
        return False

    pdf = Pdf.open(file.file.path, allow_overwriting_input=True)

    # Attach README.md from template
    readme_path = os.path.join(settings.BASE_DIR, "doc", "templates", "pdf", "README.md")
    if readme_path and os.path.exists(readme_path):
        with open(readme_path, "rb") as readme_file:
            readme_data = readme_file.read()
            readme_spec = AttachedFileSpec(
                pdf,
                readme_data,
                filename="README.md",
                mime_type="text/markdown"
            )
            pdf.attachments["README.md"] = readme_spec

    # Serialized data (jsonl)
    doc_jsonl = serialize("jsonl", [doc, *doc.files.all()])
    serialized_data = AttachedFileSpec(pdf, doc_jsonl.encode("utf-8"), mime_type="application/json")
    pdf.attachments["data.json"] = serialized_data

    # Serialized data (yaml)
    doc_yaml = serialize("yaml", [doc, *doc.files.all()])
    serialized_data = AttachedFileSpec(pdf, doc_yaml.encode("utf-8"), mime_type="application/x-yaml")
    pdf.attachments["data.yaml"] = serialized_data

    # Attach all the files of the document
    for f in doc.files.all():
        with open(f.file.path, 'rb') as af:
            file_data = af.read()
        filename = f'file.{f.id}.{f.uuid}.{f.extension}'
        filespec = AttachedFileSpec(
            pdf,
            file_data,
            filename=filename,
            mime_type=f.mime_type or "application/octet-stream"
        )
        pdf.attachments[filename] = filespec

    pdf.save(file.file.path)

    if settings.DOC_ALLOW_GHOSTSCRIPT:
        icc_profile = settings.DOC_SRGB_ICC_PATH
        output_path = file.file.path.replace(".pdf", ".pdfa.pdf")
        if os.path.exists(output_path):
            os.remove(output_path)
        cmd = [
            "gs",
            "-dPDFA=3",
            "-dBATCH",
            "-dNOPAUSE",
            "-dNOOUTERSAVE",
            "-sColorConversionStrategy=UseDeviceIndependentColor",
            f"-sOutputIntentProfile={icc_profile}",
            "-sOutputIntent=Custom",
            "-dPDFACompatibilityPolicy=1",
            "-sDEVICE=pdfwrite",
            f"-sOutputFile={output_path}",
            "-dShowAnnots=false",
            file.file.path,
        ]
        subprocess.run(cmd, check=True, capture_output=True, text=True)
        with open(output_path, "rb") as pdfa_file:
            pdfa_content = pdfa_file.read()
            pdfa_filename = os.path.basename(output_path)

            pdfa_file_obj = File()
            pdfa_file_obj.name = pdfa_filename
            pdfa_file_obj.file.save(pdfa_filename, ContentFile(pdfa_content))
            pdfa_file_obj.file.close()
            pdfa_file_obj.is_volatile = True
            pdfa_file_obj.save()

            file = pdfa_file_obj
            if os.path.exists(output_path):
                os.remove(output_path)

    with Pdf.open(file.file.path, allow_overwriting_input=True) as pdf:
        pdf.save(file.file.path)

    return file
