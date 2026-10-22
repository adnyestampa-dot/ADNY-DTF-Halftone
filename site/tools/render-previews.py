"""Renderiza estudos gráficos com o motor original do repositório informado."""
from pathlib import Path
import argparse,sys,json
import numpy as np
from PIL import Image,ImageDraw,ImageFont

parser=argparse.ArgumentParser()
parser.add_argument('--app-root',required=True,type=Path)
parser.add_argument('--output',required=True,type=Path)
args=parser.parse_args()
sys.path.insert(0,str(args.app_root))
from app.engines.central import MotorCentral
from app.engines.export_engine import gravar_png,alfa_binario
from app.model.settings import Settings

out=args.output;out.mkdir(parents=True,exist_ok=True)
w,h=1200,800
y,x=np.mgrid[0:h,0:w].astype(np.float32)
u=(x-660)/360;v=(y-360)/300
r=np.sqrt(u*u+v*v)
angle=np.arctan2(v,u)
ring=np.exp(-((r-.75)/.22)**2)
light=.35+.65*(np.sin(angle-.8)+1)/2
alpha=np.clip(ring*light,0,1)
alpha[alpha<.025]=0
phase=(np.sin(angle+1.2)+1)/2
rgba=np.zeros((h,w,4),dtype=np.uint8)
rgba[...,0]=(70+180*phase).astype(np.uint8)
rgba[...,1]=(190-150*phase).astype(np.uint8)
rgba[...,2]=(255-20*phase).astype(np.uint8)
rgba[...,3]=(alpha*255).astype(np.uint8)
rgba[rgba[...,3]==0]=0
art=Image.fromarray(rgba)
draw=ImageDraw.Draw(art)
font_path='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
font=ImageFont.truetype(font_path,185)
draw.text((85,455),'DTF',font=font,fill=(235,240,225,255),stroke_width=0)
small=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf',17)
draw.text((98,682),'ADNY / HALFTONE STUDY 001',font=small,fill=(190,190,190,255))
art.save(out/'study-original.png',dpi=(300,300))
source=np.array(art)
motor=MotorCentral()
rows=[]
for lpi in [20,30,45]:
 for shape in ['circle','square','line']:
  result=motor.processar(source,Settings(lpi=lpi,dot_shape=shape,dpi=300,dpi_informado=True,underbase=True))
  assert result.separacao.shape==source.shape
  assert alfa_binario(result.separacao)
  name=f'study-{lpi}-{shape}.png'
  gravar_png(out/name,result.separacao,dpi=(300,300))
  rows.append({'file':name,'lpi':lpi,'shape':shape,'pixels':list(source.shape[:2]),'binary_alpha':True})
  if lpi==30 and shape=='circle':
   gravar_png(out/'study-underbase.png',result.base_branca,dpi=(300,300))
   Image.fromarray(result.tinta.astype(np.uint8)*255).save(out/'study-mask.png')
   for choke in [1,2]:
    white=motor.processar(source,Settings(lpi=30,dpi=300,dpi_informado=True,underbase=True,choke_px=choke))
    gravar_png(out/f'study-underbase-{choke}.png',white.base_branca,dpi=(300,300))
sample=np.array(Image.open(out/'teste_dtf.png').convert('RGBA'))
result=motor.processar(sample,Settings(lpi=30,dpi=300,dpi_informado=True))
gravar_png(out/'sample-separated.png',result.separacao,dpi=(300,300))
# desktop.webp é uma captura separada da interface executada na revisão auditada.
# Não substituir pela imagem histórica docs/validacao-tela.png.
(out/'previews.json').write_text(json.dumps({'source':'adnyestampa-dot/ADNY-DTF-Halftone','angle':22.5,'dpi':300,'previews':rows},indent=2))
print('Rendered',len(rows),'previews with the original engine; binary alpha and dimensions verified.')
