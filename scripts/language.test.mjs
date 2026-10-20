import test from 'node:test';import assert from 'node:assert/strict';import {readFile} from 'node:fs/promises';
test('HOI AN English publication and correct catalogue scope',async()=>{
 const files=await Promise.all(['index.html','credits.html','app.js','tour.js','contact.js'].map(f=>readFile(new URL('../dist/'+f,import.meta.url),'utf8')));
 assert.match(files[0],/<html lang="en">/);assert.match(files[1],/<html lang="en">/);
 for(const s of files){assert.doesNotMatch(s,/SIENNA|WARM BROWN|chevron|LV463|LV446|Dining collection|Living collection|unduh|ruangan|hubungi/i);}
 assert.match(files[0],/Muhammad Rizky/);assert.match(files[0],/GOLDEN SYRUP/);assert.match(files[0],/Want a project like this\? Get in touch with me on WhatsApp\./);
 assert.match(files[3],/window\.hoian=/);assert.match(files[3],/hoi-an-exhibition\.glb/);assert.match(files[0],/public website assets are not access-controlled/);
});
