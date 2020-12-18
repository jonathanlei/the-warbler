
let $newWarbleForm = $("#new-warble-form");

async function handleNewWarbleSubmit(evt){
  evt.preventDefault();
  $form = $(evt.target);
  let data = $form.serialize();
  let message_html = await $.post(`/messages/new`, data=data);
  let user_id = $('#user_id').data("userid")
  $("#home-messages").prepend(message_html)
  $(`#${user_id}-messages`).prepend(message_html)
}


$newWarbleForm.on("submit", handleNewWarbleSubmit);
