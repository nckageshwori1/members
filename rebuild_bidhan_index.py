#!/usr/bin/env python3
"""Rebuild the PDF + browser index locally. Requires pip install pymupdf."""
import fitz, json, hashlib, re, shutil, sys
from pathlib import Path
mp={"÷":"/","v":"ख","r":"च","\"":"ू","~":"ञ्","z":"श","ç":"ॐ","f":"ा","b":"द","n":"ल","j":"व","×":"×","V":"ख्","R":"च्","ß":"द्म","^":"६","Û":"!","Z":"श्","F":"ँ","B":"द्य","N":"ल्","Ë":"ङ्ग","J":"व्","6":"ट","2":"द्द","¿":"रू",">":"श्र",":":"स्","§":"ट्ट","&":"७","£":"घ्","•":"ड्ड",".":"।","«":"्र","*":"८","„":"ध्र","w":"ध","s":"क","g":"न","æ":"“","c":"अ","o":"य","k":"प","W":"ध्","Ö":"=","S":"क्","Ò":"¨","_":")","[":"ृ","Ú":"’","G":"न्","ˆ":"फ्","C":"ऋ","O":"इ","Î":"ङ्ख","K":"प्","7":"ठ","¶":"ठ्ठ","3":"घ","9":"ढ","?":"रु",";":"स","'":"ु","#":"३","¢":"द्घ","/":"र","+":"ं","ª":"ङ","t":"त","p":"उ","|":"्र","x":"ह","å":"द्व","d":"म","`":"ञ","l":"ि","h":"ज","T":"त्","P":"ए","Ý":"ट्ठ","\\":"्","Ù":";","X":"ह्","Å":"हृ","D":"म्","@":"२","Í":"ङ्क","L":"ी","H":"ज्","4":"द्ध","±":"+","0":"ण्","<":"?","8":"ड","¥":"र्‍","$":"४","¡":"ज्ञ्",",":",","©":"र","(":"९","‘":"ॅ","u":"ग","q":"त्र","}":"ै","y":"थ","e":"भ","a":"ब","i":"ष्","‰":"झ्","U":"ग्","Q":"त्त","]":"े","˜":"ऽ","Y":"थ्","Ø":"्य","E":"भ्","A":"ब्","M":"ः","Ì":"न्न","I":"क्ष्","5":"छ","´":"झ","1":"ज्ञ","°":"ङ्ढ","=":".","Æ":"”","‹":"ङ्घ","%":"५","¤":"झ्","!":"१","-":"(","›":"द्र",")":"०","…":"‘","Ü":"%"}
rules=[('्ा',''),('(त्र|त्त)([^उभप]+?)m',r'\1m\2'),('त्रm','क्र'),('त्तm','क्त'),('([^उभप]+?)m',r'm\1'),('उm','ऊ'),('भm','झ'),('पm','फ'),('इ{','ई'),('ि((.्)*[^्])',r'\1ि'),('(.[ािीुूृेैोौंःँ]*?){',r'{\1'),('((.्)*){',r'{\1'),('{','र्'),('([ाीुूृेैोौंःँ]+?)(्(.्)*[^्])',r'\2\1'),('्([ाीुूृेैोौंःँ]+?)((.्)*[^्])',r'्\2\1'),('([ंँ])([ािीुूृेैोौः]*)',r'\2\1'),('ँँ','ँ'),('ंं','ं'),('ेे','े'),('ैै','ै'),('ुु','ु'),('ूू','ू'),('^ः',':'),('टृ','ट्ट'),('ेा','ाे'),('ैा','ाै'),('अाे','ओ'),('अाै','औ'),('अा','आ'),('एे','ऐ'),('ाे','ो'),('ाै','ौ')]
def conv(s):
    s=''.join(mp.get(c,c) for c in s)
    for a,b in rules:
        s=re.sub(a,b,s)
    return s

def main():
    if len(sys.argv)<2: raise SystemExit('Usage: python rebuild_bidhan_index.py /path/to/new.pdf')
    source=Path(sys.argv[1]);out=Path(__file__).resolve().parent
    doc=fitz.open(source); records=[];fonts={};blank=[]
    for pno,page in enumerate(doc,1):
        count=0
        for b in page.get_text('dict',sort=True)['blocks']:
            for line in b.get('lines',[]):
                spans=line.get('spans',[])
                if not spans:continue
                raw=''.join(s['text'] for s in spans).strip()
                if not raw:continue
                ff=list(dict.fromkeys(s['font'] for s in spans))
                for f in ff:fonts[f]=fonts.get(f,0)+1
                uni=re.sub(r'\s+',' ',conv(raw)).strip()
                if not uni:continue
                count+=1;records.append({'page':pno,'line':count,'text':uni,'raw':raw,'fonts':ff,'status':'REVIEW_REQUIRED'})
        if not count:blank.append(pno)
    meta={'source':source.name,'sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'pages':len(doc),'records':len(records),'unverified':True,'fonts':fonts,'emptyPages':blank}
    (out/'bidhan-index.json').write_text(json.dumps({'meta':meta,'records':records},ensure_ascii=False,separators=(',',':')),encoding='utf-8')
    shutil.copyfile(source,out/'NC_bidhan_2082.pdf')
    print('Generated',len(records),'records from',len(doc),'pages; human verification required.')
if __name__=='__main__':main()
