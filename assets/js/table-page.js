$(document).ready(function() {
      initTablesorter();
      initFilters();
      initCreationYearSlider();
});
  
// sorter for the archival records table - Collection -> Series -> File -> Item
function initTablesorter() {
    $.tablesorter.addParser({
        id: 'level',
        is: function(s) {
        return false;
        },
        format: function(s) {
        return s.toLowerCase()
                .replace("collection", "0")
                .replace("series", "1")
                .replace("file", "2")
                .replace("item", "3");
        },
        type: 'numeric'
    });  
    $('.tablesorter').each(function(i, el) {
        $.tablesorter.customPagerControls({
        table          : $('#'+$(el).attr('id')),                   // point at correct table (string or jQuery object)
        pager          : $('#'+$(el).parent('.table-container').next('.pager').attr('id')),                   // pager wrapper (string or jQuery object)
        pageSize       : '.page-size a',                // container for page sizes
        currentPage    : '.page-list a',               // container for page selectors
        ends           : 2,                        // number of pages to show of either end
        aroundCurrent  : 1,                        // number of pages surrounding the current page
        link           : '<a href="#" class="page">{page}</a>', // page element; use {page} to include the page number
        currentClass   : 'current',                // current page class name
        adjacentSpacer : '',       // spacer for page numbers next to each other
        distanceSpacer : '<span> &#133; <span>',   // spacer for page numbers away from each other (ellipsis = &#133;)
        addKeyboard    : true,                     // use left,right,up,down,pageUp,pageDown,home, or end to change current page
        pageKeyStep    : 10                        // page step to use for pageUp and pageDown
        });
        //add tablesorter to the tables; had to go with an if-statement because tablesorter parameters cannot be modified once linked to a table
        if ($(el).attr('id') === 'records-list-table') {
        $('#records-list-table')
            .tablesorter({
                widgets: ['filter'],
                widgetOptions: {
                    filter_columnFilters: true,
                    filter_filterLabel: 'Filter by {{label}}',
                },
                sortList: [[2,0]],
                headers: {
                2: {
                    sorter: 'level'
                }
                }
            })
        
        } 
        else if ($(el).attr('id') === 'deleted-records-table') {
        $('#'+$(el).attr('id'))
            .tablesorter({
                sortList: [[2,1]],
                widgets: ['filter'],
                widgetOptions: {
                    filter_columnFilters: true,
                    filter_filterLabel : 'Filter by {{label}}',
                }
            })
        }
        else {
        $('#'+$(el).attr('id'))
            .tablesorter({
                sortList: [[3,1]],
                widgets: ['filter'],
                widgetOptions: {
                    filter_columnFilters: true,
                    filter_filterLabel : 'Filter by {{label}}',
                }
            })
        }

        $('#'+$(el).attr('id')).tablesorterPager({
        container: $('#'+$(el).parent('.table-container').next('.pager').attr('id')),
        size: 10
        });
        
        //  make sure that corrent 'rows per page' number is active
        var rowsPerPage = $('#'+$(el).attr('id')).find('tbody > tr').filter(function() {
        return $(this).css('display') !== 'none';
        }).length;
        var label = 0;
        var rows = [10, 25, 50, 100];
        for (var i = 0; i < rows.length; i++) {
        if (rowsPerPage <= rows[i]) {
            label = rows[i];
            break;
        }
        }
        $("#"+$(el).attr('id')).parent('.table-container').next('.pager').find('a[data-label="'+label+'"]').addClass("current");
    });
}

function initFilters() {
    // add clear all filters button when one of the facet options is selected
    if ($('.checkbox-anchor').children('input[type=checkbox]:checked').length > 0) {
        $('.clear-filters').addClass('active');
    } else {
        $('.clear-filters').removeClass('active');
    }
    // reduce the filter list size by adding the show all button
    $('.filter-list').each(function() {
        if ($(this).children("a").length > 5) {
        $(this).children("a").slice(5, $(this).children("a").length).hide();
        $(this).append(`<button class="button-link show-more" onclick="toggleFilters()"><i class="far fa-plus"></i> Show all (`+$(this).children("a").length+`)</button>`);
        }
    });
    // search in filter options and display options that match the query
    $('.instant-search').on('focus', function (e) {
        var filterOptions = $(e.target).siblings('.checkbox-anchor');
        $(e.target).on('keyup change', function () {
        var query = $(e.target).val().toLowerCase();
        if (query == '') {
            filterOptions.slice(0, 5).show();
            filterOptions.slice(6, filterOptions.length).hide();
            $(e.target).closest('fieldset').children('.show-more').remove();
            $(e.target).closest('fieldset').append(`<button class="button-link show-more" onclick="toggleFilters()"><i class="far fa-plus"></i> Show all (`+$(e.target).closest('fieldset').children("a").length+`)</button>`);
        }
        else {
            $(e.target).closest('fieldset').children('button.show-more').hide();
            filterOptions.each(function() {
            var option = $(this).text().toLowerCase();
            if (option.includes(query)) {
                $(this).show();
            }
            else{
                $(this).hide();
            }
            });
        }
        })  
    });
}

