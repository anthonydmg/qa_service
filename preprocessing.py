from operator import itemgetter
import nltk
import re
import fitz

try:
    nltk.data.find("tokenizers/punkt")
except LookupError:
    nltk.download("punkt")

class PreProcessorPDF:
    def __init__(self):
        pass
    def extract_headings(self, doc_pdf):
        headings_pages = {}
        subHeading_pages = {}
        for idx , page in enumerate(doc_pdf):
            blocks = page.get_text('dict')['blocks']
            blocks = [ block for block in blocks if block['type'] == 0] ## contienes texto
            font_counts = {}
            for b in blocks:
                for line in b['lines']:
                    for s in line['spans']:
                        id = round(s['size'],2)
                        font_counts[id] = font_counts.get(id, 0) + 1

            font_counts = sorted(font_counts.items(), key=itemgetter(1), reverse=True)
            normal_size = font_counts[0][0]
            subheadings = []
            headings = []
            for b in blocks:
                ## Find sub headings
                prev_sub_mean_sizes = None
                prev_is_sub = False
            
                prev_head_mean_sizes = None
                prev_is_head = False
            

                for line in b['lines']:
                    subhead= ""
                    head = ""
                    spans_bold = [s for s in line['spans'] if ("-Bold"  in s['font']) and s['text'].strip()]
                    sizes = [s['size'] for s in spans_bold]
                    if len(sizes) == 0: 
                        continue 
                    mean_sizes = sum(sizes) / len(sizes)
                    texts = [ s['text'] for s in spans_bold ]
                    
                    if len(texts) < len(line['spans']):
                        continue

                    if len(sizes) > 0 and (mean_sizes >=  normal_size - 0.5) and  (mean_sizes <=  normal_size + 1.0):
                        #Subheadning
                        subhead = " ".join(texts)
                        prev_sub_mean_sizes = mean_sizes
                    elif len(sizes) > 0 and (mean_sizes >  normal_size + 1.0):
                        #headning
                        head = " ".join(texts)
                        prev_head_mean_sizes = mean_sizes

                    if subhead!= "":
                            if prev_is_sub and prev_sub_mean_sizes and round(prev_sub_mean_sizes,2) == round(mean_sizes,2):
                                subhead = subheadings[-1] + " " + subhead.strip()
                                subheadings = subheadings[:-1]
                            subheadings.append(subhead.strip())
                            prev_is_sub = True
                    else:
                        prev_is_sub = False
                        prev_sub_mean_sizes = None
                    
                    if head!= "":
                            if prev_is_head and prev_head_mean_sizes and round(prev_head_mean_sizes,2) == round(mean_sizes,2):
                                head = headings[-1] + " " + head.strip()
                                headings = headings[:-1]
                            headings.append(head.strip())
                            prev_is_head = True
                    else:
                        prev_is_head = False
                        prev_head_mean_sizes = None

                ## Find sub headings

            ## Clean no subheadings
            subheadings = [sub for sub in subheadings if not re.search('Art.', sub)] # Delete Arts
            subheadings = [sub for sub in subheadings if not re.search(':$', sub)] # Delete Inline Subtities
            subheadings = [sub for sub in subheadings if not re.search('\.$', sub)] # Delete bold text
            subheadings = [sub for sub in subheadings if not re.search(',$', sub)] # Delete bold text
            subheadings = [sub for sub in subheadings if len(sub)> 5] # Delete bold characters

            subHeading_pages[idx] = subheadings

            headings = self.remove_non_alfanumeric_lines("\n".join(headings)).split("\n")
            headings = self.remove_lines_low_size_word_pages("\n".join(headings)).split("\n")
            headings = [head for head in  headings if not re.search('\.$', head)]
            headings = [head for head in  headings if len(head)> 3]
            headings_pages[idx] = headings
        return headings_pages, subHeading_pages
    
    def remove_non_alfanumeric_lines(self, text):
        lines = text.splitlines();
        cleaned_lines = []
        for line in lines:
            words = nltk.tokenize.word_tokenize(line, language = "spanish")
            alfnum = [word for word in words if word.isalnum()]

            # remove lines having < 40% of non alfanumeric tokens
            if words and len(alfnum) / len(words) <= 0.4:
                    continue
            cleaned_lines.append(line)
        clean_text = "\n".join(cleaned_lines)
        return clean_text
    
    def remove_lines_low_size_word_pages(self, text):
        pages = text.split('\f')
        cleaned_pages = []
        for page in pages:
            lines = page.splitlines()
            cleaned_lines = []
            for line in lines:
                words = line.split()
                total_chars = sum([len(word) for word in words])

                # remove lines having < 2 mean size of words
                if words and total_chars / len(words) < 2:
                        continue
                cleaned_lines.append(line)

            page = "\n".join(cleaned_lines)
            cleaned_pages.append(page)
        text = "\f".join(cleaned_pages)
        return text

    def remove_numeric_tables(self, text, except_regex = [] ):
        pages = text.split('\f')
        cleaned_pages = []
        for page in pages:
            # pdftotext tool provides an option to retain the original physical layout of a PDF page. This behaviour
            # can be toggled by using the layout param.
            #  layout=True
            #      + table structures get retained better
            #      - multi-column pages(eg, research papers) gets extracted with text from multiple columns on same line
            #  layout=False
            #      + keeps strings in content stream order, hence multi column layout works well
            #      - cells of tables gets split across line
            #
            #  Here, as a "safe" default, layout is turned off.
            lines = page.splitlines()
            cleaned_lines = []
            for line in lines:
                if except_regex and any([re.search(pattern, line) for pattern in except_regex]):
                    cleaned_lines.append(line)
                    continue
                
                words = nltk.tokenize.word_tokenize(line, language = "spanish")
                digits = [word for word in words if any(i.isdigit() for i in word)]

                # remove lines having > 40% of words as digits AND not ending with a period(.)
                if words and len(digits) / len(words) > 0.4 and not line.strip().endswith("."):
                        continue
                cleaned_lines.append(line)

            page = "\n".join(cleaned_lines)
            cleaned_pages.append(page)
            text = "\f".join(cleaned_pages)
        return text

    def remove_non_alfanumeric_lines(self, text):
        lines = text.splitlines();
        cleaned_lines = []
        for line in lines:
            words = nltk.tokenize.word_tokenize(line, language = "spanish")
            alfnum = [word for word in words if word.isalnum()]

            # remove lines having < 40% of non alfanumeric tokens
            if words and len(alfnum) / len(words) <= 0.4:
                    continue
            cleaned_lines.append(line)
        clean_text = "\n".join(cleaned_lines)
        return clean_text

    def fix_splitted_passages(self, text):
        lines = text.splitlines()
        lines = [line.strip() for line in lines if line.strip() != '']
        new_lines = []
        new_line = ''
        for idx, line in enumerate(lines):
            line = line.strip()
            new_line = " ".join([new_line, line])
            
            if (line[-1])=='.':
                new_line = new_line.strip()
                new_line = new_line.replace('\n*',' ')
                new_lines.append(new_line)
                new_line = ''
                
            if (idx == (len(lines) - 1)) and (new_line != ''):
                new_line = new_line.strip()
                new_line = new_line.replace('\n*',' ')
                new_lines.append(new_line)
        new_page = "\n".join(new_lines)
        return new_page

    def get_match_spans(self, text, patterns = []):
        spans = []
        for p in patterns:
            match = re.search(p, text)
            if match: 
                text_span = {'text': p, 'span': [match.start(), match.end()]}
                spans.append(text_span)
        return spans

    def clean_page(self, text):
        header_uni = 'UNIVERSIDAD NACIONAL DE INGENIERIA \n'
        # Remover Header UNI
        text = text.replace(header_uni, '')
        # Remove header characters
        text = re.sub(r'~?J\'?Vo-?\.*\s?.*\n\d*\n?','\n',text)
        text = text.replace('~ ','')
        # Remove Footer pages
        text = re.sub(r'Página \d+ de \d+','',text)
        # Remove special character
        text = re.sub(r'\x0c[A-Z]','',text)
        ## Remove numeric tables
        text = self.remove_numeric_tables(text, except_regex = ['CAPÍTULO \d*', 'ANEXO \d*'])
        ## Remove lines with many non alfanumic charaters
        text = self.remove_non_alfanumeric_lines(text)
        # Fix passages splitead in the middle of an sentences
        text = self.fix_splitted_passages(text)
        
        return text
    
    def split_pages_by_headings(self, pages, headings_pages, subHeading_pages):
        documents = []
        for idx, page in enumerate(pages):
            heads = headings_pages[idx]

            docs_by_heads = [{'text': page,
                            'heading': None, 
                            'subheadings' : [] }]
            concat_first_to_prev = True
            ## Split pages by headings
            for head in heads:
                head = head.replace('  ',' ')
                last_doc = docs_by_heads[-1]['text'].strip()
                match = re.search(head, last_doc)
                if match: 
                    if match.start() == 0: # head in the start of the page
                        concat_first_to_prev = False
                        docs_by_heads[-1]['heading'] = {'text': head, 'span': [match.start(), match.end()]}
                    else: 
                        docs_by_heads[-1]['text'] = last_doc[0: match.start()-1].strip()
                        docs_by_heads.append({
                            'text': last_doc[match.start():].strip(), 
                            'heading': { 
                                'text': head, 
                                'span':[ 0, match.end() - match.start() ]
                            }, 
                            'subheadings':[]
                            })         

            ## Save subheading by docs
            subheads = subHeading_pages[idx]
            subheads = [sub.replace('  ',' ') for sub in subheads]
            for d in docs_by_heads:
                subheads_indoc = self.get_match_spans(d['text'], subheads)
                subs = []
                prev_end_span = 0
                ## CONCATENERAR CONTIGUOS SUBHEADS
                for subh in subheads_indoc:
                    if subh['span'][0] == (prev_end_span + 1):
                        subs[-1]['text'] = subs[-1]['text'] + " "  + subh['text']
                        subs[-1]['span'] = [subs[-1]['span'][0], subs[-1]['span'][0] + len(subs[-1]['text'])]
                    else:
                        subs.append(subh)
                    prev_end_span = subh['span'][1]
        
                d['subheadings'].extend(subs)
            if idx == 0: # First page
                documents.extend(docs_by_heads)
            else: 
                ## Concat first part to previus document
                if concat_first_to_prev:
                    prev_doc = documents[-1]['text'].strip()
                    documents[-1]['text'] = prev_doc + " " + docs_by_heads[0]['text'].strip()
                    ## Corregir el spand
                    subheads = docs_by_heads[0]['subheadings']
                    for subhead in subheads:
                        span = subhead['span'] 
                        subhead['span'][0] = len(prev_doc) + span[0] + 1
                        subhead['span'][1] = len(prev_doc) + span[1] + 1
                    documents[-1]['subheadings'] = documents[-1]['subheadings'] + subheads
                    docs_by_heads = docs_by_heads[1:]
                ## Append  docs
                documents.extend(docs_by_heads)
        return documents

    def split_by_subheads(self, doc):
        subheads = doc['subheadings']
        
        if len(subheads) == 0:
            return [doc]

        text = doc['text']
        heading = doc['heading']

        first_subhead = subheads[0]
        span_subhead = first_subhead['span']
        span_head = heading['span']
        
        doc_splits = []
        if (span_head[1] + 1) != span_subhead[0]:  # if head is no contiguos to subhead
            sub_doc = {
                'text': text[0: span_subhead[0] - 1],
                'heading': heading,
                'subheadings': []
                }
            doc_splits.append(sub_doc)
        for idx , sub in enumerate(subheads):
            current_span = sub['span']

            if idx == len(subheads) -1: ## Last Subhead
                sub_doc_text = text[current_span[0]:]
            else:
                next_span = subheads[idx + 1] ['span']
                sub_doc_text = text[current_span[0] : next_span[0] - 1]
            
            ## Add head in the start
            sub_doc_text = heading['text'] + " " + sub_doc_text
            sub_doc = {
            'text': sub_doc_text,
            'heading': heading,
            'subheadings': [sub]
            }
            
            doc_splits.append(sub_doc)
        
        return doc_splits
    def split_sentences(self, text):
        sentences_tokenzed = nltk.tokenize.sent_tokenize(text, language = "spanish")
        sentences = []
        splitted_sent = ""
        for idx ,sent in enumerate(sentences_tokenzed):
            if re.search('Art\.$', sent) and idx < len(sentences_tokenzed):
                splitted_sent = " ".join([splitted_sent, sent]).strip()
            else:
                if splitted_sent:
                    sent = " ".join([splitted_sent, sent]).strip()
                    splitted_sent = ""
                sentences.append(sent)
        return sentences

    ## Despues generalizar esto
    def split_doc(self, doc, split_length, split_overlap):
        text = doc['text']
        heading = doc['heading']
        subheadings = doc['subheadings'] 
        sentences = self.split_sentences(text)
        
        context_heads =  heading['text'] if heading else ""
        if subheadings:
            context_heads = context_heads + " " + subheadings[0]['text']
        print('context_heads:', context_heads)
        count_word_slice = 0
        text_splits = []
        list_splits = []

        current_split = []
        for sent in sentences:
            count_word_sen = len(sent.split())
            count_word_slice += count_word_sen 
            current_split.append(sent)
            #if count_word_sen > 
            if count_word_slice > split_length:
                list_splits.append(current_split)
                count_word_slice = 0
                n_sent_split = len(current_split)
                if split_overlap > 0 and n_sent_split > 1:
                    cut_idx = len(current_split) - 1
                    #print('cut_idx 1:', cut_idx)
                    for s in reversed(current_split):
                        count_word_slice += len(s.split())
                        if count_word_slice > split_overlap:
                            break
                        cut_idx -= 1
                    #print('cut_idx 2:', cut_idx)
                    if cut_idx != 0:
                        current_split = current_split[cut_idx:]
                        if context_heads: 
                            count_word_slice = len(context_heads.split()) + count_word_slice
                            current_split = [context_heads] + current_split
                    else:
                        current_split = []
                        ## Puede que mejor sea considerarlos en la suma
                        if context_heads:
                            count_word_slice = len(context_heads.split())
                            current_split = [context_heads]
                else:
                    current_split = []
                    count_word_slice = 0
                    if context_heads:
                        count_word_slice = len(context_heads.split())
                        current_split = [context_heads]
            
        if current_split:
            list_splits.append(current_split)

        for ls in list_splits:
            text = " ".join(ls)
            text_splits.append(text)
        return text_splits

    def fix_splitted_sentences_end_pages(self, pages):
        ## Fix Splited sentences in the end pages
        line_to_next_page = None
        fixed_pages = []
        for page in pages:
            page = page.strip('\n')
            if line_to_next_page!= None:
                page = " ".join([line_to_next_page, page])
                line_to_next_page = None
            if(page[-1]) != '.':
                lines = page.splitlines()
                page = "\n".join(lines[:-1])
                line_to_next_page = lines[-1]
            fixed_pages.append(page)
        return fixed_pages

    def process(self, doc_file, split_length = 300, split_overlap = 100):
        doc_pdf = fitz.open(doc_file)
        # headings
        headings_pages, subHeading_pages = self.extract_headings(doc_pdf)
        # clean Pages
        pages = [ self.clean_page(page.get_text()) for page in doc_pdf]
        # Fix passages splitead in the middle of an sentences on the end of pages
        pages = self.fix_splitted_sentences_end_pages(pages)
        ## Split by headings
        documents = self.split_pages_by_headings(pages, headings_pages, subHeading_pages)
        ## Split
        docs_splitted = []
        for doc in documents:
            sub_docs = self.split_by_subheads(doc)
            for d in sub_docs:
                text_splits = self.split_doc(d, split_length, split_overlap)
                docs_splitted.extend(text_splits)
        return docs_splitted