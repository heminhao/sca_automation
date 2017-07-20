#!/usr/bin/python_curr
# coding=utf-8

import sys
import io
import getopt
import logging
import collections as cl
import pdb

from pdfminer.pdfinterp import PDFResourceManager, process_pdf
from pdfminer.pdfdevice import TagExtractor
from pdfminer.converter import PDFConverter
from pdfminer.layout import LAParams, LTContainer, LTText, LTTextBox
from pdfminer.utils import set_debug_logging

class PdfTxtStore(object) :
    
    def __init__(self, t_callback_func_store) :
        self.m_func_store = t_callback_func_store
        self.m_curr_x = -1
        self.m_curr_y = -1
        self.m_curr_w = 0
        # 通过有限状态机及状态转换实现有意义文本的提取
        # 需要两个状态表示，a为行提取状态，b为单词提取状态
        # a状态0：初始状态，待开始
        # a状态1：尺寸名称行的提取，名称行一般以DIM开头
        # a状态2：尺寸标题行的提取，标题行位于名称行的下一行
        # a状态3：尺寸数据行的提取，数据行位于标题行的下一行
        # b状态0：初始状态，待开始
        # b状态1：单词逐字符读取状态
        # b状态由1变成0时（一个单词提取完毕）才处理a状态的变化
        self.m_a_status = 0
        self.m_b_status = 0
        self.m_curr_words = ''
        self.m_curr_words_beg_x = 0
        self.m_curr_words_end_x = 0
        self.m_meas_name = ''
        self.m_head_num = 0
        self.m_head_desc = cl.OrderedDict()
        self.m_sig_data = {}
        self.m_tot_line = 0
        self.m_txt_data = []
        
    def pro_new_word(self, t_ltchar) :
        char_x = t_ltchar.bbox[0]
        char_y = t_ltchar.matrix[5]
        char_w = t_ltchar.adv
        if self.m_a_status == 1 :
            self.m_meas_name = self.m_meas_name + self.m_curr_words
            self.m_curr_words = t_ltchar.get_text()
            self.m_curr_x = char_x
            self.m_curr_y = char_y
            self.m_curr_w = char_w
        elif self.m_a_status == 2 :
            tmp_exist_bit = 0
            for i in range(self.m_head_num) :
                if self.m_head_desc[i]['col_name'] == self.m_curr_words :
                    tmp_exist_bit = 1
                    break
            if tmp_exist_bit == 0 :
                tmp_sig_head = {}
                tmp_sig_head['col_name'] = self.m_curr_words
                tmp_sig_head['beg_x'] = self.m_curr_words_beg_x
                tmp_sig_head['end_x'] = self.m_curr_words_end_x
                self.m_head_desc[self.m_head_num] = tmp_sig_head
                self.m_head_num = self.m_head_num + 1
            self.m_curr_words_beg_x = char_x
            self.m_curr_words_end_x = char_x + char_w
            self.m_curr_words = t_ltchar.get_text()
            self.m_curr_x = char_x
            self.m_curr_y = char_y
            self.m_curr_w = char_w
        elif self.m_a_status == 3 :
            tmp_data_pos = -1
            for i in range(self.m_head_num) :
                if ( ((self.m_curr_words_beg_x>=self.m_head_desc[i]['beg_x']) 
                      and (self.m_curr_words_beg_x<=self.m_head_desc[i]['end_x']))
                     or
                     ((self.m_curr_words_end_x>=self.m_head_desc[i]['beg_x']) 
                      and (self.m_curr_words_beg_x<=self.m_head_desc[i]['end_x'])) ) :
                        tmp_data_pos = i
                        break
            if tmp_data_pos != -1 :
                self.m_sig_data[self.m_head_desc[tmp_data_pos]['col_name']] = self.m_curr_words
            self.m_curr_words_beg_x = char_x
            self.m_curr_words_end_x = char_x + char_w
            self.m_curr_words = t_ltchar.get_text()
            self.m_curr_x = char_x
            self.m_curr_y = char_y
            self.m_curr_w = char_w
    
    
    def save_pdf_char(self, t_ltchar) :
        char_x = t_ltchar.bbox[0]
        char_y = t_ltchar.matrix[5]
        char_w = t_ltchar.adv
        if self.m_b_status == 0 :
            self.m_curr_x = char_x
            self.m_curr_y = char_y
            self.m_curr_w = char_w
            self.m_curr_words = t_ltchar.get_text()
            self.m_b_status = 1
        elif self.m_b_status == 1 :
            if abs(self.m_curr_y-char_y)>1 :
                self.pro_new_line(t_ltchar)
            elif abs(self.m_curr_x+self.m_curr_w-char_x)>3 :
                self.pro_new_word(t_ltchar)
            else :
                self.m_curr_words = self.m_curr_words + t_ltchar.get_text()
                self.m_curr_x = char_x
                self.m_curr_y = char_y
                self.m_curr_w = char_w
        else :
            raise Exception("internal err")

