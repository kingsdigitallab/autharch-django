$(document).ready(function() {

  // Return the text nodes of the context. Code by Mark Baijens from
  // https://stackoverflow.com/questions/4106809/how-can-i-change-an-elements-text-without-changing-its-child-elements/4106957
  jQuery.fn.textNodes = function() {
    return this.contents().filter(function() {
      return (this.nodeType === Node.TEXT_NODE);
    });
  };

  initAutocompleteWidgets();

  // In order to not cause problems with client-side form validation
  // when required fields are hidden, remove the required attribute
  // from all form controls in the logging dialogue, to be added back
  // when it is shown.
  //
  // This is a better approach than toggling novalidate on the form,
  // since we presumably do want that minimal validation to occur when
  // submitting, and this just stops it from failing on specific
  // fields that aren't editable yet.
  let dialogueRequiredControls = $('#log-modal').find('*[required]');
  toggleRequiredControls(dialogueRequiredControls, false);

  // Cancel buttons on modal dialogues should close the modal and not
  // allow default handling of the event.
  $('.modal-cancel').click(function(event) {
    // Even if this is not the logging dialogue being cancelled, set
    // its required controls to false; this is the most convenient
    // place to perform this sadly necessary operation.
    toggleRequiredControls(dialogueRequiredControls, false);
    let modal = $(event.target).parents('.modal').first().removeClass('active');
    event.preventDefault();
  });
  
  // Open popup to log changes when saving a record, then actually
  // submit the form when submitting from the popup.
  $('#record-form').submit(function(event) {
    event.preventDefault();
    if ($('#log-modal').hasClass('active')) {
      event.target.submit();
    } else {
      event.preventDefault();
      toggleRequiredControls(dialogueRequiredControls, true);
      $('#log-modal').addClass('active');
    }
  });

  // SELECT-WITH-SEARCH
  // add search bar to the select dropdown
  $('.select-with-search').select2({
    placeholder: 'Select',
    allowClear: true
  });
  $('select[name="entity"]').select2({
    placeholder: 'Add a duplicate by record ID or display name',
    allowClear: true
  });
  $('.select2-search__field').each(function() {
    if ($(this).attr('placeholder') == '') {
      $(this).attr('placeholder', 'Enter your search term...');
    }
  });
  // add aria-label to select2 input
  $('form').on('select2:opening', function(e) {
    setTimeout(function() {
      $('.select2-container--open').find('.select2-search__field').attr('placeholder', 'Enter your search term...').focus();
    }, 500);
  });

  // TABLESORTER
  // sorter for the archival records table - Collection -> Series -> File -> Item
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
    if ($(el).attr('id') !== 'records-list-table') {
      $('#'+$(el).attr('id'))
        .tablesorter({
            widgets: ['filter'],
            widgetOptions: {
                filter_columnFilters: true,
                filter_filterLabel : 'Filter by {{label}}',
            }
        })
    } else {
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

  // toggle name part message
  $('.formset').on('click', 'input[id$="is_royal_name"]', function(e) {
    if ($(e.target).prop("checked")) {
      $(e.target).next('.namePartField-required').text(`A royal name must contain a "forename" part type and a "proper title" part type.`);
    } else {
      $(e.target).next('.namePartField-required').text(`A personal name must contain a "surname" part type.`);
    }
  });

  // close tooltips when clicked anywhere on the page
  $('form').on('click', function(e) {
    if (!$(e.target).is('.additional-info')) {
      if($('.additional-info').length) {
        $('.additional-info').siblings('[role=button]').text("");
        $('.additional-info').remove();
      }
    }
  });

  // optional functionality (can be removed if needed) - dynamic styling of the sections
  // style border for preferred names and identities
  $('input[name*="preferred"]:checked').parents('fieldset').addClass('border-left');
  $('input[name*="authorised"]:checked').closest('fieldset').addClass('border-left');

  $(document).on('click', 'input[name*="preferred"]', function(e) {
    // find other identities and uncheck their preferred status
    $(e.target).parents('fieldset').siblings().find('input[name*="preferred"]:checked').prop('checked', false);
    // find the identity where the checkbox was checked and set its checkbox as checked
    $(e.target).closest('fieldset').find('input[name*="preferred"]').prop('checked', true);
    // find other identities and make sure that a blue border-left is removed
    $(e.target).parents('fieldset').siblings().removeClass('border-left');
    // set blue-border left to the preferred fieldset
    if ($(e.target).is(':checked')) {
      $(e.target).closest('fieldset').addClass('border-left');
    }
  });

  $(document).on('click', 'input[name*="authorised"]', function(e) {
    // find other name parts (within the same scope!) and uncheck their authorised status
    $(e.target).closest('fieldset').siblings().find('input[name*="authorised"]:checked').prop('checked', false);
    // find the name part that was checked and set its checkbox as checked
    $(e.target).closest('fieldset').find('input[name*="authorised"]').prop('checked', true);
    // find other name parts where the border-left is set to authorised and remove the border
    $(e.target).closest('fieldset').siblings().removeClass('border-left');
    // find the checked name part and set its border to blue
    if ($(e.target).is(':checked')) {
      $(e.target).closest('fieldset').addClass('border-left');
    }
  });
  
  
  //FILTERS
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
  setUpCreationYearSlider();

  // RICHTEXT FIELDS
  tinymce.init({
    menubar: '',
    content_style: '.mce-content-body {font-size:14px;}',
    plugins: 'charmap image media link table lists code',
    toolbar: 'bold italic underline strikethrough | insertfile image media link | table | formatselect | alignleft aligncenter alignright alignjustify | numlist bullist | charmap | removeformat | undo redo | code',
    setup: function (editor) {
      editor.on('change', function (e) {
          editor.save();
      });
    }
  });
  // initialise TinyMCE for all visible editors
  $('.richtext').each(function () {
    if (!$(this).attr('id').includes('prefix')) {
      tinymce.EditorManager.execCommand('mceAddEditor', true, $(this).attr('id'));
    }
  });
  
  
  // TRANSCRIPTIONS - if collapsed by default
  $('.transcription-toggle').on('click', function() {
    // fetch transcriptions when the transcription section is expanded and there are no transcriptions yet 
    if ($('#transcription-div').hasClass('expand') && $( 'textarea.richtext-transcription' ).length == 0) {
      fetchTranscriptions();
    }
  });
  
});

// TRANSCRIPTIONS
// fetch transcriptions
async function fetchTranscriptions() {
  await fetch(window.location.pathname + 'transcriptions').then(
    function(response) {
      response.json().then(function(data) {
        let orderedData = data.sort(function(a, b) {return parseInt(a.fields.order) - parseInt(b.fields.order)});
        let transcriptions = '';
        orderedData.forEach(function(t, i) {
          transcriptions += `<input type="hidden" name="transcription-`+i+`-id" value="`+t.pk+`" id="id_transcription-`+i+`-id" aria-label="input field">
                            <textarea name="transcription-`+i+`-transcription" class="richtext-transcription" rows="8" id="id_transcription-`+i+`-transcription" cols="40" aria-label="richtext field">`+t.fields.transcription+`</textarea>`;
        });
        $('#transcription').append(transcriptions);
        document.addEventListener("fullscreenchange", exitHandler);
        addCKEditor();
        addPagination();
      });
    }
  )
  .catch(function(err) {
    console.log(err);
  });
}
// exit fullscreen mode and update the browsed page
function exitHandler() {
  if (!document.fullscreenElement && !document.webkitIsFullScreen && !document.mozFullScreen && !document.msFullscreenElement) {
    $('#rte-pagination').pagination('selectPage', parseInt(viewer.currentPage()+1));
  }
} 
// hide all transcriptions and generate ckeditor for the first transcription on the list
function addCKEditor() {
  $('textarea.richtext-transcription').hide();
  $('textarea#id_transcription-0-transcription').ckeditor();
}
// add pagination
function addPagination() {
  $('#rte-pagination').pagination({
    items: $("textarea.richtext-transcription").length,
    itemsOnPage: 1,
    useAnchors: false,
    displayedPages: 3,
    prevText: ' ',
    nextText: ' ',
    onPageClick: function(pageNumber, event) {
      goToTranscription(pageNumber-1);
      viewer.goToPage(pageNumber-1);
    }
  });
}
function goToTranscription(i) {
  $('div[id^="cke_id_transcription"]').hide();
  $('textarea#id_transcription-'+i+'-transcription').ckeditor();
  $('div[id="cke_id_transcription-'+i+'-transcription"]').css('display', 'block');
}


/**
 * Add a new empty form of the specified form_type.
 *
 * The blueprints for new forms are in div[@id='empty_forms'], and each
 * has a @data-form-type specifying the form_type.
 *
 * Updates the containing formset's management form controls and sets
 * the name and ids of the new form's controls to use the correct
 * prefix.
 *
 * The place where the new form is put, the location of the management
 * form's TOTAL_FORMS control that is edited, and the determination of
 * nested form's @id/@name prefix is based solely on the provided
 * context element; see {@link getManagementFormTotalControl} and
 * {@link getNewFormParent}.
 *
 * @param {string} formType - the type of form to add, corresponding to
 *                            the @data-form-type of the blueprint
 *                            empty form
 * @param {Element} context - the element from which the call to this
 *                            function was made
 */
function addEmptyForm(formType, context) {
  let jContext = $(context);
  let managementFormContainer = getManagementFormContainer(jContext);
  let maxNumControl = managementFormContainer.children('input[name$="MAX_NUM_FORMS"]');
  let maxNumForms = Number(maxNumControl.attr('value'));
  let totalControl = managementFormContainer.children('input[name$="TOTAL_FORMS"]');
  let newFormPrefixNumber = Number(totalControl.attr('value'));
  if ((newFormPrefixNumber+1) >= maxNumControl.attr('value')) {
    $(jContext).parent('label').hide();
  }
  // Clone the formType form and add it as the last child of the
  // parent of these forms.
  let formParent = getNewFormParent(jContext);
  let newForm = $('#empty_forms').children('*[data-form-type=' + formType + ']').clone();
  newForm.appendTo(formParent);
  // Update the new form's controls' @name and @id to use the correct
  // values for its context in the hierarchy of formsets. Their prefix
  // (the part up to the end of the last "__prefix__") should be
  // replaced with the prefix generated from the TOTAL_FORMS control
  // of the containing formset's management form (plus the number of
  // this form), which conveniently already has the full prefix
  // hierarchy in it.
  let newControls = newForm.find('*[name*="__prefix__"]');
  let newFormPrefixName = generateNewFormPrefix(totalControl, 'name', newFormPrefixNumber);
  let newFormPrefixId = generateNewFormPrefix(totalControl, 'id', newFormPrefixNumber);
  let prefixLength = '__prefix__'.length;
  newControls.each(function(index) {
    $(this).attr('name', function(i, val) {
      return newFormPrefixName + val.slice(val.lastIndexOf('__prefix__') + prefixLength);
    });
    $(this).attr('id', function(i, val) {
      return newFormPrefixId + val.slice(val.lastIndexOf('__prefix__') + prefixLength);
    });
    if ($(this).attr('data-voc-prefix')) {
      $(this).select2( {
        allowClear: true,
        ajax: {
          url: '/vocabularies/terms',
          data: function (params) {
            var query = {
              prefix: $(this).attr('data-voc-prefix'),
            }
    
            return query;
          }
        }
      } );
    }
    if ($(this).hasClass('admin-autocomplete')) {
      $(this).next('.select2').find('.select2-selection__placeholder').text('Select');
    }
    if ($(this).hasClass('select-with-search-dynamic')) {
      $(this).select2({
        allowClear: true,
      } );
    }
    if ($(this).hasClass('richtext')) {
      tinymce.EditorManager.execCommand('mceAddEditor', true, $(this).attr('id'));
    }
  });
  // The management form for the formset of the new form must have its
  // TOTAL_FORMS value incremented by 1 to account for the new form.
  totalControl.attr('value', newFormPrefixNumber + 1);
  initAutocompleteWidgets();
}

/**
 * Return a string prefix for a new form whose TOTAL_FORMS control is
 * the supplied control, based on its attrName attribute value and the
 * prefixNumber.
 *
 * @param {jQuery} control - TOTAL_FORMS control
 * @param {String} attrName - name of control's attribute to use as the base
 * @param {Number} prefixNumber - number of the new form
 * @returns {String}
 */
function generateNewFormPrefix(control, attrName, prefixNumber) {
  let attrValue = control.attr(attrName);
  return attrValue.slice(0, attrValue.indexOf('TOTAL_FORMS')) + String(prefixNumber);
}


/**
 * Return the container for the Django formset's management form
 * controls associated with the supplied context element.
 *
 * This function is specific to a particular HTML structure, and
 * should be adapted if/when that structure changes.
 *
 * @param {jQuery} context - the element from which to traverse the
 *                           DOM to find the management form's container
 * @returns {jQuery}
 */
function getManagementFormContainer(context) {
  return context.parents('.formset').first().children('div.management_form');
}


/**
 * Return the jQuery object containing the element that is to be the
 * container for a new form.
 *
 * This function is specific to a particular HTML structure, and
 * should be adapted if/when that structure changes.
 *
 * @param {jQuery} context - the element from which to traverse the
 *                           DOM to find the parent for the new form
 * @returns {jQuery}
 */
function getNewFormParent(context) {
  return context.parents('.formset').first().children('div.fieldsets').last();
}

/**
 * Initialise all autocomplete widgets except ones in an empty
 * template form.
 *
 * Multiple initialisations of the same widgets does not appear to
 * cause problems.
 */
function initAutocompleteWidgets() {
  $('.autocomplete').not('[name*=__prefix__]').select2();
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


/**
 * Create and initialise the creation year slider, handling all of its
 * varied updates to the 'submit' link etc.
 */
function setUpCreationYearSlider() {
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


 /**
 * Mark/unmark an inline form for deletion.
 *
 * This involves three changes:
 *
 * 1. Toggling the DELETE checkbox for the form.
 * 2. Toggling the visibility of the form.
 * 3. Toggling the delete/undo icon.
 *
 * This code requires the following HTML structure in order to behave
 * correctly:
 *
 * 1. The toggling instigator (the delete/undo icon) must be a
 * descendant of an element with the data-form-type attribute
 * set. This attribute marks the element that encompasses the whole of
 * an inline form.
 *
 * 2. The part of the form to be hidden/shown must have the class
 * attribute value "inline-deletable".
 *
 * 3. The part of the form to be hidden/shown must be a descendant of
 * the encompassing element (see #1).
 *
 * 4. The DELETE checkbox for the form must be a descendant (within an
 * element with a class of "inline-delete-form-field") of the part of
 * the form to be hidden/shown (see #2).
 *
 * @param {Element} button - the button element that triggered the toggle
 */
function toggleDeleteInline(event, button) {
  event.preventDefault();
  let jButton = $(button);
  let label = jButton.parent('label');
  let header = label.parents('.fieldset-header');
  let fieldset = header.parent('fieldset');

  // grey out the header if inactive
  header.toggleClass('inactive');
  // uncheck preferred identity
  header.find('input[type="checkbox"]:checked').prop('checked', false);
  fieldset.removeClass('border-left');
  // remove toggle button
  header.find('.toggle-tab-button').toggleClass('inactive');
  //toggle the display of preferred identity and authorised form
  header.find('input[type="checkbox"]').parent().toggleClass('none');

  // Find the element for the part of the form to be shown/hidden,
  // and toggle its visibility.
  let form_part = jButton.closest('[data-form-type]').find('[class~="inline-deletable"]').first();
  form_part.toggleClass('none');

  // toggle the checkbox button and text label
  if (form_part.hasClass('none')) {
    jButton.val('');
    label.removeClass('danger');
    label.addClass('save');
    label.append(`<span>Undo</span>`);
    label.parent().after(`<button class="button-link danger" onclick="deleteField(this, '[data-form-type]')"><i class="fas fa-trash-alt"></i>Delete permanently</button>`)
  }
  else {
    jButton.val('');
    label.removeClass('save');
    label.addClass('danger');
    label.children('span').remove();
    label.parent().siblings('button.danger').remove();
  }

  // Find and toggle the DELETE checkbox for the form.
  let deleteField = form_part.children('[class~="inline-delete-form-field"]').find('[name$="DELETE"]').first();
  deleteField.prop('checked', !deleteField.prop('checked'));
}


/**
 * Set/remove the required attribute of the supplied form controls.
 *
 * @param {jQuery} controls - controls to manipulate
 * @param {Boolean} add_required - whether to add (true) or remove the
 *                                 required attribute
 */
function toggleRequiredControls(controls, add_required) {
  let value = null;
  if (add_required) {
    value = 'required';
  }
  controls.attr('required', value);
}


// expand/collapse entity/archival record sections and individual sections on the hierarchy page
function toggleTab() {
  event.preventDefault();
  let header = $(event.target).closest('.fieldset-header');
  $(header).siblings('.fieldset-body').first().toggleClass('expand');
  $(header).find('.toggle-tab-button').toggleClass('active');
}


// expand a hierarchical tree
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


// show all information on the table pages
function toggleAllMoreInformation() {
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


// hide/show help text on single entity and archival records pages
function toggleHelpText(help_text) {
  event.stopPropagation();
  event.preventDefault();
  if ($(event.target).siblings('p.additional-info').length) {
    // change icon to 'question mark'
    $(event.target).text('');
    $(event.target).siblings('p.additional-info').remove();
  }
  else {
    var position = $(event.target).position();
    $(event.target).before('<p class="additional-info" style="top:'+ (position.top - 40) + 'px; left:' + (position.left + 25) + 'px">' + help_text + '</p>');
    // change icon to 'close'
    $(event.target).text('');
  }
}


/**
 * Create confirmation modal dialogue with form to delete the current
 * record (whether Archival Record or Entity), to merge two records, or to mark them as not related.
 */
function showModal(modalName) {
  $('#'+modalName).addClass('active');
}


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


// this won't delete the field(s), just hide them. The deletion needs to be executed in the backend, once the form is submitted.
function deleteField(el, toDelete) {
  event.preventDefault();
  $(el).closest(toDelete).addClass('none');
  $(el).parents('.formset').first().children('label').show();
}


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


function removeNotification() {
  $(event.target).parent().remove();
}
