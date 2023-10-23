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
        if page.hashobject == None or page.hashroot == None or page.hashleafs == None:
            raise Exception("No hash values found in PDF")
        obj = page.hashobject.replace("(","").replace(")","")
        root = page.hashroot.replace("(","").replace(")","")
        leafs = [val.replace("(","").replace(")","") for val in page.hashleafs]
        hashes.append({"object":obj,"root":root,"leafs":leafs})

    return hashes

#Retrieve the previously stored Root Hash Values
def getRootHashValues(root = {}):
    if root == {}:
        raise Exception("No root object provided")
    

    if root.hashinfo == None or root.hashroot == None:
        raise Exception("No hash values found in PDF")
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
        print(F"Protecting: {path}")

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
        print(F"Assessing: {path}")

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
        print("Process Completed\n")
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
        for j in range(len(ca["leafs"])):
            if st["leafs"][j] != ca["leafs"][j]:
                print(f"Changes detected in the {j} th 256 bytes of the content stream")

    print("\nHashes used to make comparison:")
    print("Stored Root Hashes: ",rootS)
    print("Computed Root Hashes: ",rootC)
    print("Stored Page Hashes: ",stored)
    print("Computed Page Hashes: ",calculated)

    return


# Function to run all tests
def testAllPDFs(protect = False):
    if protect:
        protectTestPDFs()
    assessTestPDFs()
    return

#Protect all of the test PDFs
def protectTestPDFs():
    pathTextSA = "./Test_PDFs/TextSA.pdf"
    pathTextMA = "./Test_PDFs/TextMA.pdf"
    pathTextSU = "./Test_PDFs/TextSU.pdf"
    pathTextMU = "./Test_PDFs/TextMU.pdf"
    pathTextSD = "./Test_PDFs/TextSD.pdf"
    pathTextMD = "./Test_PDFs/TextMD.pdf"
    pathTextC  = "./Test_PDFs/TextC.pdf"

    pathImageSA = "./Test_PDFs/ImageSA.pdf"
    pathImageMA = "./Test_PDFs/ImageMA.pdf"
    pathImageSU = "./Test_PDFs/ImageSU.pdf"
    pathImageMU = "./Test_PDFs/ImageMU.pdf"
    pathImageSD = "./Test_PDFs/ImageSD.pdf"
    pathImageMD = "./Test_PDFs/ImageMD.pdf"
    pathImageC  = "./Test_PDFs/ImageC.pdf"

    pathMetaSU = "./Test_PDFs/MetaSU.pdf"
    pathMetaMU = "./Test_PDFs/MetaMU.pdf"
    pathMetaSD = "./Test_PDFs/MetaSD.pdf"
    pathMetaMD = "./Test_PDFs/MetaMD.pdf"
    pathMetaC  = "./Test_PDFs/MetaC.pdf"

    pathCAll  = "./Test_PDFs/CAll.pdf"
    
    protectPDF(pathTextSA)
    protectPDF(pathTextMA)
    protectPDF(pathTextSU)
    protectPDF(pathTextMU)
    protectPDF(pathTextSD)
    protectPDF(pathTextMD)
    protectPDF(pathTextC)

    protectPDF(pathImageSA)
    protectPDF(pathImageMA)
    protectPDF(pathImageSU)
    protectPDF(pathImageMU)
    protectPDF(pathImageSD)
    protectPDF(pathImageMD)
    protectPDF(pathImageC)

    protectPDF(pathMetaSU)
    protectPDF(pathMetaMU)
    protectPDF(pathMetaSD)
    protectPDF(pathMetaMD)
    protectPDF(pathMetaC)

    protectPDF(pathCAll)

    return

# Assess all of the test PDFs
def assessTestPDFs():
    pathNoHash = "./Test_PDFs/NoHash.pdf"

    pathTextSA = "./Test_PDFs/TextSA_hash.pdf"
    pathTextMA = "./Test_PDFs/TextMA_hash.pdf"
    pathTextSU = "./Test_PDFs/TextSU_hash.pdf"
    pathTextMU = "./Test_PDFs/TextMU_hash.pdf"
    pathTextSD = "./Test_PDFs/TextSD_hash.pdf"
    pathTextMD = "./Test_PDFs/TextMD_hash.pdf"
    pathTextC  = "./Test_PDFs/TextC_hash.pdf"

    pathImageSA = "./Test_PDFs/ImageSA_hash.pdf"
    pathImageMA = "./Test_PDFs/ImageMA_hash.pdf"
    pathImageSU = "./Test_PDFs/ImageSU_hash.pdf"
    pathImageMU = "./Test_PDFs/ImageMU_hash.pdf"
    pathImageSD = "./Test_PDFs/ImageSD_hash.pdf"
    pathImageMD = "./Test_PDFs/ImageMD_hash.pdf"
    pathImageC  = "./Test_PDFs/ImageC_hash.pdf"

    pathMetaSU = "./Test_PDFs/MetaSU_hash.pdf"
    pathMetaMU = "./Test_PDFs/MetaMU_hash.pdf"
    pathMetaSD = "./Test_PDFs/MetaSD_hash.pdf"
    pathMetaMD = "./Test_PDFs/MetaMD_hash.pdf"
    pathMetaC  = "./Test_PDFs/MetaC_hash.pdf"

    pathCAll  = "./Test_PDFs/CAll_hash.pdf"

    assessForForgery(pathNoHash)

    assessForForgery(pathTextSA)
    assessForForgery(pathTextMA)
    assessForForgery(pathTextSU)
    assessForForgery(pathTextMU)
    assessForForgery(pathTextSD)
    assessForForgery(pathTextMD)
    assessForForgery(pathTextC)

    assessForForgery(pathImageSA)
    assessForForgery(pathImageMA)
    assessForForgery(pathImageSU)
    assessForForgery(pathImageMU)
    assessForForgery(pathImageSD)
    assessForForgery(pathImageMD)
    assessForForgery(pathImageC)

    assessForForgery(pathMetaSU)
    assessForForgery(pathMetaMU)
    assessForForgery(pathMetaSD)
    assessForForgery(pathMetaMD)
    assessForForgery(pathMetaC)

    assessForForgery(pathCAll)

    return


test = False
protect = False
#Main function
if __name__ == '__main__':
    
    if test:
        testAllPDFs(protect)

    protect = input("Would you like to protect a PDF? (y/n): ")
    if protect == "y":
        path = input("Enter the path to the PDF you would like to protect: ")
        protectPDF(path)

    assess = input("Would you like to assess a PDF for tampering? (y/n): ")
    if assess == "y":
        path = input("Enter the path to the PDF you would like to assess: ")
        assessForForgery(path)