/**
 * Create and initialise the creation year slider, handling all of its
 * varied updates to the 'submit' link etc.
 */
function initCreationYearSlider() {
    // year range filters
    let minValue = Number($('#id_start_year').attr('min'));
    let maxValue = Number($('#id_end_year').attr('max'));
    if ($('#id_start_year').val() == '') {
        $('#id_start_year').val(minValue);
    }
    let startYear = parseInt($('#id_start_year').val());
    if ($('#id_end_year').val() == '') {
        $('#id_end_year').val(maxValue);
    }
    let endYear = parseInt($('#id_end_year').val());
    let queryString = generateCreationYearURL(startYear, endYear);

    $('#year-range-anchor').attr('href', queryString);

    $('#year-range').slider({
        range: true,
        min: minValue,
        max: maxValue,
        values: [startYear, endYear],
        slide: function( event, ui ) {
        let startYear = ui.values[0];
        let endYear = ui.values[1];
        let queryString = generateCreationYearURL(startYear, endYear);
        $('#id_start_year').val(startYear);
        $('#id_end_year').val(endYear);
        $('#year-range-anchor').attr('href', queryString);
        }
    });

    $( "#id_start_year" ).on('keyup change', function(el) {
        var endYear = parseInt($( "#id_end_year" ).val());
        if ($(el.target).val() >= minValue && $(el.target).val() <= endYear) {
        $('#year-range').slider("values", 0, $(el.target).val());
        let queryString = generateCreationYearURL($('#id_start_year').val(),
                                                    $('#id_end_year').val());
        $('#year-range-anchor').attr('href', queryString);
        }
    });
    $( '#id_end_year' ).on('keyup change', function(el) {
        var startYear = parseInt($( '#id_start_year' ).val());
        if ($(el.target).val() >= startYear && $(el.target).val() <= maxValue) {
        $('#year-range').slider('values', 1, $(el.target).val());
        let queryString = generateCreationYearURL($('#id_start_year').val(),
                                                    $('#id_end_year').val());
        $('#year-range-anchor').attr('href', queryString);
        }
    });
}
/**
 * Return the current URL's querystring with the start_year and
 * end_year parameters set to the supplied startYear and endYear.
 *
 * @param {Number} startYear - the year to set as start_year in the querystring
 * @param {Number} endYear - the year to set as end_year in the querystring
 * @returns {String}
 */
function generateCreationYearURL(startYear, endYear) {
    let searchParams = new URLSearchParams(location.search);
    searchParams.set('start_year', startYear)
    searchParams.set('end_year', endYear)
    return '?' + searchParams.toString();
}

// show all information on the table pages
function toggleAllMoreInformation() {
    event.preventDefault();
    $('[id^="checkbox_"]').prop('checked', !$('[id^="checkbox_"]').prop('checked'));
    if ($('[id^="checkbox_"]').prop('checked')) {
        $(event.target).text('Collapse all');
    } else {
        $(event.target).text('Expand all');
    }
}

// show more/less facet options
function toggleFilters() {
    event.preventDefault();
    var fieldset = $(event.target).parent('fieldset').first();
    $(fieldset).children('.show-more').remove();
    if ($(fieldset).children('a[style="display: none;"]').length) {
      $(fieldset).children('a').show();
      $(fieldset).children('a:first-of-type').before(`<button class="button-link show-more" onclick="toggleFilters()"><i class="far fa-minus"></i> Show less</button>`);
      $(fieldset).append(`<button class="button-link show-more" onclick="toggleFilters()"><i class="far fa-minus"></i> Show less</button>`);
    }
    else {
      $(fieldset).children('a').slice(5, $(fieldset).children('a').length).hide();
      $(fieldset).append(`<button class="button-link show-more" onclick="toggleFilters()"><i class="far fa-plus"></i> Show all (`+ $(fieldset).children("a").length +`)</button>`);
    }
  }