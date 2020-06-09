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
  let dialogueRequiredControls = $("#log-modal").find("*[required]");
  toggleRequiredControls(dialogueRequiredControls, false);

  // Cancel buttons on modal dialogues should close the modal and not
  // allow default handling of the event.
  $(".modal-cancel").click(function(event) {
    // Even if this is not the logging dialogue being cancelled, set
    // its required controls to false; this is the most convenient
    // place to perform this sadly necessary operation.
    toggleRequiredControls(dialogueRequiredControls, false);
    let modal = $(event.target).parents(".modal").first().removeClass("active");
    event.preventDefault();
  });


  // Open popup to log changes when saving a record, then actually
  // submit the form when submitting from the popup.
  $("#record-form").submit(function(event) {
    if ($("#log-modal").hasClass('active')) {
      event.target.submit();
    } else {
      event.preventDefault();
      toggleRequiredControls(dialogueRequiredControls, true);
      $("#log-modal").addClass('active');
    }
  });

  // SELECT-WITH-SEARCH
  // add search bar to the select dropdown
  $(".select-with-search").select2( {
    placeholder: "Select",
    allowClear: true
  } );
  //add aria-label to select2 input
  $('.select2-search__field').attr('aria-label', 'select with search');
  $('.select2-selection__rendered').attr('aria-label', 'select2-selection__rendered');
  $('.select2-selection--multiple').attr({
    'aria-label': 'select2-selection--multiple',
    'role': 'list'
  });
  $('.select2-selection--single').attr({
    'role': 'list'
  });

  // TABLE PAGINATION / TABLESORTER
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

  $('table').each(function(i, el) {
    $.tablesorter.customPagerControls({
      table          : $("#"+$(el).attr('id')),                   // point at correct table (string or jQuery object)
      pager          : $("#"+$(el).parent(".table-container").next('.pager').attr('id')),                   // pager wrapper (string or jQuery object)
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
      $("#"+$(el).attr('id'))
        .tablesorter({
            widgets: ["filter"],
            widgetOptions: {
                filter_columnFilters: true,
                filter_filterLabel : 'Filter "{{label}}"',
            }
        })
    } else {
      $("#records-list-table")
        .tablesorter({
            widgets: ["filter"],
            widgetOptions: {
                filter_columnFilters: true,
                filter_filterLabel: 'Filter "{{label}}"'
            },
            sortList: [[2,0]],
            headers: {
              2: {
                sorter: 'level'
              }
            }
        })
    }

    $("#"+$(el).attr('id')).tablesorterPager({
      container: $("#"+$(el).parent(".table-container").next('.pager').attr('id')),
      size: 10
    });
   
    //  make sure that corrent 'rows per page' number is active
    var rowsPerPage = $("#"+$(el).attr('id')).find("tbody > tr").filter(function() {
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
    $("#"+$(el).attr('id')).parent('.table-container').next(".pager").find("a[data-label='"+label+"']").addClass("current");
  });

  // optional functionality (can be removed if needed) - dynamic styling of the sections
  // style border for preferred names and identities
  $("fieldset:has(input[name*='preferred']:checked)").addClass('border-left');
  $("fieldset:has(input[name*='authorised']:checked)").addClass('border-left');
  $('body').on('click', 'input[name*="preferred"]', function (el) {
    $('input[name*="preferred"]:checked').prop('checked', false);
    $(el.target).parents('fieldset').first().find('input[name*="preferred"]').prop('checked', true);
    $(el.target).parents('fieldset').siblings().removeClass('border-left');
    if ($(el.target).is(':checked')) {
      $(el.target).parents('fieldset').first().addClass('border-left');
    }
  });

  $('body').on('click', 'input[name*="authorised"]', function (el) {
    $('input[name*="authorised"]:checked').prop('checked', false);
    $(el.target).parents('fieldset').first().find('input[name*="authorised"]').prop('checked', true);
    $(el.target).parents('fieldset').siblings().removeClass('border-left');
    if ($(el.target).is(':checked')) {
      $(el.target).parents('fieldset').first().addClass('border-left');
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
      $(this).append(`<button class="button-link show-more" onclick="toggleFilters('`+$(this).attr('id')+`')"><i class="far fa-plus"></i> Show all (`+$(this).children("a").length+`)</button>`);
    }
  });
  // search in filter options and display options that match the query
  $('.instant-search').on('focus', function (el) {
    var filterOptions = $(el.target).siblings('.checkbox-anchor');
    $(el.target).on('keyup change', function () {
      var query = $(el.target).val().toLowerCase();
      if (query == '') {
        filterOptions.slice(0, 5).show();
        filterOptions.slice(6, filterOptions.length).hide();
      }
      else {
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
    content_style: ".mce-content-body {font-size:14px;font-family:Roboto,sans-serif;}",
    plugins: 'charmap image media link table lists code',
    toolbar: 'bold italic underline strikethrough | insertfile image media link | table | formatselect | alignleft aligncenter alignright alignjustify | numlist bullist | charmap | removeformat | undo redo | code',
  });
  // initialise TinyMCE for all visible editors
  $('.richtext').each(function () {
    if (!$(this).attr('id').includes("prefix")) {
      tinymce.EditorManager.execCommand('mceAddEditor', true, $(this).attr('id'));
    }
  });
  

  // SAVE ADMIN TABLE BUTTON
  // enable Save admin table button once one of the input fields is clicked
  $('.admin-table').find('label').on('click', function() {
    if ($('.save-admin-table').hasClass('none')) {
      $('.save-admin-table').removeClass('none');
    }
  });

  // TRANSCRIPTIONS - if expanded by default (WILL BE REMOVED ONCE THE RTE DEVELOPMENT IS COMPLETED)
  if ($('#transcription-div').hasClass('expand') && $( 'textarea.richtext-transcription' ).length == 0) {
    fetchTranscriptions();
  }
  
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
        let transcriptionManagementForm = `<input type="hidden" name="transcription-TOTAL_FORMS" value="`+orderedData.length+`" id="id_transcription-TOTAL_FORMS"><input type="hidden" name="transcription-INITIAL_FORMS" value="`+orderedData.length+`" id="id_transcription-INITIAL_FORMS"><input type="hidden" name="transcription-MIN_NUM_FORMS" value="0" id="id_transcription-MIN_NUM_FORMS"><input type="hidden" name="transcription-MAX_NUM_FORMS" value="1000" id="id_transcription-MAX_NUM_FORMS">`;
        let transcriptions = '';
        orderedData.forEach(function(t, i) {
          transcriptions += `<input type="hidden" name="transcription-`+i+`-id" value="`+t.pk+`" id="id_transcription-`+i+`-id" aria-label="input field">
                            <textarea name="transcription-`+i+`-transcription" class="richtext-transcription" rows="8" id="id_transcription-`+i+`-transcription" cols="40" aria-label="richtext field">`+t.fields.transcription+`</textarea>`;
        });
        $('#transcription').append(transcriptionManagementForm);
        $('#transcription').append(transcriptions);
        addCKEditor();
      });
    }
  )
  .catch(function(err) {
    console.log(err);
  });
}

/** 
  hide all transcriptions and generate ckeditor for the first transcription on the list
*/
function addCKEditor() {
  $( 'textarea.richtext-transcription' ).hide();
  $( 'textarea#id_transcription-0-transcription' ).ckeditor();
  $('#rte-pagination').pagination({
    items: $("textarea.richtext-transcription").length,
    itemsOnPage: 1,
    useAnchors: false,
    displayedPages: 3,
    prevText: ' ',
    nextText: ' ',
    onPageClick: function(pageNumber, event) {
      $("div[id^=cke_id_transcription]").hide();
      $("textarea#id_transcription-"+(pageNumber-1)+"-transcription").ckeditor();
      $("div[id='cke_id_transcription-"+(pageNumber-1)+"-transcription']").css('display', 'block');
      viewer.goToPage(pageNumber-1);
    }
  });
}

// expand/collapse entity/archival record sections
function toggleTab(el) {
  $(el).parents('.fieldset-header').siblings('.fieldset-body').toggleClass('expand');
  $(el).toggleClass('active');
}

// show more/less facet options
function toggleFilters(el) {
  $('#'+el).children(".show-more").remove();
  if ($('#'+el).children("a[style='display: none;']").length) {
    $('#'+el).children("a").show();
    $('#'+el).append(`<button class="button-link show-more" onclick="toggleFilters('`+$('#'+el).attr('id')+`')"><i class="far fa-minus"></i> Show less</button>`);
  }
  else {
    $('#'+el).children("a").slice(5, $('#'+el).children("a").length).hide();
    $('#'+el).append(`<button class="button-link show-more" onclick="toggleFilters('`+$('#'+el).attr('id')+`')"><i class="far fa-plus"></i> Show all (`+ $('#'+el).children("a").length +`)</button>`);
  }
}

// hide/show help text on single entity and archival records pages
function toggleHelpText(el, help_text) {
  event.preventDefault();
  if ($(el).siblings('p.additional-info').length) {
    // change icon to 'question mark'
    $(el).text("");
    $(el).siblings('p.additional-info').remove();
  }
  else {
    var position = $(el).position();
    $(el).before('<p class="additional-info" style="top:'+ (position.top - 40) + 'px; left:' + (position.left + 25) + 'px">' + help_text + '</p>');
    // change icon to 'close'
    $(el).text("");
  }
}

/**
 * Create confirmation modal dialogue with form to delete the current
 * record (whether Archival Record or Entity).
 */
function deleteRecord(event) {
  $("#delete-modal").addClass('active');
  event.preventDefault();
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
  let maxNumControl = managementFormContainer.children("input[name$='MAX_NUM_FORMS']");
  let maxNumForms = Number(maxNumControl.attr("value"))
  let totalControl = managementFormContainer.children("input[name$='TOTAL_FORMS']");
  let newFormPrefixNumber = Number(totalControl.attr("value"));
  if ((newFormPrefixNumber+1) >= maxNumControl.attr("value")) {
    $(jContext).parent("label").hide();
  }
  // Clone the formType form and add it as the last child of the
  // parent of these forms.
  let formParent = getNewFormParent(jContext);
  let newForm = $("#empty_forms").children("*[data-form-type=" + formType + "]").clone();
  newForm.appendTo(formParent);
  // Update the new form's controls' @name and @id to use the correct
  // values for its context in the hierarchy of formsets. Their prefix
  // (the part up to the end of the last "__prefix__") should be
  // replaced with the prefix generated from the TOTAL_FORMS control
  // of the containing formset's management form (plus the number of
  // this form), which conveniently already has the full prefix
  // hierarchy in it.
  let newControls = newForm.find("*[name*='__prefix__']");
  let newFormPrefixName = generateNewFormPrefix(totalControl, "name", newFormPrefixNumber);
  let newFormPrefixId = generateNewFormPrefix(totalControl, "id", newFormPrefixNumber);
  let prefixLength = "__prefix__".length;
  newControls.each(function(index) {
    $(this).attr("name", function(i, val) {
      return newFormPrefixName + val.slice(val.lastIndexOf("__prefix__") + prefixLength);
    });
    $(this).attr("id", function(i, val) {
      return newFormPrefixId + val.slice(val.lastIndexOf("__prefix__") + prefixLength);
    });
    if ($(this).hasClass("select-with-search-dynamic")) {
      $(this).select2( {
        placeholder: "Select",
        allowClear: true
      } );
    }
    if ($(this).hasClass("richtext")) {
      tinymce.EditorManager.execCommand('mceAddEditor', true, $(this).attr('id'));
    }
  });
  // The management form for the formset of the new form must have its
  // TOTAL_FORMS value incremented by 1 to account for the new form.
  totalControl.attr("value", newFormPrefixNumber + 1);
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
  return attrValue.slice(0, attrValue.indexOf("TOTAL_FORMS")) + String(prefixNumber);
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
  return context.parents(".formset").first().children("div.management_form");
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
  return context.parents(".formset").first().children("div.fieldsets").last();
}


// this won't delete the field(s), just hide them. The deletion needs to be executed in the backend, once the form is submitted.
function deleteField(el, toDelete) {
  event.preventDefault();
  $(el).closest(toDelete).addClass('none');
  $(el).parents(".formset").first().children("label").show();
}


function deleteRow(el) {
  if (!$(el).parent().siblings('td').hasClass('none')) {
    $(el).parent().siblings('td').addClass('none');
    $(el).parent().attr('colspan', '6');
    $(el).after(`<i class="fas fa-trash-alt"></i><input name="all_users_submit" aria-label="save admin table" type="submit" class="button-link danger" value="Delete permanently and save table" />`)
  } else {
    $(el).parent().attr('colspan', '1');
    $(el).parent().siblings('td').removeClass('none');
    $(el).next('button').remove();
  }
  // Find and toggle the DELETE checkbox for the form.
  let deleteField = $(el).closest("[data-form-type]").find("[class~='delete-form-field']").find("[name$='DELETE']").first();
  deleteField.prop("checked", !deleteField.prop("checked"));
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
  searchParams.set("start_year", startYear)
  searchParams.set("end_year", endYear)
  return '?' + searchParams.toString();
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

  /* these values should be specified via start_year and end_year in the template:
     $( "#id_start_year" ).val( $( "#year-range" ).slider( "values", 0 ));
     $( "#id_end_year" ).val( $( "#year-range" ).slider( "values", 1 ));
  */
  $( "#id_start_year" ).on('keyup change', function(el) {
    var endYear = parseInt($( "#id_end_year" ).val());
    if ($(el.target).val() >= minValue && $(el.target).val() <= endYear) {
      $('#year-range').slider("values", 0, $(el.target).val());
      let queryString = generateCreationYearURL($('#id_start_year').val(),
                                                $('#id_end_year').val());
      $('#year-range-anchor').attr('href', queryString);
    }
  });
  $( "#id_end_year" ).on('keyup change', function(el) {
    var startYear = parseInt($( "#id_start_year" ).val());
    if ($(el.target).val() >= startYear && $(el.target).val() <= maxValue) {
      $('#year-range').slider("values", 1, $(el.target).val());
      let queryString = generateCreationYearURL($('#id_start_year').val(),
                                                $('#id_end_year').val());
      $('#year-range-anchor').attr('href', queryString);
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
  let form_part = jButton.closest("[data-form-type]").find("[class~='inline-deletable']").first();
  form_part.toggleClass("none");

  // toggle the checkbox button and text label
  if (form_part.hasClass('none')) {
    jButton.val("");
    label.removeClass('danger');
    label.addClass('save');
    label.append(`<span>Undo</span>`);
    label.parent().after(`<button class="button-link danger" onclick="deleteField(this, '[data-form-type]')"><i class="fas fa-trash-alt"></i>Delete permanently</button>`)
  }
  else {
    jButton.val("");
    label.removeClass('save');
    label.addClass('danger');
    label.children('span').remove();
    label.parent().siblings('button').remove();
  }

  // Find and toggle the DELETE checkbox for the form.
  let deleteField = form_part.children("[class~='inline-delete-form-field']").find("[name$='DELETE']").first();
  deleteField.prop("checked", !deleteField.prop("checked"));
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
    value = "required";
  }
  controls.attr("required", value);
}
