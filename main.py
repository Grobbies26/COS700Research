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

#Standard encode the root object to later use for hashing
def standardEncodeRoot(obj):
    kidsString = ""
    for kid in obj.Pages.Kids:
        kidsString += json.dumps(kid.Type) + json.dumps(kid.MediaBox) + json.dumps(kid.Contents) + json.dumps(kid.hashobject.replace("(","").replace(")","")) + json.dumps(kid.hashroot.replace("(","").replace(")",""))

    values = json.dumps(obj.Type) + json.dumps(obj.Pages.Type) + json.dumps(obj.Pages.Count) + kidsString

    return values

#Standard encode the info object to later use for hashing
def standardEncodeInfo(obj):
    values = json.dumps(obj.Creator) + json.dumps(obj.Producer) + json.dumps(obj.CreationDate) + json.dumps(obj.ModificationDate) + json.dumps(obj.Title) + json.dumps(obj.Author) + json.dumps(obj.Subject) + json.dumps(obj.Keywords) + json.dumps(obj.CreatorTool) + json.dumps(obj.PDFFormatVersion) + json.dumps(obj.RenditionClass) + json.dumps(obj.Trapped) + json.dumps(obj.PDFVersion)
    
    return values


#Strip objects of stored hashes before computing
def stripHashes(filePageObjects = []):
    for i, page in enumerate(filePageObjects):
        del page["/hashobject"]
        del page["/hashroot"]
        del page["/hashleafs"]

    return filePageObjects

#Strip root object of stored hashes before computing
def stripRootHashes(root = {}):
    del root["/hashinfo"]
    del root["/hashroot"]

    return root


#Calculate the Hash Values for the PDF
def calculateHashValues(filePageObjects = [], strip = False):
    if filePageObjects == []:
        raise Exception("No file page objects provided")


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

#Calculate Root Hash Values for the PDF
def calculateRootHashValues(root = {}, info = {}, strip = False):
    if root == {}:
        raise Exception("No root object provided")
    
    if info == {}:
        raise Exception("No metadata object provided")

    if strip:
        root = stripRootHashes(root)

    encoded = standardEncodeRoot(root)
    hroot = hashlib.sha256(encoded.encode('utf-8')).hexdigest()

    encoded = standardEncodeInfo(info)
    hinfo = hashlib.sha256(encoded.encode('utf-8')).hexdigest()

    hash = {"root": hroot,"info": hinfo}

    return hash


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

#Retrieve the previously stored Root Hash Values
def getRootHashValues(root = {}):
    if root == {}:
        raise Exception("No root object provided")
    
    hinfo = root.hashinfo.replace("(","").replace(")","")
    hroot = root.hashroot.replace("(","").replace(")","")

    return {"root": hroot,"info": hinfo}

#Insert the Hash Values into the PDF
def insertHashValues(writer, pages=[], hashes = []):
    if hashes == [] or pages == []:
        raise Exception("No hashes or pages provided")
    
    for i, page in enumerate(pages):
        page.hashobject = hashes[i]["object"]
        page.hashroot = hashes[i]["root"]
        page.hashleafs = hashes[i]["leafs"]

    writer.addpages(pages)

    return writer


#Get the file page objects for the PDF
def getFilePageObjects(pdf = {}):
    if pdf == {}:
        raise Exception("Invalid PDF provided")
    
    filePageObjects = pdf.pages

    return filePageObjects


#Save the PDf 
def savePDF(writer):
    writer.write()

    return


