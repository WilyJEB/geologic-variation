/* Optional control unit check. This is NOT a browser/layout test. */
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const path=require('node:path');
const page=fs.readFileSync(path.join(__dirname,'../docs/evidence/td-story.html'),'utf8');
const button={hidden:true,textContent:'Hide conceptual domains',addEventListener(_,f){this.click=f}};
const overlays=Array.from({length:30},()=>({style:{}}));
const document={getElementById:id=>{assert.equal(id,'toggle');return button},querySelectorAll:s=>{assert.equal(s,'.domain,.contact');return overlays}};
vm.runInNewContext(page.match(/<script>([\s\S]*?)<\/script>/)[1],{document});
assert.equal(button.hidden,false);button.click();
assert(overlays.every(e=>e.style.visibility==='hidden'));
assert.equal(button.textContent,'Show conceptual domains');button.click();
assert(overlays.every(e=>e.style.visibility==='visible'));
assert.equal(button.textContent,'Hide conceptual domains');
console.log('PASS optional story overlay control; actual browser layout unverified');
