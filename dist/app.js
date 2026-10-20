import {initTour,start,inspect} from './tour.js?v=hoi-an-1';
import {initContact,syncDialogScroll} from './contact.js?v=hoi-an-1';
const $=s=>document.querySelector(s),$$=s=>[...document.querySelectorAll(s)];
let allProducts=[],filter='all',noticeTimer;
function renderProducts(){
  const query=$('#product-search').value.toLowerCase().trim();
  const products=allProducts.filter(p=>(filter==='all'||p.category===filter)&&(!query||(p.name+' '+p.sku).toLowerCase().includes(query)));
  $('#products').replaceChildren(...products.map(p=>{const button=document.createElement('button');button.className='product-card';button.dataset.sku=p.sku;button.setAttribute('aria-label','Inspect in 3D: '+p.name+', '+p.sku);
    const frame=document.createElement('div');frame.className='product-image';const img=document.createElement('img');img.src='assets/catalogue/'+p.sku+'.jpg';img.alt=p.name+' — HOI AN catalogue reference';img.loading='lazy';img.width=800;img.height=600;frame.append(img);const arrow=document.createElement('span');arrow.textContent='↗';arrow.setAttribute('aria-hidden','true');frame.append(arrow);button.append(frame);
    const sku=document.createElement('span');sku.className='sku';sku.textContent=p.sku;const h=document.createElement('h3');h.textContent=p.name;const dim=document.createElement('span');dim.className='dimension';dim.textContent=p.dimensions.join(' × ')+' mm';button.append(sku,h,dim);
    button.addEventListener('click',()=>{$('#tour').scrollIntoView({behavior:matchMedia('(prefers-reduced-motion:reduce)').matches?'instant':'smooth'});inspect(p.sku);});return button;}));$('#no-products').hidden=products.length>0;
}
initTour();initContact();
fetch('assets/products.json').then(r=>{if(!r.ok)throw Error('products');return r.json();}).then(data=>{allProducts=data;renderProducts();}).catch(()=>{$('#no-products').hidden=false;$('#no-products').textContent='The product list could not be loaded. Please reload the page.';});
$$('[data-filter]').forEach(b=>b.addEventListener('click',()=>{filter=b.dataset.filter;$$('[data-filter]').forEach(x=>x.setAttribute('aria-pressed',x===b));renderProducts();}));$('#product-search').addEventListener('input',renderProducts);
function closeMenu(){$('#nav').classList.remove('open');$('.menu-toggle').setAttribute('aria-expanded','false');$('.menu-toggle span').textContent='＋';}
$('.menu-toggle').addEventListener('click',()=>{const open=$('.menu-toggle').getAttribute('aria-expanded')!=='true';$('.menu-toggle').setAttribute('aria-expanded',String(open));$('#nav').classList.toggle('open',open);$('.menu-toggle span').textContent=open?'−':'＋';});$$('#nav a,.mobile-shortcuts a').forEach(a=>a.addEventListener('click',closeMenu));document.addEventListener('click',event=>{if(!event.target.closest('.header'))closeMenu();});document.addEventListener('keydown',event=>{if(event.key==='Escape')closeMenu();});
$$('[data-enter-tour]').forEach(a=>a.addEventListener('click',()=>start()));
document.addEventListener('tour:notice',e=>{const n=$('#notification');clearTimeout(noticeTimer);n.textContent=e.detail;n.hidden=false;noticeTimer=setTimeout(()=>n.hidden=true,4500);});
const dialog=$('#render-dialog'),labels={overview:'The open exhibition / Four displays',king:'King suite / Golden timber & olive',queen:'Queen suite / White cotton & rattan',storage:'Storage gallery / Woven details'};let lastRenderTrigger;
$$('[data-render]').forEach(button=>button.addEventListener('click',()=>{const name=button.dataset.render;lastRenderTrigger=button;$('#render-image').src='assets/'+name+'.jpg';$('#render-image').alt=labels[name]+' — Blender EEVEE 4K';$('#render-caption').textContent=labels[name]+' · EEVEE · 3840 × 2160';$('#render-download').dataset.downloadRequest='the 4K PNG render: '+labels[name];dialog.showModal();syncDialogScroll();}));
$('#close-render').addEventListener('click',()=>dialog.close());dialog.addEventListener('click',event=>{if(event.target===dialog){const r=dialog.getBoundingClientRect();if(event.clientX<r.left||event.clientX>r.right||event.clientY<r.top||event.clientY>r.bottom)dialog.close();}});dialog.addEventListener('close',()=>{syncDialogScroll();lastRenderTrigger?.focus({preventScroll:true});});
