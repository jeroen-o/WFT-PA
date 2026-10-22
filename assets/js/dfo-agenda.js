/* Verbergt verlopen activiteiten in de DFO-agenda en toont een melding als er niets meer staat. */
(function () {
  var d = new Date(), t = d.getFullYear() + '-' + ('0' + (d.getMonth() + 1)).slice(-2) + '-' + ('0' + d.getDate()).slice(-2);
  var items = document.querySelectorAll('.ag-item'), zichtbaar = 0;
  for (var i = 0; i < items.length; i++) {
    if (items[i].getAttribute('data-datum') < t) items[i].hidden = true; else zichtbaar++;
  }
  var leeg = document.getElementById('ag-leeg');
  if (leeg) leeg.hidden = zichtbaar > 0;
})();
