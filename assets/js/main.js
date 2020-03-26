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

  // ADD-ONS

  // Change textareas to richtext fields. A unique ID must be
  // provided for each, to avoid the contents being duplicated.
  $('.richtext').each(function(index) {
    $(this).richText({
      imageUpload:false,
      fileUpload:false,
      videoEmbed:false,
      code:false,
      id: "richText-" + index
    });
  });
  $('.richtext').attr('aria-label', 'richtext editor');
  $('.richText-toolbar').each(function(i) {
    $(this).find('li').each(function(j) {
      var updatedId = $(this).find("[for^=richText-]").attr('id')+'-'+i+'-'+j;
      $(this).find("label").attr('for', updatedId);
      $(this).find("[id^=richText-]").attr('id', updatedId);
      $(this).find("[id^=openIn]").attr({
        'id': $(this).find("[id^=openIn]").attr('id')+'-'+i+'-'+j,
        'aria-label': 'richText-form-item'
      });
    });
    $(this).find(".richText-form-item").each(function(k) {
      $(this).find("input").attr({
        'id': $(this).find("input").attr('id')+'-'+i+'-'+k,
        'aria-label': 'id'
      });
    });
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
    //add tablesorter to the tables
    $("#"+$(el).attr('id'))
      .tablesorter({
          widgets: ["filter"],
          widgetOptions: {
              filter_columnFilters: true,
              filter_filterLabel : 'Filter "{{label}}"',
          }
      })
      .tablesorterPager({
        container: $("#"+$(el).parent(".table-container").next('.pager').attr('id')),
        size: 10
      });

    var rowsPerPage = $("#"+$(el).attr('id')).find("tbody > tr").filter(function() {
      return $(this).css('display') !== 'none';
    }).length;
    var label = 0;
    if (rowsPerPage <= 10) {
      label = 10;
    }
    else if (rowsPerPage <= 25) {
      label = 25;
    }
    else if (rowsPerPage <= 50) {
      label = 50;
    }
    else {
      label = 100;
    }
    $("#"+$(el).attr('id')).parent('.table-container').next(".pager").find("a[data-label='"+label+"']").addClass("current");
  });

  // add search bar to the select dropdown
  $(".select-with-search").select2( {
    placeholder: "Select",
    allowClear: true
  } );
  $('.select2-search__field').attr('aria-label', 'select with search');
  $('.select2-selection__rendered').attr('aria-label', 'select2-selection__rendered');
  $('.select2-selection--multiple').attr({
    'aria-label': 'select2-selection--multiple',
    'role': 'list'
  });
  $('.select2-selection--single').attr({
    'role': 'list'
  });
  // optional functionality (can be removed if needed) - dynamic styling of the sections

  // style border for preferred names and identities
  $( "fieldset:has(input[name*='preferred']:checked)").addClass('border-left');
  $( "fieldset:has(input[name*='authorised']:checked)").addClass('border-left');

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
  
  if ($('.checkbox-anchor').children('input[type=checkbox]:checked').length > 0) {
    $('.clear-filters').addClass('active');
  } else {
    $('.clear-filters').removeClass('active');
  }

  $('.filter-list').each(function() {
    if ($(this).children("a").length > 5) {
      $(this).children("a").slice(5, $(this).children("a").length).hide();
      $(this).append(`<button class="button-link show-more" onclick="toggleFilters('`+$(this).attr('id')+`')"><i class="far fa-plus"></i> Show all (`+$(this).children("a").length+`)</button>`);
    }
  });

});

//start MODAL TEMPLATES

// update entity name part fields if the 'Royal name' checkbox is checked
function updateBlock(el) {
  var val= el.name.slice(0, -10);
  if($(el).is(":checked")){
    $(el).siblings('.required-fields').html(`
            <div class="grid">
                <span class="required">Forename(s)</span>
                <input type="text" placeholder="Forename(s)" onfocus="this.placeholder=''" onblur="this.placeholder='Forename(s)'" value="" aria-label="forename" name="`+ val +`forename"/>
            </div>
            <div class="grid">
                <span class="required">Proper title</span>
                <input type="text" placeholder="Proper title" onfocus="this.placeholder=''" onblur="this.placeholder='Proper title'" value="" aria-label="proper title" name="`+ val +`proper-title"/>
            </div>
        `);
  }
  else if($(el).is(":not(:checked)")){
    $(el).siblings('.required-fields').html(`
            <div class="grid">
                <span class="required">Surname</span>
                <input type="text"  placeholder="Surname" onfocus="this.placeholder=''" onblur="this.placeholder='Surname'" value="" aria-label="surname" name="`+ val +`surname"/>
            </div>
        `);
  }
}

