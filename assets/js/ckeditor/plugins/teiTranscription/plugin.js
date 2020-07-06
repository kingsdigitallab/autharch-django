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
    checkMissingClasses();
    removeEmptyTags(editorSelection);
}

function removeEmptyTags(editorSelection) {
    var elements = editorSelection.document.getBody().getElementsByTag( '*' );
    for ( var i = 0; i < elements.count(); ++i ) {
        if (elements.getItem(i).$.className !== 'tei-lb' && elements.getItem(i).$.innerHTML.length == 0 || elements.getItem(i).$.innerHTML == "<br>") {
            elements.getItem(i).remove();
        } else if (elements.getItem(i).$.innerHTML == '<br class="tei-lb">') {
            elements.getItem(i).$.outerHTML = elements.getItem(i).$.innerHTML;
        }
    }
}

// TODO
function checkMissingClasses() {
    return false;
}


CKEDITOR.plugins.add( 'teiTranscription', {
    icons: 'teiPageBreak,teiAdd,teiDel,teiParagraph,teiLineBreak,teiNote,teiUnclear,teiUnderline,teiFormula,teiFigure,teiCatchwords,teiForeign,teiSpaceBefore,teiSpaceAfter,howToUse',
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
                // else if (teiObject.className === startTag.$.className) {
                //     var newElement = unwrapStartTag(teiObject.elToInsert, teiObject.tag, teiObject.className);
                //     editor.insertHtml(newElement);
                // }
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
                // else if (teiObject.className === startTag.$.className) {
                //     var newElement = unwrapStartTag(teiObject.elToInsert, teiObject.tag, teiObject.className);
                //     editor.insertHtml(newElement);
                // }
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
                // else if (teiObject.className === startTag.$.className) {
                //     var newElement = unwrapStartTag(teiObject.elToInsert, teiObject.tag, teiObject.className);
                //     editor.insertHtml(newElement);
                // }
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
                // else if (teiObject.className === startTag.$.className) {
                //     var newElement = unwrapStartTag(teiObject.elToInsert, teiObject.tag, teiObject.className);
                //     editor.insertHtml(newElement);
                // }
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
                // else if (teiObject.className === startTag.$.className) {
                //     var newElement = unwrapStartTag(teiObject.elToInsert, teiObject.tag, teiObject.className);
                //     editor.insertHtml(newElement);
                // }
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
    

        editor.addCommand( 'howToUse', new CKEDITOR.dialogCommand( 'howToUseDialog' ) );
        CKEDITOR.dialog.add( 'howToUseDialog', function ( editor ) {
            var size = CKEDITOR.document.getWindow().getViewPaneSize();
            
            // Make it maximum 800px wide, but still fully visible in the viewport.
            var width = Math.min( size.width - 70, 800 );

            // Make it use 2/3 of the viewport height.
            var height = size.height / 1.5;
            return {
                title: 'How to use the trascription editor',
                minWidth: width,
                minHeight: height,
        
                contents: [
                    {
                        id: 'tab-use',
                        label: 'How To Use Tab',
                        elements: [
                            {
                                type: 'html',
                                id: 'description',
                                html: `
                                    <div id="rte-doc-dialog">
                                        <h2>Introduction</h2>
                                        <p>The transcription editor was developed for you to review and edit the existing transcriptions of archival records. The editing process involves encoding, i.e., adding new or detecting missing document features, such as identifying a missing markup of a paragraph, encoding foreign words/figures/formulas/catchwords, spotting missing notes/deleted text/added text, or highlighting text that cannot be transcribed with certainty.</p>
                                        <p>You are not expected to be familiar with a TEI-related syntax before editing transcriptions. The toolbar in the transcription editor has all the buttons needed to encode text:</p>
                                        <img src="/static/images/RTEtoolbar.png" alt="RTE toolbar" />
                                        <p>For instance, if you noticed that some text needs to be underlined, you select this text and click on the Underline button <img src="/static/images/icons/teiUnderline.png" alt="tei underlined text" class="inline-img"/>. To remove the underline (i.e., to unwrap the text), you need to follow the same steps: you select the text that you want to unwrap and then you click on the Underline button <img src="/static/images/icons/teiUnderline.png" alt="tei underlined text" class="inline-img"/>.</p>
                                        <h2>List of tags</h2>
                                        <h3>Paragraph</h3>
                                        <div class="two-column-table">
                                            <img src="/static/images/icons/teiParagraph.png" alt="tei paragraph" class="tag-icon"/>
                                            <p class="tag">&lt;p class="tei-p"&gt;</p>
                                        </div>
                                        <p>This element is used to insert a new paragraph.</p>
                                        <h3>Note</h3>
                                        <div class="two-column-table">
                                            <img src="/static/images/icons/teiNote.png" alt="tei note" class="tag-icon"/>
                                            <p class="tag">&lt;span class="tei-note"&gt;</p> 
                                        </div>
                                        <p>This element inserts notes or annotations made by an author in the source text.</p>
                                        <h3>Page break</h3>
                                        <div class="two-column-table">
                                            <img src="/static/images/icons/teiPageBreak.png" alt="tei page break" class="tag-icon"/>
                                            <p class="tag">&lt;span class="tei-pb" data-tei-n=""&gt;</p>
                                        </div>
                                        <p>This element marks the beginning of a new page in a paginated document. You can find 'Page #' at the beginning of each transcribed page.</p>
                                        <h3>Underlined text</h3>
                                        <div class="two-column-table">
                                            <img src="/static/images/icons/teiUnderline.png" alt="tei underlined text" class="tag-icon"/>
                                            <p class="tag">&lt;u class="tei-hi" data-tei-rend="underline"&gt;</p>
                                        </div>
                                        <p>This element highlights text that was underlined by an author in the source text.</p>
                                        <h3>Deleted text</h3>
                                        <div class="two-column-table">
                                            <img src="/static/images/icons/teiDel.png" alt="tei deleted text" class="tag-icon"/>
                                            <p class="tag">&lt;del class="tei-del"&gt;</p>
                                        </div>
                                        <p>This element highlights text that was marked as deleted by an author in the source text.</p>
                                        <h3>Inserted text</h3>
                                        <div class="two-column-table">
                                            <img src="/static/images/icons/teiAdd.png" alt="tei inserted text" class="tag-icon"/>
                                            <p class="tag">&lt;ins class="tei-add"&gt;</p>
                                        </div>
                                        <p>This element is used to highlight text that was inserted in the source text by an author.</p>
                                        <h3>Unclear text</h3>
                                        <div class="two-column-table">
                                            <img src="/static/images/icons/teiUnclear.png" alt="tei unclear text" class="tag-icon"/>
                                            <p class="tag">&lt;span class="tei-unclear"&gt;</p>
                                        </div>
                                        <p>This element highlights illegible text that cannot be transcribed with certainty. You can either wrap a word or a sentence that is unclear (select an unclear word or a sentence and click on the Unclear button), or you can add '[unclear]' directly to the trascription (click on the Unclear button).</p>
                                        <h3>Catchword</h3>
                                        <div class="two-column-table">
                                            <img src="/static/images/icons/teiCatchwords.png" alt="tei catchword" class="tag-icon"/>
                                            <p class="tag">&lt;span class="tei-catchwords"&gt;</p>
                                        </div>
                                        <p>This element indicates annotations at the foot of the page.</p>
                                        <h3>Foreign word</h3>
                                        <div class="two-column-table">
                                            <img src="/static/images/icons/teiForeign.png" alt="tei foreign word" class="tag-icon"/>
                                            <p class="tag">&lt;span class="tei-foreign" data-tei-lang=""&gt;</p>
                                        </div>
                                        <p>This element identifies a word or phrase as belonging to some language other than that of the surrounding text. When you click on the Foreign button, you will be prompted to select a language the word or phrase belongs to in a dialog box.</p>
                                        <h3>Formula</h3>
                                        <div class="two-column-table">
                                            <img src="/static/images/icons/teiFormula.png" alt="tei formula" class="tag-icon"/>
                                            <p class="tag">&lt;span class="tei-formula"&gt;[mathematical formula or graphic depicted in document]&lt;/span&gt;</p>
                                        </div>
                                        <p>This element is inserted before selected text. It indicates that text contains a mathematical or other formula.</p>
                                        <h3>Figure (images or symbols)</h3>
                                        <div class="two-column-table">
                                            <img src="/static/images/icons/teiFigure.png" alt="tei figure" class="tag-icon"/>
                                            <p class="tag">&lt;span class="tei-figure"&gt;&lt;span class="tei-figDesc"&gt;[image or symbol depicted in document]&lt;/span&gt;&lt;/span&gt;</p>
                                        </div>
                                        <p>This element is inserted before selected text. It is used to represent graphic information such as an illustration, drawing, doodle, symbol, emblem.</p>
                                        <h3>Line break</h3>
                                        <div class="two-column-table">
                                            <img src="/static/images/icons/teiLineBreak.png" alt="line break" class="tag-icon"/>
                                            <p class="tag">&lt;br class="tei-lb"&gt;</p>
                                        </div>
                                        <p>This element is used to insert a line break.</p>
                                        <h3>Space before tag</h3>
                                        <div class="two-column-table">
                                            <img src="/static/images/icons/teiSpaceBefore.png" alt="space before" class="tag-icon"/>
                                        </div>
                                        <p>This element inserts extra space before the opening tag in case you cannot put the cursor before text.</p>
                                        <h3>Space after tag</h3>
                                        <div class="two-column-table">
                                            <img src="/static/images/icons/teiSpaceAfter.png" alt="space after" class="tag-icon"/>
                                        </div>
                                        <p>This element inserts extra space after the closing tag in case you cannot put the cursor after text.</p>
                                        <h3>Source code</h3>
                                        <p>You can edit transcriptions directly in the source code (see the Source button in the toolbar), which, however, is not recommended. When editing in the source code, you are required to follow the syntax for each tag and you cannot add new tags; otherwise, we will not be able to convert transcriptions back to the TEI format.</p>
                                    </div>
                                `
                            }
                        ]
                    }
                ],
                buttons: [
                    {
                        type: 'button',
                        id: 'rte-close-button',
                        label: 'CLOSE',
                        title: 'close',
                        style: 'display: none'
                    }
                ],
                onShow: function(){
                },
                onOk: function() {
                    var dialog = this;
                }
            };
        });
        editor.ui.addButton('HowToUse', {
            label: 'How to Use',
            command: 'howToUse',
            toolbar: 'tei-howToUse'
        });
        
        // TODO - unwrap elements with only br in them
        // TODO - make sure that only markup relevant to the tag is removed, not all text markup - currently removing parents
    }
});