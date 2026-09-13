(()=>{"use strict";
const init=()=>{
  const toggle=document.querySelector("[data-menu-toggle]");
  const nav=document.querySelector("[data-navlinks]");
  const header=document.querySelector(".site-header");
  if(!toggle||!nav||!header)return;
  const mq=matchMedia("(min-width:861px) and (max-width:1380px)");
  let backdrop=document.querySelector(".nav-panel-backdrop");
  if(!backdrop){
    backdrop=document.createElement("button");
    backdrop.type="button";
    backdrop.className="nav-panel-backdrop";
    backdrop.tabIndex=-1;
    backdrop.setAttribute("aria-hidden","true");
    backdrop.setAttribute("aria-label",(document.documentElement.lang||"").toLowerCase().startsWith("en")?"Close menu":"Cerrar menú");
    document.body.appendChild(backdrop);
  }
  nav.id||(nav.id="iberfit-nav-panel");
  toggle.setAttribute("aria-controls",nav.id);
  const targets=()=>Array.from(document.querySelectorAll("main,.site-footer,.footer,.device-dock,.wa-float")).filter(el=>el!==nav&&el!==toggle);
  const setInert=value=>targets().forEach(el=>{"inert"in el&&(el.inert=value)});
  const focusables=()=>[toggle,...Array.from(nav.querySelectorAll('a[href],button:not([disabled]),[tabindex]:not([tabindex="-1"])'))].filter(el=>{
    const s=getComputedStyle(el);return s.display!=="none"&&s.visibility!=="hidden"&&el.getClientRects().length>0&&!el.closest("[inert]");
  });
  let managedOpen=false;
  const setTop=()=>document.documentElement.style.setProperty("--nav-panel-top",Math.round(Math.max(0,header.getBoundingClientRect().bottom)+8)+"px");
  const cleanup=()=>{
    document.body.classList.remove("nav-panel-open");
    backdrop.classList.remove("is-visible");
    backdrop.setAttribute("aria-hidden","true");
    setInert(false);
    managedOpen=false;
  };
  const sync=()=>{
    setTop();
    if(!mq.matches){cleanup();return}
    const open=nav.classList.contains("open");
    document.body.classList.toggle("nav-panel-open",open);
    backdrop.classList.toggle("is-visible",open);
    backdrop.setAttribute("aria-hidden",String(!open));
    nav.setAttribute("aria-hidden",String(!open));
    setInert(open);
    if(open&&!managedOpen)queueMicrotask(()=>nav.querySelector("a[href]")?.focus({preventScroll:true}));
    else if(!open&&managedOpen)queueMicrotask(()=>toggle.focus({preventScroll:true}));
    managedOpen=open;
  };
  new MutationObserver(sync).observe(nav,{attributes:true,attributeFilter:["class"]});
  toggle.addEventListener("click",()=>queueMicrotask(sync));
  backdrop.addEventListener("click",()=>{if(mq.matches&&nav.classList.contains("open"))toggle.click()});
  document.addEventListener("keydown",event=>{
    if(!mq.matches)return;
    if(event.key==="Escape"){queueMicrotask(sync);return}
    if(event.key!=="Tab"||!nav.classList.contains("open"))return;
    const items=focusables();if(!items.length)return;
    const idx=items.indexOf(document.activeElement);
    if(event.shiftKey&&idx<=0){event.preventDefault();items[items.length-1].focus()}
    else if(!event.shiftKey&&idx===items.length-1){event.preventDefault();items[0].focus()}
  });
  const onMedia=()=>{if(!mq.matches&&nav.classList.contains("open"))toggle.click();queueMicrotask(sync)};
  mq.addEventListener?mq.addEventListener("change",onMedia):mq.addListener(onMedia);
  addEventListener("resize",()=>{setTop();queueMicrotask(sync)},{passive:true});
  sync();
};
document.readyState==="loading"?document.addEventListener("DOMContentLoaded",init,{once:true}):init();
})();