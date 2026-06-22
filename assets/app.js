
(function(){
  const toggle=document.querySelector('[data-menu-toggle]');
  const nav=document.querySelector('[data-navlinks]');
  if(toggle&&nav){
    toggle.addEventListener('click',()=>{
      const open=nav.classList.toggle('open');
      toggle.setAttribute('aria-expanded', open ? 'true':'false');
    });
  }
  document.querySelectorAll('a[href^="#"]').forEach(a=>{
    a.addEventListener('click',()=>{
      if(nav) nav.classList.remove('open');
      if(toggle) toggle.setAttribute('aria-expanded','false');
    });
  });
})();
