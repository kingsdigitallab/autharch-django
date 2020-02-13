$(document).ready(function() {

  // Return the text nodes of the context. Code by Mark Baijens from
  // https://stackoverflow.com/questions/4106809/how-can-i-change-an-elements-text-without-changing-its-child-elements/4106957
  jQuery.fn.textNodes = function() {
    return this.contents().filter(function() {
      return (this.nodeType === Node.TEXT_NODE);
    });
  };

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
  $("#record-form").submit((event) => {
    if ($("#log-modal").hasClass('active')) {
      event.target.submit();
    } else {
      event.preventDefault();
      toggleRequiredControls(dialogueRequiredControls, true);
      $("#log-modal").addClass('active');
    }
  });

  // open popup to add new user who can access the admin panel
  $('#add-form').click(() => {
    $('#add-user-form').addClass('active');
  });

  // open popup to add new user who can access the admin panel
  $('#edit-form').click(() => {
    $('#edit-user-form').addClass('active');
  });

  // ADD-ONS

  // Change textareas to richtext fields. A unique ID must be
  // provided for each, to avoid the contents being duplicated.
  $('.richtext').each(function(index) {
    $(this).richText({id: "richtext-" + index});
  });

  //add tablesorter to the tables
  $(function() {
    $("[id$='table']").tablesorter({
        widgets: ["filter"],
        widgetOptions: {
            filter_columnFilters: true
        }
    });
    
});

  // add search bar to the select dropdown
  $(".select-with-search").select2( {
    placeholder: "Select",
    allowClear: true
  } );


  // optional functionality (can be removed if needed) - dynamic styling of the sections

  // style border for preferred names and identities
  $( "fieldset:has(input[name*='preferred']:checked)").addClass('border-left');
  $( "fieldset:has(input[name*='authorised']:checked)").addClass('border-left');

  $('body').on('click', 'input[name*="preferred"]', (el) => {
    $('input[name*="preferred"]:checked').prop('checked', false);
    $(el.target).parents('fieldset').first().find('input[name*="preferred"]').prop('checked', true);
    $(el.target).parents('fieldset').siblings().removeClass('border-left');
    if ($(el.target).is(':checked')) {
      $(el.target).parents('fieldset').first().addClass('border-left');
    }
  });

  $('body').on('click', 'input[name*="authorised"]', (el) => {
    $('input[name*="authorised"]:checked').prop('checked', false);
    $(el.target).parents('fieldset').first().find('input[name*="authorised"]').prop('checked', true);
    $(el.target).parents('fieldset').siblings().removeClass('border-left');
    if ($(el.target).is(':checked')) {
      $(el.target).parents('fieldset').first().addClass('border-left');
    }
  });

});

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
                                    <input type="button" class="icon-only" aria-label="close" onclick="closeBlock('modal')" value="&#xf00d;" />
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
                                        <input type="button" class="icon-only" aria-label="close" onclick="closeBlock('modal')" value="&#xf00d;" />
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

function closeBlock(el) {
  $('.'+el).removeClass('active');
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
  // Clone the formType form and add it as the last child of the
  // parent of these forms.
  let formParent = getNewFormParent(jContext);
  console.log($("#empty_forms").children("*[data-form-type=event]").html());
  let newForm = $("#empty_forms").children("*[data-form-type=" + formType + "]").clone();
  newForm.appendTo(formParent);
  // Update the new form's controls' @name and @id to use the correct
  // values for its context in the hierarchy of formsets. Their prefix
  // (the part up to the end of the last "__prefix__") should be
  // replaced with the prefix generated from the TOTAL_FORMS control
  // of the containing formset's management form (plus the number of
  // this form), which conveniently already has the full prefix
  // hierarchy in it.
  let totalControl = getManagementFormTotalControl(jContext);
  let newFormPrefixNumber = totalControl.attr("value");
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
  totalControl.attr("value", Number(newFormPrefixNumber) + 1);
}

/**
 * Return a string prefix for a new form whose TOTAL_FORMS control is
 * the supplied control, based on its attrName attribute value and the
 * prefixNumber.
 *
 * @param {jQuery} control - TOTAL_FORMS control
 * @param {String} attrName - name of control's attribute to use as the base
 * @param {String} prefixNumber - string number of the new form
 * @returns {String}
 */
function generateNewFormPrefix(control, attrName, prefixNumber) {
  let attrValue = control.attr(attrName);
  return attrValue.slice(0, attrValue.indexOf("TOTAL_FORMS")) + prefixNumber;
}


/**
 * Return the TOTAL_FORMS form control for the Django formset's
 * management forms associated with the supplied context element.
 *
 * This function is specific to a particular HTML structure, and
 * should be adapted if/when that structure changes.
 *
 * @param {jQuery} context - the element from which to traverse the
 *                           DOM to find the management forms' controls
 * @returns {jQuery}
 */
function getManagementFormTotalControl(context) {
  return context.parents(".formset").first().children("div.management_form").children("input[name$='TOTAL_FORMS']");
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
function deleteField(el) {
  event.preventDefault();
  $(el).closest('[data-form-type]').addClass('none');
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
    label.parent().after(`<button class="button-link danger" onclick="deleteField(this)"><i class="fas fa-trash-alt"></i>Delete forever</button>`)
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


function toggleDeleteUserForm(event, button) {
/**
 * Mark/unmark a user form for deletion.
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
 * 1. The toggling instigator (the delete/undo icon) must be 
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
