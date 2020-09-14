$(document).ready(function() {
});

function deleteRow(el) {
    if (!$(el).parent().siblings('td').hasClass('none')) {
      $(el).parent().siblings('td').addClass('none');
      $(el).parent().attr('colspan', '6');
      $(el).after(`<span class="confirm-deletion"><i class="fas fa-trash-alt"></i><input name="all_users_submit" aria-label="save admin table" type="submit" class="button-link danger" value="Delete permanently and save table" /></span>`)
    } else {
      $(el).parent().attr('colspan', '1');
      $(el).parent().siblings('td').removeClass('none');
      $(el).siblings('.confirm-deletion').remove();
    }
    // Find and toggle the DELETE checkbox for the form.
    let deleteField = $(el).closest('[data-form-type]').find('[class~="delete-form-field"]').find('[name$="DELETE"]').first();
    deleteField.prop('checked', !deleteField.prop('checked'));
}