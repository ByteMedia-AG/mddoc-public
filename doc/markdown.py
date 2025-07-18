from bs4 import BeautifulSoup
import markdown


def md2html(md_text):
    """
    Nimmt einen Markdown-Text und gibt HTML zurück.
    :param md_text:
    :return:
    """

    html = markdown.markdown(
        md_text,
        extensions=['fenced_code', 'codehilite', 'tables'],
        extension_configs={
            'codehilite': {
                'guess_lang': True,
                'noclasses': False,
            }
        },
        output_format='html5',
    )
    soup = BeautifulSoup(html, 'html.parser')

    for code_div in soup.find_all('div', class_='codehilite'):
        wrapper = soup.new_tag('div', **{
            'class': 'bg-black font-monospace px-3 pt-4 pb-2 mb-3 border rounded position-relative'
        })
        button = soup.new_tag('button', **{
            'type': 'button',
            'class': 'btn btn-sm btn-outline-secondary position-absolute top-0 end-0 m-2 copy-code',
            'title': 'Copy to clipboard'
        })
        button.string = 'copy'
        code_div.wrap(wrapper)
        wrapper.insert(0, button)

    for a in soup.find_all('a'):
        a['class'] = 'text-decoration-none link-secondary align-items-center'
        a['target'] = '_blank'
        icon = soup.new_tag('i', **{'class': 'bi bi-link me-2'})
        a.insert(0, icon)

    for tag, cls in [('h1', 'h2 mt-4 mb-2'), ('h2', 'h3 mt-4 mb-2'),
                     ('h3', 'h4 mt-4 mb-2'), ('h4', 'h5 mt-3 mb-2')]:
        for el in soup.find_all(tag):
            el['class'] = cls

    for hr in soup.find_all('hr'):
        hr['class'] = 'my-5'

    for bq in soup.find_all('blockquote'):
        bq['class'] = 'blockquote'

    for table in soup.find_all('table'):
        # wrapper = soup.new_tag('div', **{'class': 'max-80-vh position-relative'})
        wrapper = soup.new_tag('div', **{'class': ''})
        table.wrap(wrapper)
        thead = table.find('thead')
        if thead:
            thead['class'] = thead.get('class', []) + ['sticky-top z-1 pos-below']
        table['class'] = 'table'

    for img in soup.find_all('img'):
        # Transform
        #   <img alt="{alt}" src="{url}" title="{title}">
        # to
        #   <figure class="figure mx-auto d-block">
        #       <img src="{url}" class="figure-img img-fluid rounded mx-auto d-block" alt="{alt}">
        #       <figcaption class="figure-caption text-center">{title}</figcaption>
        #   </figure>
        alt = img.get('alt', '')
        src = img.get('src', '')
        title = img.get('title', '')
        figure = soup.new_tag('figure', **{'class': 'figure mx-auto d-block'})
        new_img = soup.new_tag('img', src=src, alt=alt, **{
            'class': 'figure-img img-fluid rounded mx-auto d-block'
        })
        figure.append(new_img)
        if title:
            caption = soup.new_tag('figcaption', **{'class': 'figure-caption text-center'})
            caption.string = title
            figure.append(caption)
        img.replace_with(figure)

    html = str(soup)

    return html
