/* IBERFIT V6.22 · Production analytics configuration
   Public measurement identifiers only. No passwords, tokens or secrets belong here. */
window.IBERFIT_ANALYTICS = Object.freeze({
  ga4MeasurementId: "G-JXD1JSN7K3",
  metaPixelId: "1784253392559009",
  consentVersion: "2026-07-12-v2",
  debug: false
});

/* Optional acquisition attribution. Stores only an allowlisted source category
   after audience consent. No message, identity, raw referrer or query storage. */
(() => {
  'use strict';
  const consentKey = 'iberfit_consent_v2', sourceKey = 'iberfit_acquisition_v1';
  const hosts = Object.freeze({
    'chatgpt.com':'chatgpt','chat.openai.com':'chatgpt','perplexity.ai':'perplexity',
    'gemini.google.com':'gemini','copilot.microsoft.com':'copilot','claude.ai':'claude',
    'google.com':'google','google.cl':'google','bing.com':'bing',
    'instagram.com':'instagram','facebook.com':'facebook'
  });
  const tags = Object.freeze({...hosts,chatgpt:'chatgpt',openai:'chatgpt',perplexity:'perplexity',
    gemini:'gemini',copilot:'copilot',claude:'claude',google:'google',bing:'bing',
    instagram:'instagram',facebook:'facebook'});
  const allowed = new Set([...Object.values(tags),'direct','other_external','internal_unknown']);
  const permitted = () => {
    try {
      const c = JSON.parse(localStorage.getItem(consentKey)||'null');
      return c?.version===window.IBERFIT_ANALYTICS.consentVersion && c.analytics===true;
    } catch { return false; }
  };
  function inbound() {
    try {
      const v=(new URL(location.href).searchParams.get('utm_source')||'').trim().toLowerCase();
      if(Object.hasOwn(tags,v)) return tags[v];
    } catch {}
    try {
      if(!document.referrer) return null;
      const r=new URL(document.referrer),h=r.hostname.toLowerCase();
      if(r.origin===location.origin||h==='iberfit.cl'||h.endsWith('.iberfit.cl')) return null;
      for(const domain of Object.keys(hosts)){
        if(h===domain||h.endsWith('.'+domain)) return hosts[domain];
      }
      return 'other_external';
    } catch { return null; }
  }
  let emitted=false,source=null;
  function resolve() {
    if(!permitted()){
      source=null;emitted=false;
      try { sessionStorage.removeItem(sourceKey); } catch {}
      return null;
    }
    if(source) return source;
    let stored=null;
    try { stored=sessionStorage.getItem(sourceKey); } catch {}
    source=inbound()||(allowed.has(stored)?stored:null)||(document.referrer?'internal_unknown':'direct');
    try { sessionStorage.setItem(sourceKey,source); } catch {}
    return source;
  }
  document.addEventListener('DOMContentLoaded',()=>{
    const track=window.iberfitTrack;
    if(typeof track!=='function') return;
    const safePage=()=>({page_location:location.origin+location.pathname,page_referrer:''});
    function emit(category){
      if(category&&!emitted){
        emitted=true;
        track('acquisition_context',{...safePage(),acquisition_source:category});
      }
    }
    window.iberfitTrack=(name,params={})=>{
      const category=resolve();
      if(category){
        emit(category);
        return track(name,{...params,...safePage(),acquisition_source:category});
      }
      return track(name,params);
    };
    emit(resolve());
  });
})();
