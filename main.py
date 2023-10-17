# Gabriel Grobler Research Project

import pdfrw
import hashlib
import json
from merkly.mtree import MerkleTree

#Standard encode an object to later use for hashing
def standardEncodeObj(obj):
    if obj.Parent:
        j = -1
        for i, kid in enumerate(obj.Parent.Kids):
            if kid is obj:
                j=i
                continue
            if "/Parent" in obj.Parent.Kids[i]:
                del obj.Parent.Kids[i]["/Parent"]
        if j != -1:
            obj.Parent.Kids.pop(j)

    # values = json.dumps(obj.Type) + json.dumps(obj.Parent) + json.dumps(obj.MediaBox) + json.dumps(obj.Resources) + json.dumps(obj.Annots) + json.dumps(obj.Contents)
    values = json.dumps(obj.Type) + json.dumps(obj.Contents) + json.dumps(obj.MediaBox)
    
    return values

#Strip objects of stored hashes before computing
def stripHashes(filePageObjects = []):
    for i, page in enumerate(filePageObjects):
        del page["/hashobject"]
        del page["/hashroot"]
        del page["/hashleafs"]

    return filePageObjects

#Calculate the Hash Values for the PDF
def calculateHashValues(filePageObjects = [], strip = False):
    if filePageObjects == []:
        return

    if strip:
        filePageObjects = stripHashes(filePageObjects)

    content = []
    hashes = []
    w = 256

    for j, page in enumerate(filePageObjects): 
        content = [page.Contents.stream[i:i + w] for i in range(0, len(page.Contents.stream), w)]

        tree = MerkleTree(content)

        encoded = standardEncodeObj(page)
        pObject = hashlib.sha256(encoded.encode('utf-8')).hexdigest()

        hash = {"object": pObject,"root": tree.root, "leafs": tree.leafs}
        hashes.append(hash)

    return hashes

#Retrieve the previously stored Hash Values
def getHashValues(filePageObjects = []):
    if filePageObjects == []:
        return
    
    hashes = []
    for i, page in enumerate(filePageObjects):
        obj = page.hashobject.replace("(","").replace(")","")
        root = page.hashroot.replace("(","").replace(")","")
        leafs = [val.replace("(","").replace(")","") for val in page.hashleafs]
        hashes.append({"object":obj,"root":root,"leafs":leafs})

    return hashes

#Get the file page objects for the PDF
def getFilePageObjects(pdf_path = ""):
    if pdf_path == "":
        return
    
    pdf = pdfrw.PdfReader(pdf_path)
    filePageObjects = pdf.pages
    print(pdf.Info)
    print(pdf.Root)

    return filePageObjects

#Insert the Hash Values into the PDF
def insertHashValues(writer, pages=[], hashes = []):
    if hashes == [] or pages == []:
        return
    
    for i, page in enumerate(pages):
        page.hashobject = hashes[i]["object"]
        page.hashroot = hashes[i]["root"]
        page.hashleafs = hashes[i]["leafs"]

    writer.addpages(pages)

    return writer

#Save the PDf 
def savePDF(writer):
    writer.write()

    return

# Protect the PDF against tampering
def protectPDF(path = "", savePath = ""):
    if path == "":
        print("Invalid Path Provided")
        return

    pdf = pdfrw.PdfReader(path)
    keys = pdf.keys()
    info = pdf.Info
    rootKeys = pdf.Root.keys()
    # print(pdf.Root)
    # print("Keys: ",keys,"\n")
    # print("Info: ",info,"\n")
    # print("Root Keys: ",rootKeys,"\n")

    filePageObjects = getFilePageObjects(path)
    fpg = filePageObjects
    hashes = calculateHashValues(fpg)

    if savePath == "":
        savePath = path.replace('.pdf',"_hash.pdf") 

    writer = pdfrw.PdfWriter(savePath,trailer=pdf.Info)
    writer = insertHashValues(writer, filePageObjects, hashes)
    writer.trailer.Info = pdf.Info
    savePDF(writer)

    writera = pdfrw.PdfWriter("./Test_PDFs/t.pdf", trailer=pdf)
    savePDF(writera)


# Assess if the PDF has been tampered with
def assessForForgery(path = ""):
    if path == "":
        print("Invalid Path Provided")
        return

    filePageObjects = getFilePageObjects(path)
    storedHashValues = getHashValues(filePageObjects)
    calculatedHashValues = calculateHashValues(filePageObjects, True)

    compareHashes(calculatedHashValues, storedHashValues)

# Compare the hashes objects to determine equality
def compareHashes(calculated = [], stored = []):
    print("Hashes To make comparison:")
    print("Computed Hashes: ",calculated)
    print("Stored Hashes: ",stored)

    if calculated == [] or stored == []:
        print("Hashes could not be compared as one set is empty")
        return

    if calculated == stored:
        print("Hashes are equal, no tampering detected\n")
        return

    print("Hashes are not equal, tampering detected")
    for i in range(len(stored)):
        st = stored[i]
        ca = calculated[i]
        if st["object"] != ca["object"]:
            print(f"Object Hashes are not equal for page: {i+1}")
        if st["root"] != ca["root"]:
            print(f"Root Hashes are not equal for page: {i+1}")
        for j in range(len(st["leafs"])):
            if st["leafs"][j] != ca["leafs"][j]:
                print(f"Changes detected in the {j} th 256 bytes of the content stream")

    return



#Main function
if __name__ == '__main__':
    patha = './Test_PDFS/simplePDF.pdf'
    pathb = './Test_PDFS/AdobeTest.pdf'
    # pathc = './Test_PDFS/test.pdf'
    path = './Test_PDFS/test.pdf'
    pathForga = './Test_PDFS/simplePDF_hash.pdf'
    pathForgb = './Test_PDFS/AdobeTest_hash.pdf'
    pathForgc = './Test_PDFS/test_hash.pdf'
    pathForg = './Test_PDFS/t.pdf'

    protectPDF(path)
    # assessForForgery(pathForg)
    assessForForgery(pathForgc)

    # protectPDF(patha)
    # assessForForgery(pathForga)

    # protectPDF(pathb)
    # assessForForgery(pathForgb)
    
