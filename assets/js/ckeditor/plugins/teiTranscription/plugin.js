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

function checkWhiteSpace() {

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

CKEDITOR.plugins.add( 'teiTranscription', {
    icons: 'teiPageBreak,teiAdd,teiDel,teiParagraph,teiLineBreak,teiNote,teiUnclear,teiUnderline',
    init: function( editor ) {
        // TEI-ADD
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
                    editor.insertHtml(el.getHtml());
                }
                else if (teiObject.className === startTag.$.className) {
                    var newElement = unwrapStartTag(el, teiObject.tag, teiObject.className);
                    editor.insertHtml(newElement);
                }
                // wrap - check if any text was selected so as not to embed an empty tag
                else if (editorSelection.getSelectedText().length > 0) {
                    //resolve conflicts
                    if (commonAncestor.$.className == 'tei-del') {
                        range.deleteContents();
                    }
                    var newElement = wrap(teiObject);
                    editor.insertElement(newElement);
                }
                else {
                    return false;
                }
                // clean up the script and remove empty tags
                removeEmptyTags(editorSelection);
            }
        });
        editor.ui.addButton('TeiAdd', {
            label: 'tei-add: highlights text that was\ninserted in the source text by an author',
            command: 'teiAdd',
            toolbar: 'tei-add'
        });

        // TEI-DELETE
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
                    editor.insertHtml(el.getHtml());
                }
                else if (teiObject.className === startTag.$.className) {
                    var newElement = unwrapStartTag(el, teiObject.tag, teiObject.className);
                    editor.insertHtml(newElement);
                }
                else if (editorSelection.getSelectedText().length > 0) {
                    //resolve conflicts
                    if (commonAncestor.$.className == 'tei-add') {
                        range.deleteContents();
                    }
                    var newElement = wrap(teiObject);
                    editor.insertElement(newElement);
                }
                else {
                    return false;
                }
                removeEmptyTags(editorSelection);
            }
        });
        editor.ui.addButton('TeiDel', {
            label: 'tei-del: highlights text that was\nmarked as deleted by an author',
            command: 'teiDelete',
            toolbar: 'tei-del'
        });

        // TEI-UNDERLINE
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
                    editor.insertHtml(el.getHtml());
                }
                else if (teiObject.className === startTag.$.className) {
                    var newElement = unwrapStartTag(el, teiObject.tag, teiObject.className);
                    editor.insertHtml(newElement);
                }
                else if (editorSelection.getSelectedText().length > 0) {
                    var newElement = wrap(teiObject);
                    editor.insertElement(newElement);
                }
                else {
                    return false;
                }
                removeEmptyTags(editorSelection);
            }
        });
        editor.ui.addButton('TeiUnderline', {
            label: 'tei-hi: highlights text\nthat was underlined by an author',
            command: 'teiUnderline',
            toolbar: 'tei-underline'
        });

        // TEI-NOTE
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
                    editor.insertHtml(el.getHtml());
                }
                else if (editorSelection.getSelectedText().length > 0) {
                    var newElement = wrap(teiObject);
                    editor.insertElement(newElement);
                }
                else {
                    return false;
                }
                removeEmptyTags(editorSelection);
            }
        });
        editor.ui.addButton('TeiNote', {
            label: 'tei-note: inserts notes or\nannotations made by an author',
            command: 'teiNote',
            toolbar: 'tei-note'
        });

        // TEI-UNCLEAR
        editor.addCommand( 'teiUnclear', {
            exec: function( editor ) {
                var editorSelection = editor.getSelection();
                var range = editorSelection.getRanges()[ 0 ];
                var el = editor.document.createElement( 'div' );
                el.append(range.cloneContents());
                var commonAncestor = editorSelection.getCommonAncestor();

                var teiObject = {
                    elToInsert: el,
                    tag: 'span',
                    className: 'tei-unclear',
                    additionalAttributes: [],
                    conflictChildren: '.tei-unclear, .tei-p'
                }

                if (teiObject.className === commonAncestor.$.className || teiObject.className === commonAncestor.$.parentElement.className) {
                    editor.insertHtml(el.getHtml());
                }
                else if (editorSelection.getSelectedText().length > 0) {
                    var newElement = wrap(teiObject);
                    editor.insertElement(newElement);
                }
                else {
                    return false;
                }
                removeEmptyTags(editorSelection);
            }
        });
        editor.ui.addButton('TeiUnclear', {
            label: 'tei-unclear: highlights illegible text\nthat cannot be transcribed with certainty',
            command: 'teiUnclear',
            toolbar: 'tei-unclear'
        });

        // TEI-LINEBREAK
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

        // TEI-PAGEBREAK
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
                    var newElement = unwrapStartTag(el, teiObject.tag, teiObject.className);
                    editor.insertHtml(newElement);
                }
                else if (editorSelection.getSelectedText().length > 0) {
                    var newElement = wrap(teiObject);
                    editor.insertElement(newElement);
                }
                else {
                    return false;
                }
                removeEmptyTags(editorSelection);
            }
        });
        editor.ui.addButton('TeiPageBreak', {
            label: 'tei-pb: marks the beginning of\na new page in a paginated document',
            command: 'teiPageBreak',
            toolbar: 'tei-pb'
        });

        // TEI-PARAGRAPH
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
                    var html = "</p>"+el.getHtml()+"<p class='tei-p'>";
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
                removeEmptyTags(editorSelection);
            }
        });
        editor.ui.addButton('TeiParagraph', {
            label: 'tei-p: inserts a paragraph',
            command: 'teiParagraph',
            toolbar: 'tei-p'
        });

        // TODO - unwrap elements with only br in them
        // TODO - make sure that only markup relevant to the tag is removed, not all text markup - currently removing parents
    }
});