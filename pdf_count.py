import re, PyPDF2


def get_words_count(path):
    
    pdf = open(path,'rb')
    pdfReader = PyPDF2.PdfFileReader(pdf)
    num_pages = pdfReader.numPages

    words_count = 0
    for num_page in range(num_pages):
        single_page = pdfReader.getPage(num_page)
        text = single_page.extractText()
        words = re.findall(r"[^\W_]+", text, re.MULTILINE) 
        words_count += len(words)
    
    return {path:words_count}

        
print(get_words_count(""))

        
    