class ScaConverter(PDFConverter):

    def __init__(self, rsrcmgr, outfp, pageno=1, laparams=None,
                 showpageno=False):
        PDFConverter.__init__(self, rsrcmgr, outfp, pageno=pageno, laparams=laparams)
        self.showpageno = showpageno

    def write_text(self, text):
        self.outfp.write(text)

    def receive_layout(self, ltpage):
        def render(item):
            if isinstance(item, LTContainer):
                for child in item:
                    render(child)
            elif isinstance(item, LTText):
                self.write_text(item.get_text())
            if isinstance(item, LTTextBox):
                self.write_text('\n')
        if self.showpageno:
            self.write_text('Page %s\n' % ltpage.pageid)
        render(ltpage)
        self.write_text('\f')

    # Some dummy functions to save memory/CPU when all that is wanted is text.
    # This stops all the image and drawing ouput from being recorded and taking
    # up RAM.
    def render_image(self, name, stream):
        pass
    def paint_path(self, gstate, stroke, fill, evenodd, path):
        pass



def main(argv):
    
    src_file = 'sge_pdf.pdf'
    out_file = 'sge_pdf.out'
    
    logging.basicConfig(level=logging.WARNING,
                format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                datefmt='%a, %d %b %Y %H:%M:%S',
                filename='readpdf_test.log',
                filemode='w')
    rsrcmgr = PDFResourceManager()
    outfp = io.open(out_file, 'wt')
    device = TextConverter(rsrcmgr, outfp)
    fp = io.open(src_file, 'rb')
    pdb.set_trace()
    process_pdf(rsrcmgr, device, fp)
    fp.close()
    device.close()
    outfp.close()
    
    return 0
    
    def usage():
        print(('usage: %s [-d] [-p pagenos] [-m maxpages] [-P password] [-o output] [-C] '
               '[-n] [-A] [-V] [-M char_margin] [-L line_margin] [-W word_margin] [-F boxes_flow] '
               '[-Y layout_mode] [-O output_dir] [-t text|html|xml|tag] [-c codec] [-s scale] file ...' % argv[0]))
        return 100
    try:
        (opts, args) = getopt.getopt(argv[1:], 'dp:m:P:o:CnAVM:L:W:F:Y:O:t:c:s:')
    except getopt.GetoptError:
        return usage()
    if not args: return usage()
    debug = False
    # input option
    password = ''
    pagenos = set()
    maxpages = 0
    # output option
    outfile = None
    outtype = None
    outdir = None
    layoutmode = 'normal'
    codec = 'utf-8'
    pageno = 1
    scale = 1
    caching = True
    showpageno = True
    laparams = LAParams()
    for (k, v) in opts:
        if k == '-d': debug = True
        elif k == '-p': pagenos.update( int(x)-1 for x in v.split(',') )
        elif k == '-m': maxpages = int(v)
        elif k == '-P': password = v
        elif k == '-o': outfile = v
        elif k == '-C': caching = False
        elif k == '-n': laparams = None
        elif k == '-A': laparams.all_texts = True
        elif k == '-V': laparams.detect_vertical = True
        elif k == '-M': laparams.char_margin = float(v)
        elif k == '-L': laparams.line_margin = float(v)
        elif k == '-W': laparams.word_margin = float(v)
        elif k == '-F': laparams.boxes_flow = float(v)
        elif k == '-Y': layoutmode = v
        elif k == '-O': outdir = v
        elif k == '-t': outtype = v
        elif k == '-c': codec = v
        elif k == '-s': scale = float(v)
    
    if debug:
        set_debug_logging()
    rsrcmgr = PDFResourceManager(caching=caching)
    if not outtype:
        outtype = 'text'
        if outfile:
            if outfile.endswith('.htm') or outfile.endswith('.html'):
                outtype = 'html'
            elif outfile.endswith('.xml'):
                outtype = 'xml'
            elif outfile.endswith('.tag'):
                outtype = 'tag'
    if outfile:
        outfp = io.open(outfile, 'wt', encoding=codec, errors='ignore')
        close_outfp = True
    else:
        outfp = sys.stdout
        close_outfp = False
    if outtype == 'text':
        device = TextConverter(rsrcmgr, outfp, laparams=laparams)
    elif outtype == 'xml':
        device = XMLConverter(rsrcmgr, outfp, laparams=laparams, outdir=outdir)
    elif outtype == 'html':
        device = HTMLConverter(rsrcmgr, outfp, scale=scale, layoutmode=layoutmode,
            laparams=laparams, outdir=outdir, debug=debug)
    elif outtype == 'tag':
        device = TagExtractor(rsrcmgr, outfp)
    else:
        return usage()
    for fname in args:
        fp = io.open(fname, 'rb')
        process_pdf(rsrcmgr, device, fp, pagenos, maxpages=maxpages, password=password,
                    caching=caching, check_extractable=True)
        fp.close()
    device.close()
    if close_outfp:
        outfp.close()

if __name__ == '__main__':
    sys.exit(main(sys.argv))
