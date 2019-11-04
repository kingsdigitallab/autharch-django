// object for popups that appear when users hover over question marks 
var additionalInfo = {
    'identities': 'This element denotes names used by the entity.',
    'general-date-from': 'Date of existence. A birth date, or for corporate bodies, a creation date.', 
    'general-date-to': 'Date of existence. A death date, or for corporate bodies, an extinction date.', 
    'general-display-date': '',
    'display-name': '',
    'name-entry': 'This element "is used to record a name by which the corporate body, the person, or the family described in the EAC-CPF instance is known". See name entry at https://eac.staatsbibliothek-berlin.de.',
    'name-date-used-from': 'Name dates are especially important for royal and aristocratic names to track their usage of particular titles. Attach dates where known, even when personal entities are not royal or aristocratic; attaching dates for corporate bodies that have changed names over time is also very useful.',
    'name-date-used-until': 'Name dates are especially important for royal and aristocratic names to track their usage of particular titles. Attach dates where known, even when personal entities are not royal or aristocratic; attaching dates for corporate bodies that have changed names over time is also very useful.',
    'name-entry-language': 'Name entry(s) will always be in their English form and use the Latin script and this information is captured in attributes within the name entry.',
    'name-entry-script': 'Name entry(s) will always be in their English form and use the Latin script and this information is captured in attributes within the name entry.',
    'date-from': '',
    'date-to': '',
    'display-date': '',
    'descriptions': 'This element encompasses several methods to describe the entity and place them/it within context',
    'gender': 'Note that gender relates to identity only and therefore should not be used to capture sexual preference (these are sometimes conflated). The term content should be taken from the Homosaurus. The most common terms likely to be used within the GPP are “women” and “men” but we need flexibility to include terms outside the binary. If the person did not live to adulthood it is acceptable to use “girls”, “boys”, or another term as appropriate.',
    'gender-descriptive-notes': '',
    'gender-citation': '',
    'biography': 'This element encompasses the biography of a person or the history of a corporate body. ',
    'biography-abstract': 'If only a short biography is available, then it will be included in the abstract; if a long-form biography is available, then the abstract will contain a derived summary.',
    'biography-content': '',
    'biography-structure-genealogy': 'This element "encodes information within the description area, information expressing the internal administrative structure(s) of a corporate body and the dates of any changes to that structure that are significant to understanding the way that corporate body conducted affairs (such as dated organization charts), or the genealogy of a family (such as a family tree) in a way that demonstrates the interrelationships of its members with relevant dates". See structureOrGenealogy at eac.staatsbibliothek-berlin.de.',
    'biography-sources': '',
    'biography-copyright': 'Copyright statements for biographies or histories are to conform to the Creative Commons Licence used throughout the GPP - http://www.chicagomanualofstyle.org/tools_citationguide/citation-guide-1.html.',
    'language': 'This element denotes the language(s) used by an entity.',
    'script': '',
    'place': 'It is used to capture geographical locations of significance in the history of the entity. The content for place is controlled and should conform to the GeoNames form of the geographic name; or the Wikidata form if the name is not available in GeoNames.',
    'place-address': '',
    'place-role': 'For preference, for personal entities we should capture, at minimum, birth and death places. If it is considered useful, further places can be captured such as residences.',
    'place-date': 'If dates are available you should  include them but do note if they are repetition of dates of existence in which case they do not need to be repeated here.',
    'event': '',
    'event-place': '',
    'mandate': 'This term captures “The source of authority or mandate for the corporate body in terms of its powers, functions, responsibilities or sphere of activities, such as a law, directive, or charter.” See mandate at eac.staatsbibliothek-berlin.de.',
    'mandate-term': '',
    'mandate-descriptive-notes': '',
    'mandate-citation': '',
    'legal-status': '',
    'legal-status-term': '',
    'legal-status-descriptive-notes': '',
    'legal-status-citation': 'This "is a generic element available within a number of descriptive elements that cites an external resource in machine and / or human readable form". See citation at eac.staatsbibliothek-berlin.de.',
    'function': 'This element captures “various information about a function, activity, role, or purpose performed or manifested by the CPF entity being described.”. See function at eac.staatsbibliothek-berlin.de.',
    'relations': 'This element captures the relationship between a person or organisation within the GPP  name authority files and the entity described in the EAC-CPF instance you are encoding. ',
    'relationship-type': '',
    'related-person-corporate-body': '',
    'relations-description': '', 
    'relations-place': '',
    'resources': '',
    'resource-relationship-type': 'This element "contains the description of a resource related to the described entity". See resourceRelation at eac.staatsbibliothek-berlin.de.',
    'resource-citation': '',
    'resource-url': '',
    'resource-notes': '',
    'sources': '',
    'source-name': '',
    'source-url': '',
    'source-notes': '',
    'control': 'This element encompasses administrative metadata.',
    'control-language': 'The language and script of the EAC-CPF file (not for the entity itself).',
    'control-rights-declaration': '',
    'control-script': '',
    'control-rights-abbreviation': '',
    'control-rights-declaration': '',
    'archival-record-summary': '',
    'archival-record-repository': 'This element is used to give the managing custodian of the material being described. "Royal Archives" is the default content. Choose "Royal Library" when necessary.',
    'archival-record-repository-code': 'This element is used to give the ARCHON code for the institution holding the material. For the Georgian Papers Project, the Royal Library will be included under the umbrella of the Royal Archives ARCHON code.',
    'archival-record-series': '',
    'archival-record-parent-file': '',
    'archival-record-references': 'This element is used for the Royal Archive, former and CALM references.',
    'archival-record-archival-level': '',
    'archival-record-record-type': 'This element is used to distinguish different types of record to enable users to filter searches to specific types of documents. This data element should be completed at the lowest level possible.',
    'archival-record-rcin': '',
    'archival-record-url': 'This element is used to give the file name of the digitised image of the document(s) (PDF) to enable users to link to Georgian Papers Online from shared catalogue data.',
    'archival-record-location-of-originals': 'This element is used to indicate the existence and location, availability and/or destruction of originals, if the unit of description consists of copies. If the original of the unit of description is available (either in the RA or elsewhere), its location should be recorded, together with any significant references. If the originals no longer exist, or their location is unknown, give that information.',
    'archival-record-related-materials': 'This element is used for the cross-referencing of relevant material held elsewhere in the Georgian Papers.',
    'archival-record-description-section': '',
    'archival-record-title': 'This element is used to provide the name of the document(s) appropriate to the level of description. The title should normally not be longer than one sentence in length. If it is possible to summarise the whole document in the Title field then do so and omit use of the Description field. Dates should not normally be included in the Title field unless integral to the name of the record in question. At collection and series level, titles should provide a concise summary of the scope and content of the papers being described. In the case of letters, give the name of the writer and addressee. For those letters with a very clear sense of subject, this can be referred to briefly in the Title field. For those letters with a less clear subject (usually personal family letters which are very hard to summarise), the broad description "on family matters" should be used.',
    'archival-record-start-date': 'This element is used to identify the start date of the document(s). For Collection and Series levels, year dates should be used. For Sub-Series level and below, dates should include day and month (if known). Some approximation of date should always be possible from the record-relationship to other records in the series, office holders named, external events referred to, etc. This data element is for machine-reading and should be replicated in the Date (free-text) data element. No letters, symbols or characters other than numbers should be entered.',
    'archival-record-end-date': 'This element is used to identify the end date of the document(s). For Collection and Series levels, year dates should be used. For Sub-Series level and below, dates should include day and month (if known). Some approximation of date should always be possible from the record-relationship to other records in the series, office holders named, external events referred to, etc. This data element is for machine-reading and should be replicated in the Date (free-text) data element. No letters, symbols or characters other than numbers should be entered.',
    'archival-record-creation-dates': 'This element identifies and records the date(s) of creation of the records being described. The bulk of the records are within a certain period with only a few records of earlier or later date. In the latter case, if significant, reference should be made in the Description field In the case of double-dating, the new style of date should be entered in the Date field. Add both the new style and old style of date in the Description field Square brackets should be used for derived dates. If there is any doubt as to the precise date, it can be preceded by "?" if the exact date is questionable or "c."; if you are only able to narrow down the date range of the document by research. Some approximation of date should always be possible from the record\'s relationship to other records in the series, office holders named, external events referred to, etc. The use of n.d. for undated should be avoided. If a document is undated, this can be noted in the Description field.',
    'archival-record-extent': 'This element is used to give the number of records at the level being described. The extent of the record(s) should be given as appropriate to the level of description. This gives the user an idea of the size of a collection, series, item or file they are interested in. At higher levels, boxes can be included to help users visualise the size of the collection. At file and item levels, number of pages in the document(s) are required (in brackets) in order to guide users as to the size of the digital image download (PDF format). This should be ascertained at the cataloguing stage and not from the PDF. One letter equals one document regardless of length.',
    'archival-record-languages': 'This element is used to give the language(s) in which the documents are written. English is the default content for this field. A new Language field should be created for each language entered. Prominence should be reflected, with the most heavily-used language being given first. At collection and series level the Language data element should give an indication of the most prominent language rather than every single language.',
    'archival-record-writer': 'This element is entered when the writer of the document can be identified. The name and title of the writer at the time of writing should be given. This data element will generally be used at File and Item level, but sometimes at Series level if the whole group of papers has been written by the same individual. If the writer cannot be identified, this data element should be left blank. Writers are those who own the intellectual content of a document, not the copyist. If the document has more than one writer, a new Writer field should be created for each name. Include life dates (in form 1765-1837) when necessary to differentiate between members of the royal family with the same name and title. Job title or occupation can be included if considered necessary, but is not mandatory. It is particularly useful for members of the Royal Household and tradespeople. Names and job titles should be separated by a semi-colon.',
    'archival-record-addressee': 'This element is entered when the recipient of the document can be identified. The name and title of the addressee at the time of writing should be given. This data element will generally be used at File and Item level, but sometimes at Series level if the whole group of papers has been sent to the same individual. If the addressee cannot be identified, this data element should be left blank. If the document has more than one addressee, a new Addressee field should be created for each name. Include life dates (in form 1765-1837) when necessary to differentiate between members of the  royal family with the same name and title. Job title or occupation can be included if considered necessary, but is not mandatory. It is particular useful for members of the Royal Household and tradespeople. Names and job titles should be separated by a semi-colon.',
    'archival-record-place-of-writing': 'The place of writing should be given whether it is a town, house, palace, ship, public house, etc. Enter what is given on the document, do not add details of the town etc. if they are not expressed in the document.',
    'archival-record-description': 'This element is used to give a concise statement that describes the scope and content of the document(s), in particular what the material is and what it relates to. This should be a summary of the content of the document(s) appropriate and relevant to the level of description. This data element should include any issues with dates that cannot be expressed in the Dates field. For higher level records, metadata in the Description field can be itemised to reflect the content of the lower levels of the hierarchy. Content included in the Title field should not be repeated in the Description field. Thought should be given to subject keywords (people, places, events and topics) when entering the Description metadata. Quotations from the document(s) are acceptable in moderation, particularly if it is the only way to summarise the content of a document. Long transcripts should not be included. Record if a document is a copy or a draft or signed or unsigned in this data element. The time the document was signed can also be entered in the Description field. Any decorations, drawings or sketcheson the document can be noted here. Include cross-references to other documents in the collection in this field, for example when referring to enclosures and replies.',
    'archival-record-notes': 'This element is used to accommodate specialised information that cannot be entered in another data element. This field should only be used if there is information about the document(s) that cannot be accommodated in any of the other data elements.',
    'archival-record-receiving-address': '',
    'archival-record-physical-description': 'This element is used to describe the physical appearance of the document(s) and/or carriers, to aid visualisation by the user. Enter at the level at which the digitised image is attached. Provide a brief description of the physical attributes of the document(s) to help users visualise the original when viewing the digitised version.',
    'archival-record-administrative-history': 'This element is used to give the administrative history, biographical details or other historical information about the individual(s) or administrative body/bodies responsible for creating and accumulating the records being described. In the case of individuals, the Administrative History should include full names and titles, the life dates of the person, significant achievements and an outline of their career, concentrating on the period covered by the records in the series. The records of few administrative bodies are included in the Georgian Papers, but for those that are a summary of the organisation (or department) should include its title, purpose and function, and dates of existence as appropriate. It should be noted that the collections within the Georgian Papers are predominately artificial in creation and are based on records to, from and about an individual, rather than being records created by an individual. Some collections are also gathered together by type, and this should be reflected in the Administrative History. This data element should not be used for information about custodial history. Information entered in this data element should be pertinent to the creation of the particular collection of papers.',
    'archival-record-context-area': '',
    'archival-record-cataloguer': '',
    'archival-record-arrangement': 'This element is used to provide information on the internal structure, order and/or system of classification of the unit of description. If the existing order of the papers has been preserved in cataloguing, this should be reflected in this data element. Re-arrangement of documents in the Georgian Papers is infrequent, but this data element should also be used to note any such re-arrangement or noteworthy points about the existing arrangement. At the top-level, a statement to note that "this collection has been artificially created as part of the Georgian Papers digitisation and cataloguing programme" should be included.',
    'archival-record-description-date': '',
    'archival-record-custodial-history-provenance': 'This element is used to give information about the stewardship of papers prior to their accession to the Royal Archives. This data element should be used at whatever level it is appropriate to record custodial history information. Information on custodial history can often be found in the relevant accession record, but it is not always possible to ascertain how a collection entered the Royal Archives. If it is possible to ascertain that the collection entered the Royal Archives with the main deposit from Apsley House, this should be recorded. The name of donor and circumstances of the accession can be given, however it is not necessary to record the cost of the accession (at auction or otherwise). Information about Royal Household departments which reflect or affect the custodial history of the papers should also be included.',
    'archival-record-subjects': '',
    'archival-record-organisations-as-subjects': '',
    'archival-record-persons-as-subjects': '',
    'archival-record-places-as-subjects': '',
    'archival-record-access-area': '',
    'archival-record-known-previous-publications': 'This element is used to identify any publications that are about or are based on the use or study of the document(s) in question. It is used to record a citation to, and/or information about, a publication that is about or based on the use or study of the unit of description, particularly transcriptions and references to published facsimiles. For the purposes of the Georgian Papers, this will predominately be the volumes edited by Aspinall, Fortescue, Namier and Donne.',
    'archival-record-copyright-status': 'This is an administrative field in which the copyright status of a document is given in order to inform the copyright clearance process for publication. This field should be completed at the level at which the digitised document is attached. It should be completed in conjunction with the internal document "Guide to Copyright Categories" for guidance as to which  option to choose from the picklist.',
    'archival-record-withheld': 'This element is used to state when the digital image of a document(s) has been withheld from publication for copyright, conservation or other reasons. This field should be completed when the digital image of a document(s) cannot be published on Georgian Papers Online because copyright clearance has not been established or the document is too fragile to be digitised. It should be completed at the level at which the image should have been attached. This data element will typically be completed by the GPP Content Delivery Project Manager or the Archivist (Digital). If an item is missing, note in this data element.',
    'archival-record-credit': '',
    'log-comments': 'This element is used for the description of changes made in the form.'
};

