'use strict';
const root=document.documentElement;
const themeButton=document.getElementById('theme-toggle');
function setTheme(theme){
  root.dataset.theme=theme;
  themeButton.setAttribute('aria-pressed',String(theme==='dark'));
  themeButton.setAttribute('aria-label',theme==='dark'?'Ativar tema claro':'Ativar tema escuro');
  document.querySelector('meta[name="theme-color"]').content=theme==='dark'?'#151516':'#f3f2ed';
  try{localStorage.setItem('adny-site-theme',theme);}catch{}
}
try{const saved=localStorage.getItem('adny-site-theme');if(saved==='dark'||saved==='light')setTheme(saved);}catch{}
themeButton.addEventListener('click',()=>setTheme(root.dataset.theme==='dark'?'light':'dark'));

const menuButton=document.querySelector('.menu-toggle');
const mobileMenu=document.getElementById('mobile-nav');
function closeMenu(){mobileMenu.hidden=true;menuButton.setAttribute('aria-expanded','false');menuButton.setAttribute('aria-label','Abrir menu');}
menuButton.addEventListener('click',()=>{const open=menuButton.getAttribute('aria-expanded')!=='true';mobileMenu.hidden=!open;menuButton.setAttribute('aria-expanded',String(open));menuButton.setAttribute('aria-label',open?'Fechar menu':'Abrir menu');});
mobileMenu.querySelectorAll('a').forEach(a=>a.addEventListener('click',closeMenu));
document.addEventListener('keydown',event=>{if(event.key==='Escape')closeMenu();});

const stage=document.getElementById('compare-stage');
const range=document.getElementById('compare-range');
const leftLabel=document.getElementById('left-label');
const rightLabel=document.getElementById('right-label');
document.querySelectorAll('[data-view]').forEach(button=>button.addEventListener('click',()=>{
  const mode=button.dataset.view;
  stage.dataset.mode=mode;
  document.querySelectorAll('[data-view]').forEach(b=>b.setAttribute('aria-pressed',String(b===button)));
  leftLabel.textContent=mode==='original'?'ORIGINAL':'RETÍCULA';
  rightLabel.hidden=mode!=='compare';
  document.getElementById('alpha-status').textContent=mode==='original'?'ORIGINAL: ALFA VARIÁVEL':'SAÍDA: ALFA 0 OU 255';
}));
range.addEventListener('input',()=>{stage.style.setProperty('--split',`${range.value}%`);range.setAttribute('aria-valuetext',`${range.value}% da imagem em retícula`);});

const lpiInput=document.getElementById('demo-lpi');
const shapeInput=document.getElementById('demo-shape');
const resultImage=document.getElementById('result-image');
const status=document.getElementById('render-status');
const shapeNames={circle:'Redondo',square:'Quadrado',line:'Linha'};
let previewRequest=0;
function updatePreview(){
  const lpi=lpiInput.value,shape=shapeInput.value;
  if(!['20','30','45'].includes(lpi)||!Object.hasOwn(shapeNames,shape))return;
  const current=++previewRequest;
  status.textContent='CARREGANDO ESTUDO…';
  const image=new Image();
  image.onload=()=>{if(current!==previewRequest)return;resultImage.src=image.src;resultImage.alt=`Estudo processado em ${lpi} LPI, ponto ${shapeNames[shape].toLowerCase()} e ângulo de 22,5 graus`;status.textContent=`${lpi} LPI / ${shapeNames[shape].toUpperCase()} / 22,5°`;};
  image.onerror=()=>{if(current===previewRequest)status.textContent='NÃO FOI POSSÍVEL CARREGAR ESTE ESTUDO.';};
  image.src=`assets/study-${lpi}-${shape}.png`;
}
lpiInput.addEventListener('change',updatePreview);
shapeInput.addEventListener('change',updatePreview);

const knockoutImage=document.getElementById('knockout-image');
document.querySelectorAll('[data-knockout]').forEach(button=>button.addEventListener('click',()=>{
  const original=button.dataset.knockout==='original';
  knockoutImage.src=original?'assets/teste_dtf.png':'assets/sample-separated.png';
  knockoutImage.alt=original?'Arte original do repositório com fundo preto':'Arte do repositório com a cor preta removida e transparência binária';
  document.getElementById('knockout-visual').dataset.state=original?'original':'result';
  document.querySelectorAll('[data-knockout]').forEach(b=>b.setAttribute('aria-pressed',String(b===button)));
}));
document.querySelectorAll('[data-choke]').forEach(button=>button.addEventListener('click',()=>{
  const choke=button.dataset.choke;
  if(!['0','1','2'].includes(choke))return;
  const image=document.getElementById('underbase-image');
  image.src=choke==='0'?'assets/study-underbase.png':`assets/study-underbase-${choke}.png`;
  image.alt=`Base branca do estudo com redução de ${choke} pixels`;
  document.querySelectorAll('[data-choke]').forEach(b=>b.setAttribute('aria-pressed',String(b===button)));
}));

const screenshotDialog=document.getElementById('screenshot-dialog');
document.getElementById('open-screenshot').addEventListener('click',()=>screenshotDialog.showModal());
document.getElementById('close-screenshot').addEventListener('click',()=>screenshotDialog.close());
screenshotDialog.addEventListener('click',event=>{if(event.target===screenshotDialog){const r=screenshotDialog.getBoundingClientRect();if(event.clientX<r.left||event.clientX>r.right||event.clientY<r.top||event.clientY>r.bottom)screenshotDialog.close();}});

document.querySelectorAll('[data-copy]').forEach(button=>button.addEventListener('click',async()=>{
  const code=document.getElementById(button.dataset.copy);
  const output=document.getElementById('copy-status');
  try{await navigator.clipboard.writeText(code.textContent);output.textContent='COMANDO COPIADO.';}
  catch{const selection=window.getSelection();const copyRange=document.createRange();copyRange.selectNodeContents(code);selection.removeAllRanges();selection.addRange(copyRange);output.textContent='COMANDO SELECIONADO. USE COPIAR NO SEU DISPOSITIVO.';}
}));

let ticking=false;
function updateScroll(){
  const height=document.documentElement.scrollHeight-innerHeight;
  const percent=height>0?Math.min(100,Math.max(0,scrollY/height*100)):0;
  document.querySelector('.ruler-position').style.top=`${percent}%`;
  document.getElementById('scroll-percentage').textContent=`${Math.round(percent)}%`;
  ticking=false;
}
addEventListener('scroll',()=>{if(!ticking){requestAnimationFrame(updateScroll);ticking=true;}},{passive:true});
addEventListener('resize',updateScroll);
updateScroll();
const navLinks=[...document.querySelectorAll('.desktop-nav a')];
const sectionObserver=new IntersectionObserver(entries=>{
  const visible=entries.filter(e=>e.isIntersecting).sort((a,b)=>a.boundingClientRect.top-b.boundingClientRect.top);
  if(visible.length){const id=visible[0].target.id;navLinks.forEach(a=>a.classList.toggle('active',a.getAttribute('href')===`#${id}`));}
},{rootMargin:'-15% 0px -60% 0px',threshold:0});
['inicio','recursos','na-pratica','como-usar'].forEach(id=>sectionObserver.observe(document.getElementById(id)));
document.getElementById('year').textContent=String(new Date().getFullYear());
