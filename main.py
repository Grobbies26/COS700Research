
import PyPDF4 # useful
import pdfrw # useful
import pdfminer # might be useful
import reportlab
import pypdftk

from io import StringIO
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfparser import PDFParser

def pypdftest(pdf_path):
    with open(pdf_path, 'rb') as f:
        pdf = PyPDF4.PdfFileReader(f)

        #print(pdf.xref) # xref table
        print(pdf.getPage(0)) # gets the page objects
        # print(pdf.getObject()) # work out how ro do this

        # information = pdf.getDocumentInfo()
        # number_of_pages = pdf.getNumPages()

    return

def pdfrwtest(pdf_path):
    pdf = pdfrw.PdfReader(pdf_path)
    
    # print(pdf.keys())
    # print(pdf.Info)
    # print(pdf.Root.keys())
    print(pdf.getPage(0))
        
    return

def pdfminertest(pdf_path):
    with open(pdf_path, 'rb') as f:
        output_string = StringIO()
        parser = PDFParser(f)
        doc = PDFDocument(parser)
        rsrcmgr = PDFResourceManager()
        device = TextConverter(rsrcmgr, output_string, laparams=LAParams())
        interpreter = PDFPageInterpreter(rsrcmgr, device)
        for page in PDFPage.create_pages(doc):
            interpreter.process_page(page)
            print(page)
        
    return

def reportlabtest(pdf_path):
    with open(pdf_path, 'rb') as f:
        output_string = StringIO()
        parser = PDFParser(f)
        doc = PDFDocument(parser)
        rsrcmgr = PDFResourceManager()
        device = TextConverter(rsrcmgr, output_string, laparams=LAParams())
        interpreter = PDFPageInterpreter(rsrcmgr, device)
        for page in PDFPage.create_pages(doc):
            interpreter.process_page(page)
            print(page)
        
    return

if __name__ == '__main__':
    path = './test.pdf'
    # pypdftest(path) # Gives page objects investigate further
    # pdfrwtest(path) # Gives page objects investigate further
    # pdfminertest(path) # can get the page objects investigate further
