"""
    I am using two pdf libraries -
      1) pypdf2 because for some reason it couldn't read document text correctly but could edit metadata (add new key value pairs);
      2) fitz because it could read the document as expected but couldn't add new metadata (although it was possible to edit existing metadata key values).

    The program contains both:
      document signing (Alice) and 
      received document signature validation (Bob).
    
    The document kino_msg.pdf is given in the zip archive.
    
    The program creates signed document result.pdf which holds the signature and the public key created by Alice which later is validated
      by Bob using the received public key (from pdf metadata) and the created md5 hash which he creates from the document text (KINO with a line feed).

    Author: Audris Arzovs aa17083
"""

from PyPDF2 import PdfFileReader, PdfFileWriter
import fitz
import hashlib

############################# Alice ###########################
# Get document text
doc = fitz.open('kino_msg.pdf')
page = doc[0]
text = page.get_text()

# RSA parameter calculation
p = 59
q = 61

n = p * q # 3599

z = (p - 1) * (q - 1) # 3480

d = 271

e = 2671
# Loop to find the value of e
# for i in range(0, 3000):
#   if (i*d)%z == 1:
#       print(i)
#       break

# MD5 hash creation from document text "KINO"
md5 = hashlib.md5(text.encode()).hexdigest()

# Encode md5 hash using RSA
MD5Cypher = []
for character in md5:
    MD5Cypher.append(pow(ord(character), d)%n)

# Signed document creation
fin = open('kino_msg.pdf', 'rb')
reader = PdfFileReader(fin)

writer = PdfFileWriter()

writer.appendPagesFromReader(reader)
metadata = reader.getDocumentInfo()
writer.addMetadata(metadata)

# Add signature and public key information
writer.addMetadata({
    '/MD5_signature': str(MD5Cypher)[1:-1],
    "/Public_key": str(e) + ", " + str(n)
})

fout = open('result.pdf', 'wb')
writer.write(fout)

fout.close()
fin.close()
doc.close()

########################### Bob ###########################
# Open the signed document
fp = open('result.pdf', 'rb')
reader_check = PdfFileReader(fp)

# Get the document metadata
metadata = reader_check.getDocumentInfo()

# Get the text of the document
doc = fitz.open('result.pdf')
page = doc[0]
text = page.get_text()

# Read the document signature and the public key
md5_to_check = []
rcv_pb = []
for k in metadata:
    if k == "/MD5_signature":
        md5_to_check = metadata[k].split(", ")
    elif k == "/Public_key":
        rcv_pb = metadata[k].split(", ")
        rcv_pb[0] = int(rcv_pb[0]) # e
        rcv_pb[1] = int(rcv_pb[1]) # n

md5_val = ""
for k in md5_to_check:
    md5_val += chr(pow(int(k), rcv_pb[0])%rcv_pb[1])

# MD5
# Create hash from the document text
md5_to_check_with = hashlib.md5(text.encode()).hexdigest()

print("")
print("======================================================")
if md5_val == md5_to_check_with:
    print("MD5: Received document signed by Alice.")
else:
    print("MD5: Received document signed by someone else.")

print("Decoded hash: " + str(md5_val))
print("Created hash: " + str(md5_to_check_with))
print("======================================================")
print("")

fp.close()
doc.close()
