
let $newWarbleForm = $("#new-warble-form");

async function handleNewWarbleSubmit(evt){
  evt.preventDefault();
  $form = $(evt.target);
  let data = $form.serialize();
  let message_html = await $.post(`/messages/new`, data=data);
  $("ul[data-page='home']").prepend(message_html);
  $("ul[data-page='show-user']").prepend(message_html);
}


$newWarbleForm.on("submit", handleNewWarbleSubmit);
