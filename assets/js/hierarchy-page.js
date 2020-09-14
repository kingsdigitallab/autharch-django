$(document).ready(function() {
    var maxCellWidth = 0;
    $('#hierarchy .fieldset-header a.dotted-underline').each(function() {
        maxCellWidth = Math.max($(this).width(), maxCellWidth);
    });
    if (maxCellWidth < 400) {
        $('#hierarchy .hierarchy-header').css('grid-template-columns',  '28px ' + (maxCellWidth + 65) +'px 400px');
        $('#hierarchy .fieldset-header').css('grid-template-columns', '0.01fr ' + (maxCellWidth + 65) +'px 400px');
        $('#hierarchy .fieldset-body .fieldset-header').css('grid-template-columns', '0.01fr ' + (maxCellWidth + 40) +'px 400px');  
    }
});
  
function hierarchyInstantSearch() {
    let query = $(event.target).val().toLowerCase();
    $('.fieldset-header').find('span').removeClass('greyed-out');
    $('.child-level').children('.fieldset-body').removeClass('expand');
    $('.expand-collapse > button').text('Collapse all');
    $('.parent-level').removeClass('not-expanded')
    $('.fieldset-header').find('a.dotted-underline').each(function() {
        let option = $(this).text().toLowerCase();
        if (!option.includes(query)) {
        $(this).parents('.fieldset-header').first().find('span').addClass('greyed-out');
        } else {
        $(this).parents('.child-level').find('.fieldset-body').addClass('expand');
        }
    });
}