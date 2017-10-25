defaultcsv="C:\\Users\\smartm13\\Desktop\\free codes\\taskypdf\\input.csv"
csvPath="{0}".format(defaultcsv)#0-csvfullpath
raw_input=input#py3
def updateLastRead(csvf):
	import os,tempfile,json
	if not os.path.exists('{}/taskypdf.log'.format(tempfile.gettempdir())):
		with open('{}/taskypdf.log'.format(tempfile.gettempdir()),'w') as f:f.write(json.dumps(dict()))
	with open('{}/taskypdf.log'.format(tempfile.gettempdir()),'r') as f:last=json.loads(f.read())
	curr=os.path.getmtime(csvf)
	if last.get(csvf,-1)>=curr:
		#print("csv file is not updated[old] : "+csvf)
		return 0
	last[csvf]=curr
	with open('{}/taskypdf.log'.format(tempfile.gettempdir()),'w') as f:f.write(json.dumps(last))
	return 1

def readcsv(csvf):
	csvSeperator=','#'\t'
	with open(csvf,'r') as f:alld=f.read()
	cells=[row.split(csvSeperator) for row in alld.split('\n')]
	#cells=toSquareMatrix(cells)
	maxC=max([len(r) for r in cells])
	for ir,r in enumerate(cells):
		cells[ir]=r+[""]*(maxC-len(r)+3)
	config=dict()
	config['blankpath']=cells[1][0]
	config['newpath']=cells[4][0]
	config['filterBank']=cells[1][7]
	config['filterType']=cells[1][8]
	config['clnt_strt_index']=cells[1][9]
	config['clnt_end_index']=cells[1][10]
	config['allclients']=[{'cName':c[8],'cArn':c[9],'cEuin':c[10]} for c in cells[7:]]
	config['allbank']=dict()
	for c in cells[7:]:
		name,type,arnl,arnh,eul,euh,ftsz=c[0:7]
		if name or type:pass
		else:continue
		bank=config['allbank'].get(name,dict())
		bank[type]={'arn':(arnl,arnh),'euid':(eul,euh),'ft':float(ftsz if ftsz.replace('.','').isdigit() else 12)}
		config['allbank'][name]=bank
	return config

def to_index(v):
	try:return int(v)-1
	except ValueError:return None
class string:
	basestr=""
	def repall(this,fromlist,to):
		s=this.basestr
		for f in fromlist:s=s.replace(f,to)
		return s
	def repallfrom(this,fromtomap):
		s=string(this.basestr)
		for k,v in fromtomap.items():s=string(s.repall(v,k))
		return s.basestr
	def __init__(this,start):this.basestr=start
#def removelast(orgPdf,char):return char.join(orgPdf.split(char)[:-1] or [orgPdf])
#file2dir=lambda orgPdf:removelast(removelast(orgPdf,'/'),'\\')
def findorgflname(basepath,bankname,typen):
	import os
	orgs=os.listdir(basepath+"/"+bankname)
	for f in orgs:
		if typen.lower() in f.lower():return f
	return "{0}-{1}.pdf".format(bankname,typen)
