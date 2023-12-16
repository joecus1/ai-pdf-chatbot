from urllib.request import urlretrieve
from pypdf import PdfReader, PdfWriter
import glob
import os

# This document pulls PDFs from the internet and edits them for use in the LLM
# This script should be run before launching the streamlit appS


def pull():
    if not os.path.isdir('./data/'):
        os.mkdir('./data/')

    urls = [
        'https://s2.q4cdn.com/299287126/files/doc_financials/2023/ar/2022-Shareholder-Letter.pdf',
    ]

    filenames = [
        'Amazon-Shareholders-2022'
    ]

    metadata = [
        dict(year=2022, source=filenames[0])
    ]

    data_root = "./data/"

    retrieved = False
    for idx, url in enumerate(urls):
        file_path = data_root + filenames[idx]
        if not os.path.isfile(file_path):
            urlretrieve(url, file_path)
            retrieved = True
            print(f'Document stored to {file_path}')

    # if retrieved:
    #     print('Truncating retrieved documents to remove repeated sections.')
    #     local_pdfs = glob.glob(data_root + '*.pdf')

    #     for local_pdf in local_pdfs:
    #         pdf_reader = PdfReader(local_pdf)
    #         pdf_writer = PdfWriter()
            
    #         for pagenum in range(len(pdf_reader.pages) -3):
    #             page = pdf_reader.pages[pagenum]
    #             pdf_writer.add_page(page)
                
    #         with open(local_pdf, 'wb') as new_file:
    #             new_file.seek(0)
    #             pdf_writer.write(new_file)
    #             new_file.truncate()

    return (filenames, metadata, data_root)
