# Gabriel Grobler Research Project

import pdfrw # useful
from merkly.mtree import MerkleTree


#Calculate the Hash Values for the PDF
def calculateHashValues(filePageObjects = []):
    if filePageObjects == []:
        return

    content = []
    hashes = []
    w = 256

    for i, page in enumerate(filePageObjects):  
        content = [page.Contents.stream[i:i + w] for i in range(0, len(page.Contents.stream), w)]

        tree = MerkleTree(content)

        hash = {"root": tree.root, "leafs": tree.leafs}
        hashes.append(hash)

    return hashes

#Retrieve the previously stored Hash Values
def getHashValues(filePageObjects = []):
    if filePageObjects == {}:
        return
    
    hashes = []
    for i, page in enumerate(filePageObjects):
        root = page.hashroot.replace("(","").replace(")","")
        leafs = [val.replace("(","").replace(")","") for val in page.hashleafs]
        hashes.append({"root":root,"leafs":leafs})

    return hashes

#Get the file page objects for the PDF
def getFilePageObjects(pdf_path = ""):
    if pdf_path == "":
        return
    
    pdf = pdfrw.PdfReader(pdf_path)
    filePageObjects = pdf.pages

    return filePageObjects

#Insert the Hash Values into the PDF
def insertHashValues(writer, pages=[], hashes = []):
    if hashes == [] or pages == []:
        return
    
    for i, page in enumerate(pages):
        page.hashroot = hashes[i]["root"]
        page.hashleafs = hashes[i]["leafs"]

        print("Page: ", page,"\n")

    writer.addpages(pages)

    return writer

#Save the PDf 
def savePDF(writer):
    writer.write()

    return

# Get all the data within the file
def getAllData(path = "", saveName = ""):
    if path == "":
        return
    
    pdf = pdfrw.PdfReader(path)
    keys = pdf.keys()
    info = pdf.Info
    rootKeys = pdf.Root.keys()
    # print("Keys: ",keys,"\n")
    # print("Info: ",info,"\n")
    # print("Root Keys: ",rootKeys,"\n")

    filePageObjects = getFilePageObjects(path)
    hashes = calculateHashValues(filePageObjects)

    if saveName == "":
        saveName = path.replace('.pdf',"_hash.pdf") 

    writer = pdfrw.PdfWriter(saveName)
    writer = insertHashValues(writer, filePageObjects, hashes)
    savePDF(writer)


    filePageObjects2 = getFilePageObjects(saveName)
    hashes2 = calculateHashValues(filePageObjects2)
    hashes3 = getHashValues(filePageObjects2)
    print(hashes2)
    print(hashes3)


# Protect the PDF against tampering
def protectPDF(path = "", saveName = ""):
    if path == "":
        print("Invalid Path Provided")
        return
    
    pdf = pdfrw.PdfReader(path)
    keys = pdf.keys()
    info = pdf.Info
    rootKeys = pdf.Root.keys()
    # print("Keys: ",keys,"\n")
    # print("Info: ",info,"\n")
    # print("Root Keys: ",rootKeys,"\n")

    filePageObjects = getFilePageObjects(path)
    hashes = calculateHashValues(filePageObjects)

    if saveName == "":
        saveName = path.replace('.pdf',"_hash.pdf") 

    writer = pdfrw.PdfWriter(saveName)
    writer = insertHashValues(writer, filePageObjects, hashes)
    savePDF(writer)

# Assess if the PDF has been tampered with
def assessForForgery(path = ""):
    if path == "":
        print("Invalid Path Provided")
        return
    
    filePageObjects2 = getFilePageObjects(path)
    hashes2 = calculateHashValues(filePageObjects2)
    hashes3 = getHashValues(filePageObjects2)
    print(hashes2)
    print(hashes3)
    print(hashes2 == hashes3)


#Main function
if __name__ == '__main__':
    path = './Test_PDFS/simplePDF.pdf'
    pathForg = './Test_PDFS/simplePDF_hash.pdf'

    # getAllData(path)

    protectPDF(path)

    assessForForgery(pathForg)
    
