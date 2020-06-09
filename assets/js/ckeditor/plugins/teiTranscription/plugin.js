/*
    checks only the closest ancestor; 
    therefore, if the text is wrapped in <u><del>text</del></u>, the condition is false
*/


function wrap(teiObject) {
    //create new element
    var newElement = new CKEDITOR.dom.element(teiObject.tag);
    newElement.setAttributes({class: teiObject.className});
    if(teiObject.additionalAttributes.length) {
        for (var i = 0; i < teiObject.additionalAttributes.length; i++) {
            newElement.setAttributes(teiObject.additionalAttributes[i]);
        }
    }
    newElement.setHtml(teiObject.elToInsert.getHtml());

    // check children - make sure the tag is not duplicated in inside the selected tag
    var children = newElement.find(teiObject.conflictChildren);
    for ( var i = 0; i < children.count(); i++ ) {
        children.getItem( i ).$.outerHTML = children.getItem( i ).$.innerHTML;
    }

    return newElement;
}

function unwrapStartTag(el, tag, className) {
    var regexStart = new RegExp("<(?:(?!<).)*?"+ className +".*?>", 'gm');
    var regexEnd = new RegExp("</"+tag+">", 'gm');
    var html = el.$.innerHTML;
    html = html.replace(regexStart, '');
    html = html.replace(regexEnd, '');
    return html;
}

function cleanUp(editorSelection) {
    checkWhiteSpace();
    checkMissingClasses();
    removeEmptyTags(editorSelection);
}

function removeEmptyTags(editorSelection) {
    var elements = editorSelection.document.getBody().getElementsByTag( '*' );
    for ( var i = 0; i < elements.count(); ++i ) {
        if (elements.getItem(i).$.className !== 'tei-lb' && elements.getItem(i).$.innerHTML.length == 0) {
            elements.getItem(i).remove();
        } else if (elements.getItem(i).$.innerHTML == '<br class="tei-lb">') {
            elements.getItem(i).$.outerHTML = elements.getItem(i).$.innerHTML;
        }
    }
}

// TODO
function checkWhiteSpace() {
    return false;
}

// TODO
function checkMissingClasses() {
    return false;
}

