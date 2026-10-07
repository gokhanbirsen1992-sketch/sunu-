/* Çevrimdışı destek: kendi dosyalarımız için önce ağ, olmazsa önbellek; yazı tipleri için önce önbellek. */
var C='gis-araclari-v1';
var FILES=['./','./index.html','./ortak.css','./ortak.js','./manifest.webmanifest','./icon-192.png','./icon-512.png',
  './yabanci-cisim/','./yabanci-cisim/index.html','./eozinofilik-ozofajit/','./eozinofilik-ozofajit/index.html'];
self.addEventListener('install',function(e){e.waitUntil(caches.open(C).then(function(c){return c.addAll(FILES);}).then(function(){return self.skipWaiting();}));});
self.addEventListener('activate',function(e){e.waitUntil(caches.keys().then(function(ks){return Promise.all(ks.filter(function(k){return k!==C;}).map(function(k){return caches.delete(k);}));}).then(function(){return self.clients.claim();}));});
self.addEventListener('fetch',function(e){
  if(e.request.method!=='GET')return;
  var u=new URL(e.request.url);
  var put=function(r){var cp=r.clone();caches.open(C).then(function(c){c.put(e.request,cp);});return r;};
  if(u.origin===self.location.origin){
    e.respondWith(fetch(e.request).then(put).catch(function(){return caches.match(e.request,{ignoreSearch:true});}));
  } else if(/(^|\.)fonts\.(googleapis|gstatic)\.com$/.test(u.hostname)){
    e.respondWith(caches.match(e.request).then(function(m){return m||fetch(e.request).then(put);}));
  }
});
