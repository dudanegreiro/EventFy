function filterCards(){
  const q=(document.getElementById('search')?.value||'').toLowerCase();
  const cat=document.getElementById('category')?.value||'';
  document.querySelectorAll('.card').forEach(card=>{
    const okName=card.dataset.name.toLowerCase().includes(q);
    const okCat=!cat || card.dataset.category===cat;
    card.style.display=(okName&&okCat)?'block':'none';
  });
}
function enviarSolicitacao(){
  window.location.href='recusada.html';
  return false;
}
