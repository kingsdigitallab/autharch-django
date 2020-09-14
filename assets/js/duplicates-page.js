$(document).ready(function() {
    $('select[name="entity"]').select2({
        placeholder: 'Add a duplicate by record ID or display name',
        allowClear: true
    });
});

/**
 * Populate confirmation modal with form data and then show it.
 */
function confirmMergeAction(modalName, action, entityId) {
    $('.modal').find('.move-from').text('Record ID: ' + entityId + ' - ').append($(event.target).parent('.cta').next('.record').children('a:first-of-type').text());
    $('.modal').find('#id_entity_id').attr('value', entityId);
    $('.modal').find('#id_action').attr('value', action);
    if (action == 'merge') {
        $('.modal').find('.action').text('merge into:');
    } else if (action == 'mark') {
        $('.modal').find('.action').text('is not a duplicate of:');
    }
    showModal(modalName);
}