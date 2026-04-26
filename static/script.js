function toggleInterp(id, btn) {
  const box = document.getElementById(id);
  const isOpen = box.style.display === 'block';
  box.style.display = isOpen ? 'none' : 'block';
  btn.classList.toggle('open', !isOpen);
  btn.textContent = isOpen ? "Voir l'interprétation" : "Masquer l'interprétation";
}
function toggleHyp(id, card) {
  const panel = document.getElementById(id);
  const isOpen = panel.classList.contains('active');
  
  // Ferme tous les panels du même groupe
  const allCards = card.parentElement.querySelectorAll('.hyp-card');
  allCards.forEach(c => c.classList.remove('active'));
  
  // Ferme tous les panels après cette grille
  const grid = card.parentElement;
  let next = grid.nextElementSibling;
  while (next && next.classList.contains('hyp-panel')) {
    next.classList.remove('active');
    next = next.nextElementSibling;
  }
  
  if (!isOpen) {
    card.classList.add('active');
    panel.classList.add('active');
  }
}