CKEDITOR.plugins.add( 'teiTranscription', {
    icons: 'teiPageBreak,teiAdd,teiDel,teiParagraph,teiLineBreak,teiNote,teiUnclear,teiUnderline,teiFormula,teiFigure,teiCatchwords,teiForeign,teiSpaceBefore,teiSpaceAfter',
    init: function( editor ) {
        // TEI-ADD <ins class="tei-add"> | <add> </add>
        editor.addCommand( 'teiAdd', {
            exec: function( editor ) {
                var editorSelection = editor.getSelection();
                var range = editorSelection.getRanges()[ 0 ];
                var el = editor.document.createElement( 'div' );
                el.append(range.cloneContents());
                var commonAncestor = editorSelection.getCommonAncestor();
                var startTag = editorSelection.getStartElement();

                var teiObject = {
                    elToInsert: el,
                    tag: 'ins',
                    className: 'tei-add',
                    additionalAttributes: [],
                    conflictChildren: '.tei-add, .tei-del, .tei-p'
                }

                // unwrap - check class of the parent element; if the same as the class of the embedded icon
                if (teiObject.className === commonAncestor.$.className || teiObject.className === commonAncestor.$.parentElement.className) {
                    editor.insertHtml(teiObject.elToInsert.getHtml());
                }
                // unwrap - optional, is used to unwrap when two or more objects are highlighted but don't have the same common ancestor
                else if (teiObject.className === startTag.$.className) {
                    var newElement = unwrapStartTag(teiObject.elToInsert, teiObject.tag, teiObject.className);
                    editor.insertHtml(newElement);
                }
                // wrap - check if any text was selected so as not to embed an empty tag
                else if (editorSelection.getSelectedText().length > 0) {
                    var newElement = wrap(teiObject);
                    //resolve conflicts
                    if (commonAncestor.$.className == 'tei-del') {
                        range.deleteContents();
                        editor.insertHtml('</del>'+newElement.$.outerHTML+'<ins class="tei-del">');
                    } else {
                        editor.insertElement(newElement);
                    }
                }
                else {
                    return false;
                }
                // clean up the script and remove empty tags
                cleanUp(editorSelection);
            }
        });
        editor.ui.addButton('TeiAdd', {
            label: 'tei-add: highlights text that was\ninserted in the source text by an author',
            command: 'teiAdd',
            toolbar: 'tei-add'
        });

        // TEI-DELETE <del class="tei-del"> | <del> </del>
        editor.addCommand( 'teiDelete', {
            exec: function( editor ) {
                var editorSelection = editor.getSelection();
                var range = editorSelection.getRanges()[ 0 ];
                var el = editor.document.createElement( 'div' );
                el.append(range.cloneContents());
                var commonAncestor = editorSelection.getCommonAncestor();
                var startTag = editorSelection.getStartElement();

                var teiObject = {
                    elToInsert: el,
                    tag: 'del',
                    className: 'tei-del',
                    additionalAttributes: [],
                    conflictChildren: '.tei-del, .tei-add, .tei-p'
                }

                if (teiObject.className === commonAncestor.$.className || teiObject.className === commonAncestor.$.parentElement.className) {
                    editor.insertHtml(teiObject.elToInsert.getHtml());
                }
                else if (teiObject.className === startTag.$.className) {
                    var newElement = unwrapStartTag(teiObject.elToInsert, teiObject.tag, teiObject.className);
                    editor.insertHtml(newElement);
                }
                else if (editorSelection.getSelectedText().length > 0) {
                    var newElement = wrap(teiObject);
                    //resolve conflicts
                    if (commonAncestor.$.className == 'tei-add') {
                        range.deleteContents();
                        editor.insertHtml('</ins>'+newElement.$.outerHTML+'<ins class="tei-add">');
                    } else {
                        editor.insertElement(newElement);
                    }
                }
                else {
                    return false;
                }
                cleanUp(editorSelection);
            }
        });
        editor.ui.addButton('TeiDel', {
            label: 'tei-del: highlights text that was\nmarked as deleted by an author',
            command: 'teiDelete',
            toolbar: 'tei-del'
        });

        // TEI-UNDERLINE <u class="tei-hi"> |  <hi rend='underline'>  </hi>
        editor.addCommand( 'teiUnderline', {
            exec: function( editor ) {
                var editorSelection = editor.getSelection();
                var range = editorSelection.getRanges()[ 0 ];
                var el = editor.document.createElement( 'div' );
                el.append(range.cloneContents());
                var commonAncestor = editorSelection.getCommonAncestor();
                var startTag = editorSelection.getStartElement();

                var teiObject = {
                    elToInsert: el,
                    tag: 'u',
                    className: 'tei-hi',
                    additionalAttributes: [{'data-tei-rend': 'underline'}],
                    conflictChildren: '.tei-hi, .tei-p'
                }

                if (teiObject.className === commonAncestor.$.className || teiObject.className === commonAncestor.$.parentElement.className) {
                    editor.insertHtml(teiObject.elToInsert.getHtml());
                }
                else if (teiObject.className === startTag.$.className) {
                    var newElement = unwrapStartTag(teiObject.elToInsert, teiObject.tag, teiObject.className);
                    editor.insertHtml(newElement);
                }
                else if (editorSelection.getSelectedText().length > 0) {
                    var newElement = wrap(teiObject);
                    editor.insertElement(newElement);
                }
                else {
                    return false;
                }
                cleanUp(editorSelection);
            }
        });
        editor.ui.addButton('TeiUnderline', {
            label: 'tei-hi: highlights text\nthat was underlined by an author',
            command: 'teiUnderline',
            toolbar: 'tei-underline'
        });

        // TEI-NOTE <span class="tei-note"> | <note>  </note>
        editor.addCommand( 'teiNote', {
            exec: function( editor ) {
                var className = 'tei-note';
                var editorSelection = editor.getSelection();
                var range = editorSelection.getRanges()[ 0 ];
                var el = editor.document.createElement( 'div' );
                el.append(range.cloneContents());
                var commonAncestor = editorSelection.getCommonAncestor();

                var teiObject = {
                    elToInsert: el,
                    tag: 'span',
                    className: 'tei-note',
                    additionalAttributes: [],
                    conflictChildren: '.tei-note, .tei-p'
                }
                
                if (className === commonAncestor.$.className || className === commonAncestor.$.parentElement.className) {
                    editor.insertHtml(teiObject.elToInsert.getHtml());
                }
                else if (editorSelection.getSelectedText().length > 0) {
                    var newElement = wrap(teiObject);
                    editor.insertElement(newElement);
                }
                else {
                    return false;
                }
                cleanUp(editorSelection);
            }
        });
        editor.ui.addButton('TeiNote', {
            label: 'tei-note: inserts notes or\nannotations made by an author',
            command: 'teiNote',
            toolbar: 'tei-note'
        });

        // TEI-UNCLEAR <span class="tei-unclear"> | <unclear>[unclear]</unclear>
        editor.addCommand( 'teiUnclear', {
            exec: function( editor ) {
                var editorSelection = editor.getSelection();
                var range = editorSelection.getRanges()[ 0 ];
                var el = editor.document.createElement( 'div' );
                el.append(range.cloneContents());
                var commonAncestor = editorSelection.getCommonAncestor();
                var startTag = editorSelection.getStartElement();

                var teiObject = {
                    elToInsert: el,
                    tag: 'span',
                    className: 'tei-unclear',
                    additionalAttributes: [],
                    conflictChildren: '.tei-unclear, .tei-p'
                }

                if (teiObject.className === commonAncestor.$.className || teiObject.className === commonAncestor.$.parentElement.className) {
                    // check if text is [unclear] which was inserted automatically
                    if (commonAncestor.$.parentElement.innerHTML == '[unclear]') {
                        commonAncestor.$.parentElement.remove();
                    } else {
                        editor.insertHtml(teiObject.elToInsert.getHtml());
                    }
                }
                else if (editorSelection.getSelectedText().length > 0) {
                    var newElement = wrap(teiObject);
                    editor.insertElement(newElement);
                } 
                else if (editorSelection.getSelectedText().length == 0) {
                    editor.insertHtml('<'+teiObject.tag+' class="'+teiObject.className+'">[unclear]</'+teiObject.tag+'> ');
                }
                else {
                    return false;
                }
                cleanUp(editorSelection);
            }
        });
        editor.ui.addButton('TeiUnclear', {
            label: 'tei-unclear: highlights illegible text\nthat cannot be transcribed with certainty',
            command: 'teiUnclear',
            toolbar: 'tei-unclear'
        });

        // TEI-LINEBREAK <br class="tei-lb"> | <lb/>
        editor.addCommand( 'teiLineBreak', {
            exec: function( editor ) {
                var className = 'tei-lb';
                var editorSelection = editor.getSelection();
                var range = editorSelection.getRanges()[ 0 ];
                var newElement = new CKEDITOR.dom.element("br");
                newElement.setAttributes({class: className});
                range.insertNode(newElement);
            }
        });
        editor.ui.addButton('TeiLineBreak', {
            label: 'tei-lb: inserts a line break',
            command: 'teiLineBreak',
            toolbar: 'tei-lb'
        });

        // EXTRA SPACE BEFORE - when the cursor cannot be placed between the tags, traverse one step up in the DOM from the selection and add extra space before the tag
        editor.addCommand( 'teiSpaceBefore', {
            exec: function( editor ) {
                var editorSelection = editor.getSelection();
                var newElement = new CKEDITOR.dom.text( '\u00A0' );
                var startTag = editorSelection.getStartElement();
                newElement.insertBefore(startTag);
            }
        });
        editor.ui.addButton('TeiSpaceBefore', {
            label: 'inserts extra space before the opening tag',
            command: 'teiSpaceBefore',
            toolbar: 'tei-spaceBefore'
        });

        // EXTRA SPACE AFTER - when the cursor cannot be placed between the tags, traverse one step up in the DOM from the selection and add extra space after the tag
        editor.addCommand( 'teiSpaceAfter', {
            exec: function( editor ) {
                var editorSelection = editor.getSelection();
                var newElement = new CKEDITOR.dom.text( '\u00A0' );
                var startTag = editorSelection.getStartElement();
                newElement.insertAfter(startTag);
            }
        });
        editor.ui.addButton('TeiSpaceAfter', {
            label: 'inserts extra space after the closing tag',
            command: 'teiSpaceAfter',
            toolbar: 'tei-spaceAfter'
        });

        // TEI-PAGEBREAK <span class="tei-pb"> | <pb n="x">
        editor.addCommand( 'teiPageBreak', {
            exec: function( editor ) {
                var editorSelection = editor.getSelection();
                var range = editorSelection.getRanges()[ 0 ];
                var el = editor.document.createElement( 'div' );
                el.append(range.cloneContents());

                var commonAncestor = editorSelection.getCommonAncestor();
                var startTag = editorSelection.getStartElement();

                var teiObject = {
                    elToInsert: el,
                    tag: 'span',
                    className: 'tei-pb',
                    additionalAttributes: [{'data-tei-n': editor.getSelection().getSelectedText()}],
                    conflictChildren: '.tei-pb, .tei-p'
                }

                if (teiObject.className === commonAncestor.$.parentElement.className) {
                    var html = commonAncestor.$.parentElement.innerHTML;
                    commonAncestor.remove();
                    editor.insertHtml(html);
                } 
                else if (teiObject.className === startTag.$.className) {
                    var newElement = unwrapStartTag(teiObject.elToInsert, teiObject.tag, teiObject.className);
                    editor.insertHtml(newElement);
                }
                else if (editorSelection.getSelectedText().length > 0) {
                    var newElement = wrap(teiObject);
                    editor.insertElement(newElement);
                }
                else {
                    return false;
                }
                cleanUp(editorSelection);
            }
        });
        editor.ui.addButton('TeiPageBreak', {
            label: 'tei-pb: marks the beginning of\na new page in a paginated document',
            command: 'teiPageBreak',
            toolbar: 'tei-pb'
        });

        // TEI-CATCHWORDS <span class="tei-catchwords"> | <catchwords>  </catchwords>
        editor.addCommand( 'teiCatchwords', {
            exec: function( editor ) {
                var editorSelection = editor.getSelection();
                var range = editorSelection.getRanges()[ 0 ];
                var el = editor.document.createElement( 'div' );
                el.append(range.cloneContents());
                var commonAncestor = editorSelection.getCommonAncestor();
                var startTag = editorSelection.getStartElement();

                var teiObject = {
                    elToInsert: el,
                    tag: 'span',
                    className: 'tei-catchwords',
                    additionalAttributes: [],
                    conflictChildren: '.tei-catchwords'
                }

                if (teiObject.className === commonAncestor.$.className || teiObject.className === commonAncestor.$.parentElement.className) {
                    editor.insertHtml(teiObject.elToInsert.getHtml());
                }
                else if (teiObject.className === startTag.$.className) {
                    var newElement = unwrapStartTag(teiObject.elToInsert, teiObject.tag, teiObject.className);
                    editor.insertHtml(newElement);
                }
                else if (editorSelection.getSelectedText().length > 0) {
                    var newElement = wrap(teiObject);
                    editor.insertElement(newElement);
                }
                else {
                    return false;
                }
                cleanUp(editorSelection);
            }
        });
        editor.ui.addButton('teiCatchwords', {
            label: 'tei-catchwords: indicates annotations at the foot of the page',
            command: 'teiCatchwords',
            toolbar: 'tei-catchwords'
        });

        // TEI-FORMULA <span class="tei-formula">[mathematical formula or graphic depicted in document]</span> | <formula> [mathematical formula or graphic depicted in document] </formula>
        editor.addCommand( 'teiFormula', {
            exec: function( editor ) {
                var teiObject = {
                    elToInsert: '[mathematical formula or graphic depicted in document]',
                    tag: 'span',
                    className: 'tei-formula',
                    additionalAttributes: [],
                    conflictChildren: '.tei-formula'
                }
                var editorSelection = editor.getSelection();
                var range = editorSelection.getRanges()[ 0 ];

                var commonAncestor = editorSelection.getCommonAncestor();

                // remove the formula reference completely
                if (teiObject.className === commonAncestor.$.className || teiObject.className === commonAncestor.$.parentElement.className) {
                    commonAncestor.remove();
                }
                // embed
                else {
                    var newElement = new CKEDITOR.dom.element(teiObject.tag);
                    newElement.setAttributes({class: teiObject.className});
                    newElement.setHtml(teiObject.elToInsert);
                    range.insertNode(newElement);
                }
                cleanUp(editorSelection);
            }
        });
        editor.ui.addButton('TeiFormula', {
            label: 'tei-formula: indicates that text contains a mathematical or other formula',
            command: 'teiFormula',
            toolbar: 'tei-formula'
        });
        
        // TEI-FIGURE <span class="tei-figure"><span class="tei-figDesc">[image or symbol depicted in document]</span></span> | <figure> <figDesc> [image or symbol depicted in document]  </figDesc> </figure>
        editor.addCommand( 'teiFigure', {
            exec: function( editor ) {
                var teiObject = {
                    elToInsert: '<span class="tei-figDesc">[image or symbol depicted in document]</span>',
                    tag: 'span',
                    className: 'tei-figure',
                    additionalAttributes: [],
                    conflictChildren: '.tei-figure'
                }
                var editorSelection = editor.getSelection();
                var range = editorSelection.getRanges()[ 0 ];

                var commonAncestor = editorSelection.getCommonAncestor();
                // remove the figure reference accessed via tei-figDesc
                if (teiObject.className === commonAncestor.$.parentNode.parentElement.className) {
                    commonAncestor.remove();
                }
                // embed
                else {
                    var newElement = new CKEDITOR.dom.element(teiObject.tag);
                    newElement.setAttributes({class: teiObject.className});
                    newElement.setHtml(teiObject.elToInsert);
                    range.insertNode(newElement);
                }
                cleanUp(editorSelection);
            }
        });
        editor.ui.addButton('TeiFigure', {
            label: 'tei-figure: used to represent graphic\ninformation such as an illustration,\ndrawing, doodle, symbol, emblem',
            command: 'teiFigure',
            toolbar: 'tei-figure'
        });

        // DIALOG BOX - added to select language for the <foreign xml:lang=""> tag
        editor.addCommand( 'foreignDialog', new CKEDITOR.dialogCommand( 'foreignDialog' ) );
        CKEDITOR.dialog.add( 'foreignDialog', function ( editor ) {
            return {
                title: 'Select language',
                minWidth: 100,
                minHeight: 100,
        
                contents: [
                    {
                        id: 'tab-lang',
                        label: 'Language Tab',
                        elements: [
                            {
                                type: 'select',
                                id: 'language',
                                minWidth: 80,
                                items: [ [ 'unknown' ], [ 'English, en' ], [ 'French, fr' ], ['German, de'], ['Greek, el'], ['Latin, la'], ['Russian, ru']],
                                'default': 'French, fr',
                                validate: CKEDITOR.dialog.validate.notEmpty( "Abbreviation field cannot be empty." )
                            },
                        ]
                    }
                ],
                onOk: function() {
                    var dialog = this;
                    var editorSelection = editor.getSelection();
                    var range = editorSelection.getRanges()[ 0 ];
                    var el = editor.document.createElement( 'div' );
                    el.append(range.cloneContents());

                    var teiObject = {
                        elToInsert: el,
                        tag: 'span',
                        className: 'tei-foreign',
                        additionalAttributes: [],
                        conflictChildren: '.tei-foreign'
                    }
                    var language = dialog.getValueOf('tab-lang', 'language').split(", ")[1];
                    teiObject.additionalAttributes.push({'data-tei-lang': language});
                    var newElement = wrap(teiObject);
                    editor.insertElement(newElement);
                }
            };
        });

        // TEI-FOREIGN <span class="tei-foreign" data-tei-lang="fr"> | <foreign xml:lang='xx'>  </foreign>
        editor.addCommand( 'teiForeign', {
            exec: function( editor ) {
                var editorSelection = editor.getSelection();
                var range = editorSelection.getRanges()[ 0 ];
                var el = editor.document.createElement( 'div' );
                el.append(range.cloneContents());
                var commonAncestor = editorSelection.getCommonAncestor();
                var startTag = editorSelection.getStartElement();

                var teiObject = {
                    elToInsert: el,
                    tag: 'span',
                    className: 'tei-foreign',
                    additionalAttributes: [],
                    conflictChildren: '.tei-foreign'
                }

                if (teiObject.className === commonAncestor.$.className || teiObject.className === commonAncestor.$.parentElement.className) {
                    editor.insertHtml(teiObject.elToInsert.getHtml());
                }
                else if (teiObject.className === startTag.$.className) {
                    var newElement = unwrapStartTag(teiObject.elToInsert, teiObject.tag, teiObject.className);
                    editor.insertHtml(newElement);
                }
                else if (editorSelection.getSelectedText().length > 0) {
                    editor.execCommand('foreignDialog');
                }
                else {
                    return false;
                }
                cleanUp(editorSelection);
            }
        });
        editor.ui.addButton('teiForeign', {
            label: 'tei-foreign: identifies a word or phrase\nas belonging to some language other\nthan that of the surrounding text',
            command: 'teiForeign',
            toolbar: 'tei-foreign'
        });

        // TEI-PARAGRAPH <p class="tei-p"> | <p>
        editor.addCommand( 'teiParagraph', {
            exec: function( editor ) {
                var editorSelection = editor.getSelection();
                var range = editorSelection.getRanges()[ 0 ];
                var el = editor.document.createElement( 'div' );
                el.append(range.cloneContents());
                var commonAncestor = editorSelection.getCommonAncestor();
                var startTag = editorSelection.getStartElement();

                var teiObject = {
                    elToInsert: el,
                    tag: 'p',
                    className: 'tei-p',
                    additionalAttributes: [],
                    conflictChildren: '.tei-p'
                }
                if (teiObject.className === commonAncestor.$.className || teiObject.className === commonAncestor.$.parentElement.className) {
                    var html = "</p>"+teiObject.elToInsert.getHtml()+"<p class='tei-p'>";
                    range.deleteContents();
                    editor.insertHtml(html);
                }
                else if (editorSelection.getSelectedText().length > 0) {
                    var newElement = wrap(teiObject);
                    editor.insertElement(newElement);
                }
                else {
                    return false;
                }
                cleanUp(editorSelection);
            }
        });
        editor.ui.addButton('TeiParagraph', {
            label: 'tei-p: inserts a paragraph',
            command: 'teiParagraph',
            toolbar: 'tei-p'
        });

        // TODO - add a popup with documentation
        // TODO - unwrap elements with only br in them
        // TODO - make sure that only markup relevant to the tag is removed, not all text markup - currently removing parents
    }
});