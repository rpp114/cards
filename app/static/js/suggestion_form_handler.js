$(document).ready(function(){

    var card_suggestion_form = `<div class="modal" id="modal">
      <div class="modal-background" onClick="close_modal()"></div>
      <div class="modal-card">
        <header class="modal-card-head">
          <p class="modal-card-title" id="modal_card_name"></p>
        </header>
        <section class="modal-card-body">
          <form action="{{url_for('suggestion')}}" method="post" name="bonus_suggestion">
            <input type="hidden" id="card_id_input" value="" name="add" />
            <div class="field is-horizontal">
              <span class="field-label">
                <label class="label">Activation Date:</label>
              </span>
            <div class="field-body">
            <div class="control">
              <input type="text" class="date_input" name="activation_date" />
            </div>
          </div>
          </div>
            <div class="field is-horizontal">
              <span class="field-label">
                <label class="label">Expiration Date:</label>
              </span>
            <div class="field-body is-right">
            <div class="control">
              <input type="text" class="date_input" name="expiration_date" />
            </div>
          </div>
          </div>
        </section>
        <footer class="modal-card-foot">
          <span class="level">
            <div class="level-left">
            <div class="level-item">

            <button class="button is-success is-small" type="submit">Add to Wallet</button>
          </div>
          </div>
            <div class="level-right">
            <div class="level-item">
              <button class="button is-light is-small" id="cancel_button" type="button" onClick="close_modal()">Cancel</button>
          </div>
          </div>
          </span>
        </footer>
        </form>
      </div>
    </div>`

    $('.suggest_signup').click(function(card_id, user_id){
        console.log('Hello');
        $(card_suggestion_form).insertAfter(this);
        show_suggestion_modal(card_id, user_id);
    })




})

function show_suggestion_modal(card_id, user_id){
  document.getElementById('modal').classList.add('is-active');
};

function close_modal(){
  document.getElementById('modal').classList.remove('is-active');
};
