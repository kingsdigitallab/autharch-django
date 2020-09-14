$(document).ready(function() {
  $('.select2-search__field:not(:disabled)').each(function() {
    if ($(this).attr('placeholder') == '') {
    $(this).attr('placeholder', 'Enter your search term...');
    }
  });
});

/**
 * Create confirmation modal dialogue with form to delete the current
 * record (whether Archival Record or Entity), to merge two records, or to mark them as not related.
 */
function showModal(modalName) {
  $('#'+modalName).addClass('active');
}

function hideModal() {
  $(event.target).parents('.modal').first().removeClass('active');
}

function removeNotification() {
  $(event.target).parent().remove();
}

// expand/collapse entity/archival record sections and individual sections on the hierarchy page
function toggleTab() {
  event.preventDefault();
  let header = $(event.target).closest('.fieldset-header');
  $(header).siblings('.fieldset-body').first().toggleClass('expand');
  $(header).find('.toggle-tab-button').toggleClass('active');
  $(header).find('.toggle-tab-button').attr('aria-expanded', String($(header).find('.toggle-tab-button').attr('aria-expanded') !== 'true'));
}

// expand collapse fieldsets on the hierarchy and form pages
function toggleExpand() {
  event.preventDefault();
  let action = $(event.target).attr('data-toggle');
  if (action == 'expand') {
      $('.fieldset-body').not('.parent-level > .fieldset-body').addClass('expand');
      $('.toggle-tab-button').not('.parent-level .fieldset-header .toggle-tab-button').addClass('active');
      $(event.target).text('Collapse all');
      $(event.target).attr('data-toggle', 'collapse');
  } else {
      $('.fieldset-body').not('.parent-level > .fieldset-body').removeClass('expand');
      $('.toggle-tab-button').not('.parent-level .fieldset-header .toggle-tab-button').removeClass('active');
      $(event.target).text('Expand all');
      $(event.target).attr('data-toggle', 'expand');
  }
}