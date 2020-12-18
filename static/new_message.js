
let $newWarbleForm = $("#new-warble-form");

async function handleNewWarbleSubmit(evt){
  evt.preventDefault();
  $form = $(evt.target);
  let data = $form.serialize();
  await $.post(`/messages/new`, data=data);
}


$newWarbleForm.on("submit", handleNewWarbleSubmit);