function editValue(val) {
  if(val == 'place') {
    $('main').append(`<div class="modal active" id="edit-place-form">
                            <div class="modal-content">
                                <div class="modal-header">
                                    <h2>Find place</h2>
                                    <input type="button" class="icon-only modal-cancel" aria-label="close" value="&#xf00d;" />
                                </div>
                                <div class="modal-body">
                                    <form action="" method="" id="edit-place">
                                        <div class="two-column-table">
                                            <div>
                                                <label>
                                                    <span class="required">Geoname id</span>
                                                    <input type="text" name="geoname-id"/>
                                                </label>
                                                <label><input type="checkbox" class="inline" name="update-geoname" onclick=""/>Update from geonames</label>
                                                <label>Address
                                                    <input type="text" name="address" disabled/>
                                                </label>
                                                <label>Class description
                                                    <input type="text" name="class-description" disabled/>
                                                </label>
                                                <label>Country
                                                    <input type="text" name="country" disabled/>
                                                </label>
                                            </div>
                                            <div>
                                                <label>Feature class
                                                    <input type="email" name="feature-class" disabled/>
                                                </label>
                                                <label>Latitude
                                                    <input type="email" name="latitude" disabled/>
                                                </label>
                                                <label>Longitude
                                                    <input type="email" name="longitude" disabled/>
                                                </label>
                                            </div>
                                        </div>
                                    </form>
                                </div>
                                <div class="modal-footer">
                                    <input type="submit" value="Save" form="edit-place" class="save"/>
                                </div>
                            </div>
                        </div>`);
  }
}


function warningModal() {
  $('main').append(`<div class="modal active">
                        <div class="modal-content">
                            <div class="modal-header">
                                <h2>Delete this record?</h2>
                            </div>
                            <div class="modal-body">
                            </div>
                            <div class="modal-footer">
                                <input type="submit" value="Cancel" class="default"/>
                                <input type="submit" value="Delete" class="danger"/>
                            </div>
                        </div>
                    </div>`);
}

function alertPopup(msg) {
  $('main').append(`<div class="modal active">
                                <div class="modal-content">
                                    <div class="modal-header">
                                        <input type="button" class="icon-only modal-cancel" aria-label="close" value="&#xf00d;" />
                                    </div>
                                    <div class="modal-body">
                                        <p>`+ msg +`</p>
                                    </div>
                                    <div class="modal-footer">
                                    </div>
                                </div>
                            </div>`);
}

//end MODAL TEMPLATES


// expand/collapse entity/archival record sections
function toggleTab(el) {
  $(el).parents('.fieldset-header').siblings('.fieldset-body').toggleClass('expand');
  $(el).toggleClass('active');
}

function toggleFilters(el) {
  $('#'+el).children(".show-more").remove();
  if ($('#'+el).children("a[style='display: none;']").length) {
    $('#'+el).children("a").show();
    $('#'+el).append(`<button class="button-link show-more" onclick="toggleFilters('`+$('#'+el).attr('id')+`')"><i class="far fa-minus"></i> Hide</button>`);
  }
  else {
    $('#'+el).children("a").slice(5, $('#'+el).children("a").length).hide();
    $('#'+el).append(`<button class="button-link show-more" onclick="toggleFilters('`+$('#'+el).attr('id')+`')"><i class="far fa-plus"></i> Show all (`+ $('#'+el).children("a").length +`)</button>`);
  }
}

function toggleHelpText(el, help_text) {
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
    $(el).after(`<button class="button-link danger" onclick="deleteField(this, 'tr')"><i class="fas fa-trash-alt"></i>Delete permanently</button>`)
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
 * 4. The DELETE checkbox for the form must be a grand-child (within
 * an element with a class of "inline-delete-form-field") of the part
 * of the form to be hidden/shown (see #2).
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
  let deleteField = form_part.children("[class~='inline-delete-form-field']").children("[name$='DELETE']").first();
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
