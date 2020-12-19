
let $newWarbleForm = $("#new-warble-form");

async function handleNewWarbleSubmit(evt){
  evt.preventDefault();
  $form = $(evt.target);
  let data = $form.serialize();
  let message_html = await $.post(`/messages/new`, data=data);
  $("ul#messages[data-page='home']").prepend(message_html);
  let user_id = $('#user_id').data("userid")
  if ($("ul>li").data("userid") === user_id){
    $("ul#messages[data-page='show-user']").prepend(message_html);
  }
}


$newWarbleForm.on("submit", handleNewWarbleSubmit);