def config2tasks(config,exect=0):
	pathPdf="{0}/{1}/{1}_{2}.pdf"#0-dir,1-bank,2-type
	tasks=[]#[<(blankpath,newpath,(arnV,(arnL,arnH)),(euidV,(euL,euH)),ftsz)>]
	banks=config['allbank'].keys()
	types=set()
	for B in config['allbank'].values():types.update(B.keys())
	selectedBanks=banks if config['filterBank']=='*' else [b for b in banks if b in config['filterBank']]
	selectedTypes=list(types) if config['filterType']=='*' else [b for b in types if b in config['filterType']]
	selectedCl=config['allclients'][to_index(config['clnt_strt_index']):to_index(config['clnt_end_index'])]
	for cl in selectedCl:
		print("Compiling for Client: {} Bank:".format(cl['cName']),end=' ')
		for bn in selectedBanks:
			print("{}[".format(bn),end=' ')
			for typ in selectedTypes:
				if typ not in config['allbank'][bn]:continue
				print("{},".format(typ),end=' ')
				orgPdfName=findorgflname(config['blankpath'],bn,typ)
				#BlankPath=pathPdf.format(config['blankpath'],bn,typ)
				#NewPath="{0}/{1}/{2}/{2}-{3}.pdf".format(config['newpath'],cl['cName'].replace(' ','-').replace('_','-'),bn.replace(' ','-').replace('_','-'),typ.replace(' ','-').replace('_','-'))
				BlankPath="{0}/{1}/{2}".format(config['blankpath'],bn,orgPdfName)
				NewPath="{0}/{1}/{2}/{3}".format(config['newpath'],cl['cName'],bn,orgPdfName)
				bnk=config['allbank'][bn][typ]
				t=[BlankPath,NewPath,(cl['cArn'],bnk['arn']),(cl['cEuin'],bnk['euid']),bnk['ft']]
				if exect==1:
					crtDir(t[1])
					execTasks([t])
				tasks.append(t)
			print("],",end=' ')
		print(".")
	return tasks

def crtDir(fpath):
	import os
	directory = os.path.dirname(fpath)
	if not os.path.exists(directory):os.makedirs(directory)

def createDirs(tasks):
	newpaths=[x[1] for x in tasks]
	import os
	for fpath in newpaths:
		directory = os.path.dirname(fpath)
		if not os.path.exists(directory):os.makedirs(directory)
	return

def testSys():
	try:
		from PyPDF2 import PdfFileWriter, PdfFileReader, PdfFileMerger
		import io
		from reportlab.pdfgen import canvas
		from reportlab.lib.pagesizes import letter
	except:
		print ("Missing packages.Install em.\n>[sudo] pip install pypdf2 io reportlab")
		exit()
def execTasks(tasks):
	from PyPDF2 import PdfFileWriter, PdfFileReader, PdfFileMerger
	import io
	from reportlab.pdfgen import canvas
	from reportlab.lib.pagesizes import letter
	for (taskI,(orgPdf,dstPdf,arn,euin,ftsz)) in enumerate(tasks):
		try:
			packet = io.BytesIO()
			existing_pdf = PdfFileReader(orgPdf)
			p=existing_pdf.getPage(0)
			h,w=p.mediaBox.getHeight(),p.mediaBox.getWidth()
			# create a new PDF with Reportlab
			can = canvas.Canvas(packet, pagesize=(h,w),bottomup=1)
			can.setFontSize(ftsz)
			can.drawString(float(arn[1][0]),float(h)-ftsz*0-float(arn[1][1]), arn[0])
			can.drawString(float(euin[1][0]),float(h)-ftsz*0-float(euin[1][1]), euin[0])
			can.save()
			#move to the beginning of the StringIO buffer
			packet.seek(0)
			new_pdf = PdfFileReader(packet)
			# read your existing PDF
			output = PdfFileWriter()
			# add the "watermark" (which is the new pdf) on the existing page
			page = existing_pdf.getPage(0)
			page.mergePage(new_pdf.getPage(0))
			##page=new_pdf.getPage(0)
			##page.mergePage(existing_pdf.getPage(0))
			output.addPage(page)
			for pi in range(1,existing_pdf.numPages):output.addPage(existing_pdf.getPage(pi))
			# finally, write "output" to a real file
			outputStream = open(dstPdf, "wb")
			output.write(outputStream)#,flatten_fields=True)
			outputStream.close()
			#existing_pdf.close()
		except:
			print ("Failed task: {}".format(tasks[taskI]))
			continue

def main():
	global csvPath
	testSys()
	#csvPath=raw_input("CSV path[{}]:".format(csvPath)) or csvPath
	if not updateLastRead(csvPath):exit()
	config=readcsv(csvPath)
	#print(config)
	Tasks=config2tasks(config,exect=1)
	#createDirs(Tasks)
	#execTasks(Tasks)

if __name__=="__main__":main()