# Protect the PDF against tampering
def protectPDF(path = ""):
    if path == "":
        print("Invalid Path Provided")
        return

    try:
        pdf = pdfrw.PdfReader(path)
        savePath = path.replace('.pdf',"_hash.pdf") 
    except:
        print("Invalid Path Provided")
        return

    try:
        #Extract the file page objects and use them to calculate the hash values
        filePageObjects = getFilePageObjects(pdf)
        fpg = filePageObjects
        hashes = calculateHashValues(fpg)

        #Create new PDF to write out and copy the old root over
        writer = pdfrw.PdfWriter(savePath)
        writer.trailer.Root = pdf.Root

        #Insert the hash values into the PDF as well as previous metadata
        writer = insertHashValues(writer, filePageObjects, hashes)
        writer.trailer.Info = pdf.Info
        writer.trailer.ID = pdf.ID
        writer.trailer.Size = pdf.Size
        writer.trailer.Encrypt = pdf.Encrypt

        #Extract the root values and use them to calculate the hash value for the root, as well as the metadata
        root = writer.trailer.Root
        rootHash = calculateRootHashValues(root, writer.trailer.Info)
        writer.trailer.Root.hashroot = rootHash["root"]
        writer.trailer.Root.hashinfo = rootHash['info']

        #Write PDF to file
        savePDF(writer)
        print(f"PDF Protected successfully, and saved to {savePath}")

    except Exception as err:
        print("There was an error protecting the PDF: ", err)
        return
    finally:
        print("Process Completed")
        return
    

# Assess if the PDF has been tampered with
def assessForForgery(path = ""):
    if path == "":
        print("Invalid Path Provided")
        return

    try:
        pdf = pdfrw.PdfReader(path)
    except:
        print("Invalid Path Provided")
        return
    
    try:
        #Calculate and retrieve all hash values in PDF
        filePageObjects = getFilePageObjects(pdf)
        storedRootHashValues = getRootHashValues(pdf.Root)
        storedHashValues = getHashValues(filePageObjects)
        calculatedRootHashValues = calculateRootHashValues(pdf.Root, pdf.Info, True)
        calculatedHashValues = calculateHashValues(filePageObjects, True)

        #Compare the hash values to determine if the PDF has been tampered with
        compareHashes(calculatedHashValues, storedHashValues, calculatedRootHashValues, storedRootHashValues)
    except Exception as err:
        print("There was an error assessing the PDF: ", err)
        return
    finally:
        print("Process Completed")
        return

    
# Compare the hashes objects to determine equality
def compareHashes(calculated = [], stored = [], rootC = {}, rootS={}):
    if calculated == [] or stored == []:
        raise Exception("Hashes could not be compared as one set is empty")

    if calculated == stored and rootC == rootS:
        print("Hashes are equal, no tampering detected")
        
        print("\nHashes used to make comparison:")
        print("Stored Root Hashes: ",rootS)
        print("Computed Root Hashes: ",rootC)
        print("Stored Page Hashes: ",stored)
        print("Computed Page Hashes: ",calculated)

        return

    print("Hashes are not equal, alterations detected: \n")
    if rootS["root"] != rootC["root"]:
        print("Root Hashes are not equal, root object has been altered")
    if rootS["info"] != rootC["info"]:
        print("Info Hashes are not equal, metadata has changed")

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

    print("\nHashes used to make comparison:")
    print("Stored Root Hashes: ",rootS)
    print("Computed Root Hashes: ",rootC)
    print("Stored Page Hashes: ",stored)
    print("Computed Page Hashes: ",calculated)

    return



#Main function
if __name__ == '__main__':
    patha = './Test_PDFS/simplePDF.pdf'
    pathb = './Test_PDFS/AdobeTest.pdf'
    pathc = './Test_PDFS/test.pdf'
    # path = './Test_PDFS/test.pdf'
    pathForga = './Test_PDFS/simplePDF_hash.pdf'
    pathForgb = './Test_PDFS/AdobeTest_hash.pdf'
    pathForgc = './Test_PDFS/test_hash.pdf'
    pathForg = './Test_PDFS/t.pdf'

    # protectPDF(path)
    # assessForForgery(pathForg)

    # protectPDF(patha)
    # assessForForgery(pathForga)

    # protectPDF(pathb)
    # assessForForgery(pathForgb)

    protectPDF(pathc)
    assessForForgery(pathForgc)
    
