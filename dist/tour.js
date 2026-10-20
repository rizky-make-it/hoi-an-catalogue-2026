import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { DRACOLoader } from 'three/addons/loaders/DRACOLoader.js';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';
import { createJoystick } from './touch-controls.js?v=mobile-nav-1';

const $=s=>document.querySelector(s),$$=s=>[...document.querySelectorAll(s)];
const P=(x,y,z)=>new THREE.Vector3(x,z,-y);
const roomNames={king:'King suite display',queen:'Queen suite display',storage:'Storage gallery',craft:'Weave study',aisle:'Open exhibition aisle'};
const keys=new Set(),roots=[],parts=[],animations=[];
let renderer,scene,camera,orbit,house,inspection,inspectionSku,ground,loader,sceneInfo,products,selected,currentRoom='king',mode='walk',ready=false,loading=false,lastTime=0,yaw=0,pitch=0,visible=true,selectionSku;
let pointer=null,dragging=false,rafId,frameCount=0,uiTick=0,needsRender=true,joystick,walkInput={x:0,y:0},expandedFocus;
const canvasPointers=new Set();
const canvas=$('#canvas'),viewer=$('#viewer'),stage=$('#viewer-stage'),ray=new THREE.Raycaster(),pointerNDC=new THREE.Vector2();
const emit=(name,detail)=>document.dispatchEvent(new CustomEvent(name,{detail}));
const note=text=>emit('tour:notice',text);
function stopMovement(){keys.clear();joystick?.reset();walkInput={x:0,y:0};}
function showControls(){for(const id of ['viewer-tools','viewer-bottom','walk-pad','zoom-controls'])$('#'+id).hidden=false;$('#load-screen').hidden=true;}
function resize(){if(!renderer)return;const w=stage.clientWidth,h=stage.clientHeight;if(!w||!h)return;renderer.setSize(w,h,false);camera.aspect=w/h;camera.updateProjectionMatrix();if(ready&&mode==='orbit')frameOverview();needsRender=true;}
function lookAt(target){camera.lookAt(target);const e=new THREE.Euler().setFromQuaternion(camera.quaternion,'YXZ');yaw=e.y;pitch=e.x;}
function setPressed(){
  $('#walk-mode').setAttribute('aria-pressed',mode==='walk');$('#orbit-mode').setAttribute('aria-pressed',mode==='orbit');
  $('#walk-pad').hidden=mode!=='walk';$('#touch-walk').hidden=mode!=='walk';$('#back-house').hidden=mode!=='product';$('#walk-mode').hidden=mode==='product';$('#orbit-mode').hidden=mode==='product';
  viewer.dataset.mode=mode;$$('[data-zone-select]').forEach(el=>el.value=mode==='orbit'?'overview':currentRoom);stopMovement();
  $('#map-dot').style.opacity=mode==='walk'?'1':'0';
  $('#view-hint').textContent=mode==='walk'?(matchMedia('(max-width:760px), (pointer:coarse)').matches?'JOYSTICK TO WALK · SWIPE TO LOOK':'DRAG TO LOOK · WASD TO WALK'):'DRAG TO ORBIT · PINCH OR USE + / −';
}
function zoomView(direction){
  if(!ready)return;
  if(mode==='walk'){camera.fov=THREE.MathUtils.clamp(camera.fov+direction*7,30,82);camera.updateProjectionMatrix();}
  else{const offset=camera.position.clone().sub(orbit.target).multiplyScalar(direction<0?.8:1.25);offset.clampLength(orbit.minDistance,orbit.maxDistance);camera.position.copy(orbit.target).add(offset);orbit.update();}
  needsRender=true;
}
function setExpanded(expanded){
  stopMovement();
  if(expanded)expandedFocus=document.activeElement;
  viewer.classList.toggle('is-expanded',expanded);document.body.classList.toggle('tour-expanded',expanded);
  viewer.setAttribute('role',expanded?'dialog':'region');if(expanded)viewer.setAttribute('aria-modal','true');else viewer.removeAttribute('aria-modal');
  $('#fullscreen').setAttribute('aria-pressed',String(expanded));$('#fullscreen').setAttribute('aria-label',expanded?'Exit expanded view':'Expand viewer');$('#fullscreen').textContent=expanded?'×':'⛶';
  document.body.style.overflow=expanded||document.querySelector('dialog[open]')?'hidden':'';
  if(expanded)$('#fullscreen').focus({preventScroll:true});else expandedFocus?.focus({preventScroll:true});
}
function closeSelection(){selected=null;selectionSku=null;$('#selection').hidden=true;}
function disposeModel(root){const geometries=new Set(),materials=new Set(),textures=new Set();root.traverse(o=>{if(o.isMesh){geometries.add(o.geometry);for(const m of(Array.isArray(o.material)?o.material:[o.material]))if(m){materials.add(m);for(const value of Object.values(m))if(value?.isTexture)textures.add(value);}}});for(const g of geometries)g.dispose();for(const m of materials)m.dispose();for(const t of textures){t.dispose();t.image?.close?.();}}
function clearInspection(){if(inspection){for(let i=animations.length-1;i>=0;i--){let part=animations[i].part;while(part&&part!==inspection)part=part.parent;if(part===inspection)animations.splice(i,1);}scene.remove(inspection);disposeModel(inspection);inspection=null;inspectionSku=null;}if(house)house.visible=true;if(ground)ground.visible=false;}
export function goRoom(id,boot=false){
  if(!boot)inspect.latest=Symbol('room-navigation');
  currentRoom=id;$$('[data-room]').forEach(b=>b.setAttribute('aria-pressed',b.dataset.room===id));$('#view-label').textContent=roomNames[id];$$('[data-zone-select]').forEach(el=>el.value=id);
  if(!ready)return;
  clearInspection();mode='walk';orbit.enabled=false;camera.fov=55;camera.near=.07;camera.updateProjectionMatrix();
  const r=sceneInfo.rooms[id],coords=r.camera;
  const loc=coords?coords[0]:[4.9,5.3,1.65];const target=coords?coords[1]:[7,5.3,1.65];
  camera.position.copy(P(...loc));lookAt(P(...target));closeSelection();setPressed();keys.clear();needsRender=true;
}
function exhibitionCorners(){
  const box=new THREE.Box3().setFromObject(house),points=[];
  for(const x of[box.min.x,box.max.x])for(const y of[box.min.y,box.max.y])for(const z of[box.min.z,box.max.z])points.push(new THREE.Vector3(x,y,z));
  return points;
}
function frameOverview(){
  const view=sceneInfo.overview;camera.fov=view.fov;camera.aspect=stage.clientWidth/stage.clientHeight;camera.updateProjectionMatrix();
  const target=new THREE.Vector3().fromArray(view.target),direction=new THREE.Vector3().fromArray(view.position).sub(target).normalize();
  const right=new THREE.Vector3(0,1,0).cross(direction).normalize(),up=direction.clone().cross(right).normalize();
  const vertical=Math.tan(THREE.MathUtils.degToRad(camera.fov/2)),horizontal=vertical*camera.aspect;
  let distance=3;
  for(const point of exhibitionCorners()){
    const relative=point.sub(target);
    distance=Math.max(distance,relative.dot(direction)+Math.max(Math.abs(relative.dot(right))/horizontal,Math.abs(relative.dot(up))/vertical));
  }
  distance*=1.07;orbit.target.copy(target);camera.position.copy(target).addScaledVector(direction,distance);
  orbit.minDistance=3;orbit.maxDistance=Math.max(45,distance*2.5);orbit.maxPolarAngle=Math.PI*.49;orbit.update();
}
function overview(boot=false){
  if(!boot)inspect.latest=Symbol('overview-navigation');
  clearInspection();mode='orbit';orbit.enabled=true;frameOverview();
  $$('[data-room]').forEach(b=>b.setAttribute('aria-pressed','false'));
  $('#view-label').textContent='HOI AN / The Woven Collection';closeSelection();setPressed();keys.clear();needsRender=true;
}
function findRoot(obj){while(obj){if(obj.userData.kind==='product')return obj;obj=obj.parent;}return null;}
function movingParts(root){const list=[];root.traverse(o=>{if(o.userData.kind==='articulation')list.push(o);});return list;}
function selectProduct(root){
  if(!root)return;selected=root;selectionSku=root.userData.product_id;const product=products.find(p=>p.sku===selectionSku);if(!product)return;
  $('#selected-sku').textContent=product.sku+' / GOLDEN SYRUP';$('#selected-name').textContent=product.name;
  $('#selected-dimensions').textContent=product.dimensions.join(' × ')+' mm · width × depth × height';
  $('#selection').hidden=false;$('#inspect-product').hidden=mode==='product';
  const moving=movingParts(root);$('#open-parts').hidden=!moving.length;$('#open-parts').textContent=moving.some(p=>p.userData.open)?'Close drawers':'Open drawers';
  $('#open-parts').setAttribute('aria-pressed',String(moving.some(p=>p.userData.open)));
  $('#download-product').dataset.downloadRequest='the GLB model for '+product.name+' ('+product.sku+')';emit('tour:selection',product);
  if(matchMedia('(max-width:760px)').matches&&!viewer.classList.contains('is-expanded'))(mode==='product'?stage:$('#selection')).scrollIntoView({block:mode==='product'?'start':'nearest',behavior:matchMedia('(prefers-reduced-motion:reduce)').matches?'instant':'smooth'});
}
function setupPart(part){
  if(part.userData.basePosition)return;
  part.userData.basePosition=part.position.clone();part.userData.baseQuaternion=part.quaternion.clone();part.userData.open=false;
}
export function toggleParts(){
  if(!selected)return;const list=movingParts(selected);const shouldOpen=!list.some(p=>p.userData.open);
  for(const part of list){setupPart(part);const startPosition=part.position.clone(),startQuaternion=part.quaternion.clone(),targetPosition=part.userData.basePosition.clone(),targetQuaternion=part.userData.baseQuaternion.clone();
    for(let i=animations.length-1;i>=0;i--)if(animations[i].part===part)animations.splice(i,1);
    if(shouldOpen){if(part.userData.action==='drawer')targetPosition.z+=Number(part.userData.distance)||.20;else targetQuaternion.multiply(new THREE.Quaternion().setFromAxisAngle(new THREE.Vector3(0,1,0),Number(part.userData.angle)||1.5));}
    animations.push({part,startPosition,startQuaternion,targetPosition,targetQuaternion,start:performance.now(),duration:650});part.userData.open=shouldOpen;
  }
  $('#open-parts').textContent=shouldOpen?'Close drawers':'Open drawers';$('#open-parts').setAttribute('aria-pressed',String(shouldOpen));
}
export async function inspect(sku){
  const requestId=Symbol();inspect.latest=requestId;
  if(!ready){await start();if(!ready||inspect.latest!==requestId)return;}
  const product=products.find(p=>p.sku===sku);if(!product)return;
  note('Loading '+product.name+'…');
  try{
    const gltf=await loader.loadAsync(product.model);if(inspect.latest!==requestId){disposeModel(gltf.scene);return;}
    clearInspection();inspection=gltf.scene;inspectionSku=sku;scene.add(inspection);house.visible=false;ground.visible=true;mode='product';orbit.enabled=true;keys.clear();
    inspection.traverse(o=>{if(o.isMesh){o.castShadow=true;o.receiveShadow=true;}if(o.userData.kind==='articulation')setupPart(o);});
    const box=new THREE.Box3().setFromObject(inspection),size=box.getSize(new THREE.Vector3()),center=box.getCenter(new THREE.Vector3());
    ground.position.set(center.x,box.min.y-.008,center.z);ground.scale.setScalar(Math.max(3,size.length()*1.2));
    const distance=size.length()*1.15*Math.max(1,.88/camera.aspect);camera.fov=40;camera.updateProjectionMatrix();camera.position.copy(center).add(new THREE.Vector3(distance*.85,distance*.55,distance));
    orbit.target.copy(center);orbit.minDistance=.25;orbit.maxDistance=Math.max(8,size.length()*3);orbit.maxPolarAngle=Math.PI*.5;orbit.update();
    $('#view-label').textContent='Product studio';setPressed();const root=findProductNode(inspection);selectProduct(root);needsRender=true;note('Product studio ready. Drag to orbit; scroll or pinch to zoom.');
  }catch(error){console.error(error);note('The product model could not be loaded. Please try again.');}
}
function findProductNode(parent){let found;parent.traverse(o=>{if(!found&&o.userData.kind==='product')found=o;});return found;}
function canStand(x,y){
  const radius=.17,[minX,minY,maxX,maxY]=sceneInfo.floorBounds;if(x<minX+radius||x>maxX-radius||y<minY+radius||y>maxY-radius)return false;
  for(const [x1,y1,x2,y2]of sceneInfo.colliders){if(x>x1-radius&&x<x2+radius&&y>y1-radius&&y<y2+radius)return false;}
  for(const placement of sceneInfo.placements){
    if(placement.sku==='LV453.B71')continue;const p=products.find(p=>p.sku===placement.sku);if(!p)continue;
    const a=-placement.rotation*Math.PI/180,dx=x-placement.position[0],dy=y-placement.position[1],lx=dx*Math.cos(a)-dy*Math.sin(a),ly=dx*Math.sin(a)+dy*Math.cos(a);
    if(Math.abs(lx)<p.dimensions[0]/2000+radius&&Math.abs(ly)<p.dimensions[1]/2000+radius)return false;
  }
  return true;
}
function move(dt){
  if(mode!=='walk'||!visible||document.querySelector('dialog[open]'))return;
  let forward=walkInput.y+(keys.has('KeyW')||keys.has('ArrowUp')||keys.has('forward')?1:0)-(keys.has('KeyS')||keys.has('ArrowDown')||keys.has('back')?1:0);
  let side=walkInput.x+(keys.has('KeyD')||keys.has('ArrowRight')||keys.has('right')?1:0)-(keys.has('KeyA')||keys.has('ArrowLeft')||keys.has('left')?1:0);
  const len=Math.hypot(forward,side);if(!len)return;if(len>1){forward/=len;side/=len;}const speed=1.45*dt;
  const dx=(-Math.sin(yaw)*forward+Math.cos(yaw)*side)*speed,dz=(-Math.cos(yaw)*forward-Math.sin(yaw)*side)*speed;
  const nx=camera.position.x+dx;if(canStand(nx,-camera.position.z))camera.position.x=nx;
  const nz=camera.position.z+dz;if(canStand(camera.position.x,-nz))camera.position.z=nz;
  needsRender=true;
}
function animate(time){
  rafId=requestAnimationFrame(animate);const dt=Math.min((time-lastTime)/1000,.05);lastTime=time;
  const animating=animations.length>0;
  for(let i=animations.length-1;i>=0;i--){const a=animations[i],t=Math.min((time-a.start)/a.duration,1),e=t*t*(3-2*t);a.part.position.lerpVectors(a.startPosition,a.targetPosition,e);a.part.quaternion.slerpQuaternions(a.startQuaternion,a.targetQuaternion,e);if(t===1)animations.splice(i,1);}
  move(dt);if(orbit.enabled)orbit.update();
  if(visible&&(needsRender||animating)){renderer.render(scene,camera);frameCount++;needsRender=false;}
  if(++uiTick%12===0&&mode==='walk'){
    const x=camera.position.x,y=-camera.position.z,[minX,minY,maxX,maxY]=sceneInfo.floorBounds;$('#map-dot').setAttribute('cx',5+(x-minX)/(maxX-minX)*230);$('#map-dot').setAttribute('cy',207-(y-minY)/(maxY-minY)*202);
    const room=Object.entries(sceneInfo.rooms).find(([,r])=>x>=r.bounds[0]&&y>=r.bounds[1]&&x<=r.bounds[2]&&y<=r.bounds[3]);
    if(room&&room[0]!==currentRoom){currentRoom=room[0];$('#view-label').textContent=roomNames[currentRoom];$$('[data-zone-select]').forEach(el=>el.value=currentRoom);$$('[data-room]').forEach(b=>b.setAttribute('aria-pressed',b.dataset.room===currentRoom));}
  }
}
export async function start(options={}){
  if(ready)return;if(loading)return start.promise;
  loading=true;$('#load-tour').disabled=true;$('#load-status').textContent='Preparing the exhibition…';
  start.promise=(async()=>{try{
    [sceneInfo,products]=await Promise.all([fetch('assets/scene.json?v=hoi-an-1').then(r=>r.json()),fetch('assets/products.json').then(r=>r.json())]);
    renderer=new THREE.WebGLRenderer({canvas,antialias:true,alpha:false,powerPreference:'high-performance'});renderer.setPixelRatio(Math.min(devicePixelRatio,innerWidth<760?1.25:1.5));renderer.outputColorSpace=THREE.SRGBColorSpace;renderer.toneMapping=THREE.ACESFilmicToneMapping;renderer.toneMappingExposure=1.05;renderer.shadowMap.enabled=true;renderer.shadowMap.type=THREE.PCFSoftShadowMap;
    scene=new THREE.Scene();scene.background=new THREE.Color('#e5e1d8');camera=new THREE.PerspectiveCamera(55,1,.07,150);
    const pmrem=new THREE.PMREMGenerator(renderer);const envRoom=new RoomEnvironment();const environment=pmrem.fromScene(envRoom,.05);scene.environment=environment.texture;envRoom.dispose();pmrem.dispose();scene.environmentIntensity=.55;
    scene.add(new THREE.HemisphereLight(0xfff5df,0xb1a58b,1.1));
    const sunlight=new THREE.DirectionalLight(0xffeed2,2.4);sunlight.position.set(-3,12,-16);sunlight.target.position.set(6,0,-5);sunlight.castShadow=true;sunlight.shadow.mapSize.set(innerWidth<760?1024:2048,innerWidth<760?1024:2048);Object.assign(sunlight.shadow.camera,{left:-10,right:10,top:10,bottom:-10,near:.1,far:40});sunlight.shadow.bias=-.0002;sunlight.shadow.normalBias=.025;scene.add(sunlight,sunlight.target);
    const fill=new THREE.DirectionalLight(0xe5efff,.65);fill.position.set(15,8,6);scene.add(fill);
    const draco=new DRACOLoader();draco.setDecoderPath('assets/vendor/draco/');loader=new GLTFLoader();loader.setDRACOLoader(draco);
    const gltf=await loader.loadAsync('assets/hoi-an-exhibition.glb?v=hoi-an-1',event=>{$('#load-status').textContent=event.total?'Loading exhibition '+Math.round(event.loaded/event.total*100)+'%…':'Loading the exhibition model…';});
    house=gltf.scene;scene.add(house);house.traverse(o=>{if(o.isMesh){o.castShadow=true;o.receiveShadow=true;}if(o.userData.kind==='product')roots.push(o);if(o.userData.kind==='articulation'){setupPart(o);parts.push(o);}});
    ground=new THREE.Mesh(new THREE.PlaneGeometry(1,1),new THREE.MeshStandardMaterial({color:0xe3ded1,roughness:.9}));ground.rotation.x=-Math.PI/2;ground.receiveShadow=true;ground.visible=false;scene.add(ground);
    orbit=new OrbitControls(camera,canvas);orbit.enableDamping=true;orbit.dampingFactor=.08;orbit.enabled=false;orbit.addEventListener('change',()=>{needsRender=true;});
    ready=true;showControls();resize();if(options.room)goRoom(options.room,true);else overview(true);new ResizeObserver(resize).observe(stage);new IntersectionObserver(entries=>{visible=entries[0].isIntersecting;if(!visible)stopMovement();else needsRender=true;},{threshold:0}).observe(stage);
    canvas.addEventListener('pointerdown',event=>{canvasPointers.add(event.pointerId);if(pointer){dragging=true;return;}canvas.focus({preventScroll:true});pointer={x:event.clientX,y:event.clientY,lastX:event.clientX,lastY:event.clientY,id:event.pointerId};dragging=canvasPointers.size>1;if(mode==='walk')canvas.setPointerCapture(event.pointerId);});
    canvas.addEventListener('pointermove',event=>{if(!pointer||pointer.id!==event.pointerId)return;const dx=event.clientX-pointer.lastX,dy=event.clientY-pointer.lastY;if(Math.hypot(event.clientX-pointer.x,event.clientY-pointer.y)>6)dragging=true;if(mode==='walk'&&dragging&&canvasPointers.size===1){yaw-=dx*.003;pitch=THREE.MathUtils.clamp(pitch-dy*.003,-1.25,1.25);camera.quaternion.setFromEuler(new THREE.Euler(pitch,yaw,0,'YXZ'));needsRender=true;}pointer.lastX=event.clientX;pointer.lastY=event.clientY;});
    canvas.addEventListener('pointerup',event=>{canvasPointers.delete(event.pointerId);if(!pointer||pointer.id!==event.pointerId)return;if(!dragging&&Math.hypot(event.clientX-pointer.x,event.clientY-pointer.y)<6){const rect=canvas.getBoundingClientRect();pointerNDC.set((event.clientX-rect.left)/rect.width*2-1,-(event.clientY-rect.top)/rect.height*2+1);ray.setFromCamera(pointerNDC,camera);const hits=ray.intersectObject(mode==='product'?inspection:house,true);const root=hits.length&&findRoot(hits[0].object);if(root)selectProduct(root);}pointer=null;});
    const cancelPointer=event=>{canvasPointers.delete(event.pointerId);if(pointer?.id===event.pointerId)pointer=null;};canvas.addEventListener('pointercancel',cancelPointer);canvas.addEventListener('lostpointercapture',cancelPointer);canvas.addEventListener('wheel',event=>{if(mode==='walk'){event.preventDefault();camera.fov=THREE.MathUtils.clamp(camera.fov+event.deltaY*.025,30,82);camera.updateProjectionMatrix();needsRender=true;}},{passive:false});
    canvas.addEventListener('webglcontextlost',event=>{event.preventDefault();note('The graphics session was interrupted. Reload the page to reopen the model.');});
    window.addEventListener('keydown',event=>{if(!ready||!visible||document.querySelector('dialog[open]')||/INPUT|TEXTAREA|SELECT/.test(document.activeElement?.tagName))return;if(['KeyW','KeyA','KeyS','KeyD','ArrowUp','ArrowDown','ArrowLeft','ArrowRight'].includes(event.code)&&viewer.contains(document.activeElement)){event.preventDefault();keys.add(event.code);}if(event.code==='Escape'){keys.clear();if(mode==='product')goRoom(currentRoom);else closeSelection();}});
    window.addEventListener('keyup',event=>keys.delete(event.code));window.addEventListener('blur',stopMovement);document.addEventListener('visibilitychange',()=>{if(document.hidden)stopMovement();});
    for(const button of $$('[data-move]')){const stop=e=>{keys.delete(button.dataset.move);e.preventDefault();};button.addEventListener('pointerdown',event=>{event.preventDefault();button.setPointerCapture(event.pointerId);keys.add(button.dataset.move);});button.addEventListener('pointerup',stop);button.addEventListener('pointercancel',stop);button.addEventListener('lostpointercapture',()=>keys.delete(button.dataset.move));}
    requestAnimationFrame(animate);emit('tour:ready',{products:roots.length,parts:parts.length});
  }catch(error){console.error(error);$('#load-tour').disabled=false;$('#load-status').textContent='The 3D model could not be opened. Try again or request the GLB file.';note('WebGL is unavailable or the model failed to load. The render gallery and file requests are still available.');loading=false;}})();return start.promise;
}
export function initTour(){
  joystick=createJoystick($('#joystick'),value=>{walkInput=value;});
  let zoneNavigation=0;
  const jumpToZone=async id=>{const requestId=++zoneNavigation;stopMovement();if(!ready)await start();if(!ready||requestId!==zoneNavigation)return;if(id==='overview')overview();else goRoom(id);};
  $('#expanded-zone-select').replaceChildren(...[...$('#zone-select').options].map(option=>option.cloneNode(true)));
  $$('[data-zone-select]').forEach(el=>el.addEventListener('change',event=>jumpToZone(event.target.value)));
  $('#zoom-in').addEventListener('click',()=>zoomView(-1));$('#zoom-out').addEventListener('click',()=>zoomView(1));
  document.addEventListener('click',event=>{if(event.target.closest('[data-download-request]'))stopMovement();});
  document.addEventListener('keydown',event=>{if(!viewer.classList.contains('is-expanded')||document.querySelector('dialog[open]'))return;if(event.key==='Escape'){event.preventDefault();event.stopImmediatePropagation();setExpanded(false);}else if(event.key==='Tab'){const controls=[...viewer.querySelectorAll('button,select,[tabindex="0"]')].filter(el=>el.getClientRects().length&&!el.disabled),first=controls[0],last=controls.at(-1);if(event.shiftKey&&document.activeElement===first){event.preventDefault();last?.focus();}else if(!event.shiftKey&&document.activeElement===last){event.preventDefault();first?.focus();}}},true);
  $('#load-tour').addEventListener('click',()=>start());$$('[data-room]').forEach(b=>b.addEventListener('click',()=>jumpToZone(b.dataset.room)));
  $('#walk-mode').addEventListener('click',()=>goRoom(currentRoom));$('#orbit-mode').addEventListener('click',()=>overview());$('#back-house').addEventListener('click',()=>goRoom(currentRoom));$('#reset-view').addEventListener('click',()=>mode==='product'?inspect(inspectionSku):mode==='orbit'?overview():goRoom(currentRoom));
  $('#inspect-product').addEventListener('click',()=>inspect(selectionSku));$('#open-parts').addEventListener('click',toggleParts);$('#close-selection').addEventListener('click',closeSelection);
  $('#help-toggle').addEventListener('click',()=>{const help=$('#viewer-help');help.hidden=!help.hidden;$('#help-toggle').setAttribute('aria-expanded',String(!help.hidden));});$('#close-help').addEventListener('click',()=>{$('#viewer-help').hidden=true;$('#help-toggle').setAttribute('aria-expanded','false');});
  $('#fullscreen').addEventListener('click',()=>setExpanded(!viewer.classList.contains('is-expanded')));
  $('#map-toggle').addEventListener('click',()=>{const map=$('#floor-map'),hidden=!map.hasAttribute('hidden');map.toggleAttribute('hidden',hidden);$('#map-toggle').setAttribute('aria-expanded',String(!hidden));$('#map-toggle span').textContent=hidden?'＋':'−';});
  // Read-only diagnostics also support repeatable browser verification.
  window.hoian={get ready(){return ready},get mode(){return mode},get room(){return currentRoom},get selected(){return selectionSku},get productCount(){return roots.length},get partsCount(){return parts.length},get frames(){return frameCount},get position(){return camera?camera.position.toArray():null},get renderInfo(){return renderer?.info.render},inspect,goRoom,overview,toggleParts,canStand,
    get layout(){return sceneInfo?.layout},get wallCount(){return sceneInfo?.walls},get hasRoof(){return sceneInfo?.roof},get floorBounds(){return sceneInfo?.floorBounds},
    get overviewFraming(){if(!ready||mode!=='orbit')return null;camera.updateMatrixWorld();const points=exhibitionCorners().map(p=>p.project(camera)),maxX=Math.max(...points.map(p=>Math.abs(p.x))),maxY=Math.max(...points.map(p=>Math.abs(p.y)));return{fits:maxX<=1&&maxY<=1,maxX,maxY};},
    get orientation(){return camera?.quaternion.toArray()},get fov(){return camera?.fov},get zoomDistance(){return camera&&orbit?camera.position.distanceTo(orbit.target):null},get movement(){return{...walkInput}},
    productScreenPoint(sku){const root=roots.find(r=>r.userData.product_id===sku);if(!root)return null;camera.updateMatrixWorld();const center=new THREE.Box3().setFromObject(root).getCenter(new THREE.Vector3()).project(camera),r=canvas.getBoundingClientRect();return{x:r.left+(center.x+1)*r.width/2,y:r.top+(1-center.y)*r.height/2};},
    select:sku=>selectProduct(roots.find(r=>r.userData.product_id===sku)),
    partState:()=>selected?movingParts(selected).map(p=>({action:p.userData.action,open:p.userData.open,position:p.position.toArray(),quaternion:p.quaternion.toArray()})):[],
    validatePath:points=>points.every(([x,y])=>canStand(x,y)),
    async validateModels(){const results=[];for(const p of products){const g=await loader.loadAsync(p.model);let count=0;g.scene.traverse(o=>{if(o.isMesh)count++;});results.push({sku:p.sku,meshes:count,products:!!findProductNode(g.scene)});disposeModel(g.scene);}return results;}
  };
}
