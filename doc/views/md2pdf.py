from django.contrib.auth.decorators import login_required, permission_required
from django.http import HttpResponseRedirect
from django.template.response import TemplateResponse
from django.urls import reverse

from doc.utils import doc_pdf, doc_pdfa


@login_required
@permission_required("doc.edit")
def create_pdf(request, **kwargs):
    """
    Creates a PDF based on the content of the specified document. The document
    will be saved in the File model but not set into relation with the document.
    After the rendering the client is redirected to the previously created PDF.
    """

    error = []
    doc_id = kwargs.get('id')

    if request.method != 'POST':
        return HttpResponseRedirect(reverse("doc:detail", args=(doc_id,)))

    try:
        variant = request.POST.get('variant', default=None)
        if variant == 'pdf':
            file = doc_pdf(doc_id)
        if variant == 'pdf-a':
            file = doc_pdfa(doc_id)
        if not file:
            error.append('The creation of the PDF of the content failed.')
    except Exception as e:
        error.append(f'An exception occurred: {e}')

    if error:
        return TemplateResponse(request, "message.html", {
            'page_title': f"PDF creation - ID {doc_id}",
            'doc_id': doc_id,
            'error': error,
        })

    return HttpResponseRedirect(file.file.url)
