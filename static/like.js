$likeForm = $(".not-liked")
$unlikeForm = $(".liked")



async function handleLikeSubmit(evt){
  evt.preventDefault();
  let $form = $(evt.target);
  let messageId = $form.attr("id");
  let data = $form.serialize();
  if ($form.hasClass("liked")){
    await $.post(`/messages/${messageId}/unlike`, data=data)
  }
  else{
    await $.post(`/messages/${messageId}/like`, data=data)
  }
  $form.children().children("i").toggleClass(["fas", "far"])
  $form.toggleClass(["liked", "not-liked"])
}

$likeForm.on("submit", handleLikeSubmit)
$unlikeForm.on("submit", handleLikeSubmit)