$(document).ready(function() {

  jQuery.fn.textNodes = function() {
    return this.contents().filter(function() {
      return (this.nodeType === Node.TEXT_NODE);
    });
  }

  // In order to not cause problems with client-side form validation
  // when required fields are hidden, remove the required attribute
  // from all form controls in the logging dialogue, to be added back
  // when it is shown.
  //
  // Might this not better be done by simply adding/removing
  // novalidate on the form?
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


    // ADD-ONS

    // Change textareas to richtext fields. A unique ID must be
    // provided for each, to avoid the contents being duplicated.
    $('.richtext').each(function(index) {
        $(this).richText({id: "richtext-" + index});
    });

    // add search bar to the select dropdown
    $(".select-with-search").select2( {
        placeholder: "Select",
        allowClear: true
    } );


    // optional functionality (can be removed if needed) - dynamic styling of the sections

    // style border for preferred names and identities
    $( "fieldset:has(input[name*='preferred']:checked)" ).addClass('border-left');

    $('body').on('click', 'input[name*="preferred"]', (el) => {
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


// delete a field or a section on the entity page
function deleteField(el) {
    var ref = $(el).closest('.optional-to-delete').attr('data-content-reference');
    if ($(el).closest('.optional-to-delete').siblings('[data-content-reference='+ref+']').length >= 1) {
        warningModal();
        $('input[type=submit]').click((e) => {
            $('.modal').removeClass('active');
            if($(e.target).attr('value') == 'Delete') {
                $(el).closest('.optional-to-delete').remove();
            }
            return false;
        });
    }
    else {
        alertPopup('You need to have at least one more element of this type to delete selected record.');
    }
}


// expand/collapse entity/archival record sections
function toggleTab(el) {
    $(el).parents('.fieldset-header').siblings('.fieldset-body').toggleClass('expand');
    $(el).toggleClass('active');
}

function closeBlock(el) {
    $('.'+el).removeClass('active');
}

function login() {
    window.location.href = "./home.html";
}

function logout() {
    window.location.href = "./login.html";
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
  let label = jButton.parent().first();
  let labelTextNode = label.textNodes();
  if (labelTextNode.text() == label.attr("data-initial-text")) {
    labelTextNode.replaceWith(label.attr("data-toggled-text"));
  } else {
    labelTextNode.replaceWith(label.attr("data-initial-text"));
  }
  // Find the element for the part of the form to be shown/hidden, and
  // toggle its visibility.
  let form_part = jButton.closest("[data-form-type]").find("[class~='inline-deletable']").first();
  form_part.toggleClass("deleted-inline");
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
