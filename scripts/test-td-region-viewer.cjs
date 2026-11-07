/* Offline JavaScript DOM-stub checks, NOT a real browser/layout test. */
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict'),path=require('node:path');
const html=fs.readFileSync(path.join(__dirname,'../docs/evidence/td-region-visual.html'),'utf8');
class E{constructor(tag){this.tag=tag;this.attrs={};this.children=[];this.handlers={};this.checked=true;this.value='height';this.textContent='';this.innerHTML=''}setAttribute(k,v){this.attrs[k]=v}append(e){this.children.push(e)}addEventListener(k,f){this.handlers[k]=f}replaceChildren(){this.children=[]}}
const names=['seed','terrain','layer','regions','contacts','scale','checks','inspect'];
const dom=Object.fromEntries(names.map(n=>[n,new E(n)]));
const document={createElementNS:(_,tag)=>new E(tag),getElementById:n=>dom[n],querySelector:s=>dom[s.slice(1)],querySelectorAll:()=>['layer','regions','contacts'].map(n=>dom[n])};
const code=html.match(/<script>([\s\S]*?)<\/script>/)[1];
assert(!code.includes('__RESULT__'));
vm.runInNewContext(code,{document,console});
function find(root,tag){return root.children.flatMap(c=>[...(c.tag===tag?[c]:[]),...find(c,tag)])}
for(const id of ['seed','terrain']){
 assert.equal(find(dom[id],'circle').length,2401);
 assert.equal(find(dom[id],'polygon').length,4);
 assert.equal(find(dom[id],'polyline').length,6);
 assert.equal(find(dom[id],'line').length,6);
}
assert(dom.checks.innerHTML.includes('149 / 2401'));
find(dom.terrain,'circle')[24*49+24].handlers.click();
assert(dom.inspect.textContent.includes('native x=4224, z=12416'));
assert(dom.inspect.textContent.includes('surface = deep history'));
assert(dom.inspect.textContent.includes('Observation error: unknown'));
dom.layer.value='difference';dom.layer.handlers.change();
assert.equal(find(dom.seed,'circle').filter(e=>e.attrs.fill==='#999').length,192);
dom.contacts.checked=false;dom.contacts.handlers.change();
assert.equal(find(dom.terrain,'polyline').length,0);
dom.regions.checked=false;dom.regions.handlers.change();
assert.equal(find(dom.terrain,'polygon').length,0);
console.log('PASS offline viewer JS: sites, contacts, evidence toggle, inspection and conceptual overlays; browser layout unverified');
