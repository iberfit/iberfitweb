(()=>{"use strict";
let raf=0;
const showNearViewport=()=>{
  raf=0;
  const vh=window.innerHeight||document.documentElement.clientHeight||800;
  document.querySelectorAll(".reveal:not(.visible)").forEach(el=>{
    const r=el.getBoundingClientRect();
    if(r.bottom>=-vh*.15&&r.top<=vh*1.15) el.classList.add("visible");
  });
};
const schedule=()=>{
  if(raf)return;
  raf=requestAnimationFrame(showNearViewport);
};
const boot=()=>{
  window.setTimeout(showNearViewport,1200);
  window.addEventListener("scroll",schedule,{passive:true});
  window.addEventListener("resize",schedule,{passive:true});
  window.addEventListener("pageshow",schedule);
};
if(document.readyState==="loading") document.addEventListener("DOMContentLoaded",boot,{once:true});
else boot();
})();