/* Ortak arayüz: sekmeler (#bağlantı), soru sihirbazı, sonuç kartı, yapışık özet, özet kopyalama. */
(function(){
  'use strict';
  var SRC=(document.currentScript&&document.currentScript.src)||'';
  var $=function(s){return document.querySelector(s);};
  var reduce=function(){try{return matchMedia('(prefers-reduced-motion: reduce)').matches;}catch(e){return false;}};
  var strip=function(h){var d=document.createElement('div');d.innerHTML=h;return (d.textContent||'').replace(/\s+/g,' ').trim();};

  function tabs(){
    var btns=[].slice.call(document.querySelectorAll('nav.tabs [role=tab]'));
    function act(b,focus,keepHash){
      btns.forEach(function(x){var on=x===b;x.setAttribute('aria-selected',on?'true':'false');x.tabIndex=on?0:-1;
        document.getElementById(x.getAttribute('aria-controls')).hidden=!on;});
      if(focus)b.focus();
      if(!keepHash){try{history.replaceState(null,'','#'+b.dataset.h);}catch(e){}}
    }
    btns.forEach(function(b,i){
      b.addEventListener('click',function(){act(b);});
      b.addEventListener('keydown',function(e){var j=null,n=btns.length;
        if(e.key==='ArrowRight')j=(i+1)%n; else if(e.key==='ArrowLeft')j=(i-1+n)%n; else if(e.key==='Home')j=0; else if(e.key==='End')j=n-1;
        if(j!==null){e.preventDefault();act(btns[j],true);}});
    });
    var h=(location.hash||'').slice(1), t=btns.filter(function(b){return b.dataset.h===h;})[0]||btns[0];
    act(t,false,true);
    return function(name){var b=btns.filter(function(x){return x.dataset.h===name;})[0]; if(b)act(b);};
  }

  function copyText(t,btn,label){
    var done=function(){btn.textContent='Kopyalandı ✓';setTimeout(function(){btn.textContent=label;},2000);};
    var fallback=function(){
      var ta=document.createElement('textarea');ta.value=t;ta.setAttribute('readonly','');ta.style.cssText='position:fixed;top:0;left:0;opacity:0';
      document.body.appendChild(ta);ta.select();var ok=false;try{ok=document.execCommand('copy');}catch(e){}ta.remove();
      if(ok){done();return;}
      var box=btn.parentNode.querySelector('.copybox');
      if(!box){box=document.createElement('textarea');box.className='copybox';btn.parentNode.appendChild(box);}
      box.value=t;box.focus();box.select();btn.textContent='Metni seçip kopyalayın';
    };
    try{ if(navigator.clipboard&&navigator.clipboard.writeText){navigator.clipboard.writeText(t).then(done,fallback);} else fallback(); }catch(e){fallback();}
  }

  /* cfg: {Q, decide, LV, tool, source, form, result, reset, sticky}
     Q: [{k,label,hint,step,show(S),opts:[[v,text]],optional}]
     decide(S) -> null | {k, lvl?, sub?, act:[], ev:[], flags:[]} */
  function wizard(cfg){
    var S={}, form=$(cfg.form), box=$(cfg.result), sticky=$(cfg.sticky), lastKey='';
    function visibleQs(){var out=[];cfg.Q.forEach(function(q){if(q.show&&!q.show(S)){delete S[q.k];return;}out.push(q);});return out;}
    function scrollToQ(k){var el=form.querySelector('[data-k="'+k+'"]');if(el)el.scrollIntoView({behavior:reduce()?'auto':'smooth',block:'center'});}
    function answers(qs){return qs.filter(function(q){return S[q.k]!==undefined;}).map(function(q){
      var t=q.opts.filter(function(o){return o[0]===S[q.k];})[0];return [q.label,t?t[1]:S[q.k]];});}
    function summary(r,lvl,sub,qs){
      var d=new Date(), p=function(n){return (n<10?'0':'')+n;};
      var L=[cfg.tool+' — '+p(d.getDate())+'.'+p(d.getMonth()+1)+'.'+d.getFullYear()+' '+p(d.getHours())+':'+p(d.getMinutes()),''];
      answers(qs).forEach(function(a){L.push(a[0]+' '+a[1]);});
      L.push('','KARAR: '+lvl+(sub?' — '+sub:''));
      (r.act||[]).forEach(function(a){L.push('- '+strip(a));});
      (r.flags||[]).forEach(function(a){L.push('Not: '+strip(a));});
      L.push('','Kaynak: '+cfg.source,'Karar desteğidir; klinik yargının yerine geçmez.');
      return L.join('\n');
    }
    function render(){
      var qs=visibleQs(); form.innerHTML=''; var lastStep='';
      qs.forEach(function(q){
        if(q.step&&q.step!==lastStep){var h=document.createElement('div');h.className='step';h.textContent=q.step;form.appendChild(h);lastStep=q.step;}
        var d=document.createElement('div');d.className='q'+(q.optional?' opt':'');d.dataset.k=q.k;
        d.innerHTML='<div class="label">'+q.label+'</div>'+(q.hint?'<div class="hint">'+q.hint+'</div>':'')+'<div class="opts" role="group"></div>';
        var o=d.querySelector('.opts');
        q.opts.forEach(function(op){var b=document.createElement('button');b.type='button';b.id='q-'+q.k+'-'+op[0];b.textContent=op[1];
          b.setAttribute('aria-pressed',S[q.k]===op[0]?'true':'false');
          b.addEventListener('click',function(){
            if(S[q.k]===op[0]&&q.optional){delete S[q.k];} else S[q.k]=op[0];
            var after=false; cfg.Q.forEach(function(qq){if(after&&!qq.keep)delete S[qq.k]; if(qq.k===q.k)after=true;});
            render();});
          o.appendChild(b);});
        form.appendChild(d);
      });
      var r=cfg.decide(S), pending=qs.filter(function(q){return S[q.k]===undefined&&!q.optional;});
      if(!r){
        box.className='result empty';
        var nx=pending[0];
        box.innerHTML='<div class="band"><div class="lvl">'+(Object.keys(S).length?'Devam et':'Soruları cevapla')+'</div>'+
          (nx?'<div class="sub">Sıradaki: <button type="button" data-go="'+nx.k+'">'+strip(nx.label)+'</button></div>':'')+'</div>';
        var g=box.querySelector('[data-go]'); if(g)g.addEventListener('click',function(){scrollToQ(g.dataset.go);});
        lastKey=''; updSticky(null); return;
      }
      var lv=cfg.LV[r.k]||['',''], lvl=r.lvl||lv[0], sub=(r.sub!==undefined&&r.sub!==null)?r.sub:lv[1];
      var sec=function(t,a){return a&&a.length?'<div><h3>'+t+'</h3><ul>'+a.map(function(x){return '<li>'+x+'</li>';}).join('')+'</ul></div>':'';};
      var ev=r.ev&&r.ev.length?'<details><summary>Kanıt (makaleden)</summary><ul>'+r.ev.map(function(x){return '<li>'+x+'</li>';}).join('')+'</ul></details>':'';
      var more=pending.length?'<div class="more">Ayrıntı için cevapla: '+pending.map(function(q){return '<button type="button" data-go="'+q.k+'">'+strip(q.label)+'</button>';}).join(' · ')+'</div>':'';
      box.className='result';
      box.innerHTML='<div class="band k-'+r.k+'"><div class="lvl">'+lvl+'</div>'+(sub?'<div class="sub">'+sub+'</div>':'')+'</div>'+
        '<div class="body">'+sec('Yap',r.act)+(r.flags||[]).map(function(x){return '<div class="flag">'+x+'</div>';}).join('')+ev+more+
        '<div class="copyrow"><button type="button" class="btn" id="copy">Özeti kopyala</button></div></div>';
      [].forEach.call(box.querySelectorAll('[data-go]'),function(g){g.addEventListener('click',function(){scrollToQ(g.dataset.go);});});
      var cb=box.querySelector('#copy'); cb.addEventListener('click',function(){copyText(summary(r,lvl,sub,qs),cb,'Özeti kopyala');});
      var key=r.k+'|'+lvl+'|'+sub;
      if(key!==lastKey){lastKey=key; if(Object.keys(S).length) setTimeout(function(){box.scrollIntoView({behavior:reduce()?'auto':'smooth',block:'start'});},30);}
      updSticky({k:r.k,lvl:lvl,sub:sub});
    }
    var cur=null;
    function inView(){var r=box.getBoundingClientRect(),h=window.innerHeight||document.documentElement.clientHeight;return r.top<h-60&&r.bottom>60;}
    function updSticky(x){if(x!==undefined)cur=x; if(!sticky)return; if(!cur||inView()||box.offsetParent===null){sticky.hidden=true;return;}
      sticky.className='sticky k-'+cur.k; sticky.textContent=cur.lvl+(cur.sub?' · '+cur.sub:'')+'  ▸'; sticky.hidden=false;}
    if(sticky){
      sticky.addEventListener('click',function(){box.scrollIntoView({behavior:reduce()?'auto':'smooth',block:'start'});});
      var tk=false; var onS=function(){if(tk)return;tk=true;requestAnimationFrame(function(){tk=false;updSticky();});};
      window.addEventListener('scroll',onS,{passive:true}); window.addEventListener('resize',onS);
      document.addEventListener('click',function(){setTimeout(onS,50);});
    }
    if(cfg.reset)$(cfg.reset).addEventListener('click',function(){Object.keys(S).forEach(function(k){delete S[k];});lastKey='';render();window.scrollTo({top:0,behavior:reduce()?'auto':'smooth'});});
    render();
    return {S:S,render:render,set:function(k,v){S[k]=v;render();}};
  }

  function store(key){
    return {get:function(){try{var v=JSON.parse(localStorage.getItem(key)||'null');if(v&&Date.now()-v.t<12*3600e3)return v;}catch(e){}return null;},
      set:function(o){try{o.t=Date.now();localStorage.setItem(key,JSON.stringify(o));}catch(e){}},
      clear:function(){try{localStorage.removeItem(key);}catch(e){}}};
  }

  try{ if(SRC&&'serviceWorker' in navigator&&(location.protocol==='https:'||location.hostname==='localhost')){navigator.serviceWorker.register(new URL('sw.js',SRC).href).catch(function(){});} }catch(e){}

  window.Ortak={tabs:tabs,wizard:wizard,copyText:copyText,store:store,strip:strip};
})();
