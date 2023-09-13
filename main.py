
import PyPDF4 # useful
import pdfrw # useful
import hashlib
# import pdfminer # might be useful
# import reportlab
# import pypdftk

# from io import StringIO
# from pdfminer.converter import TextConverter
# from pdfminer.layout import LAParams
# from pdfminer.pdfdocument import PDFDocument
# from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
# from pdfminer.pdfpage import PDFPage
# from pdfminer.pdfparser import PDFParser

def pypdftest(pdf_path):
    with open(pdf_path, 'rb') as f:
        pdf = PyPDF4.PdfFileReader(f)

        print(pdf.xref) # xref table
        print()
        pages = list(pdf.pages)
        print(pages)
        print()
        print(pages[0].extractText())
        print()
        print(pages[1])
        print()
        # print(pdf.resolvedObjects) # gets the page objects
        # print() 
        # print(pdf.resolvedObjects[(0,1)]) # gets the page objects
        # print() 
        # print(pdf.resolvedObjects[(0,2)])
        # print() 
        # print(pdf.resolvedObjects[(0,3)])
        # print()
        # print(pdf.resolvedObjects[(0,14)])
        # print()
        # print(pdf.getObject((0,1))) # work out how ro do this

        # information = pdf.getDocumentInfo()
        # number_of_pages = pdf.getNumPages()

    return

def pdfrwtest(pdf_path):
    pdf = pdfrw.PdfReader(pdf_path)
    
    print(pdf.keys())
    print()
    print(pdf.Info)
    print()
    print(pdf.Root.keys())
    print()
    pages = pdf.pages
    print(pages)
    print()
    print(pages[0])
    print()
    print(pages[0].Contents)
    print()
    print(pages[0].Contents.stream)
    print()
    hash = hashlib.sha256(pages[0].Contents.stream.encode('utf-8')).hexdigest()
    print(hash)    
    print()
    print(pages[1])
    print()
    print(pages[1].Contents.stream)
    print()

    # opages = []
    # opages.append(pages.pop(0))
    # pdfrw.PdfWriter('./Test_PDFS/spamPDF.pdf').addpages(opages).write()

    return

# def pdfminertest(pdf_path):
#     with open(pdf_path, 'rb') as f:
#         output_string = StringIO()
#         parser = PDFParser(f)
#         doc = PDFDocument(parser)
#         rsrcmgr = PDFResourceManager()
#         device = TextConverter(rsrcmgr, output_string, laparams=LAParams())
#         interpreter = PDFPageInterpreter(rsrcmgr, device)
#         for page in PDFPage.create_pages(doc):
#             interpreter.process_page(page)
#             print(page)
        
#     return

# def reportlabtest(pdf_path):
#     with open(pdf_path, 'rb') as f:
#         output_string = StringIO()
#         parser = PDFParser(f)
#         doc = PDFDocument(parser)
#         rsrcmgr = PDFResourceManager()
#         device = TextConverter(rsrcmgr, output_string, laparams=LAParams())
#         interpreter = PDFPageInterpreter(rsrcmgr, device)
#         for page in PDFPage.create_pages(doc):
#             interpreter.process_page(page)
#             print(page)
        
#     return

if __name__ == '__main__':
    # path = './Test_PDFS/test.pdf'
    path = './Test_PDFS/simplePDF.pdf'
    # pypdftest(path) # Gives page objects investigate further
    pdfrwtest(path) # Gives page objects investigate further
    
