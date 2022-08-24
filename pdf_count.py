import re, PyPDF2


def get_words_count(path: str ) -> dict:
    
    '''
    Function for counting number of pages and words in single PDF document. 
    Returns results in form of dict containing PDF id (as a key) and number of pages and words (in list)
    ex. {id123: [12, 1234]}
    '''
    
    pdf = open(path,'rb')
    pdfReader = PyPDF2.PdfFileReader(pdf)
    num_pages = pdfReader.numPages

    words_count = 0
    for num_page in range(num_pages):
        single_page = pdfReader.getPage(num_page)
        text = single_page.extractText()
        words = re.findall(r"[^\W_]+", text, re.MULTILINE) 
        words_count += len(words)
    
    return {path:[num_pages, words_count]}

        
print(get_words_count("699ecc0a-4927-47b3-a1bd-341f86fa9735.pdf"))

        
    


